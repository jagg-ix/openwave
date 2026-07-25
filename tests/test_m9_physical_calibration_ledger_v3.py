from openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v3 import (
    run_physical_calibration_ledger_v3,
)


def test_dynamics_calibration_ledger_preserves_three_partial_rows():
    result = run_physical_calibration_ledger_v3()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(result["rows"]) == 3
    assert result["status_counts"]["blocked_by_model"] == 3
    assert {row["criterion"] for row in result["rows"]} == {
        "magnetic_moment_spin",
        "electric_force",
        "magnetic_force",
    }
    assert not result["decision"]["magnetic_moment_spin_promoted"]
    assert not result["decision"]["electric_force_promoted"]
    assert not result["decision"]["magnetic_force_promoted"]


def test_ledger_distinguishes_closed_subreductions_from_promotion_blockers():
    result = run_physical_calibration_ledger_v3()
    by_key = {row["criterion"]: row for row in result["rows"]}
    assert any(
        "full Dirac generator" in item
        for item in by_key["magnetic_moment_spin"]["closed_now"]
    )
    assert any(
        "kinetic-momentum transfer" in item
        for item in by_key["electric_force"]["closed_now"]
    )
    assert any(
        "covariant" in item
        for item in by_key["magnetic_force"]["blocking_obligations"]
    )
    assert "stable charged spinorial branch" in result["decision"]["shared_blocker"]
    assert not result["decision"]["out_of_sample_physical_prediction_ready"]
