from openwave.xperiments.m9_cat_ept.bssn_screen_gravity import (
    BSSNScreenConfig,
    damp_gamma_constraint,
    damp_tensor_momentum_constraint,
    enforce_unit_determinant,
    source_tidal_tensor,
)
from openwave.xperiments.m9_cat_ept.bssn_screen_refinement import (
    run_bssn_refinement_study,
)
from openwave.xperiments.m9_cat_ept.compatible_discrete_geometry import (
    PeriodicFourierGeometry,
)
from openwave.xperiments.m9_cat_ept.model_registration_m116 import (
    run_model_registration_study,
)

import numpy as np


def test_source_tidal_and_constraint_damping_helpers():
    cfg = BSSNScreenConfig(steps=10, sample_stride=5)
    geometry = PeriodicFourierGeometry(
        (cfg.points, cfg.points, cfg.points),
        (2.0 * cfg.half_width / cfg.points,) * 3,
    )
    axis = -cfg.half_width + geometry.spacings[0] * np.arange(cfg.points)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    source = np.cos(x) * np.cos(y) * np.cos(z)
    tidal = source_tidal_tensor(source, geometry, cfg.anchor.newton_coupling)
    assert np.isfinite(tidal).all()
    assert np.linalg.norm(tidal) > 0.0

    metric = np.zeros((3, 3, cfg.points, cfg.points, cfg.points))
    metric[0, 0] = np.exp(0.02 * source)
    metric[1, 1] = np.exp(-0.02 * source)
    metric[2, 2] = 1.0
    metric = enforce_unit_determinant(metric)
    assert np.max(
        np.abs(np.linalg.det(np.moveaxis(metric, (0, 1), (-2, -1))) - 1.0)
    ) < 1.0e-12

    a_tilde = np.zeros_like(metric)
    current = tuple(
        component / (8.0 * np.pi) for component in geometry.gradient(source)
    )
    _, tensor_audit = damp_tensor_momentum_constraint(
        a_tilde,
        current,
        geometry,
        1.0,
        cfg.tensor_constraint_damping,
        cfg.time_step,
    )
    assert tensor_audit["tensor_momentum_after"] < tensor_audit[
        "tensor_momentum_before"
    ]

    zeros = tuple(np.zeros_like(source) for _ in range(3))
    transported = tuple(component + 0.1 for component in zeros)
    _, gamma_audit = damp_gamma_constraint(
        transported,
        zeros,
        cfg.gamma_constraint_damping,
        cfg.time_step,
    )
    assert gamma_audit["gamma_constraint_after"] < gamma_audit[
        "gamma_constraint_before"
    ]


def test_bssn_refinement_closes_manufactured_bridges():
    result = run_bssn_refinement_study()
    assert result["passed"]
    assert result["acceptance"][
        "screen_source_tidal_tensor_matches_analytic_mode"
    ]
    assert result["acceptance"][
        "stf_tensor_divergence_correction_is_exact_on_active_modes"
    ]
    assert result["acceptance"][
        "ricci_and_source_invariants_are_cauchy_consistent"
    ]
    assert len(result["rows"]) == 3
    assert not result["decision"]["continuum_BSSN_convergence_proved"]


def test_m116_registration_preserves_scope():
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_116"]
    assert current["metric_built_conformal_ricci"]
    assert current["source_coupled_tracefree_curvature"]
    assert current["tensor_constraint_damping"]
    assert current["three_grid_refinement"]
    assert current["finite_grid_cauchy_consistency"]
    assert not current["continuum_convergence_proved"]
    assert not current["production_BSSN_constructed"]
    assert not current["physical_calibration_complete"]
    assert current["physical_claims_promoted"] == []
