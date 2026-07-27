"""Stable current M9 registration entry point through M9.123."""
from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_registration import M9_REGISTRATION as HISTORICAL_M9_REGISTRATION
from .model_registration_m123 import canonical_registration_payload as _m123_payload, run_model_registration_study as _run_m123_registration

CURRENT_MILESTONE = "M9.123"
CURRENT_SCHEMA = "openwave.model-registration.v26"
CURRENT_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_m123"
CURRENT_ALIAS_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_current"
CURRENT_CONFORMANCE_RUNNER = "openwave.xperiments.m9_cat_ept.model_conformance_current:run_conformance_study"

M9_REGISTRATION = replace(HISTORICAL_M9_REGISTRATION, conformance_runner=CURRENT_CONFORMANCE_RUNNER, comparison_profile="MODELS_M9.md")


def canonical_registration_payload() -> dict[str, Any]:
    versioned = _m123_payload()
    return {**versioned, "registration": asdict(M9_REGISTRATION), "current_alias": {"milestone": CURRENT_MILESTONE, "module": CURRENT_ALIAS_MODULE, "versioned_module": CURRENT_MODULE, "conformance_runner": CURRENT_CONFORMANCE_RUNNER}}


def canonical_payload() -> dict[str, Any]:
    return canonical_registration_payload()


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def run_model_registration_study() -> dict[str, Any]:
    versioned = _run_m123_registration()
    payload = canonical_registration_payload()
    acceptance = {**versioned["acceptance"], "stable_alias_preserves_schema_v26": payload["schema"] == CURRENT_SCHEMA, "stable_registration_points_to_current_conformance": payload["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER, "stable_profile_is_MODELS_M9": payload["registration"]["comparison_profile"] == "MODELS_M9.md", "current_alias_fingerprint_is_deterministic": registration_fingerprint(payload) == registration_fingerprint(payload)}
    return {**payload, "task": "M9-current-registration", "registration_fingerprint": registration_fingerprint(payload), "acceptance": acceptance, "passed": all(acceptance.values()), "decision": {**versioned["decision"], "stable_registration_alias_is_current": True, "physical_claims_promoted": []}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"


__all__ = ("CURRENT_ALIAS_MODULE", "CURRENT_CONFORMANCE_RUNNER", "CURRENT_MILESTONE", "CURRENT_MODULE", "CURRENT_SCHEMA", "M9_REGISTRATION", "canonical_payload", "canonical_registration_payload", "registration_fingerprint", "result_to_json", "run_model_registration_study")
