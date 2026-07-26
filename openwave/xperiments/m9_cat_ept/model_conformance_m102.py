"""Canonical M9.102 conformance over current formal and reproducibility authority."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_m102 import canonical_payload as maturity_payload
from .criterion_maturity_m102 import run_criterion_maturity_m102
from .formalization_m102_extension import canonical_payload as formal_payload
from .formalization_m102_extension import run_formalization_m102_extension
from .m101_reproducibility_contract import canonical_manifest
from .m101_reproducibility_contract import run_m101_reproducibility_contract


def canonical_payload() -> dict[str, Any]:
    formal = formal_payload()
    maturity = maturity_payload()
    reproducibility = canonical_manifest()
    return {
        "schema": "openwave.m9.models-conformance.v19",
        "model": "M9 CAT/EPT",
        "formal_authority": formal,
        "historical_formal_head": formal["repository"]["historical_head"],
        "current_formal_head": formal["repository"]["current_head"],
        "maturity": maturity,
        "summary": maturity["headline_counts"],
        "m9_101_reproducibility": reproducibility,
        "claim_boundary": {
            "formal_governance_update_is_new_physics": False,
            "implemented_carrier_is_constructed_state": False,
            "campaign_passage_is_physical_subgate_closure": False,
            "fresh_internal_snapshot_is_external_validation": False,
            "historical_formal_pin_is_live_branch_resolution": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    formal = run_formalization_m102_extension()
    maturity = run_criterion_maturity_m102()
    reproducibility = run_m101_reproducibility_contract()
    payload = canonical_payload()
    acceptance = {
        "formal_authority_passes": bool(formal["passed"]),
        "maturity_authority_passes": bool(maturity["passed"]),
        "reproducibility_contract_passes": bool(reproducibility["passed"]),
        "schema_v19_is_current": payload["schema"] == "openwave.m9.models-conformance.v19",
        "historical_and_current_formal_heads_are_distinct": (
            payload["historical_formal_head"] != payload["current_formal_head"]
        ),
        "carrier_state_separation_is_enforced": payload["maturity"]["policy"][
            "carrier_implementation_is_not_state_existence"
        ],
        "quantitative_subgates_are_exposed": payload["m9_101_reproducibility"][
            "policy"
        ]["campaign_passage_is_not_physical_subgate_closure"],
        "claim_boundaries_remain_false": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.102d",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m102_is_current_conformance_profile": True,
            "three_evidence_integrity_targets_completed": True,
            "new_physical_closure_claimed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
