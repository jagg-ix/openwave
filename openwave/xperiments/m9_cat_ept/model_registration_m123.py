"""M9.123 registration for broad non-particle physics modeling and scope gates."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m123_nonparticle_physics_authority import (
    run_m123_nonparticle_physics_authority,
)
from .model_registration_m122 import canonical_registration_payload as previous_payload


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m123_nonparticle_physics_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v26",
        "m9_123": {
            "nonparticle_physics_authority_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["current_formal_head"],
            "merged_formal_branch": formal["branch"],
            "physlib_root_blob": formal["physlib_root_blob"],
            "zil_public_head": formal["zil_public_head"],
            "nonparticle_domain_count": component["domain_count"],
            "nonparticle_control_count": component["control_count"],
            "broad_internal_physics_modeling": component[
                "broad_internal_physics_modeling"
            ],
            "particle_spectroscopy_primary": component[
                "particle_spectroscopy_primary"
            ],
            "predictive_fundamental_theory_ready": component[
                "predictive_fundamental_theory_ready"
            ],
            "independent_calibration_complete": component[
                "independent_calibration_complete"
            ],
            "external_validation_complete": component[
                "external_validation_complete"
            ],
            "external_physical_promotion_allowed": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "nonparticle_scope_profile_is_external_validation": False,
            "control_benchmark_is_parameter_free_prediction": False,
            "broad_internal_modeling_is_complete_unification": False,
        },
    }


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m123_nonparticle_physics_authority()
    payload = canonical_registration_payload()
    current = payload["m9_123"]
    acceptance = {
        "M9_123_authority_passes": evidence["passed"],
        "schema_v26_is_current": payload["schema"] == "openwave.model-registration.v26",
        "eleven_formal_sources_are_registered": current["formal_source_count"] == 11
        and len(current["formal_authority_fingerprint"]) == 64,
        "eight_domains_and_six_controls_are_registered": current[
            "nonparticle_domain_count"
        ]
        == 8
        and current["nonparticle_control_count"] == 6,
        "scope_is_not_particle_spectroscopy_primary": not current[
            "particle_spectroscopy_primary"
        ],
        "broad_internal_modeling_is_registered_without_unification_promotion": current[
            "broad_internal_physics_modeling"
        ]
        and not current["predictive_fundamental_theory_ready"],
        "calibration_validation_and_promotion_remain_blocked": not current[
            "independent_calibration_complete"
        ]
        and not current["external_validation_complete"]
        and not current["external_physical_promotion_allowed"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.123-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "nonparticle_physics_modeling_layer_is_current": True,
            "particle_spectroscopy_is_not_primary_scope": True,
            "predictive_fundamental_theory_ready": False,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
