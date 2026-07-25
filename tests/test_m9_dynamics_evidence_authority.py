from dataclasses import replace

from openwave.xperiments.m9_cat_ept.charged_maxwell_source_bridge import (
    source_candidate,
)
from openwave.xperiments.m9_cat_ept.dynamics_evidence_authority import (
    dynamics_authority_fingerprint,
    evaluate_dynamics_identity,
    run_dynamics_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.particle_model import (
    CatEptParticleModel,
    CatEptParticleState,
    field_fingerprint,
)


def test_dynamics_authority_records_closed_and_open_reductions_without_promotion():
    result = run_dynamics_evidence_authority()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["dynamics"]["four_spinor_sources_drive_initial_fields"]
    assert result["dynamics"]["momentum_transfer_closed"]
    assert result["dynamics"]["spin_generator_closed"]
    assert not result["dynamics"]["center_acceleration_closed"]
    assert not result["dynamics"]["center_response_has_lorentz_sign"]
    assert not result["dynamics"]["rest_frame_bmt_closed"]
    assert not result["stationary"]["charged_spinor_stationary_branch_constructed"]
    assert result["status"] == {
        "magnetic_moment_spin": "partial",
        "electric_force": "partial",
        "magnetic_force": "partial",
    }
    assert result["decision"]["criterion_rows_promoted"] == []
    assert not result["decision"]["physical_identity_established"]


def test_dynamics_authority_fingerprint_is_deterministic():
    result = run_dynamics_evidence_authority()
    payload = {
        key: value
        for key, value in result.items()
        if key not in {"fingerprint", "acceptance", "passed", "decision"}
    }
    assert len(result["fingerprint"]) == 64
    assert dynamics_authority_fingerprint(payload) == dynamics_authority_fingerprint(
        payload
    )


def test_identity_remains_blocked_even_when_external_flags_are_asserted():
    field, grid, _observables = source_candidate()
    spacing = float(grid[5])
    model = CatEptParticleModel.repository_default(winding_sector=3)
    state = CatEptParticleState(
        field=field,
        spacing=spacing,
        simulation_time=0.0,
        center=(0.0, 0.0, 0.0),
        phase_origin=0.0,
        declared_winding_sector=3,
        winding_embedded=True,
        reference_branch_fingerprint=field_fingerprint(field, spacing),
        construction="m9-97-identity-blocker-control",
    )
    candidate = CatEptParticleModel(
        replace(
            model.spec,
            physical_assignment="electron-candidate",
            calibration_id="external-control",
        )
    )
    flags = {
        "charge_unit_calibrated": True,
        "rest_energy_calibrated": True,
        "clock_identified": True,
        "spin_and_exchange_closed_on_same_branch": True,
        "physical_magnetic_moment_calibrated": True,
        "physical_force_calibrated": True,
        "out_of_sample_prediction": True,
    }
    certificate = evaluate_dynamics_identity(candidate, state, flags)
    assert not certificate["passed"]
    assert not certificate["gates"]["charged_spinor_stationary_branch_is_closed"]
    assert not certificate["gates"]["center_acceleration_is_closed"]
    assert not certificate["gates"]["rest_frame_spin_torque_is_closed"]
    assert not certificate["decision"]["physical_identity_established"]
