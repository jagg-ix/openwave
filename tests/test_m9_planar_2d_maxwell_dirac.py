from __future__ import annotations

import json
import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.planar_2d_maxwell_dirac import (
    Planar2DGrid,
    Planar2DParameters,
    gauss_metrics,
    initial_state,
    result_to_json,
    run_planar_2d_study,
    signed_charge_density,
    total_norm,
    wave_numbers,
)


def test_parameter_and_grid_validation() -> None:
    with pytest.raises(ValueError):
        Planar2DParameters(mass=0.0)
    with pytest.raises(ValueError):
        Planar2DParameters(gauge_charge=-0.1)
    with pytest.raises(ValueError):
        Planar2DGrid(points_x=15)
    with pytest.raises(ValueError):
        Planar2DGrid(dt_over_spacing=0.5)


def test_initial_state_is_normalized_and_neutral() -> None:
    parameters = Planar2DParameters()
    grid = Planar2DGrid(points_x=48, points_y=48, final_time=1.0)
    xx, yy, dx, dy, plus, minus, _ax, _ay, ex, ey = initial_state(
        parameters, grid
    )
    assert xx.shape == yy.shape == (48, 48)
    assert math.isclose(total_norm(plus, minus, dx * dy), 1.0, abs_tol=2e-14)
    charge = signed_charge_density(plus, minus, parameters)
    assert abs(dx * dy * float(np.sum(charge))) <= 2e-14
    kx, ky = wave_numbers(grid, dx, dy)
    absolute, relative = gauss_metrics(ex, ey, plus, minus, parameters, kx, ky)
    assert absolute <= 1e-12
    assert relative <= 2e-10


def test_two_dimensional_refinement_converges() -> None:
    result = run_planar_2d_study()
    assert result["refinement"]["observed_order"] >= 3.0
    differences = result["refinement"]["successive_spinor_l2_differences"]
    assert differences[1] < differences[0]


def test_norm_energy_and_gauss_close() -> None:
    summary = run_planar_2d_study()["long_run"]
    assert summary["max_norm_drift"] <= 2e-8
    assert summary["max_corrected_energy_relative_drift"] <= 5e-5
    assert summary["final"]["gauss_residual_absolute"] <= 2e-4
    assert summary["final"]["gauss_residual_relative"] <= 5e-2


def test_transport_is_two_dimensional() -> None:
    result = run_planar_2d_study()
    summary = result["long_run"]
    assert summary["final_separation"] < summary["initial_separation"]
    angles = result["transport_angles"]
    assert abs(angles["final"] - angles["initial"]) >= 1e-3


def test_magnetic_and_emitted_energy_are_nonzero() -> None:
    summary = run_planar_2d_study()["long_run"]
    assert summary["final"]["max_magnetic_field"] >= 1e-4
    assert abs(summary["emitted_energy"]) >= 1e-7


def test_domain_shape_study_is_stable() -> None:
    spreads = run_planar_2d_study()["domain_shape_study"]["relative_spreads"]
    assert spreads["final_separation"] <= 0.08
    assert spreads["emitted_energy"] <= 0.30


def test_result_schema_and_claims() -> None:
    result = run_planar_2d_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]
    assert json.loads(result_to_json(result))["passed"] is True
