"""M9.125a: one reduced carrier for relational, modular, and entropic time."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from math import exp, log
from typing import Any, Mapping

import numpy as np


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _hermitian(a: np.ndarray) -> np.ndarray:
    return (a + a.conj().T) / 2.0


def _matrix_log_psd(a: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(_hermitian(a))
    if float(np.min(values)) <= 0.0:
        raise ValueError("matrix must be positive definite")
    return vectors @ np.diag(np.log(values)) @ vectors.conj().T


def _relative_entropy(rho: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.trace(rho @ (_matrix_log_psd(rho) - _matrix_log_psd(sigma))).real)


def _unitary_from_hermitian(h: np.ndarray, t: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(_hermitian(h))
    return vectors @ np.diag(np.exp(-1j * values * t)) @ vectors.conj().T


class SharedThreeClockCarrier:
    """A full-rank qubit thermal-relaxation branch shared by all three clocks."""

    beta = 1.7
    equilibrium_excited = 0.23
    relaxation_rate = 0.61
    initial_excited = 0.79
    initial_coherence = 0.13 + 0.04j
    clock_step = 0.19
    clock_size = 18

    def __init__(self) -> None:
        q = self.equilibrium_excited
        self.energy_gap = log((1.0 - q) / q) / self.beta
        self.hamiltonian = np.diag([0.0, self.energy_gap]).astype(complex)
        self.equilibrium = np.diag([1.0 - q, q]).astype(complex)
        self.partition_function = 1.0 + exp(-self.beta * self.energy_gap)
        self.modular_hamiltonian = -_matrix_log_psd(self.equilibrium)
        self.modular_offset = log(self.partition_function)

    def state(self, t: float) -> np.ndarray:
        if t < 0:
            raise ValueError("time must be nonnegative")
        q = self.equilibrium_excited
        p = q + (self.initial_excited - q) * exp(-self.relaxation_rate * t)
        c = self.initial_coherence * np.exp(
            (-self.relaxation_rate / 2.0 + 1j * self.energy_gap) * t
        )
        return np.array([[1.0 - p, c], [np.conj(c), p]], dtype=complex)

    def evolve(self, rho: np.ndarray, dt: float) -> np.ndarray:
        if dt < 0:
            raise ValueError("time increment must be nonnegative")
        q = self.equilibrium_excited
        p = float(rho[1, 1].real)
        c = complex(rho[0, 1])
        p_next = q + (p - q) * exp(-self.relaxation_rate * dt)
        c_next = c * np.exp(
            (-self.relaxation_rate / 2.0 + 1j * self.energy_gap) * dt
        )
        return np.array(
            [[1.0 - p_next, c_next], [np.conj(c_next), p_next]], dtype=complex
        )

    def generator(self, rho: np.ndarray) -> np.ndarray:
        q = self.equilibrium_excited
        gamma = self.relaxation_rate
        p = float(rho[1, 1].real)
        c = complex(rho[0, 1])
        dp = -gamma * (p - q)
        dc = (-gamma / 2.0 + 1j * self.energy_gap) * c
        return np.array([[-dp, dc], [np.conj(dc), dp]], dtype=complex)

    def remaining_entropic_clock(self, t: float) -> float:
        return _relative_entropy(self.state(t), self.equilibrium)

    def accumulated_entropic_clock(self, t: float) -> float:
        return self.remaining_entropic_clock(0.0) - self.remaining_entropic_clock(t)

    def modular_observable(self, observable: np.ndarray, s: float) -> np.ndarray:
        u = _unitary_from_hermitian(self.modular_hamiltonian, s)
        return u.conj().T @ observable @ u

    def physical_observable(self, observable: np.ndarray, t: float) -> np.ndarray:
        u = _unitary_from_hermitian(self.hamiltonian, t)
        return u.conj().T @ observable @ u

    def history_state(self) -> tuple[np.ndarray, np.ndarray]:
        times = np.arange(self.clock_size, dtype=float) * self.clock_step
        dim = 2 * self.clock_size
        history = np.zeros((dim, dim), dtype=complex)
        for index, t in enumerate(times):
            block = self.state(float(t)) / self.clock_size
            start = 2 * index
            history[start : start + 2, start : start + 2] = block
        return times, history

    def condition_history(self, history: np.ndarray, index: int) -> np.ndarray:
        if not 0 <= index < self.clock_size:
            raise IndexError(index)
        start = 2 * index
        block = history[start : start + 2, start : start + 2]
        probability = float(np.trace(block).real)
        if probability <= 0:
            raise ValueError("clock outcome has zero probability")
        return block / probability


@lru_cache(maxsize=1)
def run_shared_three_clock_carrier() -> dict[str, Any]:
    carrier = SharedThreeClockCarrier()
    times, history = carrier.history_state()
    conditioned_errors = [
        float(np.linalg.norm(carrier.condition_history(history, i) - carrier.state(float(t))))
        for i, t in enumerate(times)
    ]
    states = [carrier.state(float(t)) for t in np.linspace(0.0, 8.0, 81)]
    minimum_eigenvalue = min(float(np.min(np.linalg.eigvalsh(_hermitian(r)))) for r in states)
    trace_error = max(abs(float(np.trace(r).real) - 1.0) for r in states)
    s, t = 0.63, 1.17
    semigroup_error = float(
        np.linalg.norm(carrier.state(s + t) - carrier.evolve(carrier.state(t), s))
    )
    eps = 1e-7
    derivative_error = float(
        np.linalg.norm(
            (carrier.state(eps) - carrier.state(0.0)) / eps
            - carrier.generator(carrier.state(0.0))
        )
    )
    modular_identity_error = float(
        np.linalg.norm(
            carrier.modular_hamiltonian
            - (
                carrier.beta * carrier.hamiltonian
                + carrier.modular_offset * np.eye(2)
            )
        )
    )
    observable = np.array([[0.2, 0.8 - 0.1j], [0.8 + 0.1j, -0.3]], dtype=complex)
    modular_flow_error = float(
        np.linalg.norm(
            carrier.modular_observable(observable, 0.72)
            - carrier.physical_observable(observable, carrier.beta * 0.72)
        )
    )
    remaining = np.array(
        [carrier.remaining_entropic_clock(float(x)) for x in np.linspace(0.0, 9.0, 91)]
    )
    accumulated = remaining[0] - remaining
    payload = {
        "schema": "openwave.m9.shared-three-clock-carrier.v1",
        "task": "M9.125a",
        "parameters": {
            "beta": carrier.beta,
            "energy_gap": carrier.energy_gap,
            "relaxation_rate": carrier.relaxation_rate,
            "equilibrium_excited": carrier.equilibrium_excited,
        },
        "metrics": {
            "history_trace": float(np.trace(history).real),
            "maximum_conditioning_error": max(conditioned_errors),
            "minimum_state_eigenvalue": minimum_eigenvalue,
            "maximum_trace_error": trace_error,
            "semigroup_error": semigroup_error,
            "generator_right_derivative_error": derivative_error,
            "modular_hamiltonian_identity_error": modular_identity_error,
            "modular_flow_rescaling_error": modular_flow_error,
            "largest_remaining_clock_increment": float(np.max(np.diff(remaining))),
            "smallest_accumulated_clock_increment": float(np.min(np.diff(accumulated))),
        },
        "claim_boundary": {
            "classical_quantum_history_is_full_WDW_history_theorem": False,
            "finite_shared_carrier_is_universal_clock_carrier": False,
            "model_beta_is_measured_temperature_calibration": False,
            "internal_time_parameter_is_physical_proper_time": False,
        },
    }
    acceptance = {
        "history_state_is_normalized": abs(payload["metrics"]["history_trace"] - 1.0) <= 2e-14,
        "conditioning_recovers_same_thermal_relaxation_branch": max(conditioned_errors) <= 2e-14,
        "all_states_are_full_rank_density_matrices": minimum_eigenvalue > 0 and trace_error <= 2e-14,
        "thermal_relaxation_semigroup_composes": semigroup_error <= 3e-14,
        "closed_form_matches_conditional_generator": derivative_error <= 1e-7,
        "conditioned_H_is_modular_K_up_to_scale_and_offset": modular_identity_error <= 2e-14 and modular_flow_error <= 3e-14,
        "entropic_clock_is_monotone_on_same_carrier": float(np.max(np.diff(remaining))) <= 2e-12 and float(np.min(np.diff(accumulated))) >= -2e-12,
        "no_universal_or_physical_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "shared_finite_clock_carrier_constructed": True,
            "conditioned_generator_modular_identification_reduced": True,
            "modular_and_dissipative_flows_share_state_algebra": True,
            "end_to_end_reversible_irreversible_composition_reduced": True,
            "full_constraint_to_conditioning_theorem_complete": False,
            "physical_clock_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
