from openwave.xperiments.m14_continuum_ads_double_copy.ads_normalized_continuum_double_copy_m143 import run_ads_normalized_continuum_double_copy_study

def test_m143():
    result=run_ads_normalized_continuum_double_copy_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 9
    assert result["decision"]["amplitude_entropy_equality_not_claimed"]
