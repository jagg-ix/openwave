from openwave.xperiments.m9_cat_ept.formalization_dynamics_extension import (
    dynamics_criterion_import_map,
    expected_dynamics_source_blobs,
    run_dynamics_formal_extension_study,
    validate_dynamics_extension,
)


def test_dynamics_overlay_imports_rest_frame_spin_and_particle_witnesses():
    result = run_dynamics_formal_extension_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["source_count"] == 3
    imports = dynamics_criterion_import_map()
    magnetic = imports["magnetic_moment_spin"]["declarations"]
    electric = imports["electric_force"]["declarations"]
    assert any(item.endswith("heisenberg_precession_of_dipole") for item in magnetic)
    assert any(item.endswith("tbmtSpinRate_rest_eq_diracPauli") for item in magnetic)
    assert any(item.endswith("coulombPotential_eq") for item in electric)
    assert any(item.endswith("threeDimPointParticle_electricField") for item in electric)
    assert not result["decision"]["full_covariant_tbmt_dynamics_imported"]
    assert not result["decision"]["formal_availability_promotes_physical_rows"]


def test_dynamics_overlay_fails_closed_on_missing_or_changed_sources():
    expected = expected_dynamics_source_blobs()
    path = next(iter(expected))

    missing = dict(expected)
    missing.pop(path)
    missing_result = validate_dynamics_extension(observed_blobs=missing)
    assert not missing_result["passed"]
    assert any("source missing" in error for error in missing_result["errors"])

    stale = dict(expected)
    stale[path] = "0" * 40
    stale_result = validate_dynamics_extension(observed_blobs=stale)
    assert not stale_result["passed"]
    assert any("source drift detected" in error for error in stale_result["errors"])


def test_dynamics_overlay_preserves_rest_frame_and_covariant_boundaries():
    result = run_dynamics_formal_extension_study()
    magnetic = result["criterion_imports"]["magnetic_moment_spin"]["boundary"]
    assert any("rest-frame" in boundary for boundary in magnetic)
    assert any("covariant boost" in boundary for boundary in magnetic)
    assert result["decision"]["rest_frame_dirac_pauli_precession_imported"]
    assert result["decision"]["rest_frame_tbmt_equivalence_imported"]
