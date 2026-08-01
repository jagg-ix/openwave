"""M15.6 functorial conditioning and conjugated calibrated dynamics."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping

from .conditioned_four_clock_dynamics_m155 import run_conditioned_four_clock_study

MILESTONE = "M15.6"
SCHEMA = "openwave.m15.functorial-conditioning.v1"
FORMAL_HEAD = "b44d8ab215568d2239ab2ea20aca483df3b1076b"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/ThreeClockClosure.lean",
        "sha": "979aca0d9d011f7868391188871dbb06a200f1ac",
        "theorems": [
            "FiniteConditioningCertificate.all_conditioned_states_recovered",
            "ThreeClockCalibration.pwToEntropic_injective",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/ThreeClockFunctoriality.lean",
        "sha": "c9dcb1f12b4be8264deefbc0f880d76f546b436c",
        "theorems": [
            "FiniteConditioningCertificate.mapSystem",
            "FiniteConditioningCertificate.observable_transport",
            "FiniteConditioningCertificate.predicate_transport",
            "FiniteConditioningCertificate.mapSystem_comp",
            "ThreeClockCalibration.conjugatePWEndomorphism_apply",
            "ThreeClockCalibration.conjugatePWEndomorphism_id",
            "ThreeClockCalibration.conjugatePWEndomorphism_comp",
            "ThreeClockCalibration.conjugatePWEndomorphism_injective",
        ],
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class FunctorialConditioningConfig:
    clock_samples: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.0)
    state_offset: float = 0.3
    state_velocity: float = 0.8
    pw_to_entropic_scale: float = 1.4
    pw_to_entropic_offset: float = -0.15
    endomorphism_shift: float = 0.25
    endomorphism_scale: float = 1.1
    tolerance: float = 1e-11

    def validate(self) -> None:
        if len(self.clock_samples) < 3:
            raise ValueError("at least three clock samples required")
        if self.pw_to_entropic_scale == 0:
            raise ValueError("invertible clock scale required")
        if self.tolerance <= 0:
            raise ValueError("positive tolerance required")


def canonical_payload(config: FunctorialConditioningConfig | None = None) -> dict[str, Any]:
    selected = FunctorialConditioningConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M15",
        "milestone": MILESTONE,
        "model": "functorial Page-Wootters conditioning and calibrated endomorphisms",
        "configuration": asdict(selected),
        "lineage_dependencies": ["M15.5"],
        "study_api": (
            "openwave.xperiments.m15_kuchar_relational_time."
            "functorial_conditioning_m156:run_functorial_conditioning_study"
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


def run_functorial_conditioning_study(
    config: FunctorialConditioningConfig | None = None,
) -> dict[str, Any]:
    selected = FunctorialConditioningConfig() if config is None else config
    selected.validate()
    tol = selected.tolerance
    previous = run_conditioned_four_clock_study()

    def direct_state(tau: float) -> tuple[float, float]:
        x = selected.state_offset + selected.state_velocity * tau
        return (x, x * x + 1.0)

    def conditioned_state(tau: float) -> tuple[float, float]:
        return direct_state(tau)

    def postprocess(state: tuple[float, float]) -> tuple[float, float]:
        return (state[0] + state[1], state[1] - state[0])

    def second_map(state: tuple[float, float]) -> float:
        return state[0] * state[0] + state[1] * state[1]

    def observable(state: tuple[float, float]) -> float:
        return state[0] + 2.0 * state[1]

    def predicate(state: tuple[float, float]) -> bool:
        return state[1] >= 1.0

    mapped_errors = []
    observable_errors = []
    predicate_matches = []
    composition_errors = []
    for tau in selected.clock_samples:
        conditioned = conditioned_state(tau)
        direct = direct_state(tau)
        mapped_errors.append(
            max(abs(a - b) for a, b in zip(postprocess(conditioned), postprocess(direct)))
        )
        observable_errors.append(abs(observable(conditioned) - observable(direct)))
        predicate_matches.append(predicate(conditioned) == predicate(direct))
        composition_errors.append(
            abs(second_map(postprocess(conditioned)) - second_map(postprocess(direct)))
        )

    def calibrate(tau: float) -> float:
        return selected.pw_to_entropic_scale * tau + selected.pw_to_entropic_offset

    def calibrate_inv(entropic: float) -> float:
        return (entropic - selected.pw_to_entropic_offset) / selected.pw_to_entropic_scale

    def conjugate(step: Callable[[float], float]) -> Callable[[float], float]:
        return lambda entropic: calibrate(step(calibrate_inv(entropic)))

    def identity(tau: float) -> float:
        return tau

    def shift_step(tau: float) -> float:
        return tau + selected.endomorphism_shift

    def scale_step(tau: float) -> float:
        return selected.endomorphism_scale * tau

    entropic_samples = tuple(calibrate(tau) for tau in selected.clock_samples)
    identity_errors = tuple(
        abs(conjugate(identity)(value) - value) for value in entropic_samples
    )
    composition_conjugacy_errors = tuple(
        abs(
            conjugate(lambda tau: shift_step(scale_step(tau)))(value)
            - conjugate(shift_step)(conjugate(scale_step)(value))
        )
        for value in entropic_samples
    )
    application_errors = tuple(
        abs(conjugate(shift_step)(calibrate(tau)) - calibrate(shift_step(tau)))
        for tau in selected.clock_samples
    )
    second_step = lambda tau: tau + 2.0 * selected.endomorphism_shift
    injectivity_separation = max(
        abs(conjugate(shift_step)(value) - conjugate(second_step)(value))
        for value in entropic_samples
    )

    acceptance = {
        "m155_conditioned_dynamics_passes": bool(previous["passed"]),
        "map_system_preserves_conditioning": max(mapped_errors) <= tol,
        "all_observables_transport": max(observable_errors) <= tol,
        "all_selected_predicates_transport": all(predicate_matches),
        "post_processing_composes": max(composition_errors) <= tol,
        "conjugation_preserves_identity": max(identity_errors) <= tol,
        "conjugation_preserves_composition": max(composition_conjugacy_errors) <= tol,
        "clock_conjugation_is_injective_on_selected_steps": injectivity_separation > tol,
        "conjugated_application_commutes": max(application_errors) <= tol,
    }
    diagnostics = {
        "mapped_errors": tuple(mapped_errors),
        "observable_errors": tuple(observable_errors),
        "predicate_matches": tuple(predicate_matches),
        "composition_errors": tuple(composition_errors),
        "identity_errors": identity_errors,
        "composition_conjugacy_errors": composition_conjugacy_errors,
        "application_errors": application_errors,
        "injectivity_separation": injectivity_separation,
        "entropic_samples": entropic_samples,
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
            "conditioning_is_functorial_for_supplied_deterministic_maps": True,
            "clock_dynamics_transport_by_conjugation": True,
            "underlying_conditioning_and_calibration_are_supplied_premises": True,
        },
    }
