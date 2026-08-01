from openwave.xperiments.m15_kuchar_relational_time.entropic_clock_synthesis_m157 import run_entropic_clock_synthesis_study


def test_m157():
    result = run_entropic_clock_synthesis_study()
    assert result["passed"]
    assert len(result["acceptance"]) == 11
