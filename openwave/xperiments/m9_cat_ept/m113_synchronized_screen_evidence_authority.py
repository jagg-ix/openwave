"""M9.113 authority for synchronized weak/nonlinear screen-gravity evolution."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m111_shared_screen_evidence_authority import run_m111_shared_screen_evidence_authority
from .synchronized_screen_gravity_evolution import run_synchronized_screen_gravity_evolution


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m113_synchronized_screen_evidence_authority() -> dict[str, Any]:
    previous = run_m111_shared_screen_evidence_authority()
    campaign = run_synchronized_screen_gravity_evolution()
    component = {
        "campaign_passed": campaign["passed"],
        "shared_matter_history": campaign["acceptance"]["shared_matter_history_closes"],
        "shared_source_history": campaign["acceptance"]["shared_source_history_closes"],
        "shared_potential_history": campaign["acceptance"]["shared_weak_potential_history_closes"],
        "shared_weak_metric_history": campaign["acceptance"]["shared_weak_metric_history_closes"],
        "nonlinear_geometry_evolved": campaign["acceptance"]["nonlinear_geometry_adds_dynamics"],
        "constraint_history_reported": campaign["acceptance"]["nonlinear_constraint_diagnostics_remain_finite"],
    }
    payload = {
        "schema": "openwave.m9.m113-synchronized-screen-evidence-authority.v1",
        "task": "M9.113",
        "previous_authority": previous,
        "component": component,
        "claim_boundary": {
            "shared_matter_history_is_full_GR_equivalence": False,
            "finite_constraint_history_is_constraint_closure": False,
            "reduced_conformal_ADM_is_general_GR": False,
            "synthetic_anchor_is_physical_calibration": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "synchronized_campaign_passes": bool(campaign["passed"]),
        "shared_weak_limit_histories_close": all(
            component[key]
            for key in (
                "shared_matter_history",
                "shared_source_history",
                "shared_potential_history",
                "shared_weak_metric_history",
            )
        ),
        "nonlinear_only_observables_are_reported": component["nonlinear_geometry_evolved"]
        and component["constraint_history_reported"],
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
            "synchronized_weak_limit_history_complete": True,
            "nonlinear_curvature_constraint_history_complete": True,
            "general_GR_evolution_complete": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
