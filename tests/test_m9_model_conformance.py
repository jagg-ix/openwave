
from openwave.xperiments.m9_cat_ept.model_conformance import CRITERIA, fingerprint, run_conformance_study, validate_profile

def test_exact_visible_criteria_count(): assert len(CRITERIA)==21
def test_domain_partition(): assert validate_profile()["domain_counts"]=={"particles":12,"forces":5,"waves":3,"thermal":1}
def test_nonplanned_statuses_have_evidence(): assert all(c.status=="not_yet" or c.evidence for c in CRITERIA)
def test_two_honest_negatives_are_preserved(): assert sum(c.status=="negative" for c in CRITERIA)==2
def test_summary_total_now_closes():
    r=validate_profile(); assert r["documented_summary_total"]==21 and r["matrix_total_mismatch"]==0
def test_thermal_criterion_is_explicit():
    assert validate_profile()["missing_explicit_criterion"] is None
    assert any(c.key=="thermal_field" for c in CRITERIA)
def test_fingerprint_is_deterministic(): assert fingerprint()==fingerprint() and len(fingerprint())==64
def test_m9_43_45_counts(): assert validate_profile()["status_counts"]=={"validated":0,"partial":18,"negative":2,"not_yet":1}
def test_full_study_passes():
    r=run_conformance_study(); assert r["passed"] and all(r["acceptance"].values())
