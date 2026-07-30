from openwave.xperiments.m14_continuum_ads_double_copy.smooth_continuum_ads_double_copy_m144 import run_smooth_continuum_ads_double_copy_study

def test_m144():
    result=run_smooth_continuum_ads_double_copy_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 10
    assert result["theorem_status"] == "conditional-model"
    assert result["decision"]["unconditional_global_ads_double_copy_theorem_not_claimed"]
