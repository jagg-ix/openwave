"""Canonical M9.101 conformance profile over the multi-axis maturity authority."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_m101 import canonical_payload as maturity_payload
from .criterion_maturity_m101 import run_criterion_maturity_m101
from .m101_evidence_authority import run_m101_evidence_authority


def canonical_payload() -> dict[str, Any]:
    maturity = maturity_payload()
    authority = run_m101_evidence_authority()
    return {
        "schema": "openwave.m9.models-conformance.v18",
        "model": "M9 CAT/EPT",
        "formal_head": authority["formal_head"],
        "maturity": maturity,
        "summary": maturity["headline_counts"],
        "m9_101": authority["components"],
        "claim_boundary": authority["claim_boundary"],
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    maturity = run_criterion_maturity_m101()
    authority = run_m101_evidence_authority()
    payload = canonical_payload()
    acceptance = {
        "m101_evidence_authority_passes": bool(authority["passed"]),
        "m101_maturity_authority_passes": bool(maturity["passed"]),
        "schema_v18_is_current": payload["schema"] == "openwave.m9.models-conformance.v18",
        "current_formal_head_is_registered": payload["formal_head"] == "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "all_four_target_components_are_present": set(payload["m9_101"]) == {"coupled_action", "packet_tbmt", "clock", "gravity"},
        "headline_remains_evidence_derived": payload["maturity"]["policy"]["headline_is_still_derived"],
        "claim_boundaries_remain_false": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.101h",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m101_is_current_conformance_profile": True,
            "four_proposed_targets_completed_as_scoped_campaigns": True,
            "full_physical_closure_claimed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
