from openwave.xperiments.m9_cat_ept.h1_concentration_closure import (
    run_concentration_compactness_closure,
    run_h1_direct_method_closure,
)


def test_h1_direct_method_uses_live_complete_carrier():
    result = run_h1_direct_method_closure()
    assert result["passed"]
    assert result["decision"]["complete_continuum_h1_carrier_proved"]
    assert result["decision"]["bounded_h1_weak_subsequence_proved"]
    assert result["decision"]["constrained_direct_method_proved"]
    assert not result["decision"]["m9_72_end_to_end_ground_state_attainment_closed"]


def test_concentration_closure_uses_negative_level_and_binding_gap():
    result = run_concentration_compactness_closure()
    assert result["passed"]
    assert result["decision"]["vanishing_excluded_by_negative_level"]
    assert result["decision"]["dichotomy_excluded_by_positive_binding_gap"]
    assert result["decision"]["compact_branch_follows_from_explicit_trichotomy"]
    assert not result["decision"]["m9_73_end_to_end_compactness_closed"]
