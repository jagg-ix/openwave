"""Tests for the M9.7b3 constrained spherical dynamic gate."""

from __future__ import annotations

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.dirac_electrostatic_3d import (
    CoupledParameters,
    StationaryGrid,
    solve_stationary_branch,
)
from openwave.xperiments.m9_cat_ept.dirac_electrostatic_dynamics_3d import (
    DynamicGrid,
    Perturbation,
    electrostatic_constraint,
    evolve_constrained_dynamics,
    number_norm,
    radial_shell_grid,
    run_dynamic_study,
)


def test_electrostatic_constraint_closes_signed_charge() -> None:
    parameters = CoupledParameters()
    grid = DynamicGrid(cells=128, final_time=1.0)
    edges, centers, volumes, _ = radial_shell_grid(grid)
    density = np.exp(-2.0 * centers)
    density /= float(np.sum(density * volumes))
    gauge = electrostatic_constraint(density, edges, centers, volumes, parameters)
    assert gauge.enclosed_charge_edges[-1] == pytest.approx(1.0, abs=1.0e-14)
    assert gauge.electric_field_edges[0] == pytest.approx(0.0)
    assert np.all(np.diff(gauge.enclosed_charge_edges) >= 0.0)


def test_weighted_split_step_conserves_norm() -> None:
    parameters = CoupledParameters()
    stationary = solve_stationary_branch(
        parameters,
        StationaryGrid(initial_points=256, tolerance=1.0e-5),
    )
    run = evolve_constrained_dynamics(
        stationary,
        DynamicGrid(cells=128, final_time=1.0, samples=5),
        Perturbation(0.01, 0.01),
    )
    initial = number_norm(run.initial_upper, run.initial_lower, run.volumes)
    final = number_norm(run.final_upper, run.final_lower, run.volumes)
    assert final == pytest.approx(initial, abs=1.0e-12)


def test_scored_dynamic_study_passes() -> None:
    result = run_dynamic_study()
    assert result["passed"] is True
    assert all(bool(value) for value in result["acceptance"].values())


def test_dynamic_refinement_is_second_order() -> None:
    orders = run_dynamic_study()["refinement"]["observed_orders"]
    assert orders["spinor_l2"] >= 1.8
    assert orders["density_l1"] >= 1.8


def test_long_time_perturbation_remains_localized() -> None:
    result = run_dynamic_study()["long_time_run"]
    assert result["phase_metrics"]["fidelity"] >= 0.999
    assert result["final"]["core_fraction_r16"] >= 0.985
    assert result["final"]["outer_fraction_20pct"] <= 2.0e-4
    assert result["max_norm_drift"] <= 2.0e-12
    assert result["max_total_energy_relative_drift"] <= 2.0e-7


def test_spherical_radiation_ledger_is_an_explicit_negative() -> None:
    radiation = run_dynamic_study()["radiation_ledger"]
    assert radiation["electromagnetic_poynting_flux"] == 0.0
    assert "negative" in radiation["classification"]


def test_radial_clock_interface_survives_dynamics() -> None:
    clock = run_dynamic_study()["radial_clock"]
    assert clock["remaining_nonincreasing"] is True
    assert clock["gain_nondecreasing"] is True
    assert clock["correlation_nonnegative"] is True
    assert clock["max_ledger_closure_error"] <= 1.0e-12


def test_invalid_dynamic_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="cells must be at least 64"):
        DynamicGrid(cells=32)
    with pytest.raises(ValueError, match="dt_over_dr"):
        DynamicGrid(dt_over_dr=0.5)
    with pytest.raises(ValueError, match="amplitude magnitude"):
        Perturbation(amplitude=0.2)
