from openwave.xperiments.m9_cat_ept.shared_screen_gravity_campaign import run_shared_screen_gravity_campaign
from openwave.xperiments.m9_cat_ept.model_registration_m111 import run_model_registration_study


def test_shared_screen_initial_observables_close():
    result = run_shared_screen_gravity_campaign()
    assert result["passed"]
    assert result["acceptance"]["one_screen_G_reaches_both_models"]
    assert result["acceptance"]["one_matter_source_is_shared"]
    assert result["acceptance"]["one_weak_potential_is_shared"]
    assert result["acceptance"]["nonlinear_metric_seed_matches_weak_g00"]


def test_registration_preserves_scope_boundaries():
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_111"]
    assert current["finite_initial_constraints"]
    assert not current["full_cross_model_time_evolution"]
    assert not current["physical_calibration_complete"]
    assert current["physical_claims_promoted"] == []
