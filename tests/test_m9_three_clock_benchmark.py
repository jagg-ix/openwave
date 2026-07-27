from openwave.xperiments.m9_cat_ept.three_clock_benchmark import (
    run_entropic_clock_control,
    run_modular_flow_control,
    run_page_wootters_conditioning_control,
    run_three_clock_benchmark,
)


def test_page_wootters_conditioning_control() -> None:
    result = run_page_wootters_conditioning_control()
    assert result["passed"]
    assert result["maximum_conditioning_error"] < 1e-12
    assert abs(result["system_marginal_entropy"] - result["clock_marginal_entropy"]) < 1e-12


def test_modular_flow_control() -> None:
    result = run_modular_flow_control()
    assert result["passed"]
    assert result["modular_identity_error"] < 1e-12
    assert result["flow_match_error"] < 1e-12
    assert abs(result["entropy_change"]) < 1e-12


def test_entropic_clock_control() -> None:
    result = run_entropic_clock_control()
    assert result["passed"]
    assert result["final_accumulated_clock"] > 0
    assert result["population_spectral_change"] > 0.1


def test_combined_benchmark_keeps_clocks_separate() -> None:
    result = run_three_clock_benchmark()
    assert result["passed"]
    assert not result["separation"]["one_parameter_identity_assumed"]
    assert not result["decision"]["single_unified_clock_parameter_established"]
