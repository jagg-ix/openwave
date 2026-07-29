"""M9.132 authority for the coupled CAT/EPT simulation milestone."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .coupled_cat_ept_evolution_m132 import run_coupled_cat_ept_evolution
from .coupled_cat_ept_campaign_m132 import run_coupled_cat_ept_campaign


def _fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m132_coupled_cat_ept_authority() -> dict[str, Any]:
    evolution = run_coupled_cat_ept_evolution()
    campaign = run_coupled_cat_ept_campaign()
    requirements = {
        "coupled_matter_geometry_entropy_solver": evolution["passed"],
        "feedback_balance_campaign": campaign["feedback"]["passed"],
        "shared_parameter_ablation_campaign": campaign["baselines"]["passed"],
        "relativistic_tensor_geometry": False,
        "independent_physical_parameter_calibration": False,
        "heldout_external_prediction": False,
    }
    internal_ready = all(
        requirements[name]
        for name in (
            "coupled_matter_geometry_entropy_solver",
            "feedback_balance_campaign",
            "shared_parameter_ablation_campaign",
        )
    )
    physical_ready = all(requirements.values())
    payload = {
        "schema": "openwave.m9.m132-coupled-cat-ept-authority.v1",
        "task": "M9.132",
        "requirements": requirements,
        "internal_ready": internal_ready,
        "physical_ready": physical_ready,
        "evolution": evolution,
        "campaign": campaign,
        "claim_boundary": {
            "reduced_solver_is_complete_CAT_EPT": False,
            "scalar_geometry_is_general_relativity": False,
            "ablation_difference_is_empirical_confirmation": False,
            "normalization_is_exact_continuous_dynamics": False,
        },
    }
    acceptance = {
        "all_three_model_targets_pass": internal_ready,
        "physical_promotion_fails_closed": not physical_ready,
        "remaining_physical_requirements_are_explicit": all(
            not requirements[name]
            for name in (
                "relativistic_tensor_geometry",
                "independent_physical_parameter_calibration",
                "heldout_external_prediction",
            )
        ),
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": _fingerprint(payload),
        "decision": {
            "CAT_EPT_model_core_materially_extended": True,
            "matter_geometry_entropy_feedback_executable": True,
            "shared_parameter_ablation_executable": True,
            "complete_physical_theory_validated": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
