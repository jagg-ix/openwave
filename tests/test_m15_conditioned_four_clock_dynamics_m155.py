from openwave.xperiments.m15_kuchar_relational_time.conditioned_four_clock_dynamics_m155 import run_conditioned_four_clock_study


def test_m155():
    result = run_conditioned_four_clock_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
