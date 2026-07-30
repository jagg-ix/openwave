from __future__ import annotations

from openwave.xperiments.m10_cat_ept.stationary_refinement_m102 import (
    central_pair_operator_descent,
    perturbation_tube,
    refinement_campaign,
    run_m10_closure_study,
    run_stationary_descent,
)


def test_m10_stationary_line_search_reduces_residual() -> None:
    result = run_stationary_descent(steps=4)
    assert result["accepted_steps"] >= 1
    assert result["final"]["relative_stationary_residual"] < result["initial"][
        "relative_stationary_residual"
    ]
    assert result["final_state"].entropic_time > 0.0
    assert result["final_state"].measured_winding == 3


def test_m10_nested_grid_invariants_close() -> None:
    result = refinement_campaign()
    assert result["all_topological_and_charge_invariants_close"]
    assert [row["points"] for row in result["rows"]] == [9, 13, 17]
    assert result["maximum_radius_spread"] <= 0.75


def test_m10_smooth_perturbation_tube_is_bounded() -> None:
    result = perturbation_tube()
    assert result["winding_preserved"]
    assert result["normalization_preserved"]
    assert result["bounded_residual_tube"]


def test_m10_central_pair_descends_through_interacting_operator() -> None:
    result = central_pair_operator_descent()
    assert result["operator_sign_descent_error"] <= 2.0e-11
    assert result["density_descent_error"] <= 2.0e-12
    assert result["cartan_contact_descent_error"] <= 2.0e-12


def test_m10_closure_study_passes() -> None:
    result = run_m10_closure_study()
    assert result["passed"]
    assert result["decision"]["stationary_residual_descent_established"]
    assert result["decision"]["nested_grid_invariants_established"]
    assert result["decision"]["perturbation_tube_established"]
    assert result["decision"]["central_pair_operator_descent_established"]
    assert result["decision"]["global_continuity_established"]
