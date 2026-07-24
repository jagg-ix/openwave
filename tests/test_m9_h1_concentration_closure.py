from openwave.xperiments.m9_cat_ept.h1_concentration_closure import (
    run_concentration_compactness_closure,
    run_h1_direct_method_closure,
)


def test_h1_direct_method_uses_live_complete_carrier():
    result = run_h1_direct_method_closure()
    assert result["passed"]
    decision = result["decision"]
    assert decision["complete_continuum_h1_carrier_proved"]
    assert decision["bounded_h1_weak_subsequence_with_norm_bound_proved"]
    assert decision["weak_plus_norm_strong_h1_closure_proved"]
    assert decision["joint_field_density_subsequence_from_tightness_proved"]
    assert decision["constrained_direct_method_proved"]
    assert decision["local_h1_existence_uniqueness_for_c1_generator_proved"]
    assert decision["compact_sublevel_orbital_stability_mechanism_proved"]
    assert not decision["m9_72_end_to_end_target_closed"]


def test_concentration_closure_uses_live_compactness_stack():
    result = run_concentration_compactness_closure()
    assert result["passed"]
    decision = result["decision"]
    assert decision["prokhorov_compactness_from_tightness_proved"]
    assert decision["joint_field_density_subsequence_from_tightness_proved"]
    assert decision["strong_h1_upgrade_from_norm_closure_proved"]
    assert decision["vanishing_excluded_by_negative_level"]
    assert decision["dichotomy_excluded_by_positive_binding_gap"]
    assert decision["compact_branch_follows_from_explicit_trichotomy"]
    assert decision["compact_sublevel_orbital_stability_mechanism_proved"]
    assert not decision["m9_73_end_to_end_target_closed"]
