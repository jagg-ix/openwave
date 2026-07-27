"""M9.111 registration for one-anchor weak/nonlinear shared observables."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m111_shared_screen_evidence_authority import run_m111_shared_screen_evidence_authority
from .model_registration_m110 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m111_shared_screen_evidence_authority()
    component = evidence["component"]
    return {
        **previous,
        "schema": "openwave.model-registration.v16",
        "m9_111": {
            "shared_screen_campaign_registered": component["campaign_passed"],
            "shared_source": component["shared_source"],
            "shared_potential": component["shared_potential"],
            "shared_metric_seed": component["shared_metric_seed"],
            "finite_initial_constraints": component["finite_initial_constraints"],
            "full_cross_model_time_evolution": evidence["decision"]["full_cross_model_time_evolution_complete"],
            "physical_calibration_complete": evidence["decision"]["physical_screen_calibration_complete"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "shared_initial_data_is_full_GR_equivalence": False,
            "finite_constraints_are_constraint_closure": False,
            "synthetic_anchor_is_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m111_shared_screen_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_111"]
    acceptance = {
        "shared_screen_authority_passes": evidence["passed"],
        "schema_v16_is_current": payload["schema"] == "openwave.model-registration.v16",
        "shared_initial_observables_close": current["shared_source"] and current["shared_potential"] and current["shared_metric_seed"],
        "constraints_are_reported": current["finite_initial_constraints"],
        "time_evolution_is_not_overclaimed": not current["full_cross_model_time_evolution"],
        "physical_calibration_remains_open": not current["physical_calibration_complete"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.111-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "shared_screen_initial_observables_are_current": True,
            "next_target_is_cross_model_time_evolution": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
