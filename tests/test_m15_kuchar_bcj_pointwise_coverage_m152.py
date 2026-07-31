from openwave.xperiments.m15_kuchar_relational_time.kuchar_bcj_pointwise_coverage_m152 import run_kuchar_bcj_pointwise_coverage_study

def test_m152():
    result = run_kuchar_bcj_pointwise_coverage_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 8
