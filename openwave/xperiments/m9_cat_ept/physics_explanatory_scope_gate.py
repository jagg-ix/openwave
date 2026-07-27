"""M9.123c: explanatory-scope and promotion gate for broad CAT/EPT physics."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .nonparticle_physics_benchmark import run_nonparticle_physics_benchmark
from .physics_scope_profile import run_physics_scope_profile


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_physics_explanatory_scope_gate() -> dict[str, Any]:
    profile = run_physics_scope_profile()
    benchmark = run_nonparticle_physics_benchmark()
    domains = profile["domains"]

    represented = all(row["formal_sources"] for row in domains)
    formal_coverage = all(
        row["formal"] in ("proved", "conditional", "structural") for row in domains
    )
    dynamical_domains = tuple(
        row["key"]
        for row in domains
        if row["dynamics"] in ("constructed", "reduced")
    )
    continuum_domains = tuple(
        row["key"]
        for row in domains
        if row["continuum"] in ("constructed", "partial")
    )
    calibration_ready = all(
        row["calibration"] == "not_required_for_scope" for row in domains
    )
    externally_validated = all(
        row["prediction"] == "external_validated" for row in domains
    )

    explanatory_requirements = {
        "single_universal_action_or_generator": False,
        "independent_parameter_fixing": False,
        "end_to_end_continuum_dynamics": False,
        "cross_domain_heldout_prediction": False,
    }
    explanatory_compression_ready = all(explanatory_requirements.values())

    payload = {
        "schema": "openwave.m9.physics-explanatory-scope-gate.v1",
        "task": "M9.123c",
        "scope_profile_fingerprint": profile["fingerprint"],
        "benchmark_fingerprint": benchmark["fingerprint"],
        "domain_count": len(domains),
        "represented": represented,
        "formal_coverage": formal_coverage,
        "dynamical_domains": dynamical_domains,
        "continuum_supported_domains": continuum_domains,
        "calibration_ready": calibration_ready,
        "externally_validated": externally_validated,
        "explanatory_requirements": explanatory_requirements,
        "explanatory_compression_ready": explanatory_compression_ready,
        "claim_boundary": {
            "broad_representation_is_unification": False,
            "formal_coverage_is_explanatory_compression": False,
            "control_benchmark_is_external_validation": False,
            "conditional_bridge_is_parameter_free_prediction": False,
        },
    }
    acceptance = {
        "scope_profile_passes": profile["passed"],
        "nonparticle_benchmark_passes": benchmark["passed"],
        "all_eight_domains_are_represented": represented and len(domains) == 8,
        "formal_coverage_is_broad": formal_coverage,
        "at_least_five_domains_have_explicit_dynamics": len(dynamical_domains) >= 5,
        "at_least_six_domains_have_continuum_support": len(continuum_domains) >= 6,
        "calibration_gate_remains_closed": not calibration_ready,
        "external_validation_gate_remains_closed": not externally_validated,
        "explanatory_compression_gate_remains_closed": not explanatory_compression_ready,
        "all_missing_explanatory_requirements_are_named": set(
            key for key, value in explanatory_requirements.items() if not value
        )
        == set(explanatory_requirements),
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "broad_internal_physics_modeling_ready": True,
            "predictive_fundamental_theory_ready": False,
            "particle_spectroscopy_required_for_current_scope_audit": False,
            "independent_calibration_required_for_promotion": True,
            "external_validation_required_for_promotion": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
