import numpy as np

from openwave.xperiments.m9_cat_ept.screen_coarse_graining_dynamics import (
    ScreenCoarseGrainingConfig,
    block_sum,
    run_screen_coarse_graining_dynamics,
    spectral_heat_flow,
)


def test_heat_and_block_maps_compose():
    cfg = ScreenCoarseGrainingConfig()
    values = np.arange(cfg.points, dtype=np.float64) + 1.0
    left = spectral_heat_flow(
        spectral_heat_flow(values, 0.3 * cfg.diffusion_time, cfg.half_width),
        0.7 * cfg.diffusion_time,
        cfg.half_width,
    )
    right = spectral_heat_flow(values, cfg.diffusion_time, cfg.half_width)
    assert np.linalg.norm(left - right) / np.linalg.norm(right) <= 2.0e-14
    assert np.allclose(
        block_sum(block_sum(values, cfg.block_factor), cfg.block_factor),
        block_sum(values, cfg.block_factor**2),
    )


def test_dynamic_screen_flow_preserves_microscopic_G():
    result = run_screen_coarse_graining_dynamics()
    assert result["passed"]
    assert result["acceptance"]["area_per_bit_and_G_are_invariant"]
    assert result["acceptance"]["physical_count_endpoints_close"]
    assert result["decision"]["finite_block_semigroup_constructed"]
    assert result["decision"]["continuous_count_flow_constructed"]
    assert result["decision"]["universal_holographic_G_preserved"]
    assert not result["decision"]["particle_mass_endpoint_derived"]
