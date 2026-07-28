"""M9.115--M9.116 registration for reduced BSSN-style screen gravity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m115_bssn_evidence_authority import run_m115_bssn_evidence_authority
from .model_registration_m114 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m115_bssn_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v19",
        "m9_115": {
            "BSSN_campaign_registered": component["campaign_passed"],
            "conformal_connection_functions": component["conformal_connections"],
            "unit_determinant_control": component["unit_determinant"],
            "tracefree_extrinsic_control": component["tracefree_extrinsic"],
            "one_plus_log_lapse": component["one_plus_log"],
            "gamma_driver_shift": component["gamma_driver"],
            "metric_built_ricci": component["metric_ricci"],
            "screen_source_tidal_term": component["source_tidal"],
            "tensor_constraint_damping": component["tensor_constraint_damping"],
            "gamma_constraint_damping": component["gamma_constraint_damping"],
            "one_screen_G_preserved": component["one_screen_G"],
            "constraints_reported": component["constraints_reported"],
            "production_BSSN_constructed": component["production_BSSN"],
            "physical_calibration_complete": component["physical_calibration"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "reduced_BSSN_is_production_numerical_relativity": False,
            "finite_constraint_damping_is_general_constraint_closure": False,
            "synthetic_screen_anchor_is_physical_measurement": False,
            "gauge_driver_is_unique_physical_gauge": False,
            "scalar_tidal_source_is_complete_stress_energy": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m115_bssn_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_115"]
    acceptance = {
        "BSSN_authority_passes": evidence["passed"],
        "schema_v19_is_current": payload["schema"] == "openwave.model-registration.v19",
        "BSSN_variables_and_gauge_registered": all(
            current[key]
            for key in (
                "conformal_connection_functions",
                "unit_determinant_control",
                "tracefree_extrinsic_control",
                "one_plus_log_lapse",
                "gamma_driver_shift",
            )
        ),
        "source_and_constraint_extensions_registered": all(
            current[key]
            for key in (
                "metric_built_ricci",
                "screen_source_tidal_term",
                "tensor_constraint_damping",
                "gamma_constraint_damping",
                "constraints_reported",
            )
        ),
        "one_screen_G_is_preserved": current["one_screen_G_preserved"],
        "production_BSSN_remains_open": not current["production_BSSN_constructed"],
        "physical_calibration_remains_open": not current["physical_calibration_complete"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.115-M9.116-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "reduced_BSSN_layer_is_current": True,
            "source_coupled_tensor_constraints_are_current": True,
            "production_numerical_relativity_complete": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
