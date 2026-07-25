import numpy as np

from openwave.xperiments.m9_cat_ept.recentered_conservation_closure import (
    RecenteredConservationConfig,
    density_centroid,
    fourier_shift,
    local_stationary_config,
    run_recentered_conservation_closure,
)
from openwave.xperiments.m9_cat_ept.stationary_non_gaussian_branch import (
    solve_stationary,
)


def test_density_centroid_fourier_recentring_removes_known_shift():
    cfg = RecenteredConservationConfig(
        points=12,
        stationary_iterations=1000,
        timesteps=(0.004, 0.002, 0.001),
    )
    state, grid = solve_stationary(
        cfg.points, "super_gaussian", local_stationary_config(cfg)
    )
    moved = np.roll(state, 1, axis=0)
    center = density_centroid(moved, grid)
    recentered = fourier_shift(moved, grid, center)
    assert np.linalg.norm(density_centroid(recentered, grid)) < 2e-4


def test_m9_79_conservation_and_refinement_pass():
    result = run_recentered_conservation_closure()
    assert result["passed"]
    assert result["acceptance"][
        "local_interaction_converges_under_time_refinement"
    ]
    assert not result["decision"]["continuum_global_conservation_theorem_proved"]
