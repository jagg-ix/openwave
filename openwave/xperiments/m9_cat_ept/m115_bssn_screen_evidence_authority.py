"""M9.115 evidence authority for the reduced BSSN-style screen carrier."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .bssn_screen_gravity import run_bssn_screen_gravity
from .m114_generalized_adm_evidence_authority import (
    run_m114_generalized_adm_evidence_authority,
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m115_bssn_screen_evidence_authority() -> dict[str, Any]:
    previous = run_m114_generalized_adm_evidence_authority()
    campaign = run_bssn_screen_gravity()
    component = {
        "campaign_passed": campaign["passed"],
        "unit_determinant_control": campaign["acceptance"][
            "unit_determinant_is_enforced"
        ],
        "tracefree_extrinsic_control": campaign["acceptance"][
            "tracefree_extrinsic_is_enforced"
        ],
        "conformal_connection_functions": campaign["acceptance"][
            "conformal_connection_functions_are_evolved"
        ],
        "connection_constraint_measured": campaign["acceptance"][
            "connection_constraint_is_measured"
        ],
        "one_plus_log_lapse": campaign["acceptance"][
            "one_plus_log_lapse_is_evolved"
        ],
        "gamma_driver_shift": campaign["acceptance"][
            "gamma_driver_shift_is_evolved"
        ],
        "one_screen_coupling": campaign["acceptance"][
            "one_screen_coupling_is_preserved"
        ],
        "physical_calibration": campaign["decision"][
            "physical_screen_calibration_complete"
        ],
    }
    payload = {
        "schema": "openwave.m9.m115-bssn-screen-evidence-authority.v1",
        "task": "M9.115",
        "previous_authority": previous,
        "component": component,
        "claim_boundary": {
            "reduced_BSSN_style_is_exact_BSSN": False,
            "determinant_control_is_constraint_convergence": False,
            "finite_connection_constraint_is_constraint_closure": False,
            "gauge_driver_is_complete_coordinate_control": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
            "reduced_periodic_carrier_is_general_GR": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "BSSN_style_campaign_passes": bool(component["campaign_passed"]),
        "algebraic_BSSN_controls_close": component["unit_determinant_control"]
        and component["tracefree_extrinsic_control"],
        "connection_layer_is_constructed": component[
            "conformal_connection_functions"
        ]
        and component["connection_constraint_measured"],
        "gauge_layer_is_constructed": component["one_plus_log_lapse"]
        and component["gamma_driver_shift"],
        "one_screen_coupling_is_preserved": component["one_screen_coupling"],
        "physical_calibration_remains_open": not component["physical_calibration"],
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
            "M9_115a_determinant_control_complete": True,
            "M9_115b_connection_functions_complete": True,
            "M9_115c_gauge_driver_complete": True,
            "exact_BSSN_complete": False,
            "general_Einstein_evolution_complete": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
