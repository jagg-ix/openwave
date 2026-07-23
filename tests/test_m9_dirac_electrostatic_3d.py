"""Tests for the M9.7b2 coupled radial Dirac--electrostatic gate."""

from __future__ import annotations

import json

import pytest

from openwave.xperiments.m9_cat_ept.dirac_electrostatic_3d import (
    CoupledParameters,
    StationaryGrid,
    result_to_json,
    run_coupled_stationary_study,
)


def _result() -> dict[str, object]:
    return run_coupled_stationary_study()


def test_complete_stationary_gate_passes() -> None:
    result = _result()
    assert result["passed"] is True
    assert all(bool(value) for value in result["acceptance"].values())


def test_frequency_is_inside_mass_gap_and_branch_is_nontrivial() -> None:
    result = _result()
    finest = result["refinement"]["levels"][-1]
    assert 0.0 < finest["frequency"] < 1.0
    assert finest["central_upper"] > 0.05
    assert finest["number_norm"] == pytest.approx(1.0, abs=2.0e-9)
    assert finest["total_charge"] == pytest.approx(1.0, abs=1.0e-10)


def test_refinement_and_stationary_residual_close() -> None:
    result = _result()
    orders = result["refinement"]["observed_orders"]
    assert min(orders.values()) >= 3.0
    finest = result["refinement"]["levels"][-1]
    assert finest["spinor_residual_relative_l2"] <= 5.0e-7
    assert finest["max_collocation_residual"] <= 6.5e-7


def test_maxwell_flux_and_energy_ledgers_close() -> None:
    finest = _result()["refinement"]["levels"][-1]
    assert finest["gauss_residual_relative_max"] <= 5.0e-6
    assert finest["potential_residual_max"] <= 1.0e-8
    assert finest["boundary_flux_error"] <= 1.0e-7
    assert finest["source_field_relative_difference"] <= 1.0e-7
    assert finest["eigenvalue_identity_relative_error"] <= 5.0e-7


def test_window_and_localization_gates_close() -> None:
    result = _result()
    spreads = result["window_study"]["relative_spreads"]
    assert spreads["frequency"] <= 1.0e-4
    assert spreads["central_potential"] <= 1.0e-4
    assert spreads["rms_radius"] <= 5.0e-3
    finest = result["refinement"]["levels"][-1]
    assert finest["core_fraction_r16"] >= 0.985
    assert finest["outer_fraction_20pct"] <= 2.0e-4


def test_initial_guess_perturbation_returns_to_same_branch() -> None:
    perturbation = _result()["initial_guess_perturbation"]
    assert perturbation["frequency_difference"] <= 1.0e-10
    assert perturbation["spinor_l2_difference"] <= 1.0e-8
    assert perturbation["density_l1_difference"] <= 1.0e-8


def test_signed_sector_and_radial_clock_close() -> None:
    result = _result()
    negative = result["negative_charge_sector"]
    assert negative["gauge_charge"] == -1.0
    assert negative["potential_sign_error"] == 0.0
    assert negative["field_energy_relative_difference"] == 0.0
    clock = result["radial_clock"]
    assert clock["remaining_nonincreasing"] is True
    assert clock["gain_nondecreasing"] is True
    assert clock["correlation_nonnegative"] is True
    assert clock["max_ledger_closure_error"] <= 1.0e-12


def test_json_and_invalid_inputs() -> None:
    result = _result()
    encoded = result_to_json(result)
    assert json.loads(encoded)["passed"] is True
    with pytest.raises(ValueError, match="mass must be positive"):
        CoupledParameters(mass=0.0)
    with pytest.raises(ValueError, match="initial_points must be at least 128"):
        StationaryGrid(initial_points=64)
