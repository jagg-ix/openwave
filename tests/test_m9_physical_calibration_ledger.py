from openwave.xperiments.m9_cat_ept.physical_calibration_ledger import (
    CRITERIA,cross_repo_control_events,gates,ledger_fingerprint,
    run_physical_calibration_ledger,unit_rank_audit,verify_cross_repo_control_events)

def test_all_criteria_are_gated():
    rows=gates()
    assert len(rows)==21 and {x.criterion for x in rows}==set(CRITERIA)

def test_anchor_rank_is_explicit():
    r=unit_rank_audit()
    assert r["rank_by_anchor_count"][4]==4
    assert r["dimensionful_prediction_dof_after_four_independent_anchors"]==0

def test_no_unearned_prediction():
    r=run_physical_calibration_ledger()
    assert r["counts"]["prediction_ready"]==0 and not r["decision"]["physical_calibration_complete"]

def test_ledger_deterministic(): assert ledger_fingerprint()==ledger_fingerprint()
def test_control_event_chain(): assert verify_cross_repo_control_events(cross_repo_control_events())
def test_full_ledger_passes(): assert run_physical_calibration_ledger()["passed"]
