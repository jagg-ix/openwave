"""M9.123 authority for the non-particle CAT/EPT physics benchmark."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m123_extension import run_formalization_m123_extension
from .m122_external_evidence_readiness_authority import (
    run_m122_external_evidence_readiness_authority,
)
from .nonparticle_physics_benchmark import run_nonparticle_physics_benchmark
from .physics_explanatory_scope_gate import run_physics_explanatory_scope_gate
from .physics_scope_profile import run_physics_scope_profile


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m123_nonparticle_physics_authority() -> dict[str, Any]:
    previous = run_m122_external_evidence_readiness_authority()
    formal = run_formalization_m123_extension()
    profile = run_physics_scope_profile()
    benchmark = run_nonparticle_physics_benchmark()
    gate = run_physics_explanatory_scope_gate()
    component = {
        "formal_authority_passed": formal["passed"],
        "scope_profile_passed": profile["passed"],
        "nonparticle_benchmark_passed": benchmark["passed"],
        "explanatory_scope_gate_passed": gate["passed"],
        "domain_count": len(profile["domains"]),
        "control_count": len(benchmark["results"]),
        "broad_internal_physics_modeling": gate["decision"][
            "broad_internal_physics_modeling_ready"
        ],
        "particle_spectroscopy_primary": profile["policy"][
            "particle_spectroscopy_is_primary_scorecard"
        ],
        "predictive_fundamental_theory_ready": gate["decision"][
            "predictive_fundamental_theory_ready"
        ],
        "independent_calibration_complete": gate["calibration_ready"],
        "external_validation_complete": gate["externally_validated"],
    }
    payload = {
        "schema": "openwave.m9.m123-nonparticle-physics-authority.v1",
        "task": "M9.123",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "headline_counts": profile["headline_counts"],
        "claim_boundary": {
            "broad_internal_modeling_is_fundamental_unification": False,
            "control_case_reproduction_is_external_prediction": False,
            "domain_count_is_scientific_score": False,
            "particle_incompleteness_is_the_only_failure_mode": False,
        },
    }
    acceptance = {
        "previous_M9_122_authority_is_preserved": previous["passed"],
        "cross_domain_formal_authority_passes": formal["passed"],
        "M9_123a_scope_profile_closes": profile["passed"]
        and component["domain_count"] == 8
        and not component["particle_spectroscopy_primary"],
        "M9_123b_six_nonparticle_controls_close": benchmark["passed"]
        and component["control_count"] == 6,
        "M9_123c_scope_gate_is_honest": gate["passed"]
        and component["broad_internal_physics_modeling"]
        and not component["predictive_fundamental_theory_ready"],
        "calibration_and_external_validation_remain_open": not component[
            "independent_calibration_complete"
        ]
        and not component["external_validation_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "profile": profile,
            "benchmark": benchmark,
            "gate": gate,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_123a_nonparticle_scope_profile_complete": True,
            "M9_123b_nonparticle_control_benchmark_complete": True,
            "M9_123c_explanatory_scope_gate_complete": True,
            "external_evidence_execution_moved_to_M9_124": True,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
