import numpy as np

from openwave.xperiments.m9_cat_ept.gaussian_covariance_scale_flow import (
    GaussianScaleFlowConfig,
    piecewise_constant_injection,
    run_gaussian_covariance_scale_flow,
)


def test_piecewise_constant_injection_is_isometric():
    injection = piecewise_constant_injection(32, 2)
    identity = injection.T @ injection
    assert np.linalg.norm(identity - np.eye(32)) <= 3.0e-14


def test_gaussian_covariance_flow_and_limits_close():
    result = run_gaussian_covariance_scale_flow()
    assert result["passed"]
    assert result["acceptance"]["Gaussian_pullback_matches_projected_covariance"]
    assert result["acceptance"]["composable_injections_give_automatic_fixed_point"]
    assert result["acceptance"]["heat_transfer_is_a_semigroup"]
    assert result["acceptance"]["principal_mode_converges_toward_one"]
    assert result["acceptance"]["image_modes_decouple_toward_zero"]
    assert result["decision"]["Gaussian_covariance_flow_adapter_constructed"]
    assert not result["decision"]["interacting_fixed_point_constructed"]
    assert GaussianScaleFlowConfig().fine_points == 64
