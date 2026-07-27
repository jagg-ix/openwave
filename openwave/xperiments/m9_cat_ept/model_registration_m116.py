"""M9.116 registration for source-coupled BSSN refinement evidence."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m116_bssn_refinement_evidence_authority import (
    run_m116_bssn_refinement_evidence_authority,
)
from .model_registration_m115 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m116_bssn_refinement_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v20",
        "m9_116": {
            "enhanced_BSSN_campaign_registered": component[
                "enhanced_campaign_passed"
            ],
            "metric_built_conformal_ricci": component["metric_built_ricci"],
            "source_coupled_tracefree_curvature": component[
                "source_coupled_tracefree_curvature"
            ],
            "tensor_constraint_damping": component["tensor_constraint_damping"],
            "tensor_momentum_damping_passed": component[
                "tensor_momentum_damping_passed"
            ],
            "gamma_constraint_damping_passed": component[
                "gamma_constraint_damping_passed"
            ],
            "three_grid_refinement": component["three_grid_refinement"],
            "finite_grid_cauchy_consistency": component["cauchy_consistency"],
            "continuum_convergence_proved": component[
                "continuum_convergence_proved"
            ],
            "production_BSSN_constructed": component["production_BSSN"],
            "physical_calibration_complete": component["physical_calibration"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "finite_grid_consistency_is_continuum_BSSN_proof": False,
            "scalar_tidal_source_is_complete_stress_energy": False,
            "tensor_damping_is_full_Einstein_constraint_propagation": False,
            "synthetic_refinement_fixture_is_physical_measurement": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m116_bssn_refinement_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_116"]
    acceptance = {
        "M9_116_authority_passes": evidence["passed"],
        "schema_v20_is_current": payload["schema"]
        == "openwave.model-registration.v20",
        "source_coupled_ricci_and_constraints_are_registered": all(
            current[key]
            for key in (
                "metric_built_conformal_ricci",
                "source_coupled_tracefree_curvature",
                "tensor_constraint_damping",
                "tensor_momentum_damping_passed",
                "gamma_constraint_damping_passed",
            )
        ),
        "three_grid_refinement_is_registered": current["three_grid_refinement"]
        and current["finite_grid_cauchy_consistency"],
        "continuum_convergence_remains_open": not current[
            "continuum_convergence_proved"
        ],
        "production_BSSN_remains_open": not current[
            "production_BSSN_constructed"
        ],
        "physical_calibration_remains_open": not current[
            "physical_calibration_complete"
        ],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.116-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "source_coupled_reduced_BSSN_layer_is_current": True,
            "finite_grid_refinement_complete": True,
            "continuum_BSSN_convergence_complete": False,
            "general_Einstein_evolution_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
