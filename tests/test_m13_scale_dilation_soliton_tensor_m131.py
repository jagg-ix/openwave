from openwave.xperiments.m13_scale_dilation_soliton import run_scale_dilation_soliton_study

def test_m13_scale_dilation_soliton_tensor():
    result = run_scale_dilation_soliton_study()
    assert result["passed"], result
    assert result["decision"]["m11_pointwise_and_infinite_mode_carriers_reused"]
    assert result["diagnostics"]["sqrt_two_half_step_error"] < 5e-14
