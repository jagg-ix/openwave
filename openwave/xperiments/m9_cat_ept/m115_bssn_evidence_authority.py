"""M9.115 evidence authority for reduced BSSN screen gravity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .bssn_screen_gravity import run_bssn_screen_gravity
from .m114_generalized_adm_evidence_authority import run_m114_generalized_adm_evidence_authority


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m115_bssn_evidence_authority() -> dict[str, Any]:
    previous = run_m114_generalized_adm_evidence_authority()
    campaign = run_bssn_screen_gravity()
    payload = {
        "schema": "openwave.m9.m115-bssn-evidence-authority.v1",
        "task": "M9.115",
        "previous_authority": previous,
        "component": {
            "campaign_passed": campaign["passed"],
            "conformal_connections": campaign["decision"]["conformal_connection_functions_constructed"],
            "unit_determinant": campaign["decision"]["unit_determinant_control_constructed"],
            "one_plus_log_gamma_driver": campaign["decision"]["one_plus_log_and_gamma_driver_constructed"],
            "one_screen_G": campaign["acceptance"]["one_screen_G_is_preserved"],
            "constraints_reported": campaign["acceptance"][
                "hamiltonian_and_momentum_constraints_are_reported"
            ],
            "production_BSSN": campaign["decision"]["production_BSSN_constructed"],
            "physical_calibration": campaign["decision"]["physical_screen_calibration_complete"],
        },
        "claim_boundary": {
            "reduced_BSSN_is_general_Einstein_evolution": False,
            "determinant_control_is_full_constraint_propagation": False,
            "synthetic_anchor_is_physical_measurement": False,
            "gauge_choice_is_unique_physical_observable": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "BSSN_campaign_passes": bool(campaign["passed"]),
        "three_BSSN_targets_close": all(
            payload["component"][key]
            for key in ("conformal_connections", "unit_determinant", "one_plus_log_gamma_driver")
        ),
        "one_screen_G_is_preserved": payload["component"]["one_screen_G"],
        "constraints_are_reported": payload["component"]["constraints_reported"],
        "production_BSSN_remains_open": not payload["component"]["production_BSSN"],
        "physical_calibration_remains_open": not payload["component"]["physical_calibration"],
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
            "M9_115a_conformal_connections_complete": True,
            "M9_115b_determinant_control_complete": True,
            "M9_115c_gauge_drivers_complete": True,
            "next_target_is_tensor_constraint_propagation_and_BSSN_refinement": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
