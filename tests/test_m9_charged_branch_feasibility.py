import pytest

from openwave.xperiments.m9_cat_ept.charged_branch_feasibility import (
    ChargedBranchFeasibilityConfig,
    charged_observables,
    charged_seed,
    run_charged_branch_feasibility,
)


def test_winding_three_seed_is_field_derived_and_normalized():
    cfg = ChargedBranchFeasibilityConfig(
        points=20,
        core_radii=(0.9,),
    )
    field, grid = charged_seed(0.9, cfg)
    result = charged_observables(field, grid, cfg)
    assert result["mass"] == pytest.approx(1.0, abs=2e-12)
    assert result["integer_winding"] == 3
    assert result["quantization_error"] <= 2e-12
    assert result["charge_from_winding"] == 1.0
    assert result["spin_z_for_up_embedding"] == pytest.approx(0.5, abs=2e-12)


def test_selected_scalar_action_does_not_close_charged_stationary_branch():
    result = run_charged_branch_feasibility()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["passing_candidate_count"] == 0
    assert not result["decision"]["charged_stationary_branch_constructed"]
    assert result["decision"]["requires_extended_gauge_or_spinorial_stationary_equation"]
    assert all(row["seed"]["integer_winding"] == 3 for row in result["rows"])
    assert any(row["sector_preserved"] for row in result["rows"])
    assert all(not row["full_charged_stationary_gate"] for row in result["rows"])


def test_failure_is_not_a_neutral_baseline_or_seed_quantization_failure():
    result = run_charged_branch_feasibility()
    neutral = result["neutral_baseline"]
    assert neutral["relative_stationary_residual"] <= 3e-3
    assert neutral["boundary_fraction"] <= 1e-4
    assert max(row["seed"]["quantization_error"] for row in result["rows"]) <= 2e-12
    assert max(row["evolved"]["relative_stationary_residual"] for row in result["rows"]) > 0.5
