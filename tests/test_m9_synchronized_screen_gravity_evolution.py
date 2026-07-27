from openwave.xperiments.m9_cat_ept.model_registration_m113 import run_model_registration_study
from openwave.xperiments.m9_cat_ept.synchronized_screen_gravity_evolution import run_synchronized_screen_gravity_evolution


def test_synchronized_histories_close_in_shared_sector():
    result = run_synchronized_screen_gravity_evolution()
    assert result["passed"]
    assert result["acceptance"]["shared_matter_history_closes"]
    assert result["acceptance"]["shared_source_history_closes"]
    assert result["acceptance"]["shared_weak_potential_history_closes"]
    assert result["acceptance"]["shared_weak_metric_history_closes"]


def test_nonlinear_only_observables_are_reported_without_overpromotion():
    result = run_synchronized_screen_gravity_evolution()
    assert result["acceptance"]["nonlinear_geometry_adds_dynamics"]
    assert result["acceptance"]["nonlinear_constraint_diagnostics_remain_finite"]
    assert not result["decision"]["general_Einstein_time_evolution_complete"]
    assert not result["decision"]["physical_screen_density_calibrated"]


def test_registration_v17_preserves_boundaries():
    result = run_model_registration_study()
    assert result["passed"]
    assert result["schema"] == "openwave.model-registration.v17"
    assert not result["m9_113"]["general_GR_evolution_complete"]
    assert result["m9_113"]["physical_claims_promoted"] == []
