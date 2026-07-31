from openwave.xperiments.m14_continuum_ads_double_copy.continuum_kernel_double_copy_m146 import run_continuum_kernel_double_copy_study


def test_m146_continuum_kernel_double_copy():
    result = run_continuum_kernel_double_copy_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
    assert result["theorem_status"] == "conditional-model"
    assert result["formal_toolchain"]["lean"] == "4.31.0"
    assert result["decision"]["arbitrary_interacting_continuum_double_copy_not_claimed"]
