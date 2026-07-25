from openwave.xperiments.m9_cat_ept.partial_reduction_audit import (
    PROMOTIONS,
    run_partial_reduction_audit,
)


def test_exactly_three_partials_are_safely_reducible():
    result = run_partial_reduction_audit()
    assert result["passed"] and all(result["acceptance"].values())
    assert set(PROMOTIONS) == {
        "spin_half_statistics",
        "em_waves",
        "thermal_field",
    }
    assert result["proposed_counts"] == {
        "validated": 3,
        "partial": 17,
        "negative": 1,
        "not_yet": 0,
    }


def test_every_remaining_partial_has_a_named_blocker():
    result = run_partial_reduction_audit()
    blocked = [
        row for row in result["rows"] if not row["eligible_for_platform_validation"]
    ]
    assert len(blocked) == 17
    assert all(row["blocking_gap"] for row in blocked)
