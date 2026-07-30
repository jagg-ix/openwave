from openwave.xperiments.m14_continuum_ads_double_copy.infinite_bcj_direct_limit_m142 import run_infinite_bcj_direct_limit_study

def test_m142():
    result=run_infinite_bcj_direct_limit_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 9
    assert result["decision"]["summability_and_gauge_orthogonality_are_visible_model_premises"]
