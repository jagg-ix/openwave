from openwave.xperiments.m9_cat_ept.bssn_screen_gravity import run_bssn_screen_gravity
from openwave.xperiments.m9_cat_ept.model_registration_m115 import (
    run_model_registration_study,
)


def test_reduced_bssn_targets_close():
    result = run_bssn_screen_gravity()
    assert result["passed"]
    for key in (
        "conformal_metric_unit_determinant_is_enforced",
        "conformal_extrinsic_curvature_remains_trace_free",
        "conformal_connection_constraint_is_measured",
        "one_plus_log_lapse_is_evolved",
        "gamma_driver_shift_is_evolved",
        "metric_built_ricci_is_evolved",
        "screen_source_tidal_term_is_evolved",
        "tensor_momentum_constraint_is_damped",
        "gamma_constraint_is_damped",
        "one_screen_G_is_preserved",
    ):
        assert result["acceptance"][key]
    assert not result["decision"]["production_BSSN_constructed"]
    assert not result["decision"]["physical_screen_calibration_complete"]


def test_bssn_registration_preserves_scope():
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_115"]
    for key in (
        "conformal_connection_functions",
        "unit_determinant_control",
        "tracefree_extrinsic_control",
        "one_plus_log_lapse",
        "gamma_driver_shift",
        "metric_built_ricci",
        "screen_source_tidal_term",
        "tensor_constraint_damping",
        "gamma_constraint_damping",
        "one_screen_G_preserved",
        "constraints_reported",
    ):
        assert current[key]
    assert not current["production_BSSN_constructed"]
    assert not current["physical_calibration_complete"]
    assert current["physical_claims_promoted"] == []
