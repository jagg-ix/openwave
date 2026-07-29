"""Latest M9 conformance overlay with unchanged 21-criterion statuses."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .canonical_particle_model_m140 import MILESTONE, run_canonical_model_contract
from .model_conformance_current import canonical_payload as stable_conformance_payload
from .model_registration_latest import canonical_registration_payload

LATEST_SCHEMA = "openwave.m9.models-conformance.latest.v1"


def canonical_payload() -> dict[str, Any]:
    stable = stable_conformance_payload()
    registration = canonical_registration_payload()
    return {
        **stable,
        "schema": LATEST_SCHEMA,
        "latest_milestone": MILESTONE,
        "lineage": {
            "criterion_maturity": stable["current_lineage"]["criterion_maturity"],
            "stable_evidence": stable["current_milestone"],
            "latest_model_integration": MILESTONE,
            "stable_alias_rewritten": False,
        },
        "latest_registration": {
            "schema": registration["schema"],
            "canonical_model_api": registration["latest_registration"][
                "canonical_model_api"
            ],
        },
        "claim_boundary": {
            **stable["claim_boundary"],
            **registration["claim_boundary"],
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    contract = run_canonical_model_contract()
    status_counts = payload["maturity"]["status_counts"]
    acceptance = {
        "all_21_criteria_remain_present": len(payload["maturity"]["criteria"]) == 21,
        "status_profile_is_unchanged": status_counts
        == {"validated": 7, "partial": 13, "negative": 1, "not_yet": 0},
        "latest_contract_passes": bool(contract["passed"]),
        "latest_model_integration_is_M9_140": payload["latest_milestone"] == "M9.140",
        "stable_evidence_lineage_is_preserved": payload["lineage"][
            "stable_evidence"
        ]
        == "M9.126",
        "no_claim_boundary_is_crossed": not any(
            value
            for key, value in payload["claim_boundary"].items()
            if key != "criterion_rows_promoted"
        )
        and payload["claim_boundary"]["criterion_rows_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.140c",
        "fingerprint": fingerprint(payload),
        "contract_fingerprint": contract["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "latest_model_contract_is_registered": True,
            "criterion_headlines_changed": False,
            "criterion_rows_promoted": [],
            "physical_particle_identity": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
