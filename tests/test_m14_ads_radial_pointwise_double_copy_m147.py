from openwave.xperiments.m14_continuum_ads_double_copy.ads_radial_pointwise_double_copy_m147 import run_ads_radial_pointwise_double_copy_study


def test_m147_ads_radial_pointwise_double_copy():
    result = run_ads_radial_pointwise_double_copy_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 9
    assert result["theorem_status"] == "conditional-model"
    assert result["formal_toolchain"]["lean"] == "4.31.0"
    assert result["decision"]["interacting_witten_or_global_ads_double_copy_not_claimed"]
