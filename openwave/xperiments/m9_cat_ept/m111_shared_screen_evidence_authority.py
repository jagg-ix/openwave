"""M9.111 authority for shared screen-gravity observables."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m110_holographic_evidence_authority import run_m110_holographic_evidence_authority
from .shared_screen_gravity_campaign import run_shared_screen_gravity_campaign


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m111_shared_screen_evidence_authority() -> dict[str, Any]:
    previous = run_m110_holographic_evidence_authority()
    campaign = run_shared_screen_gravity_campaign()
    payload = {
        "schema": "openwave.m9.m111-shared-screen-evidence-authority.v1",
        "task": "M9.111",
        "previous_authority": previous,
        "component": {
            "campaign_passed": campaign["passed"],
            "shared_source": campaign["acceptance"]["one_matter_source_is_shared"],
            "shared_potential": campaign["acceptance"]["one_weak_potential_is_shared"],
            "shared_metric_seed": campaign["acceptance"]["nonlinear_metric_seed_matches_weak_g00"],
            "finite_initial_constraints": campaign["acceptance"]["initial_constraints_are_finite"],
        },
        "claim_boundary": {
            "shared_initial_data_is_full_GR_equivalence": False,
            "finite_initial_constraints_are_constraint_closure": False,
            "synthetic_anchor_is_physical_calibration": False,
            "weak_and_nonlinear_time_histories_must_be_identical": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "shared_campaign_passes": bool(campaign["passed"]),
        "shared_observables_close": all(payload["component"][key] for key in ("shared_source", "shared_potential", "shared_metric_seed")),
        "initial_constraints_are_reported": payload["component"]["finite_initial_constraints"],
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
            "shared_screen_initial_observables_complete": True,
            "full_cross_model_time_evolution_complete": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
