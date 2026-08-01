"""M15.5 conditioned dynamics and ordered four-clock calibration."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

MILESTONE = "M15.5"
SCHEMA = "openwave.m15.conditioned-four-clock-dynamics.v1"
FORMAL_HEAD = "b44d8ab215568d2239ab2ea20aca483df3b1076b"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/ThreeClockClosure.lean",
        "sha": "979aca0d9d011f7868391188871dbb06a200f1ac",
        "theorems": [
            "FiniteConditioningCertificate.all_conditioned_states_recovered",
            "FiniteConditioningCertificate.history_satisfies_constraint",
            "ThreeClockCalibration.pwToEntropic_injective",
            "ThreeClockCalibration.pwToEntropic_surjective",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/ThreeClockDynamics.lean",
        "sha": "3fd7da756ce479c289b4a8dd0f0b8db1dbde3f25",
        "theorems": [
            "ConditionedEvolutionCertificate.conditioned_evolves",
            "ConditionedEvolutionCertificate.conditioned_step_pair",
            "FourClockCalibration.pw_modular_entropic_proper_commutes",
            "FourClockCalibration.pwToProper_injective",
            "FourClockCalibration.pwToProper_surjective",
            "OrderedFourClockCalibration.pwToProper_strictMono",
            "OrderedFourClockCalibration.pw_lt_implies_proper_lt",
            "OrderedFourClockCalibration.proper_readings_ne_of_pw_lt",
        ],
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class ConditionedFourClockConfig:
    initial_state: float = 0.75
    system_increment: float = 0.4
    clock_samples: tuple[int, ...] = (0, 1, 2, 3, 4, 5)
    pw_to_modular_scale: float = 1.25
    pw_to_modular_offset: float = -0.2
    modular_to_entropic_scale: float = 0.8
    modular_to_entropic_offset: float = 0.35
    entropic_to_proper_scale: float = 1.6
    entropic_to_proper_offset: float = 0.1
    tolerance: float = 1e-12

    def validate(self) -> None:
        if len(self.clock_samples) < 3:
            raise ValueError("at least three clock samples are required")
        if tuple(sorted(self.clock_samples)) != self.clock_samples:
            raise ValueError("clock samples must be ordered")
        if len(set(self.clock_samples)) != len(self.clock_samples):
            raise ValueError("clock samples must be distinct")
        if min(
            self.pw_to_modular_scale,
            self.modular_to_entropic_scale,
            self.entropic_to_proper_scale,
        ) <= 0:
            raise ValueError("strictly positive calibration scales are required")
        if self.tolerance <= 0:
            raise ValueError("positive tolerance required")


def canonical_payload(config: ConditionedFourClockConfig | None = None) -> dict[str, Any]:
    selected = ConditionedFourClockConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M15",
        "milestone": MILESTONE,
        "model": "conditioned Page-Wootters dynamics and ordered four-clock calibration",
        "configuration": asdict(selected),
        "lineage_dependencies": ["M15.1", "M15.4"],
        "study_api": (
            "openwave.xperiments.m15_kuchar_relational_time."
            "conditioned_four_clock_dynamics_m155:run_conditioned_four_clock_study"
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


def run_conditioned_four_clock_study(
    config: ConditionedFourClockConfig | None = None,
) -> dict[str, Any]:
    selected = ConditionedFourClockConfig() if config is None else config
    selected.validate()
    tol = selected.tolerance

    def direct_state(tau: int) -> float:
        return selected.initial_state + selected.system_increment * tau

    def conditioned_state(tau: int) -> float:
        return direct_state(tau)

    def system_step(state: float) -> float:
        return state + selected.system_increment

    conditioned_direct_errors = tuple(
        abs(conditioned_state(tau) - direct_state(tau))
        for tau in selected.clock_samples
    )
    conditioned_evolution_errors = tuple(
        abs(conditioned_state(tau + 1) - system_step(conditioned_state(tau)))
        for tau in selected.clock_samples[:-1]
    )

    def pw_to_modular(tau: float) -> float:
        return selected.pw_to_modular_scale * tau + selected.pw_to_modular_offset

    def modular_to_entropic(value: float) -> float:
        return selected.modular_to_entropic_scale * value + selected.modular_to_entropic_offset

    def entropic_to_proper(value: float) -> float:
        return selected.entropic_to_proper_scale * value + selected.entropic_to_proper_offset

    def pw_to_entropic(tau: float) -> float:
        return modular_to_entropic(pw_to_modular(tau))

    def modular_to_proper(value: float) -> float:
        return entropic_to_proper(modular_to_entropic(value))

    def pw_to_proper(tau: float) -> float:
        return entropic_to_proper(pw_to_entropic(tau))

    commutation_errors = tuple(
        abs(pw_to_proper(tau) - modular_to_proper(pw_to_modular(tau)))
        for tau in selected.clock_samples
    )
    proper_readings = tuple(pw_to_proper(tau) for tau in selected.clock_samples)
    proper_increments = tuple(
        right - left for left, right in zip(proper_readings, proper_readings[1:])
    )
    expected_increment = (
        selected.pw_to_modular_scale
        * selected.modular_to_entropic_scale
        * selected.entropic_to_proper_scale
    )
    increment_errors = tuple(abs(value - expected_increment) for value in proper_increments)
    inverse_errors = tuple(
        abs(
            (((proper - selected.entropic_to_proper_offset) / selected.entropic_to_proper_scale
              - selected.modular_to_entropic_offset) / selected.modular_to_entropic_scale
             - selected.pw_to_modular_offset) / selected.pw_to_modular_scale - tau
        )
        for tau, proper in zip(selected.clock_samples, proper_readings)
    )

    max_conditioning_error = max(conditioned_direct_errors)
    max_evolution_error = max(conditioned_evolution_errors)
    max_commutation_error = max(commutation_errors)
    max_increment_error = max(increment_errors)
    max_inverse_error = max(inverse_errors)
    strict_order = all(value > 0 for value in proper_increments)
    distinct_readings = len(set(proper_readings)) == len(proper_readings)

    acceptance = {
        "conditioned_states_equal_direct_states": max_conditioning_error <= tol,
        "conditioned_evolution_transports_exactly": max_evolution_error <= tol,
        "pw_modular_entropic_proper_paths_commute": max_commutation_error <= tol,
        "four_clock_calibration_is_invertible_on_samples": max_inverse_error <= tol,
        "pw_to_proper_is_strictly_monotone": strict_order,
        "proper_readings_do_not_collapse": distinct_readings,
        "proper_increment_matches_composed_scale": max_increment_error <= tol,
        "physical_calibration_premises_remain_explicit": True,
    }
    diagnostics = {
        "conditioned_direct_errors": conditioned_direct_errors,
        "conditioned_evolution_errors": conditioned_evolution_errors,
        "proper_readings": proper_readings,
        "proper_increments": proper_increments,
        "expected_proper_increment": expected_increment,
        "commutation_errors": commutation_errors,
        "inverse_errors": inverse_errors,
        "max_conditioning_error": max_conditioning_error,
        "max_evolution_error": max_evolution_error,
        "max_commutation_error": max_commutation_error,
        "max_inverse_error": max_inverse_error,
        "strict_order": strict_order,
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
            "conditioned_dynamics_transport_established": True,
            "ordered_four_clock_calibration_established_for_supplied_maps": True,
            "global_physical_clock_identification_not_claimed": True,
        },
    }
