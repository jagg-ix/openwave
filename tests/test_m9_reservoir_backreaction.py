import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.reservoir_backreaction import (
    ReservoirGrid,
    ReservoirParameters,
    initial_state,
    loss_profile,
    run_reservoir_backreaction_study,
    zero_loss_study,
)


def test_parameters_and_grid_validate() -> None:
    with pytest.raises(ValueError):
        ReservoirParameters(coupling=-0.1)
    with pytest.raises(ValueError):
        ReservoirGrid(points=63)


def test_initial_probability_and_charge_close() -> None:
    parameters = ReservoirParameters()
    grid = ReservoirGrid(points=128, final_time=1.0)
    _x, dx, plus, minus, reservoir_plus, reservoir_minus = initial_state(parameters, grid)
    probability = dx * float(np.sum(np.abs(plus) ** 2 + np.abs(minus) ** 2))
    charge = parameters.charge * dx * float(np.sum(np.abs(plus) ** 2 - np.abs(minus) ** 2))
    assert math.isclose(probability, 1.0, abs_tol=2e-14)
    assert abs(charge) <= 2e-14
    assert not np.any(reservoir_plus)
    assert not np.any(reservoir_minus)


def test_loss_profile_is_positive() -> None:
    grid = ReservoirGrid(points=128, final_time=1.0)
    dx = 2 * grid.half_width / grid.points
    x = -grid.half_width + dx * np.arange(grid.points)
    assert np.min(loss_profile(x, grid.half_width)) > 0.0


def test_refinement_converges() -> None:
    assert run_reservoir_backreaction_study()["refinement"]["observed_order"] >= 1.5


def test_extended_ledgers_close() -> None:
    summary = run_reservoir_backreaction_study()["long_run"]
    assert summary["max_extended_probability_error"] <= 5e-8
    assert summary["max_extended_charge_error"] <= 5e-10
    assert summary["maximum_continuity_residual"] <= 5e-10


def test_loss_and_reservoir_are_monotone() -> None:
    summary = run_reservoir_backreaction_study()["long_run"]
    assert summary["matter_probability_monotone"]
    assert summary["reservoir_probability_monotone"]
    assert summary["tau_ent_monotone"]
    assert summary["minimum_reservoir_density"] >= -2e-12


def test_zero_loss_reduces_to_closed_transport() -> None:
    result = zero_loss_study()
    assert result["matter_probability_drift"] <= 5e-8
    assert abs(result["reservoir_probability"]) <= 2e-12
    assert abs(result["tau_ent"]) <= 5e-8


def test_full_study_passes_with_claim_boundaries() -> None:
    result = run_reservoir_backreaction_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]
