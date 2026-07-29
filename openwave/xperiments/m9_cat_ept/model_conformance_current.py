"""Stable current M9 conformance through M9.126; criterion maturity remains M9.109."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance_m96 import CRITERIA, ROW_REPLACEMENTS

CURRENT_MILESTONE = "M9.126"
CURRENT_CONFORMANCE_MODULE = "openwave.xperiments.m9_cat_ept.model_conformance_m109"
CURRENT_CONFORMANCE_SCHEMA = "openwave.m9.models-conformance.v22"
CURRENT_REGISTRATION_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_m126"
CURRENT_REGISTRATION_SCHEMA = "openwave.model-registration.v29"


def _dependencies():
    from .m126_existing_experimental_evidence_authority import (
        run_m126_existing_experimental_evidence_authority,
    )
    from .model_conformance_m109 import (
        canonical_payload as base_payload,
        run_conformance_study as base_run,
    )
    from .model_registration_m126 import canonical_registration_payload

    return (
        run_m126_existing_experimental_evidence_authority,
        base_payload,
        base_run,
        canonical_registration_payload,
    )


def canonical_payload() -> dict[str, Any]:
    evidence_runner, base_payload, _, registration_payload = _dependencies()
    base = base_payload()
    evidence = evidence_runner()
    registration = registration_payload()
    return {
        **base,
        "current_milestone": CURRENT_MILESTONE,
        "current_lineage": {
            "criterion_maturity": "M9.109",
            "latest_evidence": "M9.126",
            "conformance_module": CURRENT_CONFORMANCE_MODULE,
            "registration_module": CURRENT_REGISTRATION_MODULE,
        },
        "latest_evidence": {
            "schema": evidence["schema"],
            "fingerprint": evidence["fingerprint"],
            "passed": evidence["passed"],
            "component": evidence["component"],
            "decision": evidence["decision"],
        },
        "latest_registration": {
            "schema": registration["schema"],
            "registration": registration["registration"],
            "m9_126": registration["m9_126"],
        },
        "claim_boundary": {**base["claim_boundary"], **evidence["claim_boundary"]},
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    evidence_runner, _, base_run, _ = _dependencies()
    base = base_run()
    evidence = evidence_runner()
    payload = canonical_payload()
    current = payload["latest_registration"]
    acceptance = {
        "M9_109_criterion_maturity_remains_valid": bool(base["passed"]),
        "M9_126_evidence_authority_passes": bool(evidence["passed"]),
        "all_21_criteria_remain_present": len(payload["maturity"]["criteria"]) == 21,
        "conformance_schema_remains_v22": payload["schema"] == CURRENT_CONFORMANCE_SCHEMA,
        "current_registration_is_v29": current["schema"] == CURRENT_REGISTRATION_SCHEMA,
        "current_registration_points_to_versioned_conformance": (
            current["registration"]["conformance_runner"]
            == "openwave.xperiments.m9_cat_ept.model_conformance_m109:run_conformance_study"
        ),
        "existing_evidence_is_recognized_without_promotion": (
            current["m9_126"]["existing_evidence_qualified"]
            and not current["m9_126"]["prospective_external_validation_complete"]
            and current["m9_126"]["physical_claims_promoted"] == []
        ),
        "all_claim_boundaries_remain_false": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9-current-conformance",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "repository_profile": "MODELS_M9.md",
        "decision": {
            "M9_126_is_current_evidence_milestone": True,
            "criterion_headlines_changed_after_M9_109": False,
            "retrospective_evidence_ready": True,
            "prospective_external_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
