from openwave.xperiments.m9_cat_ept.planckian_paper_holdout_m126 import run_planckian_paper_holdout

def test_paper_level_holdout_is_retrospective_and_non_discriminating():
    r=run_planckian_paper_holdout()
    assert r["passed"]
    assert len(r["folds"])==3
    assert r["summary"]["broad_band_pass_rate"]==1.0
    assert not r["decision"]["entropic_time_uniquely_selected"]
    assert not r["decision"]["prospective_external_validation_complete"]
