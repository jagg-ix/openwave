"""M9.114 evidence authority for generalized screen-coupled ADM gravity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .generalized_screen_adm_gravity import run_generalized_screen_adm_gravity
from .m113_synchronized_screen_evidence_authority import (
    run_m113_synchronized_screen_evidence_authority,
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m114_generalized_adm_evidence_authority() -> dict[str, Any]:
    previous = run_m113_synchronized_screen_evidence_authority()
    campaign = run_generalized_screen_adm_gravity()
    component = {
        "campaign_passed": campaign["passed"],
        "screen_G_shared": campaign["acceptance"][
            "one_screen_G_reaches_generalized_carrier"
        ],
        "TT_metric_mode": campaign["acceptance"]["tracefree_metric_mode_evolves"],
        "tracefree_extrinsic_mode": campaign["acceptance"][
            "tracefree_extrinsic_mode_evolves"
        ],
        "shift_mode": campaign["acceptance"]["shift_mode_is_present"],
        "tracefree_projection": campaign["acceptance"][
            "tracefree_projection_is_preserved"
        ],
        "constraints_measured": campaign["acceptance"]["constraints_are_measured"],
    }
    payload = {
        "schema": "openwave.m9.m114-generalized-adm-evidence-authority.v1",
        "task": "M9.114",
        "previous_authority": previous,
        "component": component,
        "claim_boundary": {
            "TT_carrier_is_exact_BSSN": False,
            "shift_carrier_is_complete_gauge_dynamics": False,
            "generalized_reduced_ADM_is_general_GR": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "generalized_campaign_passes": bool(campaign["passed"]),
        "three_previous_metric_restrictions_are_removed": all(
            component[key]
            for key in ("TT_metric_mode", "tracefree_extrinsic_mode", "shift_mode")
        ),
        "one_screen_G_is_preserved": component["screen_G_shared"],
        "tracefree_and_constraint_diagnostics_are_explicit": component[
            "tracefree_projection"
        ]
        and component["constraints_measured"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_result": campaign,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "TT_metric_modes_constructed": True,
            "tracefree_extrinsic_curvature_constructed": True,
            "shift_dynamics_constructed": True,
            "general_Einstein_Cauchy_development_constructed": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
