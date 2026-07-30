from openwave.xperiments.m13_scale_dilation_soliton.holographic_rg_cutoff_flow_m136 import run_holographic_rg_study
def test_m136():
    result=run_holographic_rg_study(); assert result["passed"]; assert len(result["acceptance"])==7
