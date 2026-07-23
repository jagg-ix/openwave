from openwave.xperiments.m9_cat_ept.model_conformance import CRITERIA, fingerprint, run_conformance_study, validate_profile

def test_exact_visible_criteria_count(): assert len(CRITERIA)==20
def test_domain_partition(): assert validate_profile()["domain_counts"]=={"particles":12,"forces":5,"waves":3}
def test_nonplanned_statuses_have_evidence(): assert all(c.status=="not_yet" or c.evidence for c in CRITERIA)
def test_honest_negative_is_preserved(): assert any(c.status=="negative" for c in CRITERIA)
def test_summary_mismatch_is_explicit():
    r=validate_profile(); assert r["documented_summary_total"]==21 and r["matrix_total_mismatch"]==1
def test_thermal_gap_is_named(): assert validate_profile()["missing_explicit_criterion"]=="heat_or_thermal_sector"
def test_fingerprint_is_deterministic(): assert fingerprint()==fingerprint() and len(fingerprint())==64
def test_m9_31_33_counts(): assert validate_profile()["status_counts"]=={"validated":0,"partial":12,"negative":1,"not_yet":7}
def test_full_study_passes():
    r=run_conformance_study(); assert r["passed"] and all(r["acceptance"].values())
