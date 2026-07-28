"""M9.128c fail-closed promotion gate for four-clock integration."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .physlib_four_clock_authority_m128 import run_physlib_four_clock_authority
from .four_clock_integration_m128 import run_four_clock_integration


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_four_clock_promotion_gate() -> dict[str, Any]:
    authority = run_physlib_four_clock_authority()
    integration = run_four_clock_integration()
    requirements = {
        "merged_conditioning_authority": authority["merged_authority"]["pr"] == 37,
        "candidate_dynamics_recorded_without_promotion": authority["candidate_authority"]["state"] == "draft-open-mergeable",
        "executable_composition_control": integration["passed"],
        "independent_pairwise_clock_calibration": False,
        "measured_monotonicity_of_pairwise_maps": False,
        "heldout_four_clock_observation": False,
        "candidate_physlib_pr_merged_and_compiled": False,
    }
    internal_ready = all(requirements[name] for name in (
        "merged_conditioning_authority",
        "candidate_dynamics_recorded_without_promotion",
        "executable_composition_control",
    ))
    physical_ready = all(requirements.values())
    payload = {
        "schema": "openwave.m9.four-clock-promotion-gate.v1",
        "task": "M9.128c",
        "requirements": requirements,
        "internal_ready": internal_ready,
        "physical_ready": physical_ready,
        "decision": {
            "formal_composition_surface_available": True,
            "candidate_dynamics_surface_available": True,
            "physical_clock_calibration_complete": False,
            "universal_clock_claim_allowed": False,
        },
    }
    acceptance = {
        "internal_gate_passes": internal_ready,
        "physical_gate_fails_closed": not physical_ready,
        "each_physical_blocker_is_explicit": all(not requirements[name] for name in (
            "independent_pairwise_clock_calibration",
            "measured_monotonicity_of_pairwise_maps",
            "heldout_four_clock_observation",
            "candidate_physlib_pr_merged_and_compiled",
        )),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
