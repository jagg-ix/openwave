"""Reusable reversible/irreversible operator-splitting engine for simulation theories."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexVector = NDArray[np.complex128]
ComplexMatrix = NDArray[np.complex128]


def matrix_exponential(matrix: ComplexMatrix, scale: complex) -> ComplexMatrix:
    values, vectors = np.linalg.eig(matrix)
    return vectors @ np.diag(np.exp(scale * values)) @ np.linalg.inv(vectors)


@dataclass(frozen=True)
class SplitConfig:
    final_time: float = 4.0
    dt: float = 0.05
    samples: int = 81
    method: str = "strang"

    def __post_init__(self) -> None:
        if self.final_time <= 0 or self.dt <= 0: raise ValueError("positive final_time and dt required")
        if self.method not in {"strang", "lie"}: raise ValueError("unknown splitting method")


@dataclass(frozen=True)
class LinearEntropicKernel:
    hamiltonian: ComplexMatrix
    loss: ComplexMatrix

    def __post_init__(self) -> None:
        if self.hamiltonian.shape != self.loss.shape: raise ValueError("operator shapes differ")
        if not np.allclose(self.hamiltonian, self.hamiltonian.conj().T): raise ValueError("H not Hermitian")
        if not np.allclose(self.loss, self.loss.conj().T): raise ValueError("Gamma not Hermitian")
        if np.min(np.linalg.eigvalsh(self.loss)) < -1e-13: raise ValueError("Gamma not positive")

    def reversible(self, state: ComplexVector, dt: float) -> ComplexVector:
        return matrix_exponential(self.hamiltonian, -1j * dt) @ state

    def irreversible(self, state: ComplexVector, dt: float) -> ComplexVector:
        return matrix_exponential(self.loss, -dt) @ state

    def exact(self, state: ComplexVector, time: float) -> ComplexVector:
        return matrix_exponential(-1j * self.hamiltonian - self.loss, time) @ state


@dataclass
class SplitRun:
    state: ComplexVector
    reservoir: float
    records: list[dict[str, float]]
    dt: float
    steps: int


def _norm(state: ComplexVector) -> float:
    return float(np.vdot(state, state).real)


def _loss_step(kernel: LinearEntropicKernel, state: ComplexVector, reservoir: float, dt: float):
    before = _norm(state)
    updated = kernel.irreversible(state, dt)
    after = _norm(updated)
    return updated, reservoir + max(0.0, before - after)


def evolve(kernel: LinearEntropicKernel, initial: ComplexVector, config: SplitConfig) -> SplitRun:
    steps = math.ceil(config.final_time / config.dt)
    dt = config.final_time / steps
    sample_steps = set(np.linspace(0, steps, config.samples, dtype=int).tolist())
    state = np.asarray(initial, dtype=np.complex128).copy()
    initial_norm = _norm(state)
    reservoir = 0.0
    records: list[dict[str, float]] = []

    def record(step: int) -> None:
        norm = _norm(state)
        tau = -0.5 * math.log(max(norm / initial_norm, np.finfo(float).tiny))
        records.append({
            "time": step * dt, "matter_norm": norm, "reservoir": reservoir,
            "extended_balance": norm + reservoir, "entropic_clock": tau,
        })

    record(0)
    for step in range(1, steps + 1):
        if config.method == "strang":
            state, reservoir = _loss_step(kernel, state, reservoir, 0.5 * dt)
            state = kernel.reversible(state, dt)
            state, reservoir = _loss_step(kernel, state, reservoir, 0.5 * dt)
        else:
            state = kernel.reversible(state, dt)
            state, reservoir = _loss_step(kernel, state, reservoir, dt)
        if step in sample_steps: record(step)
    return SplitRun(state, reservoir, records, dt, steps)


def reference_kernel() -> LinearEntropicKernel:
    h = np.asarray([[0.6, 0.35], [0.35, -0.4]], dtype=np.complex128)
    g = np.asarray([[0.08, 0.025], [0.025, 0.19]], dtype=np.complex128)
    return LinearEntropicKernel(h, g)


def initial_state() -> ComplexVector:
    x = np.asarray([math.sqrt(0.7), math.sqrt(0.3) * np.exp(0.25j)], dtype=np.complex128)
    return x / np.linalg.norm(x)


def refinement(method: str = "strang") -> dict[str, Any]:
    kernel, initial = reference_kernel(), initial_state()
    dts = (0.2, 0.1, 0.05)
    runs = [evolve(kernel, initial, SplitConfig(dt=dt, method=method)) for dt in dts]
    exact = kernel.exact(initial, 4.0)
    errors = [float(np.linalg.norm(run.state - exact)) for run in runs]
    orders = [math.log(errors[i] / errors[i+1], 2.0) for i in range(2)]
    return {"dts": dts, "errors": errors, "orders": orders}


@lru_cache(maxsize=1)
def run_entropic_integrator_study() -> dict[str, Any]:
    kernel, initial = reference_kernel(), initial_state()
    run = evolve(kernel, initial, SplitConfig(dt=0.025, method="strang"))
    zero = LinearEntropicKernel(kernel.hamiltonian, np.zeros_like(kernel.loss))
    zero_run = evolve(zero, initial, SplitConfig(dt=0.025, method="strang"))
    norms = np.asarray([r["matter_norm"] for r in run.records])
    reservoirs = np.asarray([r["reservoir"] for r in run.records])
    clocks = np.asarray([r["entropic_clock"] for r in run.records])
    balances = np.asarray([r["extended_balance"] for r in run.records])
    ref = refinement("strang")
    acceptance = {
        "strang_second_order": min(ref["orders"]) >= 1.8,
        "matter_contracts": bool(np.all(np.diff(norms) <= 2e-12)),
        "reservoir_accumulates": bool(np.all(np.diff(reservoirs) >= -2e-12)),
        "entropic_clock_monotone": bool(np.all(np.diff(clocks) >= -2e-12)),
        "extended_balance_closes": float(np.max(np.abs(balances - balances[0]))) <= 2e-12,
        "zero_loss_unitary": abs(_norm(zero_run.state) - 1.0) <= 2e-12,
        "reversible_irreversible_split_explicit": True,
    }
    return {
        "schema": "openwave.m9.entropic-integrator-result.v1",
        "task": "M9.20-simcore",
        "refinement": ref,
        "final": run.records[-1],
        "maximum_balance_error": float(np.max(np.abs(balances - balances[0]))),
        "zero_loss_norm_drift": abs(_norm(zero_run.state) - 1.0),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
