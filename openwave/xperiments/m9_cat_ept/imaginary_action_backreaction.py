"""M9.15: bounded imaginary-action amplitude-loss qualification.

The selected control evolves an unnormalized two-level state by

    d psi / dt = (-i H_R - Gamma) psi,

with positive-semidefinite ``Gamma``.  For the scalar-loss gate
``Gamma = gamma I`` and a normalized initial state,

    ||psi(t)||^2 = exp(-2 gamma t),
    tau_ent(t) = -1/2 log ||psi(t)||^2 = gamma t,
    |W(t)| = exp(-tau_ent(t)).

This is a selected non-Hermitian model, not a derivation of physical time.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Callable, Sequence

import numpy as np
from numpy.typing import NDArray

ComplexVector = NDArray[np.complex128]
ComplexMatrix = NDArray[np.complex128]
RealArray = NDArray[np.float64]

SIGMA_X: ComplexMatrix = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
SIGMA_Z: ComplexMatrix = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
IDENTITY: ComplexMatrix = np.eye(2, dtype=np.complex128)


@dataclass(frozen=True)
class ImaginaryActionParameters:
    omega: float = 1.3
    mixing: float = 0.35
    gamma: float = 0.17
    final_time: float = 5.0

    def __post_init__(self) -> None:
        if self.gamma < 0.0:
            raise ValueError("gamma must be nonnegative")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")


def initial_state() -> ComplexVector:
    state = np.asarray(
        [math.sqrt(0.7), math.sqrt(0.3) * np.exp(0.3j)],
        dtype=np.complex128,
    )
    return state / np.linalg.norm(state)


def real_hamiltonian(parameters: ImaginaryActionParameters) -> ComplexMatrix:
    return 0.5 * parameters.omega * SIGMA_Z + parameters.mixing * SIGMA_X


def matrix_exponential_hermitian(matrix: ComplexMatrix, factor: complex) -> ComplexMatrix:
    values, vectors = np.linalg.eigh(matrix)
    return (vectors * np.exp(factor * values)[None, :]) @ vectors.conj().T


def exact_uniform_state(
    time: float,
    parameters: ImaginaryActionParameters,
    state0: ComplexVector | None = None,
) -> ComplexVector:
    state = initial_state() if state0 is None else np.asarray(state0, dtype=np.complex128)
    unitary = matrix_exponential_hermitian(real_hamiltonian(parameters), -1j * time)
    return np.exp(-parameters.gamma * time) * (unitary @ state)


def rhs_uniform(
    state: ComplexVector,
    parameters: ImaginaryActionParameters,
) -> ComplexVector:
    return (-1j * real_hamiltonian(parameters) - parameters.gamma * IDENTITY) @ state


def rk4_step(
    state: ComplexVector,
    dt: float,
    rhs: Callable[[ComplexVector], ComplexVector],
) -> ComplexVector:
    k1 = rhs(state)
    k2 = rhs(state + 0.5 * dt * k1)
    k3 = rhs(state + 0.5 * dt * k2)
    k4 = rhs(state + dt * k3)
    return state + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def evolve_uniform(
    dt: float,
    parameters: ImaginaryActionParameters = ImaginaryActionParameters(),
    *,
    samples: int = 101,
) -> dict[str, Any]:
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    steps = max(1, math.ceil(parameters.final_time / dt))
    actual_dt = parameters.final_time / steps
    sample_steps = set(np.linspace(0, steps, samples, dtype=int).tolist())
    state = initial_state()
    records: list[dict[str, float]] = []

    def record(step: int) -> None:
        time = step * actual_dt
        norm = float(np.vdot(state, state).real)
        tau = -0.5 * math.log(max(norm, np.finfo(float).tiny))
        exact_norm = math.exp(-2.0 * parameters.gamma * time)
        records.append(
            {
                "time": time,
                "norm": norm,
                "tau_ent": tau,
                "weight_modulus": math.sqrt(norm),
                "exact_norm": exact_norm,
                "exact_tau_ent": parameters.gamma * time,
            }
        )

    record(0)
    for step in range(1, steps + 1):
        state = rk4_step(state, actual_dt, lambda value: rhs_uniform(value, parameters))
        if step in sample_steps:
            record(step)

    exact = exact_uniform_state(parameters.final_time, parameters)
    error = float(np.linalg.norm(state - exact))
    norms = np.asarray([item["norm"] for item in records])
    taus = np.asarray([item["tau_ent"] for item in records])
    return {
        "dt": actual_dt,
        "steps": steps,
        "state_error_l2": error,
        "final_norm": records[-1]["norm"],
        "final_exact_norm": records[-1]["exact_norm"],
        "final_tau_ent": records[-1]["tau_ent"],
        "final_exact_tau_ent": records[-1]["exact_tau_ent"],
        "max_norm_error": float(
            max(abs(item["norm"] - item["exact_norm"]) for item in records)
        ),
        "max_tau_error": float(
            max(abs(item["tau_ent"] - item["exact_tau_ent"]) for item in records)
        ),
        "norm_monotone": bool(np.all(np.diff(norms) <= 2.0e-13)),
        "tau_monotone": bool(np.all(np.diff(taus) >= -2.0e-13)),
        "weight_identity_error": float(
            max(
                abs(item["weight_modulus"] - math.exp(mitem["tau_ent"]))
                for item in records
            )
        ),
        "records": records,
    }


def nonuniform_loss_study(
    parameters: ImaginaryActionParameters = ImaginaryActionParameters(),
) -> dict[str, float | bool]:
    gamma_matrix = np.diag([0.08, 0.22]).astype(np.complex128)
    minimum_eigenvalue = float(np.min(np.linalg.eigvalsh(gamma_matrix)))
    state = initial_state()
    dt = 0.0025
    steps = math.ceil(parameters.final_time / dt)
    dt = parameters.final_time / steps
    hamiltonian = real_hamiltonian(parameters)
    initial_z = float(np.vdot(state, SIGMA_Z @ state).real)
    maximum_norm_derivative = -math.inf
    minimum_norm_derivative = math.inf
    previous_norm = float(np.vdot(state, state).real)
    monotone = True
    for _ in range(steps):
        derivative = -2.0 * float(np.vdot(state, gamma_matrix @ state).real)
        maximum_norm_derivative = max(maximum_norm_derivative, derivative)
        minimum_norm_derivative = min(minimum_norm_derivative, derivative)
        state = rk4_step(
            state,
            dt,
            lambda value: (-1j * hamiltonian - gamma_matrix) @ value,
        )
        norm = float(np.vdot(state, state).real)
        monotone = monotone and norm <= previous_norm + 2.0e-13
        previous_norm = norm
    normalized = state / np.linalg.norm(state)
    final_z = float(np.vdot(normalized, SIGMA_Z @ normalized).real)
    return {
        "minimum_gamma_eigenvalue": minimum_eigenvalue,
        "minimum_norm_derivative": minimum_norm_derivative,
        "maximum_norm_derivative": maximum_norm_derivative,
        "norm_monotone": monotone,
        "initial_normalized_sigma_z": initial_z,
        "final_normalized_sigma_z": final_z,
        "normalized_sigma_z_change": final_z - initial_z,
    }


def zero_loss_study(
    parameters: ImaginaryActionParameters = ImaginaryActionParameters(),
) -> dict[str, float]:
    zero = ImaginaryActionParameters(
        omega=parameters.omega,
        mixing=parameters.mixing,
        gamma=0.0,
        final_time=parameters.final_time,
    )
    numerical = evolve_uniform(0.025, zero, samples=51)
    return {
        "state_error_l2": numerical["state_error_l2"],
        "norm_drift": abs(numerical["final_norm"] - 1.0),
        "tau_ent": numerical["final_tau_ent"],
    }


def refinement_study(
    steps: Sequence[float] = (0.2, 0.1, 0.05),
) -> dict[str, Any]:
    records = [evolve_uniform(dt, samples=81) for dt in steps]
    errors = [float(item["state_error_l2"]) for item in records]
    orders = [
        math.log(errors[index] / errors[index + 1], 2.0)
        for index in range(len(errors) - 1)
    ]
    return {
        "requested_dts": list(steps),
        "records": [
            {
                key: value
                for key, value in item.items()
                if key != "records"
            }
            for item in records
        ],
        "errors": errors,
        "observed_orders": orders,
    }


@lru_cache(maxsize=1)
def run_imaginary_action_study() -> dict[str, Any]:
    parameters = ImaginaryActionParameters()
    refinement = refinement_study()
    finest = evolve_uniform(0.025, parameters, samples=121)
    nonuniform = nonuniform_loss_study(parameters)
    zero_loss = zero_loss_study(parameters)
    acceptance = {
        "scalar_loss_positive": parameters.gamma > 0.0,
        "rk4_converges_fourth_order": min(refinement["observed_orders"]) >= 3.8,
        "norm_monotone": finest["norm_monotone"],
        "tau_ent_monotone": finest["tau_monotone"],
        "imaginary_action_identity_closes": finest["max_tau_error"] <= 2.0e-8,
        "weight_modulus_identity_closes": finest["weight_identity_error"] <= 2.0e-15,
        "zero_loss_reduces_to_unitary": (
            zero_loss["norm_drift"] <= 2.0e-8
            and zero_loss["state_error_l2"] <= 2.0e-7
            and abs(zero_loss["tau_ent"]) <= 2.0e-8
        ),
        "positive_nonuniform_loss_is_contracting": (
            nonuniform["minimum_gamma_eigenvalue"] >= 0.0
            and nonuniform["maximum_norm_derivative"] <= 1.0e-13
            and bool(nonuniform["norm_monotone"])
        ),
    }
    return {
        "schema": "openwave.m9.imaginary-action-result.v1",
        "task": "M9.15",
        "model": "selected positive non-Hermitian two-level control",
        "parameters": asdict(parameters),
        "refinement": refinement,
        "finest": {key: value for key, value in finest.items() if key != "records"},
        "nonuniform_loss": nonuniform,
        "zero_loss": zero_loss,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a positive scalar imaginary-action amplitude-loss control",
                "tau_ent=-1/2 log norm and |W|=exp(-tau_ent) for that control",
                "fourth-order numerical convergence and the zero-loss unitary limit",
                "contractivity for a selected positive nonuniform loss matrix",
            ],
            "does_not_establish": [
                "that Nature uses the selected non-Hermitian generator",
                "a trace-preserving open-system evolution",
                "a unique physical-time operator or particle identity",
                "derivation of gamma from CAT/EPT",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
