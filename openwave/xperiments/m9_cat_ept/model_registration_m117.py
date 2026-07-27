"""M9.117 registration for dynamical holographic coarse graining."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m117_coarse_graining_evidence_authority import (
    run_m117_coarse_graining_evidence_authority,
)
from .model_registration_m116 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m117_coarse_graining_evidence_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v21",
        "m9_117": {
            "dynamic_screen_flow_registered": component["screen_flow_passed"],
            "finite_block_semigroup": component["finite_block_semigroup"],
            "continuous_count_flow": component["continuous_count_flow"],
            "universal_holographic_G_preserved": component["universal_G_preserved"],
            "Gaussian_covariance_flow_registered": component["Gaussian_flow_passed"],
            "Gaussian_covariance_fixed_point": component["Gaussian_covariance_fixed_point"],
            "principal_and_image_limits": component["principal_image_limits"],
            "multi_resolution_gravity_registered": component["gravity_scale_campaign_passed"],
            "one_G_injected_across_resolutions": component[
                "one_G_injected_across_resolutions"
            ],
            "low_mode_gravity_scale_consistency": component[
                "low_mode_gravity_scale_consistency"
            ],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "particle_mass_endpoint_derived": component["mass_endpoint_derived"],
            "interacting_CAT_EPT_fixed_point_constructed": component[
                "interacting_fixed_point_constructed"
            ],
            "physical_calibration_complete": component["physical_calibration"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "dynamic_count_flow_is_particle_mass_derivation": False,
            "free_Gaussian_flow_is_interacting_CAT_EPT_renormalisation": False,
            "multi_grid_gravity_consistency_is_general_Einstein_equivalence": False,
            "synthetic_screen_scale_is_external_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m117_coarse_graining_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_117"]
    acceptance = {
        "M9_117_authority_passes": bool(evidence["passed"]),
        "schema_v21_is_current": payload["schema"] == "openwave.model-registration.v21",
        "three_dynamic_coarse_graining_targets_are_registered": all(
            current[key]
            for key in (
                "dynamic_screen_flow_registered",
                "finite_block_semigroup",
                "continuous_count_flow",
                "universal_holographic_G_preserved",
                "Gaussian_covariance_flow_registered",
                "Gaussian_covariance_fixed_point",
                "principal_and_image_limits",
                "multi_resolution_gravity_registered",
                "one_G_injected_across_resolutions",
                "low_mode_gravity_scale_consistency",
            )
        ),
        "four_formal_sources_are_registered": current["formal_source_count"] == 4
        and len(current["formal_authority_fingerprint"]) == 64,
        "mass_endpoint_interacting_fixed_point_and_calibration_remain_open": not current[
            "particle_mass_endpoint_derived"
        ]
        and not current["interacting_CAT_EPT_fixed_point_constructed"]
        and not current["physical_calibration_complete"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.117-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "dynamical_holographic_coarse_graining_is_current": True,
            "external_screen_calibration_complete": False,
            "next_executable_target_is_non_Abelian_and_electroweak_carriers": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
