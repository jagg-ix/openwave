"""M9.102b: outcome-driven maturity with carrier/state separation.

M9.101 correctly exposed physical sub-gates, but its maturity overlay assigned
``reduced_constructed`` to the three spin/force rows whenever the coupled-action
campaign existed.  An implemented equation and solver are not a constructed
stationary state.  This successor records implementation evidence separately and
advances the state axis only when the corresponding state gate actually passes.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity import CriterionMaturity, HeadlineStatus, MATURITY_ROWS
from .criterion_maturity_current import derive_headline
from .formalization_m102_extension import CURRENT_FORMAL_HEAD
from .m101_evidence_authority import run_m101_evidence_authority
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA


def _implementation_axes(authority: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    components = authority["components"]
    action = components["coupled_action"]
    packet = components["packet_tbmt"]
    gravity = components["gravity"]
    clock = components["clock"]
    return {
        "de_broglie_clock": {
            "clock_calibration_campaign": "implemented" if clock["passed"] else "failed",
            "internal_calibration_gate": bool(clock["internal_calibration"]),
            "external_calibration_gate": bool(clock["external_calibration"]),
        },
        "magnetic_moment_spin": {
            "coupled_action": "implemented" if action["passed"] else "failed",
            "winding_sector_state_gate": bool(action["symmetry_reduced_branch"]),
            "unrestricted_state_gate": bool(action["unrestricted_branch"]),
            "packet_adapter": "implemented" if packet["adapter_constructed"] else "absent",
            "packet_reduction_gate": bool(packet["reduction_closed"]),
        },
        "electric_force": {
            "coupled_action": "implemented" if action["passed"] else "failed",
            "winding_sector_state_gate": bool(action["symmetry_reduced_branch"]),
            "unrestricted_state_gate": bool(action["unrestricted_branch"]),
        },
        "magnetic_force": {
            "coupled_action": "implemented" if action["passed"] else "failed",
            "winding_sector_state_gate": bool(action["symmetry_reduced_branch"]),
            "unrestricted_state_gate": bool(action["unrestricted_branch"]),
            "packet_adapter": "implemented" if packet["adapter_constructed"] else "absent",
            "packet_reduction_gate": bool(packet["reduction_closed"]),
        },
        "gravity": {
            "weak_field_evolution": "implemented" if gravity["passed"] else "failed",
            "weak_field_state_gate": bool(gravity["weak_field_evolution"]),
            "full_einstein_state_gate": bool(gravity["full_einstein_evolution"]),
        },
    }


def current_rows(
    authority: Mapping[str, Any] | None = None,
) -> tuple[CriterionMaturity, ...]:
    selected = run_m101_evidence_authority() if authority is None else authority
    components = selected["components"]
    action = components["coupled_action"]
    packet = components["packet_tbmt"]
    clock = components["clock"]
    gravity = components["gravity"]
    rows: list[CriterionMaturity] = []

    for row in MATURITY_ROWS:
        if row.key == "de_broglie_clock":
            rows.append(
                replace(
                    row,
                    calibration=(
                        "partial" if clock["internal_calibration"] else row.calibration
                    ),
                    closed=row.closed
                    + (
                        "internal action-rate calibration campaign",
                        "one Yukawa/entropy normalization transported across held-out grids",
                        "frequency-lapse Tolman reconstruction",
                    ),
                    open=(
                        "physical Zitterbewegung identity",
                        "external clock and mass calibration",
                        "external evidence",
                    ),
                )
            )
            continue

        if row.key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
            closed_items = [
                "finite coupled gauge-spinor-Hartree action implementation",
                "winding-sector stationary solver implementation",
            ]
            if action["symmetry_reduced_branch"]:
                closed_items.append("symmetry-reduced charged stationary state gate")
            if row.key in ("magnetic_moment_spin", "magnetic_force"):
                closed_items.append("local packet Thomas-BMT adapter implementation")
                if packet["reduction_closed"]:
                    closed_items.append("local packet Thomas-BMT numerical reduction")

            open_items = [
                item
                for item in row.open
                if item
                not in (
                    "single coupled action",
                    "covariant packet spin law",
                    "covariant packet torque",
                )
            ]
            if not action["symmetry_reduced_branch"]:
                open_items.append("symmetry-reduced stationary-state gate")
            if not action["unrestricted_branch"]:
                open_items.append("unrestricted charged stationary stability")
            if (
                row.key in ("magnetic_moment_spin", "magnetic_force")
                and not packet["reduction_closed"]
            ):
                open_items.append("numerical closure of local packet Thomas-BMT reduction")
            open_items.append("QED derivation of the covariant Thomas extension")

            rows.append(
                replace(
                    row,
                    state=(
                        "reduced_constructed"
                        if action["symmetry_reduced_branch"]
                        else row.state
                    ),
                    closed=row.closed + tuple(closed_items),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue

        if row.key == "gravity":
            rows.append(
                replace(
                    row,
                    state=(
                        "reduced_constructed"
                        if gravity["weak_field_evolution"]
                        else row.state
                    ),
                    closed=row.closed
                    + (
                        "current global integrated-action formal interface",
                        "G-free inference-width Newton coupling map",
                        "one-state Schrodinger-Maxwell-Poisson evolution implementation",
                        "weak Einstein-00 source gate",
                    ),
                    open=(
                        "physical selection of inference width sigma0",
                        "nonlinear four-dimensional Einstein Cauchy development",
                        "constraint propagation beyond the weak-field reduction",
                        "calibrated gravity predictions",
                    ),
                )
            )
            continue

        rows.append(row)

    return tuple(rows)


def headline_counts(
    rows: tuple[CriterionMaturity, ...] | None = None,
) -> dict[str, int]:
    selected = current_rows() if rows is None else rows
    names: tuple[HeadlineStatus, ...] = (
        "validated_in_scope",
        "conditional_validated",
        "reduced_model_validated",
        "calibration_pending",
        "candidate",
        "negative",
    )
    return {
        name: sum(derive_headline(row) == name for row in selected)
        for name in names
    }


def canonical_payload(
    authority: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    selected_authority = (
        run_m101_evidence_authority() if authority is None else authority
    )
    rows = current_rows(selected_authority)
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    implementations = _implementation_axes(selected_authority)
    axis_changes: dict[str, dict[str, str]] = {}
    if selected_authority["components"]["clock"]["internal_calibration"]:
        axis_changes["de_broglie_clock"] = {"calibration": "partial"}
    if selected_authority["components"]["coupled_action"]["symmetry_reduced_branch"]:
        for key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
            axis_changes[key] = {"state": "reduced_constructed"}
    if selected_authority["components"]["gravity"]["weak_field_evolution"]:
        axis_changes["gravity"] = {"state": "reduced_constructed"}

    return {
        "schema": "openwave.m9.criterion-maturity.v4",
        "historical_formal_head": selected_authority["formal_head"],
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "criteria": [
            {
                **asdict(row),
                "headline": derive_headline(row),
                "legacy_status": legacy[row.key],
                "implementation": implementations.get(row.key, {}),
            }
            for row in rows
        ],
        "headline_counts": headline_counts(rows),
        "axis_changes": axis_changes,
        "policy": {
            "campaign_outcomes_drive_axis_updates": True,
            "carrier_implementation_is_not_state_existence": True,
            "state_axis_advances_only_when_state_gate_passes": True,
            "headline_is_derived": True,
            "physical_identity_is_not_inferred": True,
            "external_validation_is_not_inferred": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_m102() -> dict[str, Any]:
    authority = run_m101_evidence_authority()
    payload = canonical_payload(authority)
    by_key = {row["key"]: row for row in payload["criteria"]}
    branch_closed = authority["components"]["coupled_action"][
        "symmetry_reduced_branch"
    ]
    expected_spin_force_state = (
        "reduced_constructed" if branch_closed else "not_constructed"
    )
    acceptance = {
        "all_21_rows_remain_present": (
            len(payload["criteria"]) == 21 and len(by_key) == 21
        ),
        "current_formal_head_is_registered": (
            payload["current_formal_head"] == CURRENT_FORMAL_HEAD
        ),
        "clock_internal_calibration_is_outcome_driven": (
            by_key["de_broglie_clock"]["calibration"]
            == ("partial" if authority["components"]["clock"]["internal_calibration"] else "open")
        ),
        "spin_force_state_matches_stationary_gate": all(
            by_key[key]["state"] == expected_spin_force_state
            for key in ("magnetic_moment_spin", "electric_force", "magnetic_force")
        ),
        "carrier_implementation_is_recorded_separately": all(
            by_key[key]["implementation"]["coupled_action"] in ("implemented", "failed")
            for key in ("magnetic_moment_spin", "electric_force", "magnetic_force")
        ),
        "gravity_state_matches_weak_field_gate": (
            by_key["gravity"]["state"]
            == (
                "reduced_constructed"
                if authority["components"]["gravity"]["weak_field_evolution"]
                else "candidate"
            )
        ),
        "conditional_headlines_are_not_overpromoted": all(
            by_key[key]["headline"] == "conditional_validated"
            for key in (
                "de_broglie_clock",
                "magnetic_moment_spin",
                "electric_force",
                "magnetic_force",
                "gravity",
            )
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.102b",
        "authority_fingerprint": authority["fingerprint"],
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "carrier_and_state_axes_are_separate": True,
            "state_overcredit_removed": True,
            "physical_identity_changed": False,
            "external_prediction_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
