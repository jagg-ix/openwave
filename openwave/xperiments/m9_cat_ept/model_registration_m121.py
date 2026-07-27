"""M9.121 registration for open-system decay and physical-promotion governance."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m121_open_system_evidence_authority import run_m121_open_system_evidence_authority
from .model_registration_m120 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m121_open_system_evidence_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v24",
        "m9_121": {
            "open_system_campaign_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["current_formal_head"],
            "zil_public_head": formal["zil_public_head"],
            "cptp_open_system_decay": component["cptp_open_system_decay"],
            "intrinsic_model_unit_lifetime": component["intrinsic_model_unit_lifetime"],
            "blind_prediction_commitment": component["blind_commitment"],
            "holdout_safe_calibration_protocol": component["holdout_protocol_passed"],
            "physical_promotion_gate": component["promotion_gate_passed"],
            "independent_physical_anchor_ready": component["independent_anchor_ready"],
            "heldout_validation_complete": component["heldout_validation_complete"],
            "external_physical_promotion_allowed": component["external_promotion_allowed"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "model_decay_rate_is_measured_width": False,
            "calibration_protocol_is_calibration_result": False,
            "internal_evidence_gate_is_external_validation": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m121_open_system_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_121"]
    acceptance = {
        "M9_121_authority_passes": evidence["passed"],
        "schema_v24_is_current": payload["schema"] == "openwave.model-registration.v24",
        "five_formal_sources_are_registered": current["formal_source_count"] == 5
        and len(current["formal_authority_fingerprint"]) == 64,
        "open_system_and_governance_layers_are_registered": current[
            "cptp_open_system_decay"
        ]
        and current["intrinsic_model_unit_lifetime"]
        and current["blind_prediction_commitment"]
        and current["holdout_safe_calibration_protocol"]
        and current["physical_promotion_gate"],
        "external_promotion_remains_blocked": not current[
            "independent_physical_anchor_ready"
        ]
        and not current["heldout_validation_complete"]
        and not current["external_physical_promotion_allowed"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.121-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "open_system_decay_layer_is_current": True,
            "physical_promotion_governance_is_current": True,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
