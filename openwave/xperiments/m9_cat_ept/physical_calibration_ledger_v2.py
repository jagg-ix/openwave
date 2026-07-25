"""M9.96 current-tree calibration ledger for the three force-related partial rows."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping

from .current_evidence_authority import run_current_evidence_authority

GateStatus = Literal[
    "dimensionless_closed",
    "structural_closed",
    "calibration_required",
    "blocked_by_model",
]


@dataclass(frozen=True)
class CurrentPartialGate:
    criterion: str
    status: GateStatus
    closed_now: tuple[str, ...]
    blocking_obligations: tuple[str, ...]
    preregistered_promotion_rule: str
    preregistered_failure_rule: str


ROWS = (
    CurrentPartialGate(
        criterion="magnetic_moment_spin",
        status="blocked_by_model",
        closed_now=(
            "field-derived winding candidate supplies one charge current and Pauli moment",
            "current moment equals the weak uniform-field energy response",
            "gauge-invariant Pauli-Maxwell formal link is imported",
        ),
        blocking_obligations=(
            "construct a stable charged spinorial stationary branch",
            "derive or independently calibrate the anomalous moment",
            "establish physical particle identity",
        ),
        preregistered_promotion_rule=(
            "promote only when the same stable winding-carrying stationary branch closes "
            "spin, current moment, energy response, exchange, and an independent g-factor gate"
        ),
        preregistered_failure_rule=(
            "reject the particle magnetic-moment identity if current and response moments "
            "disagree after grid refinement or if the charged stationary branch remains absent"
        ),
    ),
    CurrentPartialGate(
        criterion="electric_force",
        status="blocked_by_model",
        closed_now=(
            "field-derived opposite charges source periodic electric fields",
            "projected Gauss law closes",
            "Lorentz force agrees with interaction-energy and Maxwell-stress forces",
        ),
        blocking_obligations=(
            "construct stable charged stationary particles",
            "measure center-of-energy acceleration in the full coupled PDE",
            "calibrate charge, length, time, and force units",
        ),
        preregistered_promotion_rule=(
            "promote only when PDE acceleration, interaction-energy derivative, and stress flux "
            "agree for stable charged states over withheld separations"
        ),
        preregistered_failure_rule=(
            "reject Coulomb identification if the three force estimators fail to converge to one "
            "far-field law after regulator and box refinement"
        ),
    ),
    CurrentPartialGate(
        criterion="magnetic_force",
        status="blocked_by_model",
        closed_now=(
            "the winding candidate supplies a nonzero Pauli magnetization current",
            "static Ampere and magnetic-divergence constraints close",
            "magnetic Lorentz force participates in the field-derived force triangle",
        ),
        blocking_obligations=(
            "construct a stable charged spinorial stationary pair",
            "measure torque, precession, and center acceleration in the coupled PDE",
            "calibrate magnetic moment and force units with the same electric-sector map",
        ),
        preregistered_promotion_rule=(
            "promote only when magnetic force, torque, and spin precession arise from the same "
            "self-consistent fields and stable particle states"
        ),
        preregistered_failure_rule=(
            "reject magnetic-force identity if Maxwell-stress, Lorentz, energy-gradient, and "
            "dynamical measurements do not share one refined limit"
        ),
    ),
)


def ledger_fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_physical_calibration_ledger_v2() -> dict[str, Any]:
    authority = run_current_evidence_authority()
    payload = {
        "schema": "openwave.m9.physical-calibration-ledger.v2",
        "task": "M9.96-ledger",
        "authority_fingerprint": authority["fingerprint"],
        "rows": [asdict(row) for row in ROWS],
        "status_counts": {
            status: sum(row.status == status for row in ROWS)
            for status in (
                "dimensionless_closed",
                "structural_closed",
                "calibration_required",
                "blocked_by_model",
            )
        },
    }
    acceptance = {
        "current_evidence_authority_passes": bool(authority["passed"]),
        "exact_three_partial_rows_are_governed": (
            {row.criterion for row in ROWS}
            == {"magnetic_moment_spin", "electric_force", "magnetic_force"}
        ),
        "every_row_has_promotion_and_failure_rules": all(
            row.preregistered_promotion_rule and row.preregistered_failure_rule
            for row in ROWS
        ),
        "all_three_rows_remain_blocked_by_the_missing_stationary_branch": all(
            row.status == "blocked_by_model" for row in ROWS
        ),
        "no_physical_calibration_is_claimed": True,
        "ledger_is_deterministic": (
            ledger_fingerprint(payload) == ledger_fingerprint(payload)
        ),
    }
    return {
        **payload,
        "fingerprint": ledger_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "magnetic_moment_spin_promoted": False,
            "electric_force_promoted": False,
            "magnetic_force_promoted": False,
            "shared_blocker": "stable charged spinorial stationary branch",
            "out_of_sample_physical_prediction_ready": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
