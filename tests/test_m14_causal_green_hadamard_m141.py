from openwave.xperiments.m14_continuum_ads_double_copy.causal_green_hadamard_m141 import run_causal_green_hadamard_study

def test_m141():
    result=run_causal_green_hadamard_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
    assert result["decision"]["wavefront_equality_not_inferred_from_global_hyperbolicity_alone"]
