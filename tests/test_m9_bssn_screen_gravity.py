import numpy as np

from openwave.xperiments.m9_cat_ept.bssn_screen_gravity import (
    enforce_unit_determinant,
    identity_metric,
    pointwise_determinant,
    run_bssn_screen_gravity,
)
from openwave.xperiments.m9_cat_ept.model_registration_m115 import (
    run_model_registration_study,
)


def test_unit_determinant_projection():
    metric = identity_metric((2, 2, 2))
    metric[0, 0] *= 1.3
    metric[1, 1] *= 0.8
    projected = enforce_unit_determinant(metric)
    assert np.max(np.abs(pointwise_determinant(projected) - 1.0)) <= 5.0e-15


def test_bssn_style_campaign_preserves_boundaries():
    result = run_bssn_screen_gravity()
    assert result["passed"]
    assert result["acceptance"]["unit_determinant_is_enforced"]
    assert result["acceptance"]["tracefree_extrinsic_is_enforced"]
    assert result["acceptance"]["conformal_connection_functions_are_evolved"]
    assert result["acceptance"]["connection_constraint_is_measured"]
    assert result["acceptance"]["one_plus_log_lapse_is_evolved"]
    assert result["acceptance"]["gamma_driver_shift_is_evolved"]
    assert result["acceptance"]["one_screen_coupling_is_preserved"]
    assert not result["decision"]["exact_BSSN_constructed"]
    assert not result["decision"]["general_Einstein_evolution_constructed"]
    assert not result["decision"]["physical_screen_calibration_complete"]


def test_schema_v19_does_not_overpromote():
    result = run_model_registration_study()
    assert result["passed"]
    assert result["schema"] == "openwave.model-registration.v19"
    current = result["m9_115"]
    assert current["unit_determinant_control"]
    assert current["conformal_connection_functions"]
    assert current["one_plus_log_lapse"]
    assert current["gamma_driver_shift"]
    assert not current["exact_BSSN_complete"]
    assert not current["general_Einstein_evolution_complete"]
    assert current["physical_claims_promoted"] == []
