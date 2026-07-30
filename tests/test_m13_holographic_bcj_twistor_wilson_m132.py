from openwave.xperiments.m13_scale_dilation_soliton.holographic_bcj_twistor_wilson_m132 import (
    run_holographic_amplitude_study,
)


def test_m13_holographic_bcj_twistor_wilson():
    result = run_holographic_amplitude_study()
    assert result["passed"], result
    assert result["diagnostics"]["m10_wilson_passed"]
    assert result["diagnostics"]["m13_1_passed"]
    assert len(result["acceptance"]) == 10
