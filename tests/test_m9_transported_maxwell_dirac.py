from __future__ import annotations

import json
import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.transported_maxwell_dirac import (
    TransportGrid,
    TransportParameters,
    gauss_metrics,
    initial_state,
    result_to_json,
    run_transport_study,
    signed_charge_density,
    total_norm,
)


def test_parameter_and_grid_validation() -> None:
    with pytest.raises(ValueError):
        TransportParameters(mass=0.0)
    with pytest.raises(ValueError):
        TransportParameters(gauge_charge=-0.1)
    with pytest.raises(ValueError):
        TransportGrid(points=127)
    with pytest.raises(ValueError):
        TransportGrid(dt_over_dx=0.5)


def test_initial_state_is_normalized_and_neutral() -> None:
    parameters = TransportParameters()
    grid = TransportGrid(points=256, final_time=1.0, samples=3)
    x, dx, plus, minus, _ax, ex, _ay, _ey = initial_state(parameters, grid)
    assert x.shape == (grid.points,)
    assert math.isclose(total_norm(plus, minus, dx), 1.0, abs_tol=2.0e-14)
    charge = signed_charge_density(plus, minus, parameters)
    assert abs(dx * float(np.sum(charge))) <= 2.0e-14
    absolute, relative = gauss_metrics(ex, plus, minus, parameters, dx)
    assert absolute <= 2.0e-13
    assert relative <= 2.0e-12


def test_refinement_is_convergent() -> None:
    result = run_transport_study()
    assert result["refinement"]["observed_order"] >= 1.6
    differences = result["refinement"]["successive_spinor_l2_differences"]
    assert differences[1] < differences[0]


def test_norm_and_energy_ledgers_close() -> None:
    summary = run_transport_study()["long_run"]
    assert summary["max_norm_drift"] <= 2.0e-8
    assert summary["max_corrected_energy_relative_drift"] <= 2.0e-6


def test_dynamic_gauss_and_net_charge_close() -> None:
    result = run_transport_study()
    final = result["long_run"]["final"]
    assert final["gauss_residual_absolute"] <= 4.0e-4
    assert final["gauss_residual_relative"] <= 5.0e-2
    assert result["long_run"]["max_net_charge"] <= 1.0e-10


def test_packets_transport_and_cross() -> None:
    transport = run_transport_study()["transport"]
    assert transport["initial_separation"] > 0.0
    assert transport["final_separation"] < 0.75 * transport["initial_separation"]


def test_transverse_backreaction_and_radiation_are_nonzero() -> None:
    result = run_transport_study()
    final = result["long_run"]["final"]
    assert final["max_transverse_field"] >= 1.0e-4
    assert result["long_run"]["emitted_energy"] >= 1.0e-7
    assert result["acceptance"]["transverse_field_backreacts"]
    assert result["acceptance"]["radiation_emitted"]


def test_result_schema_claims_and_json() -> None:
    result = run_transport_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["task"] == "M9.9"
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]
    decoded = json.loads(result_to_json(result))
    assert decoded["passed"] is True
