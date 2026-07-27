"""M9.125 fail-closed gate after constructing one reduced shared carrier."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from .shared_three_clock_carrier import run_shared_three_clock_carrier
from .three_clock_calibration_contract import run_three_clock_calibration_contract
from .three_clock_holdout_protocol import run_three_clock_holdout_protocol

REDUCED_REQUIREMENTS = (
    "carrier:shared_finite_state_algebra",
    "identity:conditioned_generator_is_modular_K_reduced",
    "identity:dissipator_and_modular_flow_share_common_carrier_reduced",
    "calibration:tauPW_to_modular_parameter_internal",
    "calibration:modular_to_entropic_parameter_branch",
    "dynamics:end_to_end_reversible_irreversible_composition_reduced",
    "commitment:three_clock_prediction_digest",
)

UNIVERSAL_REQUIREMENTS = REDUCED_REQUIREMENTS + (
    "theorem:constraint_to_conditioned_dynamics",
    "carrier:general_quantum_field_or_continuum",
    "calibration:clock_parameters_to_proper_time_external",
    "calibration:independent_temperature_and_dissipation_scales",
    "evidence:heldout_three_clock_test",
    "universality:carrier_independent_clock_equivalence",
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def evaluate(relations: Iterable[str], requirements: tuple[str, ...]) -> dict[str, Any]:
    observed = set(relations)
    missing = tuple(item for item in requirements if item not in observed)
    return {"passed": not missing, "missing": missing, "observed": tuple(sorted(observed))}


@lru_cache(maxsize=1)
def run_three_clock_unification_gate_m125() -> dict[str, Any]:
    carrier = run_shared_three_clock_carrier()
    calibration = run_three_clock_calibration_contract()
    holdout = run_three_clock_holdout_protocol()
    current = set(REDUCED_REQUIREMENTS)
    reduced = evaluate(current, REDUCED_REQUIREMENTS)
    universal = evaluate(current, UNIVERSAL_REQUIREMENTS)
    synthetic_complete = set(UNIVERSAL_REQUIREMENTS)
    removal_failures = {
        requirement: not evaluate(synthetic_complete - {requirement}, UNIVERSAL_REQUIREMENTS)["passed"]
        for requirement in UNIVERSAL_REQUIREMENTS
    }
    payload = {
        "schema": "openwave.m9.three-clock-unification-gate.v2",
        "task": "M9.125",
        "reduced_requirements": REDUCED_REQUIREMENTS,
        "universal_requirements": UNIVERSAL_REQUIREMENTS,
        "reduced_gate": reduced,
        "universal_gate": universal,
        "claim_boundary": {
            "reduced_common_carrier_is_universal_clock_theorem": False,
            "internal_calibration_is_external_proper_time_calibration": False,
            "blind_protocol_is_heldout_result": False,
            "finite_qubit_carrier_is_continuum_field_clock": False,
        },
    }
    acceptance = {
        "all_M9_125_components_pass": carrier["passed"] and calibration["passed"] and holdout["passed"],
        "reduced_common_carrier_gate_passes": reduced["passed"],
        "universal_physical_clock_gate_remains_blocked": not universal["passed"],
        "all_universal_missing_relations_are_named": set(universal["missing"]) == set(UNIVERSAL_REQUIREMENTS) - current,
        "every_universal_requirement_is_load_bearing": all(removal_failures.values()),
        "no_universal_or_external_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "removal_failures": removal_failures,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "reduced_shared_three_clock_carrier_ready": True,
            "model_internal_parameter_maps_ready": True,
            "blinded_three_clock_protocol_ready": True,
            "single_universal_physical_clock_established": False,
            "external_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
