"""M9.125 authority for common carrier, calibration contract, and holdout protocol."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m125_extension import run_formalization_m125_extension
from .m124_three_clock_authority import run_m124_three_clock_authority
from .shared_three_clock_carrier import run_shared_three_clock_carrier
from .three_clock_calibration_contract import run_three_clock_calibration_contract
from .three_clock_holdout_protocol import run_three_clock_holdout_protocol
from .three_clock_unification_gate_m125 import run_three_clock_unification_gate_m125


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m125_three_clock_common_carrier_authority() -> dict[str, Any]:
    previous = run_m124_three_clock_authority()
    formal = run_formalization_m125_extension()
    carrier = run_shared_three_clock_carrier()
    calibration = run_three_clock_calibration_contract()
    holdout = run_three_clock_holdout_protocol()
    gate = run_three_clock_unification_gate_m125()
    component = {
        "formal_authority_passed": formal["passed"],
        "shared_carrier_passed": carrier["passed"],
        "calibration_contract_passed": calibration["passed"],
        "holdout_protocol_passed": holdout["passed"],
        "unification_gate_passed": gate["passed"],
        "shared_finite_carrier": carrier["decision"]["shared_finite_clock_carrier_constructed"],
        "conditioned_modular_identification_reduced": carrier["decision"]["conditioned_generator_modular_identification_reduced"],
        "internal_clock_maps": calibration["decision"]["page_wootters_to_modular_internal_calibration_constructed"] and calibration["decision"]["modular_to_entropic_branch_map_constructed"],
        "prediction_commitment": holdout["decision"]["three_clock_prediction_commitment_constructed"],
        "real_data_ingested": holdout["decision"]["real_three_clock_data_ingested"],
        "reduced_gate_ready": gate["decision"]["reduced_shared_three_clock_carrier_ready"],
        "universal_clock_established": gate["decision"]["single_universal_physical_clock_established"],
        "external_validation_complete": gate["decision"]["external_validation_complete"],
    }
    payload = {
        "schema": "openwave.m9.m125-three-clock-common-carrier-authority.v1",
        "task": "M9.125",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "reduced_common_carrier_is_full_Page_Wootters_theorem": False,
            "internal_parameter_maps_are_measured_clock_calibration": False,
            "synthetic_holdout_fixture_is_external_evidence": False,
            "reduced_gate_is_universal_clock_promotion": False,
        },
    }
    acceptance = {
        "previous_M9_124_authority_is_preserved": previous["passed"],
        "formal_authority_continuity_passes": formal["passed"],
        "M9_125a_shared_carrier_closes": carrier["passed"] and component["shared_finite_carrier"] and component["conditioned_modular_identification_reduced"],
        "M9_125b_internal_calibration_contract_closes": calibration["passed"] and component["internal_clock_maps"],
        "M9_125c_holdout_protocol_closes_without_evidence_claim": holdout["passed"] and component["prediction_commitment"] and not component["real_data_ingested"],
        "reduced_gate_passes_while_universal_gate_fails_closed": gate["passed"] and component["reduced_gate_ready"] and not component["universal_clock_established"],
        "external_validation_remains_open": not component["external_validation_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "carrier": carrier,
            "calibration": calibration,
            "holdout": holdout,
            "gate": gate,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_125a_shared_finite_carrier_complete": True,
            "M9_125b_internal_clock_calibration_contract_complete": True,
            "M9_125c_three_clock_holdout_protocol_complete": True,
            "full_constraint_theorem_complete": False,
            "independent_proper_time_calibration_complete": False,
            "external_three_clock_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
