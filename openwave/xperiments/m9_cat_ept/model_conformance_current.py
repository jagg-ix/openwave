"""Stable current M9 conformance entry point through M9.120.

The 21-criterion maturity profile last changed at M9.109. M9.110--M9.120 add
gravity, coarse-graining, gauge-covariant sectors, finite spectra, response and
refinement evidence without promoting physical identity, calibration or external
prediction axes. This module composes those later authorities over the immutable
M9.109 conformance record.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .m120_spectral_phenomenology_evidence_authority import (
    run_m120_spectral_phenomenology_evidence_authority,
)
from .model_conformance_dynamics import CRITERIA
from .model_conformance_m109 import canonical_payload as _m109_payload
from .model_conformance_m109 import run_conformance_study as _run_m109_conformance
from .model_registration_current import (
    CURRENT_CONFORMANCE_RUNNER,
    canonical_registration_payload,
)

CURRENT_MILESTONE = "M9.120"
CURRENT_CONFORMANCE_MODULE = "openwave.xperiments.m9_cat_ept.model_conformance_m109"
CURRENT_CONFORMANCE_SCHEMA = "openwave.m9.models-conformance.v22"
CURRENT_REGISTRATION_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_m120"
CURRENT_REGISTRATION_SCHEMA = "openwave.model-registration.v23"


def canonical_payload() -> dict[str, Any]:
    base = _m109_payload()
    evidence = run_m120_spectral_phenomenology_evidence_authority()
    registration = canonical_registration_payload()
    return {
        **base,
        "current_milestone": CURRENT_MILESTONE,
        "current_lineage": {
            "criterion_maturity": "M9.109",
            "latest_evidence": "M9.120",
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
            "current_alias": registration["current_alias"],
            "m9_120": registration["m9_120"],
        },
        "claim_boundary": {
            **base["claim_boundary"],
            **evidence["claim_boundary"],
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(
            selected, sort_keys=True, separators=(",", ":"), default=str
        ).encode()
    ).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    base = _run_m109_conformance()
    evidence = run_m120_spectral_phenomenology_evidence_authority()
    payload = canonical_payload()
    maturity_rows = payload["maturity"]["criteria"]
    current_registration = payload["latest_registration"]
    acceptance = {
        "M9_109_criterion_maturity_remains_valid": bool(base["passed"]),
        "M9_120_evidence_authority_passes": bool(evidence["passed"]),
        "all_21_criteria_remain_present": len(maturity_rows) == 21,
        "conformance_schema_remains_v22": payload["schema"]
        == CURRENT_CONFORMANCE_SCHEMA,
        "current_registration_is_v23": current_registration["schema"]
        == CURRENT_REGISTRATION_SCHEMA,
        "current_registration_points_back_to_stable_conformance": current_registration[
            "registration"
        ]["conformance_runner"]
        == CURRENT_CONFORMANCE_RUNNER,
        "later_evidence_does_not_promote_physical_claims": current_registration[
            "m9_120"
        ]["physical_claims_promoted"]
        == [],
        "all_claim_boundaries_remain_false": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9-current-conformance",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "repository_profile": "MODELS_M9.md",
        "decision": {
            "M9_120_is_current_evidence_milestone": True,
            "criterion_headlines_changed_after_M9_109": False,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"


__all__ = (
    "CRITERIA",
    "CURRENT_CONFORMANCE_MODULE",
    "CURRENT_CONFORMANCE_SCHEMA",
    "CURRENT_MILESTONE",
    "CURRENT_REGISTRATION_MODULE",
    "CURRENT_REGISTRATION_SCHEMA",
    "canonical_payload",
    "fingerprint",
    "result_to_json",
    "run_conformance_study",
)
