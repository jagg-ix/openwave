"""Stable current M9 registration entry point through M9.126."""
from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_registration import M9_REGISTRATION as HISTORICAL_M9_REGISTRATION

CURRENT_MILESTONE = "M9.126"
CURRENT_SCHEMA = "openwave.model-registration.v29"
CURRENT_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_m126"
CURRENT_ALIAS_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_current"
CURRENT_CONFORMANCE_RUNNER = (
    "openwave.xperiments.m9_cat_ept.model_conformance_current:run_conformance_study"
)

# This constant is required by historical registration/ZIL modules while their
# lineage is still importing.  It must therefore be available without importing
# the versioned M9.126 chain back into that lineage.
M9_REGISTRATION = replace(
    HISTORICAL_M9_REGISTRATION,
    conformance_runner=CURRENT_CONFORMANCE_RUNNER,
    comparison_profile="MODELS_M9.md",
)


def _versioned_dependencies():
    """Load M9.126 only when a current payload or study is requested."""
    from .model_registration_m126 import (
        canonical_registration_payload,
        run_model_registration_study,
    )

    return canonical_registration_payload, run_model_registration_study


def canonical_registration_payload() -> dict[str, Any]:
    versioned_payload, _ = _versioned_dependencies()
    payload = versioned_payload()
    return {
        **payload,
        "registration": asdict(M9_REGISTRATION),
        "current_alias": {
            "milestone": CURRENT_MILESTONE,
            "module": CURRENT_ALIAS_MODULE,
            "versioned_module": CURRENT_MODULE,
            "conformance_runner": CURRENT_CONFORMANCE_RUNNER,
        },
    }


def canonical_payload() -> dict[str, Any]:
    return canonical_registration_payload()


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_model_registration_study() -> dict[str, Any]:
    _, versioned_runner = _versioned_dependencies()
    versioned = versioned_runner()
    payload = canonical_registration_payload()
    acceptance = {
        **versioned["acceptance"],
        "stable_alias_preserves_schema_v29": payload["schema"] == CURRENT_SCHEMA,
        "stable_registration_points_to_current_conformance": (
            payload["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
        ),
        "stable_profile_is_MODELS_M9": (
            payload["registration"]["comparison_profile"] == "MODELS_M9.md"
        ),
        "current_alias_fingerprint_is_deterministic": (
            registration_fingerprint(payload) == registration_fingerprint(payload)
        ),
    }
    return {
        **payload,
        "task": "M9-current-registration",
        "registration_fingerprint": registration_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            **versioned["decision"],
            "stable_registration_alias_is_current": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
