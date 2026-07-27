import math

from openwave.xperiments.m9_cat_ept.newton_g_anchor_protocol import (
    audit_bundle,
    circular_inversion_bundle,
    default_bundle,
    execute_frozen_prediction,
    run_newton_G_anchor_protocol,
    synthetic_independent_planck_scale_bundle,
)
from openwave.xperiments.m9_cat_ept.newton_g_gravity_adapter import (
    GravityUnitMap,
    coupling_contract,
    dimensionless_newton_G,
    inference_width_from_dimensionless_G,
    run_newton_G_gravity_adapter,
)


def test_default_particle_clock_does_not_unlock_G_prediction():
    result = run_newton_G_anchor_protocol()
    assert result["passed"]
    assert not audit_bundle(default_bundle())["prediction_ready"]
    assert not result["default_prediction"]["executed"]


def test_G_inversion_is_rejected_as_circular():
    audit = audit_bundle(circular_inversion_bundle())
    assert audit["newton_G_circularity_detected"]
    assert not audit["prediction_ready"]


def test_synthetic_anchor_exercises_positive_prediction_path():
    result = execute_frozen_prediction(synthetic_independent_planck_scale_bundle())
    assert result["executed"]
    assert result["passed"]
    assert result["withheld_relative_error"] < 1e-6


def test_unit_map_reconstructs_one_G_for_both_gravity_levels():
    units = GravityUnitMap(2.0, 4.0, 8.0)
    G_dim = dimensionless_newton_G(3.0, units)
    assert math.isclose(G_dim, 6.0)
    sigma = inference_width_from_dimensionless_G(
        G_dim, hbar_dimensionless=2.0, light_speed_dimensionless=3.0
    )
    assert math.isclose(2.0 * 3.0 * sigma**4, G_dim)

    prediction = execute_frozen_prediction(synthetic_independent_planck_scale_bundle())
    contract = coupling_contract(prediction, GravityUnitMap(1.0, 1.0, 1.0))
    assert contract["ready"]
    assert contract["same_frozen_G_used_in_both_gravity_levels"]
    assert math.isclose(
        contract["weak_field_config"]["newton_coupling"],
        contract["nonlinear_metric_config"]["newton_coupling"],
    )


def test_default_adapter_blocks_unexecuted_prediction():
    result = run_newton_G_gravity_adapter()
    assert result["passed"]
    assert not result["blocked_default"]["ready"]
