from openwave.xperiments.m13_scale_dilation_soliton.wilson_rt_surface_scaling_m137 import run_wilson_rt_scaling_study
def test_m137():
    result=run_wilson_rt_scaling_study(); assert result["passed"]; assert result["decision"]["wilson_rt_equality_is_not_claimed"]
