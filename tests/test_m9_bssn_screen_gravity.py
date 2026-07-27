from openwave.xperiments.m9_cat_ept.bssn_screen_gravity import run_bssn_screen_gravity
from openwave.xperiments.m9_cat_ept.model_registration_m115 import run_model_registration_study


def test_reduced_bssn_targets_close():
    result = run_bssn_screen_gravity()
    assert result["passed"]
    assert result["acceptance"]["conformal_metric_unit_determinant_is_enforced"]
    assert result["acceptance"]["conformal_extrinsic_curvature_remains_trace_free"]
    assert result["acceptance"]["conformal_connection_constraint_is_measured"]
    assert result["acceptance"]["one_plus_log_lapse_is_evolved"]
    assert result["acceptance"]["gamma_driver_shift_is_evolved"]


def test_bssn_registration_preserves_scope():
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_115"]
    assert current["conformal_connection_functions"]
    assert current["unit_determinant_control"]
    assert current["one_plus_log_gamma_driver"]
    assert current["one_screen_G_preserved"]
    assert not current["production_BSSN_constructed"]
    assert not current["physical_calibration_complete"]
    assert current["physical_claims_promoted"] == []
