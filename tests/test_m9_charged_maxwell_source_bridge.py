import pytest

from openwave.xperiments.m9_cat_ept.charged_maxwell_source_bridge import (
    run_charged_maxwell_source_bridge,
)
from openwave.xperiments.m9_cat_ept.formalization_force_extension import (
    extension_source_blobs,
    run_force_formal_extension_study,
    validate_force_formal_extension,
)


def test_force_formal_overlay_imports_missing_current_and_pauli_links():
    result = run_force_formal_extension_study()
    assert result["schema"] == "openwave.m9.force-formal-extension.v2"
    assert result["passed"] and all(result["acceptance"].values())
    assert result["source_count"] == 2
    magnetic = result["criterion_imports"]["magnetic_moment_spin"]["declarations"]
    electric = result["criterion_imports"]["electric_force"]["declarations"]
    assert any(item.endswith("pauliCoupling_gauge_invariant") for item in magnetic)
    assert any(item.endswith("fourCurrent_conserved") for item in electric)
    assert not result["decision"]["formal_availability_promotes_physical_rows"]


def test_force_formal_overlay_rejects_missing_and_changed_sources():
    expected = extension_source_blobs()
    path = next(iter(expected))

    changed = dict(expected)
    changed[path] = "0" * 40
    changed_result = validate_force_formal_extension(observed_blobs=changed)
    assert not changed_result["passed"]
    assert any("source drift detected" in error for error in changed_result["errors"])

    missing = dict(expected)
    missing.pop(path)
    missing_result = validate_force_formal_extension(observed_blobs=missing)
    assert not missing_result["passed"]
    assert any("source missing" in error for error in missing_result["errors"])


def test_winding_candidate_closes_static_maxwell_constraints_and_moment_response():
    result = run_charged_maxwell_source_bridge()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["candidate"]["integer_winding"] == 3
    assert result["source"]["integrated_charge"] == pytest.approx(1.0, abs=2e-12)
    assert result["maxwell"]["projection_loss"] <= 1.5e-2
    assert result["maxwell"]["gauss_relative_residual"] <= 2e-12
    assert result["maxwell"]["ampere_relative_residual"] <= 2e-12
    assert result["maxwell"]["magnetic_divergence_max"] <= 2e-12
    assert result["maxwell"]["electric_energy"] > 0.0
    assert result["maxwell"]["magnetic_energy"] > 0.0
    assert result["magnetic_response"]["absolute_error"] <= 2e-10
    assert result["source"]["magnetic_moment_z"] == pytest.approx(
        result["magnetic_response"]["energy_response_moment"],
        abs=2e-10,
    )


def test_source_bridge_retains_stationary_and_calibration_boundaries():
    result = run_charged_maxwell_source_bridge()
    assert result["decision"]["same_field_supplies_winding_charge_current_and_moment"]
    assert result["decision"]["static_maxwell_source_equations_closed"]
    assert result["decision"]["magnetic_moment_response_closed_on_candidate"]
    assert not result["decision"]["maxwell_backreaction_in_stationary_equation"]
    assert not result["decision"]["charged_stationary_branch_constructed"]
    assert not result["decision"]["physical_charge_or_moment_calibrated"]
