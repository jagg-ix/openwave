"""M9.16: trace-preserving Lindblad information-loss qualification.

The selected two-level dephasing control evolves

    d rho / dt = -i [H, rho] + gamma (sigma_z rho sigma_z - rho),

with ``H = omega sigma_z / 2``.  Trace and populations are preserved while
coherence decays as ``exp(-(2 gamma + i omega)t)``.  This is deliberately kept
separate from M9.15's trace-decreasing imaginary-action amplitude loss.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Callable, Sequence

import numpy as np
from numpy.typing import NDArray

ComplexMatrix = NDArray[np.complex128]

SIGMA_Z: ComplexMatrix = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


@dataclass(frozen=True)
class LindbladParameters:
    omega: float = 1.1
    gamma: float = 0.23
    final_time: float = 4.0

    def __post_init__(self) -> None:
        if self.gamma < 0.0:
            raise ValueError("gamma must be nonnegative")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")


def initial_density() -> ComplexMatrix:
    population = 0.65
    phase = 0.4
    state = np.asarray(
        [math.sqrt(population), math.sqrt(1.0 - population) * np.exp(1j * phase)],
        dtype=np.complex128,
    )
    return np.outer(state, state.conj())


def hamiltonian(parameters: LindbladParameters) -> ComplexMatrix:
    return 0.5 * parameters.omega * SIGMA_Z


def lindblad_rhs(rho: ComplexMatrix, parameters: LindbladParameters) -> ComplexMatrix:
    h = hamiltonian(parameters)
    commutator = h @ rho - rho @ h
    dephasing = SIGMA_Z @ rho @ SIGMA_Z - rho
    return -1j * commutator + parameters.gamma * dephasing


def rk4_step(
    rho: ComplexMatrix,
    dt: float,
    rhs: Callable[[ComplexMatrix], ComplexMatrix],
) -> ComplexMatrix:
    k1 = rhs(rho)
    k2 = rhs(rho + 0.5 * dt * k1)
    k3 = rhs(rho + 0.5 * dt * k2)
    k4 = rhs(rho + dt * k3)
    return rho + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def exact_density(
    time: float,
    parameters: LindbladParameters,
    rho0: ComplexMatrix | None = None,
) -> ComplexMatrix:
    rho = initial_density() if rho0 is None else np.asarray(rho0, dtype=np.complex128)
    result = rho.copy()
    result[0, 1] *= np.exp(-(2.0 * parameters.gamma + 1j * parameters.omega) * time)
    result[1, 0] = result[0, 1].conj()
    return result


def von_neumann_entropy(rho: ComplexMatrix) -> float:
    hermitian = 0.5 * (rho + rho.conj().T)
    values = np.linalg.eigvalsh(hermitian)
    values = np.clip(values.real, 0.0, 1.0)
    nonzero = values[values > 1.0e-15]
    return -float(np.sum(nonzero * np.log(nonzero)))


def coherence_relative_entropy(rho: ComplexMatrix) -> float:
    diagonal = np.diag(np.diag(rho))
    return von_neumann_entropy(diagonal) - von_neumann_entropy(rho)


def purity(rho: ComplexMatrix) -> float:
    return float(np.trace(rho @ rho).real)


def evolve_lindblad(
    dt: float,
    parameters: LindbladParameters = LindbladParameters(),
    *,
    samples: int = 101,
) -> dict[str, Any]:
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    steps = max(1, math.ceil(parameters.final_time / dt))
    actual_dt = parameters.final_time / steps
    sample_steps = set(np.linspace(0, steps, samples, dtype=int).tolist())
    rho = initial_density()
    records: list[dict[str, float]] = []

    def record(step: int) -> None:
        exact = exact_density(step * actual_dt, parameters)
        eigenvalues = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T)).real
        records.append(
            {
                "time": step * actual_dt,
                "trace": float(np.trace(rho).real),
                "trace_imaginary": float(np.trace(rho).imag),
                "hermiticity_error": float(np.linalg.norm(rho - rho.conj().T)),
                "minimum_eigenvalue": float(np.min(eigenvalues)),
                "purity": purity(rho),
                "coherence_l1": 2.0 * float(abs(rho[0, 1])),
                "coherence_relative_entropy": coherence_relative_entropy(rho),
                "population_zero": float(rho[0, 0].real),
                "exact_error_frobenius": float(np.linalg.norm(rho - exact)),
            }
        )

    record(0)
    for step in range(1, steps + 1):
        rho = rk4_step(rho, actual_dt, lambda value: lindblad_rhs(value, parameters))
        if step in sample_steps:
            record(step)

    exact = exact_density(parameters.final_time, parameters)
    traces = np.asarray([item["trace"] for item in records])
    purities = np.asarray([item["purity"] for item in records])
    coherences = np.asarray([item["coherence_relative_entropy"] for item in records])
    return {
        "dt": actual_dt,
        "steps": steps,
        "final_error_frobenius": float(np.linalg.norm(rho - exact)),
        "max_trace_error": float(np.max(np.abs(traces - 1.0))),
        "max_hermiticity_error": float(max(item["hermiticity_error"] for item in records)),
        "minimum_eigenvalue": float(min(item["minimum_eigenvalue"] for item in records)),
        "max_population_drift": float(
            max(abs(item["population_zero"] - records[0]["population_zero"]) for item in records)
        ),
        "purity_monotone": bool(np.all(np.diff(purities) <= 2.0e-13)),
        "relative_coherence_monotone": bool(np.all(np.diff(coherences) <= 2.0e-13)),
        "final_purity": records[-1]["purity"],
        "final_coherence_l1": records[-1]["coherence_l1"],
        "final_relative_coherence": records[-1]["coherence_relative_entropy"],
        "records": records,
    }


def zero_loss_study(parameters: LindbladParameters = LindbladParameters()) -> dict[str, float]:
    zero = LindbladParameters(
        omega=parameters.omega,
        gamma=0.0,
        final_time=parameters.final_time,
    )
    result = evolve_lindblad(0.025, zero, samples=51)
    return {
        "final_error_frobenius": result["final_error_frobenius"],
        "max_trace_error": result["max_trace_error"],
        "purity_drift": abs(result["final_purity"] - 1.0),
        "coherence_drift": abs(
            result["final_coherence_l1"]
            - 2.0 * abs(initial_density()[0, 1])
        ),
    }


def refinement_study(steps: Sequence[float] = (0.2, 0.1, 0.05)) -> dict[str, Any]:
    records = [evolve_lindblad(dt, samples=81) for dt in steps]
    errors = [float(item["final_error_frobenius"]) for item in records]
    orders = [
        math.log(errors[index] / errors[index + 1], 2.0)
        for index in range(len(errors) - 1)
    ]
    return {
        "requested_dts": list(steps),
        "errors": errors,
        "observed_orders": orders,
        "records": [
            {key: value for key, value in item.items() if key != "records"}
            for item in records
        ],
    }


@lru_cache(maxsize=1)
def run_lindblad_information_study() -> dict[str, Any]:
    parameters = LindbladParameters()
    refinement = refinement_study()
    finest = evolve_lindblad(0.025, parameters, samples=121)
    zero_loss = zero_loss_study(parameters)
    initial_purity = purity(initial_density())
    acceptance = {
        "dephasing_rate_nonnegative": parameters.gamma >= 0.0,
        "rk4_converges_fourth_order": min(refinement["observed_orders"]) >= 3.8,
        "trace_preserved": finest["max_trace_error"] <= 2.0e-12,
        "hermiticity_preserved": finest["max_hermiticity_error"] <= 2.0e-12,
        "positivity_preserved": finest["minimum_eigenvalue"] >= -2.0e-12,
        "populations_preserved": finest["max_population_drift"] <= 2.0e-12,
        "information_loss_monotone": (
            finest["purity_monotone"]
            and finest["relative_coherence_monotone"]
            and finest["final_purity"] < initial_purity - 1.0e-3
        ),
        "zero_loss_reduces_to_unitary": (
            zero_loss["max_trace_error"] <= 2.0e-12
            and zero_loss["purity_drift"] <= 2.0e-8
            and zero_loss["coherence_drift"] <= 2.0e-8
        ),
    }
    return {
        "schema": "openwave.m9.lindblad-information-loss-result.v1",
        "task": "M9.16",
        "model": "selected trace-preserving two-level dephasing channel",
        "parameters": asdict(parameters),
        "refinement": refinement,
        "finest": {key: value for key, value in finest.items() if key != "records"},
        "zero_loss": zero_loss,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a trace-preserving completely positive dephasing control",
                "monotone purity and relative-coherence loss for the selected initial state",
                "fourth-order numerical convergence and the zero-dephasing unitary limit",
                "mathematical inequivalence to trace-decreasing amplitude loss",
            ],
            "does_not_establish": [
                "that dephasing is the CAT/EPT imaginary-action mechanism",
                "a unique information clock or physical time",
                "a spatial reservoir or energy-exchange model",
                "derivation of gamma from microscopic physics",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
