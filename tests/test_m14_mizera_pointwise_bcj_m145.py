from openwave.xperiments.m14_continuum_ads_double_copy.mizera_pointwise_bcj_m145 import run_mizera_pointwise_bcj_study


def test_m145_mizera_pointwise_bcj():
    result = run_mizera_pointwise_bcj_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
    assert result["theorem_status"] == "conditional-model"
    assert result["formal_toolchain"]["lean"] == "4.31.0"
    assert result["decision"]["full_chy_or_loop_level_double_copy_not_claimed"]
