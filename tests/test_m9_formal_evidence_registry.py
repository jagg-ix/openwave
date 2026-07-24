from dataclasses import replace
import pytest
from openwave.xperiments.m9_cat_ept.formal_evidence_registry import (
    EvidenceItem,drift_control,evaluate_registry,illegal_promotion_control,
    registry,registry_fingerprint,run_formal_evidence_study,validate_dependencies)

def test_registry_pins_exact_formal_branch():
    assert all(item.branch=="entropic-physlib-linear-full" for item in registry() if item.repository=="jagg-ix/entropic-physlib-private")

def test_current_snapshot_has_no_drift():
    counts=evaluate_registry()["counts"]; assert counts["stale"]==0 and counts["missing"]==0

def test_pending_and_open_not_promoted():
    r=illegal_promotion_control(); assert r["pending_not_formal"] and r["open_not_formal"]

def test_drift_and_missing_detected():
    r=drift_control(); assert r["stale_status"]=="stale" and r["missing_status"]=="missing"

def test_computational_items_verified(): assert evaluate_registry()["counts"]["computationally_verified"]==2

def test_no_formal_promotions_yet(): assert evaluate_registry()["counts"]["formal_promoted"]==0

def test_circular_dependencies_rejected():
    a=EvidenceItem("a","local","main","a","x"*40,"computational","a","a",("b",))
    b=EvidenceItem("b","local","main","b","y"*40,"computational","b","b",("a",))
    with pytest.raises(ValueError): validate_dependencies((a,b))

def test_full_evidence_study_passes():
    r=run_formal_evidence_study(); assert r["passed"] and all(r["acceptance"].values())
    assert len(registry_fingerprint())==64
