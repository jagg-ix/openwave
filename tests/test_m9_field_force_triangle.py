import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.field_force_triangle import (
    FieldForceTriangleConfig,
    run_field_force_triangle,
)


def test_field_force_triangle_closes_on_winding_candidates():
    result = run_field_force_triangle()
    cfg = FieldForceTriangleConfig()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["charges"][0] == pytest.approx(1.0, abs=2e-12)
    assert result["charges"][1] == pytest.approx(-1.0, abs=2e-12)
    assert abs(result["electric_force"][2]) > 1e-8
    assert abs(result["magnetic_force"][2]) > 1e-8
    assert result["lorentz_force"][2] > 0.0
    assert result["relative_errors"]["energy_vs_lorentz"] <= cfg.energy_relative_tolerance
    assert result["relative_errors"]["stress_vs_lorentz"] <= cfg.stress_relative_tolerance
    assert result["relative_errors"]["action_reaction"] <= cfg.action_reaction_relative_tolerance


def test_reverse_lorentz_force_is_action_reaction_partner():
    result = run_field_force_triangle()
    forward = np.asarray(result["lorentz_force"])
    reverse = np.asarray(result["reverse_lorentz_force"])
    relative = np.linalg.norm(forward + reverse) / np.linalg.norm(forward)
    assert relative <= FieldForceTriangleConfig().action_reaction_relative_tolerance


def test_force_triangle_does_not_promote_missing_dynamics_or_calibration():
    result = run_field_force_triangle()
    assert result["decision"]["field_derived_force_triangle_closed_on_charged_candidates"]
    assert result["decision"]["electric_and_magnetic_kernels_replaced_by_source_fields"]
    assert not result["decision"]["center_acceleration_measured_from_full_pde"]
    assert not result["decision"]["stable_charged_stationary_pair_constructed"]
    assert not result["decision"]["physical_force_calibration_complete"]
    assert result["decision"]["criterion_rows_promoted"] == []
