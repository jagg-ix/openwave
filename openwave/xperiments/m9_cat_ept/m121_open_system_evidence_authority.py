"""M9.121 authority for model-unit decay, holdout protocol, and promotion gates."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .calibration_holdout_protocol import run_calibration_holdout_protocol
from .formalization_m121_extension import run_formalization_m121_extension
from .gauge_sector_open_decay import run_gauge_sector_open_decay
from .m120_spectral_phenomenology_evidence_authority import (
    run_m120_spectral_phenomenology_evidence_authority,
)
from .physical_promotion_gate import run_physical_promotion_gate


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m121_open_system_evidence_authority() -> dict[str, Any]:
    previous = run_m120_spectral_phenomenology_evidence_authority()
    formal = run_formalization_m121_extension()
    decay = run_gauge_sector_open_decay()
    calibration = run_calibration_holdout_protocol()
    promotion = run_physical_promotion_gate()
    component = {
        "formal_authority_passed": formal["passed"],
        "open_decay_campaign_passed": decay["passed"],
        "cptp_open_system_decay": decay["decision"]["cptp_open_system_decay_constructed"],
        "intrinsic_model_unit_lifetime": decay["decision"][
            "intrinsic_model_unit_lifetime_constructed"
        ],
        "physical_decay_calibrated": decay["decision"]["physical_decay_width_calibrated"],
        "holdout_protocol_passed": calibration["passed"],
        "blind_commitment": calibration["decision"]["blind_prediction_commitment_constructed"],
        "independent_anchor_ready": calibration["decision"][
            "independent_physical_anchor_supplied"
        ],
        "heldout_validation_complete": calibration["decision"]["external_validation_complete"],
        "promotion_gate_passed": promotion["passed"],
        "internal_promotion_allowed": promotion["decision"]["internal_model_promotion_allowed"],
        "external_promotion_allowed": promotion["decision"][
            "external_physical_promotion_allowed"
        ],
    }
    payload = {
        "schema": "openwave.m9.m121-open-system-evidence-authority.v1",
        "task": "M9.121",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "model_unit_decay_is_measured_lifetime": False,
            "blind_protocol_is_physical_calibration": False,
            "internal_promotion_is_external_validation": False,
            "missing_identity_bridge_is_ignored": False,
        },
    }
    acceptance = {
        "previous_M9_120_authority_is_preserved": previous["passed"],
        "merged_formal_open_system_authority_passes": formal["passed"],
        "M9_121a_cptp_decay_closes": component["open_decay_campaign_passed"]
        and component["cptp_open_system_decay"]
        and component["intrinsic_model_unit_lifetime"],
        "M9_121b_holdout_protocol_closes_without_calibration_claim": component[
            "holdout_protocol_passed"
        ]
        and component["blind_commitment"]
        and not component["independent_anchor_ready"]
        and not component["heldout_validation_complete"],
        "M9_121c_promotion_gate_is_fail_closed": component["promotion_gate_passed"]
        and component["internal_promotion_allowed"]
        and not component["external_promotion_allowed"],
        "physical_decay_calibration_and_validation_remain_open": not component[
            "physical_decay_calibrated"
        ]
        and not component["heldout_validation_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "decay": decay,
            "calibration": calibration,
            "promotion": promotion,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_121a_open_system_decay_complete": True,
            "M9_121b_blind_calibration_protocol_complete": True,
            "M9_121c_physical_promotion_gate_complete": True,
            "external_physical_validation_complete": False,
            "next_target_requires_external_anchor_and_heldout_data": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
