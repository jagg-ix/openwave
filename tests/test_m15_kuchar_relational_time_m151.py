from openwave.xperiments.m15_kuchar_relational_time import (
    run_kuchar_relational_time_study,
)


def test_m151_kuchar_relational_time():
    result = run_kuchar_relational_time_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
    assert result["decision"]["global_preferred_time_not_claimed"]
    assert result["decision"]["global_kuchar_decomposition_not_claimed"]
