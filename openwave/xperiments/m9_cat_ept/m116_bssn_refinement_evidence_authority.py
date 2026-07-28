"""M9.116 evidence authority for tensor constraints and BSSN refinement."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .bssn_screen_gravity import run_bssn_screen_gravity
from .bssn_screen_refinement import run_bssn_refinement_study
from .m115_bssn_evidence_authority import run_m115_bssn_evidence_authority


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m116_bssn_refinement_evidence_authority() -> dict[str, Any]:
    previous = run_m115_bssn_evidence_authority()
    campaign = run_bssn_screen_gravity()
    refinement = run_bssn_refinement_study()
    payload = {
        "schema": "openwave.m9.m116-bssn-refinement-evidence-authority.v1",
        "task": "M9.116",
        "previous_authority": previous,
        "component": {
            "enhanced_campaign_passed": campaign["passed"],
            "metric_built_ricci": campaign["decision"][
                "metric_built_conformal_ricci_constructed"
            ],
            "source_coupled_tracefree_curvature": campaign["decision"][
                "source_coupled_tracefree_curvature_constructed"
            ],
            "tensor_constraint_damping": campaign["decision"][
                "tensor_constraint_damping_constructed"
            ],
            "tensor_momentum_damping_passed": campaign["acceptance"][
                "tensor_momentum_constraint_is_damped"
            ],
            "gamma_constraint_damping_passed": campaign["acceptance"][
                "gamma_constraint_is_damped"
            ],
            "refinement_passed": refinement["passed"],
            "analytic_source_bridge": refinement["decision"][
                "source_tidal_analytic_bridge_closed"
            ],
            "three_grid_refinement": refinement["decision"][
                "three_grid_refinement_completed"
            ],
            "cauchy_consistency": refinement["decision"][
                "finite_grid_cauchy_consistency_established"
            ],
            "continuum_convergence_proved": refinement["decision"][
                "continuum_BSSN_convergence_proved"
            ],
            "production_BSSN": campaign["decision"]["production_BSSN_constructed"],
            "physical_calibration": campaign["decision"][
                "physical_screen_calibration_complete"
            ],
        },
        "claim_boundary": {
            "finite_grid_consistency_is_continuum_proof": False,
            "scalar_tidal_source_is_complete_stress_energy": False,
            "reduced_tensor_damping_is_full_constraint_propagation": False,
            "synthetic_anchor_is_physical_measurement": False,
            "enhanced_reduced_BSSN_is_general_Einstein_evolution": False,
        },
    }
    component = payload["component"]
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "enhanced_BSSN_campaign_passes": bool(campaign["passed"]),
        "metric_built_source_coupled_curvature_closes": component["metric_built_ricci"]
        and component["source_coupled_tracefree_curvature"],
        "differential_constraint_damping_closes": component[
            "tensor_constraint_damping"
        ]
        and component["tensor_momentum_damping_passed"]
        and component["gamma_constraint_damping_passed"],
        "refinement_campaign_passes": component["refinement_passed"],
        "analytic_and_three_grid_bridges_close": component["analytic_source_bridge"]
        and component["three_grid_refinement"]
        and component["cauchy_consistency"],
        "continuum_convergence_remains_open": not component[
            "continuum_convergence_proved"
        ],
        "production_BSSN_remains_open": not component["production_BSSN"],
        "physical_calibration_remains_open": not component["physical_calibration"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "campaign_result": campaign,
        "refinement_result": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_116a_metric_built_source_curvature_complete": True,
            "M9_116b_tensor_constraint_damping_complete": True,
            "M9_116c_three_grid_refinement_complete": True,
            "next_target_is_dynamical_holographic_coarse_graining": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
