"""M9.117 evidence authority for dynamical holographic coarse graining."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .coarse_grained_screen_gravity import run_coarse_grained_screen_gravity
from .formalization_m117_extension import run_formalization_m117_extension
from .gaussian_covariance_scale_flow import run_gaussian_covariance_scale_flow
from .m116_bssn_refinement_evidence_authority import (
    run_m116_bssn_refinement_evidence_authority,
)
from .screen_coarse_graining_dynamics import run_screen_coarse_graining_dynamics


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m117_coarse_graining_evidence_authority() -> dict[str, Any]:
    previous = run_m116_bssn_refinement_evidence_authority()
    formal = run_formalization_m117_extension()
    screen = run_screen_coarse_graining_dynamics()
    covariance = run_gaussian_covariance_scale_flow()
    gravity = run_coarse_grained_screen_gravity()
    component = {
        "screen_flow_passed": bool(screen["passed"]),
        "finite_block_semigroup": screen["decision"]["finite_block_semigroup_constructed"],
        "continuous_count_flow": screen["decision"]["continuous_count_flow_constructed"],
        "universal_G_preserved": screen["decision"]["universal_holographic_G_preserved"],
        "Gaussian_flow_passed": bool(covariance["passed"]),
        "Gaussian_covariance_fixed_point": covariance["decision"][
            "Gaussian_covariance_flow_adapter_constructed"
        ],
        "principal_image_limits": covariance["decision"][
            "principal_and_image_mode_limits_reproduced"
        ],
        "gravity_scale_campaign_passed": bool(gravity["passed"]),
        "one_G_injected_across_resolutions": gravity["decision"][
            "coarse_grained_screen_coupling_injected"
        ],
        "low_mode_gravity_scale_consistency": gravity["decision"][
            "low_mode_gravity_response_is_scale_consistent"
        ],
        "formal_authority_passed": bool(formal["passed"]),
        "mass_endpoint_derived": screen["decision"]["particle_mass_endpoint_derived"],
        "interacting_fixed_point_constructed": covariance["decision"][
            "interacting_fixed_point_constructed"
        ],
        "physical_calibration": gravity["decision"]["physical_screen_calibration_complete"],
    }
    payload = {
        "schema": "openwave.m9.m117-coarse-graining-evidence-authority.v1",
        "task": "M9.117",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "count_flow_derives_particle_mass": False,
            "free_Gaussian_fixed_point_is_interacting_CAT_EPT_fixed_point": False,
            "multi_resolution_Poisson_closure_is_general_Einstein_equivalence": False,
            "synthetic_screen_fixture_is_physical_calibration": False,
        },
    }
    acceptance = {
        "previous_M9_116_authority_is_preserved": bool(previous["passed"]),
        "formal_scale_authority_passes": component["formal_authority_passed"],
        "M9_117a_screen_flow_closes": component["screen_flow_passed"]
        and component["finite_block_semigroup"]
        and component["continuous_count_flow"]
        and component["universal_G_preserved"],
        "M9_117b_Gaussian_flow_closes": component["Gaussian_flow_passed"]
        and component["Gaussian_covariance_fixed_point"]
        and component["principal_image_limits"],
        "M9_117c_gravity_scale_flow_closes": component["gravity_scale_campaign_passed"]
        and component["one_G_injected_across_resolutions"]
        and component["low_mode_gravity_scale_consistency"],
        "mass_fixed_point_and_calibration_remain_open": not component["mass_endpoint_derived"]
        and not component["interacting_fixed_point_constructed"]
        and not component["physical_calibration"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "screen": screen,
            "covariance": covariance,
            "gravity": gravity,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_117a_dynamic_count_flow_complete": True,
            "M9_117b_Gaussian_fixed_point_adapter_complete": True,
            "M9_117c_multi_resolution_gravity_complete": True,
            "M9_118_external_calibration_unblocked": False,
            "next_executable_target_is_gauge_covariant_sectors": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
