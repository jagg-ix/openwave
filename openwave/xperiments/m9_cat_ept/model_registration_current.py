"""Stable current M9 registration entry point through M9.117.

Versioned registration modules remain immutable evidence records.  Callers that need
the current CAT/EPT model state should import this module rather than guessing the
latest ``model_registration_mNNN`` filename.
"""
from __future__ import annotations

from typing import Any, Mapping

from .model_registration import M9_REGISTRATION
from .model_registration_m117 import (
    canonical_registration_payload,
    fingerprint as _fingerprint,
    result_to_json,
    run_model_registration_study,
)

CURRENT_MILESTONE = "M9.117"
CURRENT_SCHEMA = "openwave.model-registration.v21"
CURRENT_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_m117"


def canonical_payload() -> dict[str, Any]:
    """Compatibility alias for the current canonical registration payload."""
    return canonical_registration_payload()


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    """Fingerprint the supplied payload, or the current registration when omitted."""
    selected = canonical_registration_payload() if payload is None else payload
    return _fingerprint(selected)


__all__ = (
    "CURRENT_MILESTONE",
    "CURRENT_MODULE",
    "CURRENT_SCHEMA",
    "M9_REGISTRATION",
    "canonical_payload",
    "canonical_registration_payload",
    "registration_fingerprint",
    "result_to_json",
    "run_model_registration_study",
)
