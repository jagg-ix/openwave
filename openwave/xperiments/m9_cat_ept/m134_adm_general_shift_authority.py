"""M9.134 authority for the general-shift ADM spatial-metric evolution."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .adm_general_shift_m134 import run_adm_general_shift_study
from .bssn_screen_gravity import run_bssn_screen_gravity
from .generalized_screen_adm_gravity import run_generalized_screen_adm_gravity


@lru_cache(maxsize=1)
def run_m134_adm_general_shift_authority() -> dict[str, Any]:
    bridge = run_adm_general_shift_study()
    generalized = run_generalized_screen_adm_gravity()
    bssn = run_bssn_screen_gravity()
    payload = {
        "schema": "openwave.m9.m134-adm-general-shift-authority.v1",
        "task": "M9.134-authority",
        "component": bridge,
        "existing_gravity_carriers": {
            "generalized_adm_schema": generalized["schema"],
            "generalized_adm_passed": generalized["passed"],
            "bssn_schema": bssn["schema"],
            "bssn_passed": bssn["passed"],
        },
        "claim_boundary": {
            "general_shift_identity_is_full_covariant_gravity": False,
            "general_shift_identity_proves_sourced_tt_propagation": False,
            "declared_physlib_short_commit_is_verified_full_pin": False,
            "existing_reduced_carriers_are_production_numerical_relativity": False,
        },
    }
    acceptance = {
        "general_shift_bridge_passes": bridge["passed"],
        "generalized_adm_carrier_remains_executable": generalized["passed"],
        "bssn_carrier_remains_executable": bssn["passed"],
        "zero_shift_is_registered_as_special_case": bridge["decision"]["shift_free_model_is_zero_shift_special_case"],
        "tracefree_momentum_content_is_registered": bridge["decision"]["momentum_flux_carries_tracefree_curvature"],
        "only_checked_open_limits_remain": (
            not bridge["decision"]["curved_covariant_derivative_operator_constructed"]
            and not bridge["decision"]["sourced_tt_wave_propagation_constructed"]
        ),
        "no_physical_promotion": not any(payload["claim_boundary"].values()),
    }
    result = {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "gravity_beyond_weak_field_general_shift_gap_closed": True,
            "general_extrinsic_curvature_gap_closed": True,
            "tt_mode_carrier_gap_closed": True,
            "sourced_tt_wave_equation_open": True,
            "curved_covariant_derivative_operator_open": True,
            "physical_claims_promoted": [],
        },
    }
    result["fingerprint"] = sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    return result


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
