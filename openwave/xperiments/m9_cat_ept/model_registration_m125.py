"""M9.125 registration for the reduced common three-clock carrier."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m125_three_clock_common_carrier_authority import run_m125_three_clock_common_carrier_authority
from .model_registration_m124 import canonical_registration_payload as previous_payload


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m125_three_clock_common_carrier_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v28",
        "m9_125": {
            "common_carrier_authority_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["merged_formal_head"],
            "development_formal_head": formal["development_head"],
            "development_formal_branch": formal["development_branch"],
            "zil_public_head": formal["zil_public_head"],
            "shared_finite_three_clock_carrier": component["shared_finite_carrier"],
            "conditioned_modular_identification_reduced": component["conditioned_modular_identification_reduced"],
            "internal_clock_parameter_maps": component["internal_clock_maps"],
            "three_clock_prediction_commitment": component["prediction_commitment"],
            "real_three_clock_data_ingested": component["real_data_ingested"],
            "reduced_common_carrier_gate": component["reduced_gate_ready"],
            "single_universal_physical_clock_established": component["universal_clock_established"],
            "external_validation_complete": component["external_validation_complete"],
            "external_physical_promotion_allowed": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "shared_finite_carrier_is_universal_clock": False,
            "internal_clock_map_is_external_calibration": False,
            "synthetic_three_clock_fixture_is_heldout_test": False,
        },
    }


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m125_three_clock_common_carrier_authority()
    payload = canonical_registration_payload()
    current = payload["m9_125"]
    acceptance = {
        "M9_125_authority_passes": evidence["passed"],
        "schema_v28_is_current": payload["schema"] == "openwave.model-registration.v28",
        "four_formal_sources_remain_registered": current["formal_source_count"] == 4 and len(current["formal_authority_fingerprint"]) == 64,
        "common_carrier_and_internal_maps_are_registered": current["shared_finite_three_clock_carrier"] and current["conditioned_modular_identification_reduced"] and current["internal_clock_parameter_maps"],
        "blind_commitment_is_registered_without_real_data": current["three_clock_prediction_commitment"] and not current["real_three_clock_data_ingested"],
        "reduced_gate_does_not_promote_universal_clock": current["reduced_common_carrier_gate"] and not current["single_universal_physical_clock_established"],
        "external_validation_and_promotion_remain_blocked": not current["external_validation_complete"] and not current["external_physical_promotion_allowed"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.125-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "reduced_three_clock_common_carrier_is_current": True,
            "physical_clock_calibration_complete": False,
            "heldout_three_clock_test_complete": False,
            "single_universal_physical_clock_established": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
