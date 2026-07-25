"""M9.97 current authority for gauge-spinor and full-PDE dynamics evidence."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .current_evidence_authority import run_current_evidence_authority
from .formalization_dynamics_extension import run_dynamics_formal_extension_study
from .gauge_spinor_stationary_current import (
    run_gauge_spinor_stationary_feasibility,
)
from .spinorial_pair_dynamics_authoritative import run_spinorial_pair_dynamics


def dynamics_authority_fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_dynamics_evidence_authority() -> dict[str, Any]:
    previous = run_current_evidence_authority()
    formal = run_dynamics_formal_extension_study()
    stationary = run_gauge_spinor_stationary_feasibility()
    dynamics = run_spinorial_pair_dynamics()
    payload = {
        "schema": "openwave.m9.dynamics-evidence-authority.v1",
        "task": "M9.97-authority",
        "previous_authority_fingerprint": previous["fingerprint"],
        "formal": {
            "passed": formal["passed"],
            "dynamics_extension_fingerprint": formal[
                "dynamics_extension_fingerprint"
            ],
            "source_count": formal["source_count"],
            "full_covariant_tbmt_imported": formal["decision"][
                "full_covariant_tbmt_dynamics_imported"
            ],
        },
        "stationary": {
            "passed": stationary["passed"],
            "schema": stationary["schema"],
            "final_residual": stationary["checkpoints"][-1][
                "relative_stationary_residual"
            ],
            "spin_drift": stationary["spin_drift"],
            "winding": stationary["checkpoints"][-1]["integer_winding"],
            "charged_spinor_stationary_branch_constructed": stationary["decision"][
                "charged_spinor_stationary_branch_constructed"
            ],
        },
        "dynamics": {
            "passed": dynamics["passed"],
            "schema": dynamics["schema"],
            "four_spinor_sources_drive_initial_fields": dynamics["decision"][
                "four_spinor_sources_drive_all_initial_fields"
            ],
            "momentum_lorentz_error": dynamics["relative_errors"][
                "momentum_vs_lorentz"
            ],
            "center_lorentz_error": dynamics["relative_errors"][
                "center_acceleration_vs_lorentz"
            ],
            "spin_generator_error": dynamics["relative_errors"][
                "finite_spin_vs_generator"
            ],
            "spin_bmt_error": dynamics["relative_errors"][
                "finite_spin_vs_rest_frame_bmt"
            ],
            "momentum_transfer_closed": dynamics["decision"][
                "momentum_transfer_matches_field_lorentz_force"
            ],
            "center_acceleration_closed": dynamics["decision"][
                "center_acceleration_closed"
            ],
            "center_response_has_lorentz_sign": dynamics["decision"][
                "center_response_has_lorentz_sign"
            ],
            "spin_generator_closed": dynamics["decision"][
                "spin_generator_integration_closed"
            ],
            "rest_frame_bmt_closed": dynamics["decision"][
                "rest_frame_bmt_torque_closed_on_winding_state"
            ],
        },
        "status": {
            "magnetic_moment_spin": "partial",
            "electric_force": "partial",
            "magnetic_force": "partial",
        },
    }
    acceptance = {
        "m9_96_authority_remains_valid": bool(previous["passed"]),
        "dynamics_formal_overlay_passes": bool(formal["passed"]),
        "gauge_spinor_stationary_campaign_passes_as_an_audit": bool(
            stationary["passed"]
        ),
        "charged_spinor_stationary_failure_is_explicit": not stationary["decision"]
        ["charged_spinor_stationary_branch_constructed"],
        "full_pair_dynamics_campaign_passes": bool(dynamics["passed"]),
        "four_spinor_sources_drive_initial_fields": dynamics["decision"][
            "four_spinor_sources_drive_all_initial_fields"
        ],
        "momentum_response_is_closed": dynamics["decision"][
            "momentum_transfer_matches_field_lorentz_force"
        ],
        "center_wrong_sign_and_rest_frame_spin_failures_are_explicit": (
            not dynamics["decision"]["center_acceleration_closed"]
            and not dynamics["decision"]["center_response_has_lorentz_sign"]
            and not dynamics["decision"][
                "rest_frame_bmt_torque_closed_on_winding_state"
            ]
        ),
        "finite_time_spin_matches_the_full_generator": dynamics["decision"][
            "spin_generator_integration_closed"
        ],
        "three_partial_statuses_are_preserved": set(payload["status"].values())
        == {"partial"},
        "no_physical_identity_or_calibration_is_inferred": True,
    }
    fingerprint = dynamics_authority_fingerprint(payload)
    return {
        **payload,
        "fingerprint": fingerprint,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "dynamics_evidence_authority_complete": True,
            "momentum_force_bridge_strengthened": True,
            "center_response_wrong_sign_blocks_electric_force_promotion": True,
            "rest_frame_bmt_mismatch_blocks_magnetic_promotion": True,
            "charged_stationary_failure_blocks_particle_identity": True,
            "criterion_rows_promoted": [],
            "physical_identity_established": False,
        },
    }


def evaluate_dynamics_identity(
    model: Any,
    state: Any,
    evidence: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    authority = run_dynamics_evidence_authority()
    observables = model.measure(state)
    supplied = dict(evidence or {})
    external = (
        "charge_unit_calibrated",
        "rest_energy_calibrated",
        "clock_identified",
        "spin_and_exchange_closed_on_same_branch",
        "physical_magnetic_moment_calibrated",
        "physical_force_calibrated",
        "out_of_sample_prediction",
    )
    gates = {
        "dynamics_evidence_authority_passes": bool(authority["passed"]),
        "state_is_normalized": observables["normalization_error"] <= 2.0e-10,
        "state_is_localized": observables["boundary_fraction"] <= 2.0e-2,
        "state_sector_matches_model": (
            state.declared_winding_sector == model.spec.winding_sector
        ),
        "winding_sector_is_embedded": bool(state.winding_embedded),
        "charged_spinor_stationary_branch_is_closed": authority["stationary"][
            "charged_spinor_stationary_branch_constructed"
        ],
        "momentum_force_response_is_closed": authority["dynamics"][
            "momentum_transfer_closed"
        ],
        "center_acceleration_is_closed": authority["dynamics"][
            "center_acceleration_closed"
        ],
        "rest_frame_spin_torque_is_closed": authority["dynamics"][
            "rest_frame_bmt_closed"
        ],
        "physical_name_is_requested": model.spec.physical_assignment is not None,
        "calibration_record_is_present": model.spec.calibration_id is not None,
        **{name: bool(supplied.get(name, False)) for name in external},
    }
    passed = all(gates.values())
    return {
        "schema": "openwave.m9.dynamics-identity-certificate.v1",
        "particle_id": model.spec.particle_id,
        "requested_assignment": model.spec.physical_assignment,
        "authority_fingerprint": authority["fingerprint"],
        "gates": gates,
        "passed": passed,
        "decision": {
            "physical_identity_established": passed,
            "stationary_center_and_spin_gates_block_identity": not passed,
            "historical_or_m9_96_authority_alone_is_not_sufficient": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
