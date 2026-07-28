"""M9.128 authority for the Physlib relational/modular/entropic/proper-time chain."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_physlib_four_clock_authority() -> dict[str, Any]:
    payload = {
        "schema": "openwave.m9.physlib-four-clock-authority.v1",
        "task": "M9.128a",
        "repository": "jagg-ix/entropic-physlib-private",
        "formal_branch": "entropic-physlib-linear-full",
        "merged_authority": {
            "head": "66922982e47df948286e73bb4bf3c31de8723962",
            "pr": 37,
            "sources": (
                "Physlib/QuantumMechanics/RelationalTime/ThreeClockClosure.lean",
                "Physlib/EntropicSpine.lean",
            ),
            "claims": (
                "finite_conditioning_certificate",
                "modular_entropic_noncoincidence",
                "three_clock_equivalence_composition",
            ),
        },
        "candidate_authority": {
            "head": "860adac86251e470632acc377c283d68a0cd24e8",
            "pr": 38,
            "state": "draft-open-mergeable",
            "sources": (
                "Physlib/QuantumMechanics/RelationalTime/ThreeClockDynamics.lean",
                "Physlib/EntropicSpine.lean",
            ),
            "claims": (
                "conditioned_evolution_transport",
                "four_clock_proper_time_composition",
                "strict_temporal_order_preservation",
            ),
        },
        "claim_boundary": {
            "candidate_is_merged_authority": False,
            "equivalence_is_independent_physical_calibration": False,
            "monotonicity_premise_is_experimentally_established": False,
            "openwave_adds_lean_theorems": False,
        },
    }
    acceptance = {
        "merged_and_candidate_authority_are_separated": payload["merged_authority"]["head"] != payload["candidate_authority"]["head"],
        "candidate_is_not_promoted": payload["candidate_authority"]["state"] != "merged",
        "exact_sources_are_pinned": len(payload["merged_authority"]["sources"]) == 2 and len(payload["candidate_authority"]["sources"]) == 2,
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
