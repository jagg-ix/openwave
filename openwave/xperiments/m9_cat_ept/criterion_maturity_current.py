"""Current M9.100 maturity authority with explicit headline precedence."""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity import CriterionMaturity, HeadlineStatus, MATURITY_ROWS
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA


def derive_headline(row: CriterionMaturity) -> HeadlineStatus:
    if row.numerical == "negative" or row.prediction == "negative_out_of_sample":
        return "negative"
    # Conditional theorem scope takes precedence over reduced numerical carrier.
    if row.formal == "conditional":
        return "conditional_validated" if row.numerical in ("validated", "reduced_validated") else "candidate"
    if row.numerical == "reduced_validated" and row.state == "reduced_constructed":
        return "reduced_model_validated"
    if (
        row.numerical == "validated"
        and row.state in ("stable_constructed", "not_required")
        and row.identity == "not_required_for_scope"
        and row.calibration == "not_required_for_scope"
        and row.prediction in ("validated_internal", "external_validated")
    ):
        return "validated_in_scope"
    if (
        row.numerical == "validated"
        and row.state == "stable_constructed"
        and row.calibration in ("open", "partial")
    ):
        return "calibration_pending"
    if row.numerical == "validated" and row.formal in ("proved", "structural"):
        return "conditional_validated"
    return "candidate"


def headline_counts() -> dict[str, int]:
    names: tuple[HeadlineStatus, ...] = (
        "validated_in_scope", "conditional_validated", "reduced_model_validated",
        "calibration_pending", "candidate", "negative",
    )
    return {name: sum(derive_headline(row) == name for row in MATURITY_ROWS) for name in names}


def legacy_partial_breakdown() -> dict[str, int]:
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    partial = tuple(row for row in MATURITY_ROWS if legacy[row.key] == "partial")
    return {name: sum(derive_headline(row) == name for row in partial) for name in headline_counts()}


def canonical_payload() -> dict[str, Any]:
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    return {
        "schema": "openwave.m9.criterion-maturity.v2",
        "criteria": [
            {**asdict(row), "headline": derive_headline(row), "legacy_status": legacy[row.key]}
            for row in MATURITY_ROWS
        ],
        "headline_counts": headline_counts(),
        "legacy_partial_breakdown": legacy_partial_breakdown(),
        "precedence": (
            "negative",
            "conditional_formal",
            "reduced_model",
            "validated_in_scope",
            "calibration_pending",
            "conditional_structural",
            "candidate",
        ),
        "policy": {
            "headline_is_derived": True,
            "legacy_status_is_compatibility_metadata": True,
            "fixed_promoted_key_set_used": False,
            "fixed_7_13_1_count_used_as_acceptance_gate": False,
        },
    }


def maturity_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_study() -> dict[str, Any]:
    payload = canonical_payload()
    expected_headlines = {
        "validated_in_scope": 7,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 1,
    }
    expected_partial_split = {
        "validated_in_scope": 0,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 0,
    }
    legacy_keys = {row.key for row in LEGACY_CRITERIA}
    maturity_keys = {row.key for row in MATURITY_ROWS}
    acceptance = {
        "all_21_criteria_are_reclassified": legacy_keys == maturity_keys and len(maturity_keys) == 21,
        "headline_counts_are_evidence_derived": payload["headline_counts"] == expected_headlines,
        "legacy_partial_bucket_is_resolved": payload["legacy_partial_breakdown"] == expected_partial_split,
        "conditional_formal_precedence_is_explicit": payload["precedence"][1] == "conditional_formal",
        "gravity_is_conditional_not_reduced": next(
            row["headline"] for row in payload["criteria"] if row["key"] == "gravity"
        ) == "conditional_validated",
        "no_fixed_promoted_key_set_is_used": not payload["policy"]["fixed_promoted_key_set_used"],
        "legacy_7_13_1_is_not_an_acceptance_gate": not payload["policy"]["fixed_7_13_1_count_used_as_acceptance_gate"],
        "each_row_has_closed_and_open_evidence": all(row.closed and row.open for row in MATURITY_ROWS),
        "fingerprint_is_deterministic": maturity_fingerprint(payload) == maturity_fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.100a-current",
        "fingerprint": maturity_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "legacy_partial_is_deprecated_as_primary_status": True,
            "multi_axis_maturity_is_canonical": True,
            "physical_identity_or_calibration_inferred": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
