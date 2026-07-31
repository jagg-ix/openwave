from openwave.xperiments.m15_kuchar_relational_time.kuchar_continuum_bcj_causal_m153 import run_kuchar_continuum_bcj_causal_study

def test_m153():
    result = run_kuchar_continuum_bcj_causal_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
