from openwave.xperiments.m9_cat_ept.generalized_screen_adm_gravity import (
    run_generalized_screen_adm_gravity,
)
from openwave.xperiments.m9_cat_ept.model_registration_m114 import (
    run_model_registration_study,
)


def test_generalized_metric_modes_and_screen_coupling():
    result = run_generalized_screen_adm_gravity()
    assert result["passed"]
    assert result["acceptance"]["one_screen_G_reaches_generalized_carrier"]
    assert result["acceptance"]["tracefree_metric_mode_evolves"]
    assert result["acceptance"]["tracefree_extrinsic_mode_evolves"]
    assert result["acceptance"]["shift_mode_is_present"]
    assert result["acceptance"]["tracefree_projection_is_preserved"]


def test_generalized_registration_preserves_scope():
    result = run_model_registration_study()
    current = result["m9_114"]
    assert result["passed"]
    assert current["TT_metric_modes"]
    assert current["tracefree_extrinsic_curvature"]
    assert current["shift_dynamics"]
    assert not current["general_Einstein_Cauchy_development"]
    assert not current["physical_screen_calibration_complete"]
    assert current["physical_claims_promoted"] == []
