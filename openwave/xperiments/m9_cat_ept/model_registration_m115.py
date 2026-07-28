"""M9.115 registration for the reduced BSSN-style screen carrier."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m115_bssn_screen_evidence_authority import (
    run_m115_bssn_screen_evidence_authority,
)
from .model_registration_m114 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m115_bssn_screen_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v19",
        "m9_115": {
            "BSSN_style_campaign_registered": component["campaign_passed"],
            "unit_determinant_control": component["unit_determinant_control"],
            "tracefree_extrinsic_control": component[
                "tracefree_extrinsic_control"
            ],
            "conformal_connection_functions": component[
                "conformal_connection_functions"
            ],
            "connection_constraint_measured": component[
                "connection_constraint_measured"
            ],
            "one_plus_log_lapse": component["one_plus_log_lapse"],
            "gamma_driver_shift": component["gamma_driver_shift"],
            "one_screen_coupling": component["one_screen_coupling"],
            "physical_calibration_complete": component["physical_calibration"],
            "exact_BSSN_complete": False,
            "general_Einstein_evolution_complete": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "BSSN_style_carrier_is_exact_BSSN": False,
            "algebraic_metric_control_is_constraint_convergence": False,
            "finite_connection_constraint_is_constraint_closure": False,
            "gauge_driver_is_complete_coordinate_control": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m115_bssn_screen_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_115"]
    acceptance = {
        "BSSN_style_authority_passes": bool(evidence["passed"]),
        "schema_v19_is_current": payload["schema"]
        == "openwave.model-registration.v19",
        "algebraic_controls_are_registered": current["unit_determinant_control"]
        and current["tracefree_extrinsic_control"],
        "connection_layer_is_registered": current["conformal_connection_functions"]
        and current["connection_constraint_measured"],
        "gauge_layer_is_registered": current["one_plus_log_lapse"]
        and current["gamma_driver_shift"],
        "one_screen_coupling_is_preserved": current["one_screen_coupling"],
        "exact_BSSN_is_not_overpromoted": not current["exact_BSSN_complete"],
        "general_GR_is_not_overpromoted": not current[
            "general_Einstein_evolution_complete"
        ],
        "physical_calibration_remains_open": not current[
            "physical_calibration_complete"
        ],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.115-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "BSSN_style_screen_carrier_is_current": True,
            "exact_BSSN_remains_open": True,
            "general_Einstein_evolution_remains_open": True,
            "physical_screen_calibration_remains_open": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
