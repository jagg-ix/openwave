"""M9.97 calibration ledger for the three dynamics-related partial rows."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping

from .dynamics_evidence_authority import run_dynamics_evidence_authority

GateStatus = Literal[
    "dimensionless_closed",
    "structural_closed",
    "calibration_required",
    "blocked_by_model",
]


@dataclass(frozen=True)
class DynamicsPartialGate:
    criterion: str
    status: GateStatus
    closed_now: tuple[str, ...]
    blocking_obligations: tuple[str, ...]
    preregistered_promotion_rule: str
    preregistered_failure_rule: str


ROWS = (
    DynamicsPartialGate(
        criterion="magnetic_moment_spin",
        status="blocked_by_model",
        closed_now=(
            "the winding candidate supplies a field-derived Pauli current and response moment",
            "finite-time four-spinor precession agrees with the full Dirac generator",
            "rest-frame Dirac-Pauli and T-BMT equivalence witnesses are imported",
        ),
        blocking_obligations=(
            "construct a stable self-consistent charged spinorial stationary branch",
            "derive the appropriate covariant Thomas-BMT reduction for the moving winding packet",
            "derive or independently calibrate the anomalous moment and physical particle identity",
        ),
        preregistered_promotion_rule=(
            "promote only when one stable winding-carrying spinor closes current and response moments, "
            "full-generator precession, the appropriate covariant spin law, exchange, and a withheld g-factor gate"
        ),
        preregistered_failure_rule=(
            "reject the magnetic identity if the refined full-generator spin trajectory does not approach "
            "one independently derived covariant precession law on the same stable branch"
        ),
    ),
    DynamicsPartialGate(
        criterion="electric_force",
        status="blocked_by_model",
        closed_now=(
            "opposite winding candidates source self-consistent periodic electric fields",
            "kinetic-momentum transfer in the Maxwell-Dirac evolution agrees with the Lorentz force",
            "the earlier Lorentz, interaction-energy, and Maxwell-stress force triangle remains closed",
        ),
        blocking_obligations=(
            "construct a stable charged spinorial stationary pair",
            "make center-of-energy acceleration converge to momentum transfer and field force",
            "calibrate charge, length, time, mass, and force units over withheld separations",
        ),
        preregistered_promotion_rule=(
            "promote only when momentum transfer, center acceleration, interaction-energy derivative, "
            "and stress flux converge for stable charged states on refined grids and withheld separations"
        ),
        preregistered_failure_rule=(
            "reject Coulomb-force identification if center acceleration and kinetic-momentum transfer "
            "do not approach the same Lorentz/stress/energy limit"
        ),
    ),
    DynamicsPartialGate(
        criterion="magnetic_force",
        status="blocked_by_model",
        closed_now=(
            "the same pair carries magnetization current and a nonzero magnetic Lorentz-force contribution",
            "finite-time spin evolution agrees with the exact Dirac generator used by the PDE",
            "rest-frame Pauli torque and T-BMT equivalence are formally available with explicit boost boundaries",
        ),
        blocking_obligations=(
            "construct a stable charged spinorial stationary pair",
            "derive and validate the moving-packet covariant spin and torque law",
            "calibrate magnetic moment and force units with the same electric-sector map",
        ),
        preregistered_promotion_rule=(
            "promote only when magnetic momentum transfer, torque, and spin precession arise from the same "
            "stable self-consistent fields and agree with an independently derived covariant dynamics law"
        ),
        preregistered_failure_rule=(
            "reject the magnetic-force identity if the refined PDE spin/torque response cannot be reconciled "
            "with its own current, field, stress, and covariant precession carriers"
        ),
    ),
)


def ledger_fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_physical_calibration_ledger_v3() -> dict[str, Any]:
    authority = run_dynamics_evidence_authority()
    payload = {
        "schema": "openwave.m9.physical-calibration-ledger.v3",
        "task": "M9.97-ledger",
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
        "dynamics_evidence_authority_passes": bool(authority["passed"]),
        "exact_three_partial_rows_are_governed": (
            {row.criterion for row in ROWS}
            == {"magnetic_moment_spin", "electric_force", "magnetic_force"}
        ),
        "every_row_has_promotion_and_failure_rules": all(
            row.preregistered_promotion_rule and row.preregistered_failure_rule
            for row in ROWS
        ),
        "all_three_rows_remain_blocked_by_model_reductions": all(
            row.status == "blocked_by_model" for row in ROWS
        ),
        "momentum_and_generator_closures_are_not_mislabeled_as_physical_promotion": (
            authority["dynamics"]["momentum_transfer_closed"]
            and authority["dynamics"]["spin_generator_closed"]
            and set(authority["status"].values()) == {"partial"}
        ),
        "stationary_center_and_bmt_failures_are_explicit": (
            not authority["stationary"]["charged_spinor_stationary_branch_constructed"]
            and not authority["dynamics"]["center_acceleration_closed"]
            and not authority["dynamics"]["rest_frame_bmt_closed"]
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
            "shared_blocker": (
                "stable charged spinorial branch with converged center and covariant spin dynamics"
            ),
            "out_of_sample_physical_prediction_ready": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
