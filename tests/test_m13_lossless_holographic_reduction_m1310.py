from openwave.xperiments.m13_scale_dilation_soliton.lossless_holographic_reduction_m1310 import run_holographic_reduction_study

def test_m1310():
    result = run_holographic_reduction_study()
    assert result["passed"]
    assert result["decision"]["random_jl_embedding_existence_not_claimed"]
