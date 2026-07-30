from openwave.xperiments.m13_scale_dilation_soliton.yukawa_rt_holographic_entropy_m134 import run_yukawa_rt_holographic_study
def test_m134():
 r=run_yukawa_rt_holographic_study(); assert r["passed"]; assert r["decision"]["rt_area_and_horizon_area_rate_are_not_identified"]
