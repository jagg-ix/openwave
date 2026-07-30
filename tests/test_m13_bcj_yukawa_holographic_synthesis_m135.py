from openwave.xperiments.m13_scale_dilation_soliton.bcj_yukawa_holographic_synthesis_m135 import run_bcj_yukawa_holographic_study
def test_m135():
 r=run_bcj_yukawa_holographic_study(); assert r["passed"]; assert r["decision"]["bcj_amplitude_is_not_identified_with_rt_entropy"]
