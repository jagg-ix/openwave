from openwave.xperiments.m9_cat_ept.existing_data_theorem_evaluators_m130 import run_theorem_specific_evaluators


def test_theorem_specific_existing_data_evaluators():
    result = run_theorem_specific_evaluators()
    assert result["passed"]
    assert result["relational"]["passed"]
    assert result["relaxation"]["observed_kl_nonincreasing"]
