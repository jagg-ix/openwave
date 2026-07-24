import numpy as np

from openwave.xperiments.m9_cat_ept.stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    initial_profile,
    normalize_state,
    phase_aligned_l2_distance,
    spectral_grid,
)


def test_normalization_and_phase_alignment():
    cfg = StationaryBranchConfig(grids=(12,), reference_grid=12, iterations=100)
    grid = spectral_grid(12, cfg.half_width)
    state = normalize_state(initial_profile("super_gaussian", grid), float(grid[5]))
    mass = float(np.sum(np.abs(state) ** 2) * float(grid[5]) ** 3)
    assert abs(mass - 1.0) < 1e-12
    assert phase_aligned_l2_distance(state, 1j * state, float(grid[5])) < 1e-12


def test_stationary_config_rejects_invalid_reference_grid():
    try:
        StationaryBranchConfig(grids=(12, 16), reference_grid=14)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid reference grid accepted")
