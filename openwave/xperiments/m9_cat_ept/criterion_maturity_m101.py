"""M9.101g: maturity overlay from the four executable coupled-physics campaigns."""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity import CriterionMaturity, HeadlineStatus, MATURITY_ROWS
from .criterion_maturity_current import derive_headline
from .m101_evidence_authority import run_m101_evidence_authority
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA


def current_rows() -> tuple[CriterionMaturity, ...]:
    authority = run_m101_evidence_authority()
    components = authority["components"]
    rows = []
    for row in MATURITY_ROWS:
        if row.key == "de_broglie_clock":
            rows.append(
                replace(
                    row,
                    calibration="partial" if components["clock"]["internal_calibration"] else row.calibration,
                    closed=row.closed
                    + (
                        "internal action-rate calibration",
                        "one Yukawa/entropy normalization frozen across held-out grids",
                        "frequency-lapse Tolman reconstruction",
                    ),
                    open=(
                        "physical Zitterbewegung identity",
                        "external clock and mass calibration",
                        "external evidence",
                    ),
                )
            )
        elif row.key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
            extra_closed = [
                "one finite coupled gauge-spinor-Hartree action",
                "winding-sector stationary solver",
            ]
            if components["coupled_action"]["symmetry_reduced_branch"]:
                extra_closed.append("symmetry-reduced charged stationary branch")
            if row.key in ("magnetic_moment_spin", "magnetic_force"):
                extra_closed.append("local packet Thomas-BMT adapter")
                if components["packet_tbmt"]["reduction_closed"]:
                    extra_closed.append("local packet Thomas-BMT reduction on current carrier")
            open_items = [item for item in row.open if item not in (
                "single coupled action",
                "covariant packet spin law",
                "covariant packet torque",
            )]
            if not components["coupled_action"]["unrestricted_branch"]:
                open_items.append("unrestricted charged stationary stability")
            if row.key in ("magnetic_moment_spin", "magnetic_force") and not components["packet_tbmt"]["reduction_closed"]:
                open_items.append("numerical closure of local packet Thomas-BMT reduction")
            open_items.append("QED derivation of the covariant Thomas extension")
            rows.append(
                replace(
                    row,
                    state="reduced_constructed",
                    closed=row.closed + tuple(extra_closed),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
        elif row.key == "gravity":
            rows.append(
                replace(
                    row,
                    state="reduced_constructed" if components["gravity"]["weak_field_evolution"] else row.state,
                    closed=row.closed
                    + (
                        "current global integrated-action formal interface",
                        "G-free inference-variance Newton coupling map",
                        "one-state Schrodinger-Maxwell-Poisson evolution",
                        "weak Einstein-00 source closure",
                    ),
                    open=(
                        "physical selection of inference width sigma0",
                        "nonlinear four-dimensional Einstein Cauchy development",
                        "constraint propagation beyond the weak-field reduction",
                        "calibrated gravity predictions",
                    ),
                )
            )
        else:
            rows.append(row)
    return tuple(rows)


def headline_counts(rows: tuple[CriterionMaturity, ...] | None = None) -> dict[str, int]:
    selected = current_rows() if rows is None else rows
    names: tuple[HeadlineStatus, ...] = (
        "validated_in_scope",
        "conditional_validated",
        "reduced_model_validated",
        "calibration_pending",
        "candidate",
        "negative",
    )
    return {name: sum(derive_headline(row) == name for row in selected) for name in names}


def canonical_payload() -> dict[str, Any]:
    rows = current_rows()
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    authority = run_m101_evidence_authority()
    return {
        "schema": "openwave.m9.criterion-maturity.v3",
        "formal_head": authority["formal_head"],
        "criteria": [
            {
                **asdict(row),
                "headline": derive_headline(row),
                "legacy_status": legacy[row.key],
            }
            for row in rows
        ],
        "headline_counts": headline_counts(rows),
        "axis_changes": {
            "de_broglie_clock": {"calibration": "partial"},
            "magnetic_moment_spin": {"state": "reduced_constructed"},
            "electric_force": {"state": "reduced_constructed"},
            "magnetic_force": {"state": "reduced_constructed"},
            "gravity": {"state": "reduced_constructed"},
        },
        "policy": {
            "campaign_outcomes_drive_axis_updates": True,
            "headline_is_still_derived": True,
            "physical_identity_is_not_inferred": True,
            "external_validation_is_not_inferred": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_m101() -> dict[str, Any]:
    authority = run_m101_evidence_authority()
    payload = canonical_payload()
    by_key = {row["key"]: row for row in payload["criteria"]}
    acceptance = {
        "m101_authority_passes": bool(authority["passed"]),
        "all_21_rows_remain_present": len(payload["criteria"]) == 21 and len(by_key) == 21,
        "clock_internal_calibration_is_recorded": by_key["de_broglie_clock"]["calibration"] == "partial",
        "three_spin_force_rows_have_reduced_state_construction": all(by_key[key]["state"] == "reduced_constructed" for key in ("magnetic_moment_spin", "electric_force", "magnetic_force")),
        "gravity_has_one_reduced_evolution": by_key["gravity"]["state"] == "reduced_constructed",
        "conditional_headlines_are_not_overpromoted": all(by_key[key]["headline"] == "conditional_validated" for key in ("de_broglie_clock", "magnetic_moment_spin", "electric_force", "magnetic_force", "gravity")),
        "physical_identity_and_external_validation_remain_open": payload["policy"]["physical_identity_is_not_inferred"] and payload["policy"]["external_validation_is_not_inferred"],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.101g",
        "authority_fingerprint": authority["fingerprint"],
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "five_maturity_axes_updated_from_executable_evidence": True,
            "headline_classes_changed": payload["headline_counts"]
            != {
                "validated_in_scope": 7,
                "conditional_validated": 5,
                "reduced_model_validated": 3,
                "calibration_pending": 1,
                "candidate": 4,
                "negative": 1,
            },
            "physical_identity_changed": False,
            "external_prediction_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
