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
    periodic_displacement,
    run_particle_kernel_study,
    wrap_periodic_coordinate,
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
    free_error = np.linalg.norm(free_back - state.field) / np.linalg.norm(state.field)
    local_error = np.linalg.norm(local_back - state.field) / np.linalg.norm(state.field)
    initial_mass = field_mass(state.field, state.spacing)
    assert free_error < 2e-14
    assert local_error < 2e-14
    assert abs(field_mass(free, state.spacing) - initial_mass) < 2e-14
    assert abs(field_mass(local, state.spacing) - initial_mass) < 2e-14


def test_periodic_coordinate_helpers_use_minimum_image():
    coordinates = np.asarray([-3.0, -2.25, 0.0, 2.25])
    assert wrap_periodic_coordinate(3.75, 6.0) == pytest.approx(-2.25)
    displacement = periodic_displacement(coordinates, -2.25, 6.0)
    assert displacement == pytest.approx([-0.75, 0.0, 2.25, -1.5])


def test_periodic_translation_preserves_particle_observables():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    baseline = model.measure(state)
    translated = model.translate_cells(state, (5, -6, 3))
    observed = model.measure(translated)
    expected_center = (-3 * state.spacing, 2 * state.spacing, 3 * state.spacing)
    assert translated.center == pytest.approx(expected_center)
    for key in ("mass", "rms_radius", "boundary_fraction", "peak_density"):
        assert observed[key] == pytest.approx(baseline[key], abs=2e-14)


def test_periodic_translation_rejects_noninteger_offsets():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    with pytest.raises(ValueError, match="integer cell offsets"):
        model.translate_cells(state, (1, 0.5, 0))


def test_phase_chirp_translation_and_split_flow_are_replay_identifiable():
    model = CatEptParticleModel.repository_default()
    state = control_state(model)
    chirped = model.apply_phase_chirp(state, 0.03, axis=1)
    translated = model.translate_cells(chirped, (1, -2, 0))
    evolved = model.evolve(translated, duration=0.006, time_step=0.002)
    expected_center = (state.spacing, -2 * state.spacing, 0.0)
    assert evolved.simulation_time == pytest.approx(0.006)
    assert evolved.center == pytest.approx(expected_center)
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
    assert certificate["gates"]["state_sector_matches_model"]
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
    assert result["decision"]["periodic_observables_are_translation_covariant"]
    assert not result["decision"]["localized_branch_is_a_physical_particle"]
    assert not result["decision"]["physical_calibration_complete"]
