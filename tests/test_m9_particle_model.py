import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept import particle_model
from openwave.xperiments.m9_cat_ept.particle_model import (
    CatEptParticleModel,
    CatEptParticleState,
    field_fingerprint,
    field_mass,
    free_subflow,
    local_subflow,
    normalized_gaussian,
    run_particle_kernel_study,
)


def control_state(model: CatEptParticleModel) -> CatEptParticleState:
    field, spacing = normalized_gaussian()
    return CatEptParticleState(
        field=field,
        spacing=spacing,
        simulation_time=0.0,
        center=(0.0, 0.0, 0.0),
        phase_origin=0.0,
        declared_winding_sector=model.spec.winding_sector,
        winding_embedded=model.spec.winding_sector == 0,
        reference_branch_fingerprint=field_fingerprint(field, spacing),
        construction="test-control",
    )


def test_default_particle_is_unassigned_and_assumptions_are_explicit():
    model = CatEptParticleModel.repository_default()
    assert model.spec.physical_assignment is None
    assert model.spec.calibration_id is None
    assert model.spec.action.assumptions
    assert len(model.spec.formal_contract_fingerprint) == 64


def test_exact_subflows_preserve_mass_and_reverse():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    time = 0.017
    free = free_subflow(
        state.field,
        time,
        state.spacing,
        model.spec.action.dispersion,
    )
    free_back = free_subflow(
        free,
        -time,
        state.spacing,
        model.spec.action.dispersion,
    )
    local = local_subflow(
        state.field,
        time,
        model.spec.action.alpha,
        model.spec.action.beta,
    )
    local_back = local_subflow(
        local,
        -time,
        model.spec.action.alpha,
        model.spec.action.beta,
    )
    assert np.linalg.norm(free_back - state.field) / np.linalg.norm(state.field) < 2e-14
    assert np.linalg.norm(local_back - state.field) / np.linalg.norm(state.field) < 2e-14
    assert abs(field_mass(free, state.spacing) - field_mass(state.field, state.spacing)) < 2e-14
    assert abs(field_mass(local, state.spacing) - field_mass(state.field, state.spacing)) < 2e-14


def test_phase_chirp_translation_and_split_flow_are_replay_identifiable():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    chirped = model.apply_phase_chirp(state, 0.03, axis=1)
    translated = model.translate_cells(chirped, (1, -2, 0))
    evolved = model.evolve(translated, duration=0.006, time_step=0.002)
    assert evolved.simulation_time == pytest.approx(0.006)
    assert evolved.center == pytest.approx((state.spacing, -2 * state.spacing, 0.0))
    assert len(evolved.state_fingerprint) == 64
    assert evolved.state_fingerprint != state.state_fingerprint
    assert abs(field_mass(evolved.field, evolved.spacing) - 1.0) < 2e-12


def test_stationary_constructor_wraps_existing_solver(monkeypatch):
    model = CatEptParticleModel.repository_default()
    field, spacing = normalized_gaussian()

    def fake_solver(points, seed, config):
        assert points == 20
        assert seed == "super_gaussian"
        return field, (None, None, None, None, None, np.asarray(spacing))

    monkeypatch.setattr(particle_model, "solve_stationary", fake_solver)
    state = model.construct_stationary_state(points=20)
    assert state.construction == "stationary-non-gaussian-branch"
    assert state.winding_embedded
    assert state.declared_winding_sector == 0
    assert len(state.reference_branch_fingerprint) == 64


def test_nonzero_winding_is_declared_but_not_claimed_as_embedded():
    model = CatEptParticleModel.repository_default(winding_sector=1)
    state = control_state(model)
    assert state.declared_winding_sector == 1
    assert not state.winding_embedded
    certificate = model.evaluate_identity(state)
    assert not certificate["passed"]
    assert not certificate["gates"]["winding_sector_is_embedded"]


def test_physical_identity_promotion_is_fail_closed():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    with pytest.raises(ValueError, match="physical identity gate failed"):
        model.promote_identity(
            state,
            physical_assignment="electron",
            calibration_id="calibration-test",
            evidence={},
        )


def test_particle_kernel_study_passes_without_particle_overclaim():
    result = run_particle_kernel_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["reusable_particle_kernel_available"]
    assert not result["decision"]["localized_branch_is_a_physical_particle"]
    assert not result["decision"]["physical_calibration_complete"]
