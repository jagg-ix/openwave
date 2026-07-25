"""Current M9 conformance overlay through M9.97.

Only the magnetic-moment, electric-force, and magnetic-force findings are
updated from the M9.96 profile. Criterion identities, domains, statuses, and
the seven validated rows remain unchanged.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from hashlib import sha256
import json
from typing import Any

from .dynamics_evidence_authority import run_dynamics_evidence_authority
from .model_conformance import Criterion, PROMOTED_KEYS, validate_profile
from .model_conformance_current import CRITERIA as M9_96_CRITERIA

ROOT = "openwave/xperiments/m9_cat_ept/"
FINDINGS = ROOT + "research/findings/"
FORMAL_STATUS = ROOT + "research/formal_status_matrix.md"

ROW_REPLACEMENTS = {
    "magnetic_moment_spin": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "gauge_spinor_stationary_current.py",
            ROOT + "spinorial_pair_dynamics_authoritative.py",
            ROOT + "formalization_dynamics_extension.py",
            ROOT + "dynamics_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v3.py",
            FINDINGS + "m9_96_method_note.md",
            FINDINGS + "m9_97_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "A field-measured winding-three candidate supplies charge/current, magnetic moment, "
            "periodic self-fields, and a weak-field response moment. M9.97 embeds the same class "
            "of source in a source-consistent four-spinor Maxwell--Dirac evolution: finite-time "
            "spin precession agrees with the exact full Dirac generator within 2.57%. The selected "
            "self-consistent gauge-spinor stationary equation still has residual 0.519, and the "
            "moving winding packet does not reduce to the imported rest-frame Pauli/T-BMT torque. "
            "The anomalous moment, covariant spin law, physical identity, and calibration remain open."
        ),
    },
    "electric_force": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "gauge_spinor_stationary_current.py",
            ROOT + "spinorial_pair_dynamics_authoritative.py",
            ROOT + "formalization_dynamics_extension.py",
            ROOT + "dynamics_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v3.py",
            FINDINGS + "m9_96_method_note.md",
            FINDINGS + "m9_97_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "Opposite field-derived winding candidates source periodic electric fields and close "
            "the M9.96 Lorentz/energy/Maxwell-stress force triangle. In the source-consistent "
            "four-spinor Maxwell--Dirac evolution, interaction-induced kinetic-momentum transfer "
            "agrees with the external Lorentz force within 2.61%. The independently fitted center "
            "response has the wrong sign and a 114.74% mismatch. No stable charged spinorial "
            "stationary pair or physical unit calibration exists."
        ),
    },
    "magnetic_force": {
        "evidence": (
            ROOT + "charged_maxwell_source_bridge.py",
            ROOT + "field_force_triangle.py",
            ROOT + "gauge_spinor_stationary_current.py",
            ROOT + "spinorial_pair_dynamics_authoritative.py",
            ROOT + "formalization_dynamics_extension.py",
            ROOT + "dynamics_evidence_authority.py",
            ROOT + "physical_calibration_ledger_v3.py",
            FINDINGS + "m9_96_method_note.md",
            FINDINGS + "m9_97_method_note.md",
            FORMAL_STATUS,
        ),
        "finding": (
            "The same winding sources carry Pauli magnetization currents, periodic magnetic fields, "
            "and a nonzero magnetic Lorentz-force contribution. The source-consistent four-spinor "
            "evolution integrates its instantaneous Dirac spin generator within 2.57%. PhysLib "
            "supplies the rest-frame Dirac--Pauli precession and rest-frame T-BMT equality, but the "
            "moving winding packet differs by 266.90% and opposite transverse sign. A stable "
            "spinorial pair, covariant Thomas/BMT reduction, torque calibration, and common physical "
            "moment/force unit map remain open."
        ),
    },
}


def current_criteria() -> tuple[Criterion, ...]:
    rows = []
    for item in M9_96_CRITERIA:
        replacement = ROW_REPLACEMENTS.get(item.key)
        rows.append(item if replacement is None else replace(item, **replacement))
    return tuple(rows)


CRITERIA = current_criteria()


def canonical_payload() -> dict[str, Any]:
    criteria = current_criteria()
    return {
        "schema": "openwave.m9.models-conformance.v15",
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
    authority = run_dynamics_evidence_authority()
    expected_counts = {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    acceptance = {
        "m9_96_21_row_identity_is_preserved": (
            [item.key for item in current_criteria()]
            == [item.key for item in M9_96_CRITERIA]
        ),
        "domain_partition_closes": payload["audit"]["domain_counts"]
        == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "m9_97_status_counts_are_unchanged": payload["audit"]["status_counts"]
        == expected_counts,
        "exactly_the_existing_seven_rows_are_validated": {
            item["key"] for item in payload["criteria"] if item["status"] == "validated"
        }
        == PROMOTED_KEYS,
        "dynamics_evidence_authority_passes": bool(authority["passed"]),
        "exactly_three_rows_are_replaced": set(ROW_REPLACEMENTS)
        == {"magnetic_moment_spin", "electric_force", "magnetic_force"},
        "three_rows_remain_partial": all(
            by_key[key]["status"] == "partial" for key in ROW_REPLACEMENTS
        ),
        "spin_row_records_generator_closure_and_bmt_boundary": (
            "full Dirac generator within 2.57%"
            in by_key["magnetic_moment_spin"]["finding"]
            and "rest-frame Pauli/T-BMT" in by_key["magnetic_moment_spin"]["finding"]
        ),
        "electric_row_records_momentum_closure_and_wrong_sign_center": (
            "kinetic-momentum transfer" in by_key["electric_force"]["finding"]
            and "wrong sign" in by_key["electric_force"]["finding"]
        ),
        "magnetic_row_records_generator_and_covariant_boundary": (
            "instantaneous Dirac spin generator" in by_key["magnetic_force"]["finding"]
            and "covariant Thomas/BMT" in by_key["magnetic_force"]["finding"]
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
            "m9_97_dynamics_overlay_applied": True,
            "momentum_and_generator_subreductions_closed": True,
            "stationary_center_and_bmt_reductions_open": True,
            "center_response_has_wrong_sign": True,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
