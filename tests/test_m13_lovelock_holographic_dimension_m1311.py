from openwave.xperiments.m13_scale_dilation_soliton.lovelock_holographic_dimension_m1311 import run_lovelock_holographic_study

def test_m1311():
    result = run_lovelock_holographic_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 6
