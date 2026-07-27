from openwave.xperiments.m9_cat_ept.three_clock_unification_gate_m125 import REDUCED_REQUIREMENTS, UNIVERSAL_REQUIREMENTS, run_three_clock_unification_gate_m125

def test_reduced_gate_passes_and_universal_gate_fails_closed():
    result = run_three_clock_unification_gate_m125()
    assert result['passed']
    assert result['reduced_gate']['passed']
    assert not result['universal_gate']['passed']
    assert set(result['universal_gate']['missing']) == set(UNIVERSAL_REQUIREMENTS) - set(REDUCED_REQUIREMENTS)
    assert all(result['removal_failures'].values())
