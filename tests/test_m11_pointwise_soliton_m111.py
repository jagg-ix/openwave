from openwave.xperiments.m11_cat_ept_soliton_qdo.pointwise_soliton_carrier_m111 import run_pointwise_soliton_study

def test_pointwise_soliton_campaign():
    result=run_pointwise_soliton_study()
    assert result['passed'], result
    assert result['diagnostics']['stationary_residual_linf'] < 5e-13
