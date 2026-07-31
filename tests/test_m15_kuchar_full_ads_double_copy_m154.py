from openwave.xperiments.m15_kuchar_relational_time.kuchar_full_ads_double_copy_m154 import run_kuchar_full_ads_double_copy_study

def test_m154():
    result = run_kuchar_full_ads_double_copy_study()
    assert result["passed"]
    assert result["coverage_count"] == result["coverage_total"]
    assert len(result["acceptance"]) == 10
