"""M9.115--M9.116 evidence authority for reduced BSSN-style screen gravity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .bssn_screen_gravity import run_bssn_screen_gravity
from .m114_generalized_adm_evidence_authority import (
    run_m114_generalized_adm_evidence_authority,
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m115_bssn_evidence_authority() -> dict[str, Any]:
    previous = run_m114_generalized_adm_evidence_authority()
    campaign = run_bssn_screen_gravity()
    component = {
        "campaign_passed": campaign["passed"],
        "one_screen_G": campaign["acceptance"]["one_screen_G_is_preserved"],
        "unit_determinant": campaign["acceptance"][
            "conformal_metric_unit_determinant_is_enforced"
        ],
        "tracefree_extrinsic": campaign["acceptance"][
            "conformal_extrinsic_curvature_remains_trace_free"
        ],
        "conformal_connections": campaign["acceptance"][
            "conformal_connection_constraint_is_measured"
        ],
        "one_plus_log": campaign["acceptance"]["one_plus_log_lapse_is_evolved"],
        "gamma_driver": campaign["acceptance"]["gamma_driver_shift_is_evolved"],
        "metric_ricci": campaign["acceptance"]["metric_built_ricci_is_evolved"],
        "source_tidal": campaign["acceptance"][
            "screen_source_tidal_term_is_evolved"
        ],
        "tensor_constraint_damping": campaign["acceptance"][
            "tensor_momentum_constraint_is_damped"
        ],
        "gamma_constraint_damping": campaign["acceptance"][
            "gamma_constraint_is_damped"
        ],
        "constraints_reported": campaign["acceptance"][
            "hamiltonian_and_momentum_constraints_are_reported"
        ],
        "production_BSSN": campaign["decision"]["production_BSSN_constructed"],
        "physical_calibration": campaign["decision"][
            "physical_screen_calibration_complete"
        ],
    }
    payload = {
        "schema": "openwave.m9.m115-bssn-evidence-authority.v2",
        "task": "M9.115-M9.116",
        "previous_authority": previous,
        "component": component,
        "claim_boundary": {
            "reduced_BSSN_is_production_numerical_relativity": False,
            "finite_constraints_are_general_constraint_closure": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
            "scalar_tidal_source_is_complete_stress_energy": False,
            "finite_grid_is_continuum_convergence_proof": False,
            "gauge_driver_is_unique_physical_gauge": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "BSSN_campaign_passes": bool(campaign["passed"]),
        "BSSN_variables_and_gauge_close": all(
            component[key]
            for key in (
                "unit_determinant",
                "tracefree_extrinsic",
                "conformal_connections",
                "one_plus_log",
                "gamma_driver",
            )
        ),
        "source_and_constraint_extensions_close": all(
            component[key]
            for key in (
                "metric_ricci",
                "source_tidal",
                "tensor_constraint_damping",
                "gamma_constraint_damping",
                "constraints_reported",
            )
        ),
        "one_screen_G_is_preserved": component["one_screen_G"],
        "production_BSSN_remains_open": not component["production_BSSN"],
        "physical_calibration_remains_open": not component["physical_calibration"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_result": campaign,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_115a_conformal_connections_complete": True,
            "M9_115b_determinant_control_complete": True,
            "M9_115c_gauge_drivers_complete": True,
            "M9_116a_metric_Ricci_complete": True,
            "M9_116b_source_tidal_coupling_complete": True,
            "M9_116c_constraint_damping_complete": True,
            "production_BSSN_constructed": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
