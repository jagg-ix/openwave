"""Current M9 conformance overlay through M9.96.

Only the three force-related partial rows are replaced. Criterion identities,
domains, statuses, and the seven validated rows remain exactly those of the
canonical M9.95 profile.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
import json
from typing import Any

from .current_evidence_authority import run_current_evidence_authority
from .model_conformance import CRITERIA as BASE_CRITERIA
from .model_conformance import Criterion, PROMOTED_KEYS, validate_profile

ROOT = "openwave/xperiments/m9_cat_ept/"
FINDINGS = ROOT + "research/findings/"
FORMAL_STATUS = ROOT + "research/formal_status_matrix.md"

ROW_REPLACEMENTS = {
    "magnetic_moment_spin": {
        "evidence": (
            ROOT + "canonical_spin_magnetic_bridge.py",
            ROOT + "charged_branch_feasibility.py",
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v2.py",
            FINDINGS + "m9_94_method_note.md",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "A field-measured winding-three candidate now supplies one charge density, "
            "convective/Pauli current, magnetic moment, periodic Maxwell self-fields, and "
            "an independent weak-uniform-field energy-response moment. The current and "
            "response moments agree at discrete precision, and the gauge-invariant Pauli--"
            "Maxwell formal link is imported. The selected scalar action produces no passing "
            "stable charged stationary branch, the anomalous moment is not derived, and "
            "physical electron identity/calibration remain open."
        ),
    },
    "electric_force": {
        "evidence": (
            ROOT + "charged_branch_feasibility.py",
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v2.py",
            FINDINGS + "m9_95_method_note.md",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "Opposite field-derived winding candidates source periodic electric fields and "
            "close projected Gauss law. The electric contribution is nonzero, and the full "
            "Lorentz force agrees with the interaction-energy derivative and cross Maxwell-"
            "stress flux within the preregistered finite-grid tolerances. No stable charged "
            "stationary pair or full-coupled-PDE center acceleration is constructed, and "
            "charge/force units remain uncalibrated."
        ),
    },
    "magnetic_force": {
        "evidence": (
            ROOT + "charged_branch_feasibility.py",
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "formalization_force_extension.py",
            ROOT + "current_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v2.py",
            FINDINGS + "m9_94_method_note.md",
            FINDINGS + "m9_95_method_note.md",
            FINDINGS + "m9_96_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "The same winding candidate supplies a nonzero Pauli magnetization current, "
            "periodic magnetic field, static Ampere closure, and a nonzero magnetic "
            "contribution to the Lorentz/energy/stress force triangle. The gauge-invariant "
            "Pauli interaction is formally linked. A stable charged spinorial pair, full-PDE "
            "torque/precession/center acceleration, anomalous-moment derivation, and physical "
            "moment/force calibration remain open."
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


def fingerprint() -> str:
    return sha256(
        json.dumps(canonical_payload(), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    by_key = {item["key"]: item for item in payload["criteria"]}
    authority = run_current_evidence_authority()
    expected_counts = {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    acceptance = {
        "base_21_row_identity_is_preserved": (
            [item.key for item in current_criteria()]
            == [item.key for item in BASE_CRITERIA]
        ),
        "domain_partition_closes": payload["audit"]["domain_counts"]
        == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "m9_96_status_counts_are_unchanged": payload["audit"]["status_counts"]
        == expected_counts,
        "exactly_the_existing_seven_rows_are_validated": {
            item["key"] for item in payload["criteria"] if item["status"] == "validated"
        }
        == PROMOTED_KEYS,
        "current_evidence_authority_passes": bool(authority["passed"]),
        "exactly_three_rows_are_replaced": set(ROW_REPLACEMENTS)
        == {"magnetic_moment_spin", "electric_force", "magnetic_force"},
        "three_rows_remain_partial": all(
            by_key[key]["status"] == "partial" for key in ROW_REPLACEMENTS
        ),
        "spin_row_records_response_and_stationary_blocker": (
            "response moments agree" in by_key["magnetic_moment_spin"]["finding"]
            and "no passing stable charged stationary branch"
            in by_key["magnetic_moment_spin"]["finding"]
        ),
        "electric_row_records_force_triangle_and_acceleration_boundary": (
            "Maxwell-stress flux" in by_key["electric_force"]["finding"]
            and "center acceleration" in by_key["electric_force"]["finding"]
        ),
        "magnetic_row_records_ampere_and_torque_boundary": (
            "static Ampere closure" in by_key["magnetic_force"]["finding"]
            and "torque/precession" in by_key["magnetic_force"]["finding"]
        ),
        "fingerprint_is_deterministic": fingerprint() == fingerprint(),
    }
    return {
        **payload,
        "fingerprint": fingerprint(),
        "authority_fingerprint": authority["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "repository_profile": "MODELS_M9.md",
        "decision": {
            "m9_96_evidence_overlay_applied": True,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
