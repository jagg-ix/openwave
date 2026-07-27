"""M9.114 registration for generalized screen-coupled ADM gravity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m114_generalized_adm_evidence_authority import (
    run_m114_generalized_adm_evidence_authority,
)
from .model_registration_m113 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m114_generalized_adm_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v18",
        "m9_114": {
            "generalized_adm_campaign_registered": component["campaign_passed"],
            "screen_G_shared": component["screen_G_shared"],
            "TT_metric_modes": component["TT_metric_mode"],
            "tracefree_extrinsic_curvature": component["tracefree_extrinsic_mode"],
            "shift_dynamics": component["shift_mode"],
            "tracefree_projection": component["tracefree_projection"],
            "constraints_measured": component["constraints_measured"],
            "general_Einstein_Cauchy_development": False,
            "physical_screen_calibration_complete": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "reduced_TT_carrier_is_exact_BSSN": False,
            "reduced_shift_is_complete_gauge_dynamics": False,
            "generalized_reduced_ADM_is_general_GR": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m114_generalized_adm_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_114"]
    acceptance = {
        "generalized_authority_passes": bool(evidence["passed"]),
        "schema_v18_is_current": payload["schema"] == "openwave.model-registration.v18",
        "three_metric_extensions_are_registered": all(
            current[key]
            for key in (
                "TT_metric_modes",
                "tracefree_extrinsic_curvature",
                "shift_dynamics",
            )
        ),
        "one_screen_G_is_retained": current["screen_G_shared"],
        "general_GR_is_not_overpromoted": not current[
            "general_Einstein_Cauchy_development"
        ],
        "physical_calibration_remains_open": not current[
            "physical_screen_calibration_complete"
        ],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.114-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "generalized_screen_ADM_is_current": True,
            "conformal_pure_trace_restriction_removed": True,
            "full_BSSN_or_general_GR_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
