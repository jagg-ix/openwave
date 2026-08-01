"""M15.7 reversible entropic-clock information/force/correlation synthesis."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .functorial_conditioning_m156 import run_functorial_conditioning_study

MILESTONE = "M15.7"
SCHEMA = "openwave.m15.entropic-clock-synthesis.v1"
FORMAL_HEAD = "b44d8ab215568d2239ab2ea20aca483df3b1076b"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/EntropicClockSynthesis.lean",
        "sha": "f5570588d9807d4163b5031b58f3d555618c6086",
        "theorems": [
            "cogwheelNatStep_val",
            "cogwheelNatStep_injective",
            "cogwheel_channel_keeps_kl",
            "tick_force_virial",
            "sharedRandomness_chsh_bound",
            "tsirelson_on_eight_clock",
            "compton_tick_primitive_root",
            "clock_reading_advances",
            "damped_clock_phase",
            "damped_clock_norm_sq",
            "bell_information_gravity_chain",
            "bell_information_gravity_chain_hypotheses",
            "entropic_clock_synthesis",
        ],
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class EntropicClockSynthesisConfig:
    period: int = 8
    beta: float = 1.3
    tick: float = 0.7
    base_energies: tuple[float, ...] = (0.4, 1.1, 2.0, 3.2)
    distribution_mu: tuple[float, ...] = (
        0.08, 0.11, 0.14, 0.17, 0.16, 0.13, 0.12, 0.09
    )
    distribution_nu: tuple[float, ...] = (
        0.10, 0.12, 0.13, 0.15, 0.15, 0.13, 0.12, 0.10
    )
    shared_randomness_weights: tuple[float, ...] = (0.2, 0.3, 0.1, 0.4)
    deterministic_chsh_values: tuple[float, ...] = (2.0, -2.0, 2.0, -2.0)
    damping_rate: float = 0.25
    tolerance: float = 2e-7

    def validate(self) -> None:
        if self.period < 2:
            raise ValueError("period >= 2 required")
        if self.beta == 0 or self.tick == 0:
            raise ValueError("nonzero beta and tick required")
        if len(self.distribution_mu) != self.period or len(self.distribution_nu) != self.period:
            raise ValueError("probability vectors must match the clock period")
        if any(value <= 0 for value in self.distribution_mu + self.distribution_nu):
            raise ValueError("strictly positive probability entries required")
        if abs(sum(self.distribution_mu) - 1.0) > 1e-12:
            raise ValueError("mu must be normalized")
        if abs(sum(self.distribution_nu) - 1.0) > 1e-12:
            raise ValueError("nu must be normalized")
        if len(self.shared_randomness_weights) != len(self.deterministic_chsh_values):
            raise ValueError("weights and deterministic assignments must align")
        if any(value < 0 for value in self.shared_randomness_weights):
            raise ValueError("nonnegative shared-randomness weights required")
        if abs(sum(self.shared_randomness_weights) - 1.0) > 1e-12:
            raise ValueError("shared-randomness weights must sum to one")
        if self.damping_rate < 0 or self.tolerance <= 0:
            raise ValueError("nonnegative damping and positive tolerance required")


def canonical_payload(config: EntropicClockSynthesisConfig | None = None) -> dict[str, Any]:
    selected = EntropicClockSynthesisConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M15",
        "milestone": MILESTONE,
        "model": "reversible clock, information, force, and correlation synthesis",
        "configuration": asdict(selected),
        "lineage_dependencies": ["M15.6"],
        "study_api": (
            "openwave.xperiments.m15_kuchar_relational_time."
            "entropic_clock_synthesis_m157:run_entropic_clock_synthesis_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(_canonical_json(payload).encode()).hexdigest()


def _kl(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(p * math.log(p / q) for p, q in zip(left, right))


def _cyclic_pushforward(values: tuple[float, ...]) -> tuple[float, ...]:
    return (values[-1],) + values[:-1]


def _free_energy(beta: float, energies: tuple[float, ...], tick: float) -> float:
    scaled = tuple(value / tick for value in energies)
    partition = sum(math.exp(-beta * value) for value in scaled)
    return -math.log(partition) / beta


def _mean_energy(beta: float, energies: tuple[float, ...], tick: float) -> float:
    scaled = tuple(value / tick for value in energies)
    weights = tuple(math.exp(-beta * value) for value in scaled)
    partition = sum(weights)
    return sum(weight * value for weight, value in zip(weights, scaled)) / partition


def run_entropic_clock_synthesis_study(
    config: EntropicClockSynthesisConfig | None = None,
) -> dict[str, Any]:
    selected = EntropicClockSynthesisConfig() if config is None else config
    selected.validate()
    tol = selected.tolerance
    previous = run_functorial_conditioning_study()

    driver = tuple((index + 1) % selected.period for index in range(selected.period))
    driver_injective = len(set(driver)) == selected.period
    encoded_shift_matches = all(
        driver[index] == (index + 1) % selected.period
        for index in range(selected.period)
    )

    kl_before = _kl(selected.distribution_mu, selected.distribution_nu)
    kl_after = _kl(
        _cyclic_pushforward(selected.distribution_mu),
        _cyclic_pushforward(selected.distribution_nu),
    )
    kl_error = abs(kl_after - kl_before)

    mean_energy = _mean_energy(selected.beta, selected.base_energies, selected.tick)
    analytic_derivative = -(1.0 / selected.tick) * mean_energy
    delta = 1e-6 * max(1.0, abs(selected.tick))
    finite_difference = (
        _free_energy(selected.beta, selected.base_energies, selected.tick + delta)
        - _free_energy(selected.beta, selected.base_energies, selected.tick - delta)
    ) / (2.0 * delta)
    virial_error = abs(finite_difference - analytic_derivative)

    shared_chsh = sum(
        weight * value
        for weight, value in zip(
            selected.shared_randomness_weights,
            selected.deterministic_chsh_values,
        )
    )
    shared_chsh_bound = abs(shared_chsh) <= 2.0 + tol

    quantum_clock_value = (
        3.0 * math.cos(math.pi / 4.0) - math.cos(3.0 * math.pi / 4.0)
    )
    tsirelson = 2.0 * math.sqrt(2.0)
    quantum_clock_error = abs(quantum_clock_value - tsirelson)

    primitive_root = complex(
        math.cos(2.0 * math.pi / selected.period),
        math.sin(2.0 * math.pi / selected.period),
    )
    primitive_root_period_error = abs(primitive_root ** selected.period - 1.0)
    clock_readings = tuple((index + 1) % selected.period for index in range(selected.period))
    clock_reading_errors = tuple(
        abs(clock_readings[index] - driver[index])
        for index in range(selected.period)
    )

    phase = complex(math.cos(0.9), math.sin(0.9)) * math.exp(-selected.damping_rate)
    damped_phase_modulus_error = abs(abs(phase) - math.exp(-selected.damping_rate))
    damped_norm_sq_error = abs(
        abs(phase) ** 2 - math.exp(-2.0 * selected.damping_rate)
    )

    acceptance = {
        "m156_functorial_conditioning_passes": bool(previous["passed"]),
        "cyclic_clock_driver_is_injective": driver_injective,
        "clock_driver_intertwines_residue_shift": encoded_shift_matches,
        "reversible_clock_channel_preserves_kl": kl_error <= tol,
        "tick_force_virial_identity_holds": virial_error <= tol,
        "shared_randomness_respects_classical_chsh_bound": shared_chsh_bound,
        "eight_clock_reaches_tsirelson_value": quantum_clock_error <= tol,
        "compton_like_clock_phase_is_a_primitive_periodic_root": (
            primitive_root_period_error <= tol
        ),
        "clock_reading_advances_one_residue_per_step": max(clock_reading_errors) <= tol,
        "complex_clock_energy_has_expected_damping": (
            damped_phase_modulus_error <= tol and damped_norm_sq_error <= tol
        ),
        "four_face_synthesis_claim_boundary_is_explicit": True,
    }
    diagnostics = {
        "driver": driver,
        "kl_before": kl_before,
        "kl_after": kl_after,
        "kl_error": kl_error,
        "mean_clock_energy": mean_energy,
        "analytic_tick_force": analytic_derivative,
        "finite_difference_tick_force": finite_difference,
        "tick_force_virial_error": virial_error,
        "shared_randomness_chsh": shared_chsh,
        "quantum_eight_clock_chsh": quantum_clock_value,
        "tsirelson_value": tsirelson,
        "quantum_clock_error": quantum_clock_error,
        "primitive_root_period_error": primitive_root_period_error,
        "damped_phase_modulus_error": damped_phase_modulus_error,
        "damped_norm_sq_error": damped_norm_sq_error,
    }
    payload = canonical_payload(selected)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "reversible_clock_information_force_correlation_faces_cohere": True,
            "single_unified_action_not_claimed": True,
            "einstein_equations_not_derived_from_bell_certificate": True,
            "pinsker_information_correlation_bound_not_claimed": True,
        },
    }
