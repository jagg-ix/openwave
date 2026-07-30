from openwave.xperiments.m13_scale_dilation_soliton.penrose_holographic_mass_entropy_m139 import run_penrose_holographic_study

def test_m139():
    result = run_penrose_holographic_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 6
