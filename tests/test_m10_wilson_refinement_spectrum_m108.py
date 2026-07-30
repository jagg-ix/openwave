from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.wilson_refinement_spectrum_m108 import (
    WilsonRefinementSpectrumConfig,
    loop_ensemble,
    refinement_diagnostics,
    run_wilson_refinement_spectrum_study,
)


def test_nested_smooth_plaquettes_refine() -> None:
    cfg = WilsonRefinementSpectrumConfig()
    result = refinement_diagnostics(cfg.refinement_sizes, cfg.amplitude)
    actions = np.asarray(result["actions"], dtype=np.float64)
    orders = np.asarray(result["observed_orders"], dtype=np.float64)
    assert np.all(np.diff(actions) < 0.0)
    assert np.min(orders) >= 2.90
    assert result["last_scaled_relative_change"] <= 0.12


def test_wilson_loop_ensemble_is_finite_and_physical() -> None:
    cfg = WilsonRefinementSpectrumConfig()
    loops, polyakov, actions = loop_ensemble(
        cfg.ensemble_size,
        cfg.samples,
        cfg.maximum_extent,
        cfg.amplitude,
    )
    assert loops.shape == (8, 3, 3)
    assert np.all(np.isfinite(loops))
    assert np.all(loops > 0.0)
    assert np.all(loops <= 1.0 + 1.0e-12)
    assert np.max(np.abs(polyakov)) <= 1.0 + 1.0e-12
    assert np.all(actions >= 0.0)


def test_complete_m10_8_refinement_spectrum_study_passes() -> None:
    result = run_wilson_refinement_spectrum_study()
    assert result["passed"]
    assert min(result["refinement"]["observed_orders"]) >= 2.90
    assert result["area_perimeter_fit"]["area_coefficient"] > 0.0
    assert result["area_perimeter_fit"]["perimeter_coefficient"] > 0.0
    assert result["area_perimeter_fit"]["rms_residual"] <= 3.0e-3
    assert result["creutz_11"] > 0.0
    assert result["loop_gauge_error"] <= 2.0e-12
    assert result["weak_spectrum"]["minimum_eigenvalue"] >= -2.0e-12
    assert result["strong_spectrum"]["minimum_eigenvalue"] >= -2.0e-12
    assert (
        result["strong_spectrum"]["offdiag_frobenius"]
        < result["weak_spectrum"]["offdiag_frobenius"]
    )
    assert result["decision"]["wilson_loop_refinement_campaign_is_constructed"]
    assert result["decision"]["positive_environment_decoherence_spectrum_is_resolved"]
