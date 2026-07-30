from openwave.xperiments.m13_scale_dilation_soliton.yukawa_dilation_gkp_m133 import run_yukawa_dilation_gkp_study

def test_m133():
    result = run_yukawa_dilation_gkp_study()
    assert result["passed"]
    assert result["decision"]["weyl_cartan_dilatonic_charge_is_not_the_global_dilation_group"]
