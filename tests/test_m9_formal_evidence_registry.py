import pytest

from openwave.xperiments.m9_cat_ept.formal_evidence_registry import (
    EvidenceItem,
    drift_control,
    evaluate_registry,
    illegal_promotion_control,
    registry,
    registry_fingerprint,
    run_formal_evidence_study,
    validate_dependencies,
)


def test_registry_pins_exact_formal_branch():
    assert all(
        item.branch == "entropic-physlib-linear-full"
        for item in registry()
        if item.repository == "jagg-ix/entropic-physlib-private"
    )


def test_computational_sources_pin_main():
    assert all(
        item.branch == "main"
        for item in registry()
        if item.repository == "jagg-ix/openwave"
    )


def test_current_snapshot_has_no_drift():
    counts = evaluate_registry()["counts"]
    assert counts["stale"] == 0 and counts["missing"] == 0


def test_pending_and_open_not_promoted():
    result = illegal_promotion_control()
    assert result["pending_not_formal"] and result["open_not_formal"]


def test_drift_and_missing_detected():
    result = drift_control()
    assert result["stale_status"] == "stale" and result["missing_status"] == "missing"


def test_computational_items_verified():
    assert evaluate_registry()["counts"]["computationally_verified"] == 6


def test_no_formal_promotions_yet():
    assert evaluate_registry()["counts"]["formal_promoted"] == 0


def test_circular_dependencies_rejected():
    first = EvidenceItem("a", "local", "main", "a", "x" * 40, "computational", "a", "a", ("b",))
    second = EvidenceItem("b", "local", "main", "b", "y" * 40, "computational", "b", "b", ("a",))
    with pytest.raises(ValueError):
        validate_dependencies((first, second))


def test_full_evidence_study_passes():
    result = run_formal_evidence_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(registry_fingerprint()) == 64
