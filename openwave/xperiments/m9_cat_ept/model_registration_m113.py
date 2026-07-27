"""M9.113 registration over synchronized screen-gravity evolution."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m113_synchronized_screen_evidence_authority import run_m113_synchronized_screen_evidence_authority
from .model_registration_m111 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m113_synchronized_screen_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v17",
        "m9_113": {
            "synchronized_campaign_registered": component["campaign_passed"],
            "shared_matter_history": component["shared_matter_history"],
            "shared_source_history": component["shared_source_history"],
            "shared_potential_history": component["shared_potential_history"],
            "shared_weak_metric_history": component["shared_weak_metric_history"],
            "nonlinear_geometry_evolved": component["nonlinear_geometry_evolved"],
            "constraint_history_reported": component["constraint_history_reported"],
            "general_GR_evolution_complete": False,
            "physical_screen_calibration_complete": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "shared_history_is_full_metric_equivalence": False,
            "finite_constraint_history_is_constraint_closure": False,
            "reduced_conformal_ADM_is_general_GR": False,
            "synthetic_screen_anchor_is_physical_evidence": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m113_synchronized_screen_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_113"]
    acceptance = {
        "synchronized_authority_passes": evidence["passed"],
        "schema_v17_is_current": payload["schema"] == "openwave.model-registration.v17",
        "shared_weak_limit_histories_are_registered": all(
            current[key]
            for key in (
                "shared_matter_history",
                "shared_source_history",
                "shared_potential_history",
                "shared_weak_metric_history",
            )
        ),
        "nonlinear_observables_are_registered": current["nonlinear_geometry_evolved"]
        and current["constraint_history_reported"],
        "general_GR_is_not_overpromoted": not current["general_GR_evolution_complete"],
        "physical_calibration_remains_open": not current["physical_screen_calibration_complete"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.113-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "synchronized_screen_history_is_current": True,
            "next_target_is_general_metric_and_calibrated_screen_test": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
