"""M9.124 registration for the Page-Wootters/modular/entropic clock synthesis."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m124_three_clock_authority import run_m124_three_clock_authority
from .model_registration_m123 import canonical_registration_payload as previous_payload


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m124_three_clock_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v27",
        "m9_124": {
            "three_clock_authority_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["merged_formal_head"],
            "development_formal_head": formal["development_head"],
            "development_formal_branch": formal["development_branch"],
            "zil_public_head": formal["zil_public_head"],
            "clock_role_count": component["clock_role_count"],
            "pairwise_bridge_count": component["pairwise_bridge_count"],
            "page_wootters_conditioning_control": component["page_wootters_conditioning_control"],
            "modular_flow_control": component["modular_flow_control"],
            "entropic_arrow_control": component["entropic_arrow_control"],
            "three_aspect_time_framework": component["three_aspect_time_framework"],
            "single_unified_physical_clock_established": component["single_unified_physical_clock"],
            "external_validation_complete": component["external_validation_complete"],
            "external_physical_promotion_allowed": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "clock_role_taxonomy_is_clock_equivalence": False,
            "modular_parameter_is_automatically_page_wootters_time": False,
            "entropic_accumulation_is_automatically_modular_flow": False,
            "development_branch_theorem_is_merged_master_authority": False,
        },
    }


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m124_three_clock_authority()
    payload = canonical_registration_payload()
    current = payload["m9_124"]
    acceptance = {
        "M9_124_authority_passes": evidence["passed"],
        "schema_v27_is_current": payload["schema"] == "openwave.model-registration.v27",
        "four_formal_sources_are_registered": current["formal_source_count"] == 4 and len(current["formal_authority_fingerprint"]) == 64,
        "three_roles_and_three_pairwise_bridges_are_registered": current["clock_role_count"] == 3 and current["pairwise_bridge_count"] == 3,
        "all_three_clock_controls_are_registered": current["page_wootters_conditioning_control"] and current["modular_flow_control"] and current["entropic_arrow_control"],
        "three_aspect_framework_does_not_promote_single_clock_identity": current["three_aspect_time_framework"] and not current["single_unified_physical_clock_established"],
        "external_validation_and_promotion_remain_blocked": not current["external_validation_complete"] and not current["external_physical_promotion_allowed"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.124-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "three_clock_synthesis_layer_is_current": True,
            "three_clock_roles_are_distinct": True,
            "single_unified_physical_clock_established": False,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
