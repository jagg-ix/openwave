from openwave.xperiments.m15_kuchar_relational_time.functorial_conditioning_m156 import run_functorial_conditioning_study


def test_m156():
    result = run_functorial_conditioning_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 9
