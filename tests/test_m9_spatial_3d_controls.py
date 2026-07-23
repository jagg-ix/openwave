from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spatial_3d import (
    Spatial3DGrid,
    Spatial3DParameters,
    clifford_residuals,
)
from openwave.xperiments.m9_cat_ept.spatial_3d import (
    run_spatial_3d_control_study,
)


def test_parameter_validation() -> None:
    for kwargs in ({"mass": 0.0}, {"gauge_charge": -0.1}, {"packet_width": 0.0}):
        try:
            Spatial3DParameters(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid parameters must fail")


def test_grid_validation() -> None:
    for kwargs in ({"points_x": 9}, {"points_y": 11}, {"dt_over_spacing": 0.2}):
        try:
            Spatial3DGrid(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid grid must fail")


def test_clifford_representation_closes() -> None:
    assert max(clifford_residuals().values()) == 0.0


def test_free_time_refinement_is_fourth_order() -> None:
    result = run_spatial_3d_control_study()
    assert min(result["free_time_refinement"]["observed_orders"]) >= 3.5


def test_free_norm_ledger_closes() -> None:
    result = run_spatial_3d_control_study()
    assert max(
        record["max_norm_drift"]
        for record in result["free_time_refinement"]["records"]
    ) <= 3.0e-7


def test_vacuum_maxwell_control_is_accurate() -> None:
    vacuum = run_spatial_3d_control_study()["vacuum_maxwell"]
    assert vacuum["a_relative_l2"] <= 2.0e-2
    assert vacuum["e_relative_l2"] <= 2.0e-2
    assert vacuum["field_energy_relative_drift"] <= 2.0e-5


def test_control_acceptance_passes() -> None:
    result = run_spatial_3d_control_study()
    assert result["passed"]
    assert all(result["acceptance"].values())


def test_control_result_is_json_serializable() -> None:
    decoded = json.loads(json.dumps(run_spatial_3d_control_study()))
    assert decoded["task"] == "M9.12"
