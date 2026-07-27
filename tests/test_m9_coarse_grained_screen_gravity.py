import math

from openwave.xperiments.m9_cat_ept.coarse_grained_screen_gravity import (
    CoarseGrainedGravityConfig,
    analytic_source,
    run_coarse_grained_screen_gravity,
)


def test_analytic_source_is_low_mode_and_mean_zero():
    cfg = CoarseGrainedGravityConfig()
    source = analytic_source(cfg.grids[-1], cfg.half_width)
    assert source.shape == (cfg.grids[-1],) * 3
    assert abs(float(source.mean())) <= 1.0e-14


def test_one_screen_G_and_low_mode_gravity_are_scale_consistent():
    result = run_coarse_grained_screen_gravity()
    assert result["passed"]
    assert result["acceptance"]["one_screen_G_reaches_every_resolution_and_carrier"]
    assert result["acceptance"]["low_mode_source_survives_spectral_coarse_graining"]
    assert result["acceptance"]["Poisson_response_closes_on_every_grid"]
    assert result["acceptance"][
        "source_potential_field_and_tidal_observables_are_scale_consistent"
    ]
    assert math.isfinite(result["maximum_cauchy_relative_change"])
    assert result["decision"]["coarse_grained_screen_coupling_injected"]
    assert not result["decision"]["physical_screen_calibration_complete"]
