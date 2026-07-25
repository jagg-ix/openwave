import pytest

from openwave.xperiments.m9_cat_ept.gauge_spinor_stationary_current import (
    SPIN_TOLERANCE,
    run_gauge_spinor_stationary_feasibility,
)


def test_self_consistent_gauge_spinor_campaign_preserves_topology_and_spin():
    result = run_gauge_spinor_stationary_feasibility()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.gauge-spinor-stationary-feasibility.v2"
    assert len(result["checkpoints"]) == 4
    initial = result["checkpoints"][0]
    final = result["checkpoints"][-1]
    assert initial["integer_winding"] == final["integer_winding"] == 3
    assert final["quantization_error"] <= 2e-12
    assert final["charge_from_winding"] == pytest.approx(1.0, abs=2e-15)
    assert final["spin_z"] == pytest.approx(0.5, abs=SPIN_TOLERANCE)
    assert result["spin_drift"] <= SPIN_TOLERANCE
    assert final["mass"] == pytest.approx(1.0, abs=2e-12)
    assert final["radius"] <= 1.75
    assert final["boundary_fraction"] <= 2e-2


def test_gauge_spinor_maxwell_constraints_close_but_stationary_residual_does_not():
    result = run_gauge_spinor_stationary_feasibility()
    final = result["checkpoints"][-1]
    maxwell = result["final_maxwell"]
    assert maxwell["gauss_relative_residual"] <= 2e-12
    assert maxwell["ampere_relative_residual"] <= 2e-12
    assert maxwell["magnetic_divergence_max"] <= 2e-12
    assert maxwell["electric_energy"] > 0.0
    assert maxwell["magnetic_energy"] > 0.0
    assert final["relative_stationary_residual"] > 0.1
    assert not result["decision"]["charged_spinor_stationary_branch_constructed"]
    assert result["decision"]["requires_additional_stationary_mechanism"]


def test_stationary_audit_does_not_promote_identity_or_criteria():
    result = run_gauge_spinor_stationary_feasibility()
    assert result["decision"]["self_consistent_gauge_spinor_equation_constructed"]
    assert result["decision"]["charge_current_and_fields_recomputed_each_iteration"]
    assert result["decision"]["criterion_rows_promoted"] == []
    assert not result["decision"]["physical_particle_identity_established"]
