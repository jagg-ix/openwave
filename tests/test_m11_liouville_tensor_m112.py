from openwave.xperiments.m11_cat_ept_soliton_qdo.liouville_soliton_tensor_m112 import run_liouville_tensor_study

def test_liouville_tensor_campaign():
    result=run_liouville_tensor_study()
    assert result['passed'], result
    assert result['diagnostics']['particle_number']==3
