import math

import numpy as np

from openwave.xperiments.m9_cat_ept.independent_mode_robustness import (
    FROZEN_RATIO,
    IndependentModeRobustnessConfig,
    frozen_record,
    periodogram_mode,
    radial_amplitude_perturbation,
    robustness_fingerprint,
)


def test_radial_amplitude_perturbation_is_normalized():
    axis = np.linspace(-2.0, 2.0, 12, endpoint=False)
    dx = float(axis[1] - axis[0])
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    r2 = x * x + y * y + z * z
    state = np.exp(-r2).astype(np.complex128)
    state /= math.sqrt(float(np.sum(np.abs(state) ** 2) * dx**3))
    perturbed = radial_amplitude_perturbation(state, r2, dx, 0.015)
    assert abs(float(np.sum(np.abs(perturbed) ** 2) * dx**3) - 1.0) < 1e-12
    assert not np.allclose(perturbed, state)


def test_periodogram_recovers_synthetic_mode():
    cfg = IndependentModeRobustnessConfig()
    times = np.arange(0.0, 16.0, cfg.dt * cfg.sample_every)
    omega = FROZEN_RATIO * 2.0 * 0.65
    radii = 1.2 + 0.006 * np.cos(omega * times + 0.3) + 2e-5 * times
    result = periodogram_mode({"times": times, "radii": radii}, cfg)
    assert abs(result["omega_over_compton"] - FROZEN_RATIO) / FROZEN_RATIO < 2e-3
    assert result["peak_power_fraction"] > cfg.minimum_peak_power_fraction


def test_frozen_record_changes_neither_perturbation_nor_estimator():
    cfg = IndependentModeRobustnessConfig()
    record = frozen_record(cfg)
    assert record["dimensionless_ratio"] == FROZEN_RATIO
    assert record["coefficients_refit"] is False
    assert record["perturbation_reused_from_derivation"] is False
    assert record["estimator_reused_from_derivation"] is False
    assert len(robustness_fingerprint(cfg, record)) == 64
