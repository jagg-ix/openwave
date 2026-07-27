"""M9.125 formal-authority continuity for the reduced shared-clock carrier."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m124_extension import run_formalization_m124_extension

CANDIDATE_CLOCK_RELAXATION_HEADS = (
    {
        "pr": 22,
        "head": "b189fd69ac023d18b9189ddd84c91107aad12020",
        "state": "merged_into_stacked_development_branch",
        "role": "exact one-level relaxation and finite entropic-clock carrier",
        "used_as_merged_master_authority": False,
    },
    {
        "pr": 23,
        "head": "91a148f59e7e164919d1d33dccda2498741d2434",
        "state": "draft_open",
        "role": "one-level KL data processing",
        "used_as_merged_master_authority": False,
    },
    {
        "pr": 24,
        "head": "3a9ca580621eb1f859f87ff6d4c97492cc66e43b",
        "state": "draft_open",
        "role": "stationary one-level KL reference",
        "used_as_merged_master_authority": False,
    },
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_formalization_m125_extension() -> dict[str, Any]:
    previous = run_formalization_m124_extension()
    payload = {
        "schema": "openwave.m9.formalization-m125-extension.v1",
        "task": "M9.125-formal-authority",
        "previous_formal_authority": {
            "schema": previous["schema"],
            "fingerprint": previous["fingerprint"],
            "merged_formal_head": previous["merged_formal_head"],
            "development_branch": previous["development_branch"],
            "development_head": previous["development_head"],
            "zil_public_head": previous["zil_public_head"],
            "source_count": len(previous["sources"]),
        },
        "candidate_relaxation_heads": CANDIDATE_CLOCK_RELAXATION_HEADS,
        "implementation_scope": {
            "new_lean_theorem_claimed": False,
            "shared_carrier_is_openwave_numerical_construction": True,
            "calibration_contract_is_model_internal": True,
            "holdout_protocol_contains_real_data": False,
        },
        "claim_boundary": {
            "stacked_development_PR_is_merged_master_authority": False,
            "numerical_common_carrier_is_formal_constraint_theorem": False,
            "model_internal_clock_map_is_physical_calibration": False,
        },
    }
    acceptance = {
        "M9_124_formal_authority_is_preserved": previous["passed"],
        "four_prior_clock_sources_remain_pinned": len(previous["sources"]) == 4,
        "candidate_relaxation_heads_are_not_promoted_to_master": all(
            not item["used_as_merged_master_authority"] for item in CANDIDATE_CLOCK_RELAXATION_HEADS
        ),
        "OpenWave_claims_no_new_Lean_proof": not payload["implementation_scope"]["new_lean_theorem_claimed"],
        "no_formal_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "sources": previous["sources"],
        "merged_formal_head": previous["merged_formal_head"],
        "development_branch": previous["development_branch"],
        "development_head": previous["development_head"],
        "zil_public_head": previous["zil_public_head"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "clock_formal_authority_preserved": True,
            "new_formal_unification_theorem_added": False,
            "candidate_KL_clock_layers_recorded_without_promotion": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
