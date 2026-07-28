from openwave.xperiments.m9_cat_ept.published_summary_evaluators_m131 import (
    run_published_summary_evaluators,
)


def test_published_summary_evaluators_pass_with_scope_boundaries():
    result = run_published_summary_evaluators()
    assert result["passed"]
    assert result["leggett_garg"]["all_observed_values_violate_classical_upper_bound"]
    assert result["qubit_fit"]["population_is_nonincreasing"]
    assert result["quantum_dot_bound"]["minimum_reported_lower_bound_us"] >= 10.0
    assert not any(result["claim_boundary"].values())
