from openwave.xperiments.m11_cat_ept_soliton_qdo.coupled_dynamics_registration_m115 import run_m11_model_study

def test_m11_complete_campaign():
    result=run_m11_model_study()
    assert result['passed'], result
    assert result['decision']['m11_registered_as_separate_model']
