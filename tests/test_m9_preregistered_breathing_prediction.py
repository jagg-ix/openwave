from openwave.xperiments.m9_cat_ept.preregistered_breathing_prediction import (
    dispersion_independence_control,
    prediction_fingerprint,
    run_preregistered_breathing_prediction,
    variational_energy_derivatives,
)


def test_reference_is_stationary_and_curved_up():
    result = variational_energy_derivatives()
    assert abs(result["first_derivative"]) < 2e-13
    assert result["second_derivative"] > 0


def test_ratio_is_dispersion_independent():
    result = dispersion_independence_control()
    assert result["ratio_is_dispersion_independent_under_selection_rule"]


def test_prediction_is_frozen_not_validated():
    result = run_preregistered_breathing_prediction()
    assert result["passed"]
    assert result["decision"]["prediction_ready_count"] == 1
    assert not result["decision"]["prediction_validated"]


def test_fingerprint_is_stable():
    assert prediction_fingerprint() == prediction_fingerprint()
