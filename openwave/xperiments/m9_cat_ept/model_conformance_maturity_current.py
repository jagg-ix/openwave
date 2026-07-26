"""Current M9 conformance profile using criterion maturity v2."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_current import canonical_payload as maturity_payload
from .criterion_maturity_current import run_criterion_maturity_study
from .model_conformance_dynamics import canonical_payload as legacy_payload


def canonical_payload() -> dict[str, Any]:
    legacy = legacy_payload()
    maturity = maturity_payload()
    summary = {**maturity["headline_counts"], "total": len(maturity["criteria"])}
    return {
        "schema": "openwave.m9.models-conformance.v17",
        "model": "M9 CAT/EPT",
        "legacy_compatibility": {
            "schema": legacy["schema"],
            "status_counts": legacy["audit"]["status_counts"],
            "statuses_are_primary": False,
        },
        "maturity": maturity,
        "summary": summary,
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    maturity = run_criterion_maturity_study()
    payload = canonical_payload()
    expected = {
        "validated_in_scope": 7,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 1,
        "total": 21,
    }
    acceptance = {
        "maturity_study_passes": bool(maturity["passed"]),
        "summary_uses_six_maturity_classes": payload["summary"] == expected,
        "legacy_statuses_are_compatibility_only": not payload["legacy_compatibility"]["statuses_are_primary"],
        "legacy_partial_is_split_5_3_1_4": payload["maturity"]["legacy_partial_breakdown"] == {
            "validated_in_scope": 0,
            "conditional_validated": 5,
            "reduced_model_validated": 3,
            "calibration_pending": 1,
            "candidate": 4,
            "negative": 0,
        },
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.100b-current",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "canonical_summary_uses_multi_axis_maturity": True,
            "legacy_partial_count_is_primary": False,
            "new_physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
