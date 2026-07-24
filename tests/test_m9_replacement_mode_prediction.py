import numpy as np

from openwave.xperiments.m9_cat_ept.replacement_mode_prediction import (
    ReplacementModeConfig,
    fit_single_radial_mode,
    prediction_fingerprint,
    preregistration,
)


def test_frequency_fit_recovers_synthetic_radial_mode():
    cfg = ReplacementModeConfig(final_time=6.0, fit_start=0.0, frequency_samples=800)
    times = np.linspace(0.0, 6.0, 1201)
    omega = 1.37
    trace = {"times": times, "radii": 1.2 + 0.01 * np.cos(omega * times)}
    fit = fit_single_radial_mode(trace, cfg)
    assert abs(fit["omega_dimensionless"] - omega) < 0.01
    assert fit["rmse_to_amplitude"] < 1e-2


def test_preregistration_fingerprint_is_deterministic():
    cfg = ReplacementModeConfig()
    record = preregistration(cfg, 1.07)
    assert record["frozen_before_held_out_comparison"]
    assert not record["coefficients_refit_after_m9_68"]
    assert prediction_fingerprint(cfg, record) == prediction_fingerprint(cfg, record)
