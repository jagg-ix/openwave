from openwave.xperiments.m11_cat_ept_soliton_qdo.optional_qcd_coupling_m114 import run_optional_qcd_study

def test_optional_qcd_campaign():
    result=run_optional_qcd_study()
    assert result['passed'], result
