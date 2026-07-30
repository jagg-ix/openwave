from openwave.xperiments.m11_cat_ept_soliton_qdo.qdo_lj_atm_interaction_m113 import run_qdo_lj_atm_study

def test_qdo_lj_atm_campaign():
    result=run_qdo_lj_atm_study()
    assert result['passed'], result
    assert abs(result['diagnostics']['far_field_log_slope']+6)<1e-10
