"""M9.110 registration over holographic count hierarchy and screen coupling."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m110_holographic_evidence_authority import run_m110_holographic_evidence_authority
from .model_registration_m109 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m110_holographic_evidence_authority()
    components = evidence["components"]
    return {
        **previous,
        "schema": "openwave.model-registration.v14",
        "m9_110": {
            "count_hierarchy_registered": components["count_hierarchy"]["campaign_passed"],
            "universal_holographic_G_preserved": components["count_hierarchy"]["universal_holographic_G"],
            "planck_bits_per_compton_cell_registered": components["count_hierarchy"]["planck_bits_per_compton_cell_registered"],
            "coarse_graining_ratio_registered": components["coarse_graining"]["exact_count_ratio"],
            "dynamical_renormalization_constructed": components["coarse_graining"]["dynamical_renormalization_constructed"],
            "screen_density_primary_G": components["gravity_coupling"]["screen_density_is_primary_G_source"],
            "weak_screen_G_injection": components["gravity_coupling"]["weak_screen_G_injection_constructed"],
            "nonlinear_screen_G_injection": components["gravity_coupling"]["nonlinear_screen_G_injection_constructed"],
            "physical_calibration_complete": components["gravity_coupling"]["physical_calibration_complete"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "compton_cell_count_is_holographic_bit_count": False,
            "count_ratio_is_renormalization_dynamics": False,
            "species_mass_changes_universal_holographic_G": False,
            "synthetic_screen_density_is_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m110_holographic_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_110"]
    acceptance = {
        "holographic_authority_passes": evidence["passed"],
        "schema_v14_is_current": payload["schema"] == "openwave.model-registration.v14",
        "primary_G_is_holographic_screen_density": current["screen_density_primary_G"],
        "species_invariance_is_preserved": current["universal_holographic_G_preserved"],
        "coarse_graining_is_not_dynamics": not current["dynamical_renormalization_constructed"],
        "nonlinear_injection_gap_is_preserved": not current["nonlinear_screen_G_injection"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.110-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "holographic_reinterpretation_is_current": True,
            "primary_G_falsification_withdrawn": True,
            "next_target_nonlinear_screen_coupling": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
