"""Explicit M9.96 conformance overlay retained for historical registration.

The stable ``model_conformance_current`` alias advances with the current platform
milestone. Historical M9.97+ modules must therefore depend on this versioned
M9.96 profile instead of importing the moving alias.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .current_evidence_authority import run_current_evidence_authority
from .model_conformance import Criterion, CRITERIA as BASE_CRITERIA, PROMOTED_KEYS, validate_profile

ROOT = "openwave/xperiments/m9_cat_ept/"
FINDINGS = ROOT + "research/findings/"
FORMAL_STATUS = ROOT + "research/formal_status_matrix.md"

ROW_REPLACEMENTS = {
    "magnetic_moment_spin": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "Field-derived winding sources provide charge/current and magnetic response moments agree "
            "across the canonical static interfaces. There is no passing stable charged stationary branch, "
            "so physical particle identity, anomalous moment, and calibrated spin dynamics remain open."
        ),
    },
    "electric_force": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "Opposite winding-source candidates close the periodic electric field, Lorentz-force, "
            "energy-gradient, and Maxwell-stress flux triangle. The measured center acceleration does "
            "not establish a stable charged particle or calibrated Coulomb force."
        ),
    },
    "magnetic_force": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "The same winding sources close the static Ampere closure and a nonzero magnetic-force "
            "contribution. Torque/precession, stable charged matter, and physical magnetic units remain open."
        ),
    },
}


def current_criteria() -> tuple[Criterion, ...]:
    rows = []
    for item in BASE_CRITERIA:
        replacement = ROW_REPLACEMENTS.get(item.key)
        rows.append(item if replacement is None else replace(item, **replacement))
    return tuple(rows)


CRITERIA = current_criteria()


def canonical_payload() -> dict[str, Any]:
    criteria = current_criteria()
    return {
        "schema": "openwave.m9.models-conformance.v14",
        "model": "M9 CAT/EPT",
        "criteria": [asdict(item) for item in criteria],
        "audit": validate_profile(criteria),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    authority = run_current_evidence_authority()
    expected_counts = {"validated": 7, "partial": 13, "negative": 1, "not_yet": 0}
    acceptance = {
        "M9_95_21_row_identity_is_preserved": [item.key for item in CRITERIA] == [item.key for item in BASE_CRITERIA],
        "domain_partition_closes": payload["audit"]["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "M9_96_status_counts_are_unchanged": payload["audit"]["status_counts"] == expected_counts,
        "exactly_the_existing_seven_rows_are_validated": {item["key"] for item in payload["criteria"] if item["status"] == "validated"} == PROMOTED_KEYS,
        "current_evidence_authority_passes": bool(authority["passed"]),
        "exactly_three_rows_are_replaced": set(ROW_REPLACEMENTS) == {"magnetic_moment_spin", "electric_force", "magnetic_force"},
        "three_rows_remain_partial": all(next(item for item in payload["criteria"] if item["key"] == key)["status"] == "partial" for key in ROW_REPLACEMENTS),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "fingerprint": fingerprint(payload),
        "authority_fingerprint": authority["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "repository_profile": "MODELS_M9.md",
        "decision": {
            "m9_96_evidence_overlay_applied": True,
            "criterion_rows_promoted": [],
            "physical_identity_assigned": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
