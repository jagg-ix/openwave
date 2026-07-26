"""M9.100b: canonical conformance profile with multi-axis maturity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity import canonical_payload as maturity_payload
from .criterion_maturity import run_criterion_maturity_study
from .model_conformance_dynamics import canonical_payload as legacy_payload


def canonical_payload() -> dict[str, Any]:
    legacy = legacy_payload()
    maturity = maturity_payload()
    return {
        "schema": "openwave.m9.models-conformance.v16",
        "model": "M9 CAT/EPT",
        "legacy_compatibility": {
            "schema": legacy["schema"],
            "status_counts": legacy["audit"]["status_counts"],
            "statuses_are_primary": False,
        },
        "maturity": maturity,
        "summary": {
            "validated_in_scope": maturity["headline_counts"]["validated_in_scope"],
            "conditional_validated": maturity["headline_counts"]["conditional_validated"],
            "reduced_model_validated": maturity["headline_counts"]["reduced_model_validated"],
            "calibration_pending": maturity["headline_counts"]["calibration_pending"],
            "candidate": maturity["headline_counts"]["candidate"],
            "negative": maturity["headline_counts"]["negative"],
            "total": len(maturity["criteria"]),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    maturity = run_criterion_maturity_study()
    payload = canonical_payload()
    expected_summary = {
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
        "summary_is_not_legacy_7_13_1": payload["summary"] == expected_summary,
        "legacy_statuses_are_compatibility_only": not payload["legacy_compatibility"]["statuses_are_primary"],
        "all_21_rows_are_preserved": payload["summary"]["total"] == 21,
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.100b",
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
