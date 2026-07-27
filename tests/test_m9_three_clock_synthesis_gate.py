from openwave.xperiments.m9_cat_ept.three_clock_synthesis_gate import (
    UNIFIED_CLOCK_REQUIREMENTS,
    evaluate_relations,
    run_three_clock_synthesis_gate,
)


def test_three_aspect_gate_passes_but_unified_clock_fails() -> None:
    result = run_three_clock_synthesis_gate()
    assert result["passed"]
    assert result["role_gate"]["passed"]
    assert not result["unified_clock_gate"]["passed"]
    assert result["unified_clock_gate"]["missing"]
    assert not result["decision"]["single_unified_physical_clock_established"]


def test_each_unified_requirement_is_load_bearing() -> None:
    complete = set(UNIFIED_CLOCK_REQUIREMENTS)
    assert evaluate_relations(complete, UNIFIED_CLOCK_REQUIREMENTS)["passed"]
    for requirement in UNIFIED_CLOCK_REQUIREMENTS:
        assert not evaluate_relations(complete - {requirement}, UNIFIED_CLOCK_REQUIREMENTS)["passed"]
