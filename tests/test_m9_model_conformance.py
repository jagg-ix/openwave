from openwave.xperiments.m9_cat_ept.model_conformance import CRITERIA,fingerprint,run_conformance_study,validate_profile

def test_exact_visible_criteria_count(): assert len(CRITERIA)==21
def test_domain_partition(): assert validate_profile()['domain_counts']=={'particles':12,'forces':5,'waves':3,'thermal':1}
def test_nonplanned_statuses_have_evidence(): assert all(c.status=='not_yet' or c.evidence for c in CRITERIA)
def test_one_honest_negative_is_preserved(): assert sum(c.status=='negative' for c in CRITERIA)==1
def test_summary_total_closes():
 r=validate_profile(); assert r['documented_summary_total']==21 and r['matrix_total_mismatch']==0
def test_no_explicit_criterion_is_unaddressed(): assert validate_profile()['status_counts']['not_yet']==0
def test_m9_59_binding_evidence_present():
 stability=next(c for c in CRITERIA if c.key=='particle_stability'); assert any('m9_59_method_note.md' in path for path in stability.evidence)
def test_status_counts_updated(): assert validate_profile()['status_counts']=={'validated':0,'partial':20,'negative':1,'not_yet':0}
def test_full_study_passes():
 r=run_conformance_study(); assert r['passed'] and all(r['acceptance'].values()) and len(fingerprint())==64
