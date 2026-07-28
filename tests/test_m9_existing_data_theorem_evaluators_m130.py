from openwave.xperiments.m9_cat_ept.cross_carrier_generalization_m130 import run_cross_carrier_generalization


def test_cross_carrier_generalization_protocol():
    result = run_cross_carrier_generalization()
    assert result["passed"]
    assert result["all_folds_pass"]
    assert not result["decision"]["real_cross_carrier_result_available"]
