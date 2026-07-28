from openwave.xperiments.m9_cat_ept.four_clock_integration_m128 import run_four_clock_integration


def test_four_clock_integration_closes():
    result = run_four_clock_integration()
    assert result["passed"]
    assert result["metrics"]["strict_order_preserved"]
    assert result["metrics"]["maximum_roundtrip_error"] < 1e-14
