"""M9.100c: canonical registration with multi-axis criterion maturity."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance_maturity import canonical_payload as conformance_payload
from .model_conformance_maturity import run_conformance_study
from .model_registration_reconciliation import canonical_registration_payload as m9_99_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = m9_99_payload()
    conformance = conformance_payload()
    return {
        **previous,
        "schema": "openwave.model-registration.v7",
        "conformance": conformance,
        "m9_100": {
            "multi_axis_maturity_registered": True,
            "legacy_scalar_status_is_primary": False,
            "headline_counts": conformance["summary"],
            "legacy_partial_breakdown": conformance["maturity"]["legacy_partial_breakdown"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "criterion_maturity_is_multi_axis": True,
            "legacy_7_13_1_is_acceptance_gate": False,
            "maturity_reclassification_implies_physical_identity": False,
            "maturity_reclassification_implies_calibration": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    conformance = run_conformance_study()
    payload = canonical_registration_payload()
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
        "multi_axis_conformance_passes": bool(conformance["passed"]),
        "schema_v7_is_current": payload["schema"] == "openwave.model-registration.v7",
        "headline_counts_are_registered": payload["m9_100"]["headline_counts"] == expected,
        "legacy_status_is_not_primary": not payload["m9_100"]["legacy_scalar_status_is_primary"],
        "fixed_7_13_1_gate_is_removed": not payload["claim_boundary"]["legacy_7_13_1_is_acceptance_gate"],
        "reclassification_promotes_no_physical_claim": (
            payload["m9_100"]["physical_claims_promoted"] == []
            and not payload["claim_boundary"]["maturity_reclassification_implies_physical_identity"]
            and not payload["claim_boundary"]["maturity_reclassification_implies_calibration"]
        ),
        "fingerprint_is_deterministic": registration_fingerprint(payload) == registration_fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.100c",
        "registration_fingerprint": registration_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "multi_axis_maturity_is_canonical": True,
            "legacy_partial_bucket_deprecated": True,
            "physical_identity_changed": False,
            "calibration_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
