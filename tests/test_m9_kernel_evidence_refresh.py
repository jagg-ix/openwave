from openwave.xperiments.m9_cat_ept.kernel_evidence_refresh import (
    observed_snapshot,
    promotion_controls,
    promotion_status,
    refresh,
    run_kernel_evidence_refresh,
    snapshot,
)


def test_default_refresh_has_zero_formal_promotions():
    assert refresh()["counts"]["formal_promoted"] == 0


def test_pending_records_wait_for_kernel():
    assert refresh()["counts"]["awaiting_kernel"] == 4


def test_interface_and_open_boundaries_are_separate():
    counts = refresh()["counts"]
    assert counts["interface_only"] == 1 and counts["open_boundary"] == 2


def test_eligible_kernel_record_can_promote():
    assert promotion_controls()["eligible_status"] == "formal_promoted"


def test_stale_missing_and_assumption_controls_fail_closed():
    controls = promotion_controls()
    assert controls["stale_status"] == "stale"
    assert controls["missing_witness_status"] == "missing_witness"
    assert controls["open_assumption_status"] == "blocked_by_assumption"


def test_open_item_cannot_promote_even_with_current_source():
    item = snapshot()[-1]
    assert promotion_status(item, observed_snapshot()) == "open_boundary"


def test_full_refresh_passes_and_records_gate():
    result = run_kernel_evidence_refresh()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["new_formal_promotions"] == 0
