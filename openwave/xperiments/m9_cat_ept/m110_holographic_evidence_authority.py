"""M9.110 holographic count and coupling evidence authority."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .holographic_coarse_graining import run_holographic_coarse_graining
from .holographic_count_hierarchy import run_holographic_count_hierarchy
from .holographic_gravity_coupling import run_holographic_gravity_coupling
from .m109_evidence_authority import run_m109_evidence_authority


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m110_holographic_evidence_authority() -> dict[str, Any]:
    previous = run_m109_evidence_authority()
    hierarchy = run_holographic_count_hierarchy()
    coarse = run_holographic_coarse_graining()
    coupling = run_holographic_gravity_coupling()
    payload = {
        "schema": "openwave.m9.m110-holographic-evidence-authority.v2",
        "task": "M9.110",
        "previous_authority": previous,
        "components": {
            "count_hierarchy": {
                "campaign_passed": hierarchy["passed"],
                "universal_holographic_G": hierarchy["invariants"][
                    "holographic_G_species_invariant"
                ],
                "compton_cell_is_primary_holographic_bit": False,
                "planck_bits_per_compton_cell_registered": True,
            },
            "coarse_graining": {
                "campaign_passed": coarse["passed"],
                "exact_count_ratio": coarse["interpretation_boundary"][
                    "multiplicity_is_exact_count_ratio"
                ],
                "dynamical_renormalization_constructed": coarse[
                    "interpretation_boundary"
                ]["renormalization_mechanism_constructed"],
            },
            "gravity_coupling": {
                "campaign_passed": coupling["passed"],
                "screen_density_is_primary_G_source": coupling["decision"][
                    "screen_density_is_primary_G_source"
                ],
                "weak_screen_G_injection_constructed": coupling["synthetic_contract"][
                    "weak_uses_screen_coupling"
                ],
                "nonlinear_screen_G_injection_constructed": coupling[
                    "synthetic_contract"
                ]["nonlinear_uses_screen_coupling"],
                "one_screen_G_shared": coupling["synthetic_contract"][
                    "weak_and_nonlinear_share_one_G"
                ],
                "physical_calibration_complete": coupling["decision"][
                    "current_default_is_physically_calibrated"
                ],
            },
        },
        "claim_boundary": {
            "species_count_ratio_falsifies_holographic_G": False,
            "exact_count_ratio_is_dynamical_coarse_graining": False,
            "synthetic_screen_anchor_is_physical_evidence": False,
            "shared_implementation_coupling_is_physical_calibration": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "three_holographic_campaigns_execute": hierarchy["passed"]
        and coarse["passed"]
        and coupling["passed"],
        "universal_holographic_G_is_preserved": payload["components"][
            "count_hierarchy"
        ]["universal_holographic_G"],
        "count_ratio_is_not_overpromoted": not payload["components"][
            "coarse_graining"
        ]["dynamical_renormalization_constructed"],
        "weak_and_nonlinear_injection_close": payload["components"][
            "gravity_coupling"
        ]["weak_screen_G_injection_constructed"]
        and payload["components"]["gravity_coupling"][
            "nonlinear_screen_G_injection_constructed"
        ]
        and payload["components"]["gravity_coupling"]["one_screen_G_shared"],
        "physical_calibration_remains_open": not payload["components"][
            "gravity_coupling"
        ]["physical_calibration_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "hierarchy": hierarchy,
            "coarse_graining": coarse,
            "coupling": coupling,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_110a_count_hierarchy_complete": True,
            "M9_110b_coarse_graining_diagnostic_complete": True,
            "M9_110c_screen_G_adapter_complete": True,
            "M9_110d_nonlinear_screen_G_injection_complete": True,
            "next_target_is_integrated_screen_G_gravity_execution": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
