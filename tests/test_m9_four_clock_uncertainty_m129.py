from openwave.xperiments.m9_cat_ept.four_clock_uncertainty_m129 import run_uncertainty_propagation


def test_uncertainty_propagation_preserves_robust_order():
    result = run_uncertainty_propagation()
    assert result["passed"]
    assert result["metrics"]["all_adjacent_orders_robust"]
