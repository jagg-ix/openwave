from openwave.xperiments.m9_cat_ept.four_clock_promotion_gate_m128 import run_four_clock_promotion_gate


def test_four_clock_promotion_fails_closed():
    result = run_four_clock_promotion_gate()
    assert result["passed"]
    assert result["internal_ready"]
    assert not result["physical_ready"]
    assert not result["decision"]["universal_clock_claim_allowed"]
