import math

import pytest

from openwave.xperiments.m9_cat_ept.canonical_spin_magnetic_bridge import (
    CanonicalSpinParameters,
    canonical_spin_observables,
    control_state,
    formal_structure_audit,
    g_factor,
    magnetic_moment_ratio,
    run_canonical_spin_magnetic_bridge,
    schwinger_anomaly,
)
from openwave.xperiments.m9_cat_ept.particle_model import CatEptParticleModel


def test_canonical_state_closes_spin_half_tree_g_and_zero_orbit():
    state = control_state()
    observables = canonical_spin_observables(state)
    assert observables["norm"] == pytest.approx(1.0, abs=2e-12)
    assert observables["spin_z"] == pytest.approx(0.5, abs=2e-12)
    assert abs(observables["orbital_z"]) < 2e-10
    assert observables["inferred_tree_g"] == pytest.approx(2.0, abs=5e-4)


def test_spin_flip_reverses_pauli_current_moment():
    state = control_state()
    up = canonical_spin_observables(state, CanonicalSpinParameters(spin=1))
    down = canonical_spin_observables(state, CanonicalSpinParameters(spin=-1))
    assert down["spin_z"] == pytest.approx(-up["spin_z"], abs=2e-12)
    assert down["magnetic_moment_z"] == pytest.approx(
        -up["magnetic_moment_z"], abs=5e-10
    )


def test_periodic_translation_preserves_spin_magnetic_observables():
    model = CatEptParticleModel.repository_default()
    state = control_state()
    translated = model.translate_cells(state, (7, -5, 3))
    base = canonical_spin_observables(state)
    shifted = canonical_spin_observables(translated)
    for key in (
        "norm",
        "spin_z",
        "orbital_z",
        "magnetic_moment_z",
        "inferred_tree_g",
    ):
        assert shifted[key] == pytest.approx(base[key], abs=5e-10)


def test_imported_schwinger_structure_closes_without_particle_derivation():
    alpha = 1.0 / 137.0
    anomaly = schwinger_anomaly(alpha)
    assert g_factor(anomaly) == pytest.approx(2.0 + alpha / math.pi, abs=2e-15)
    assert g_factor(anomaly) == pytest.approx(
        2.0 * magnetic_moment_ratio(anomaly), abs=2e-15
    )
    audit = formal_structure_audit(alpha)
    assert audit["g_factor"] == pytest.approx(audit["schwinger_expected_g"], abs=2e-15)


def test_full_canonical_spin_bridge_passes_with_physical_boundary():
    result = run_canonical_spin_magnetic_bridge()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["formal_spin_magnetic_surface_imported"]
    assert result["decision"]["tree_level_g_factor_closed_in_platform"]
    assert not result["decision"]["schwinger_anomaly_derived_from_cat_ept_particle"]
    assert not result["decision"]["physical_electron_identity_established"]
