import numpy as np

from openwave.xperiments.m9_cat_ept.dirac_ehrenfest_diagnostics import (
    center_velocity_alpha_diagnostic,
    interaction_velocity_diagnostic,
    linear_rate,
)


def _records(center_velocity: float, alpha_velocity: float):
    times = (0.0, 0.1, 0.2, 0.3)
    return [
        {
            "time": time,
            "plus_center": [0.0, 0.0, center_velocity * time],
            "plus_velocity": [0.0, 0.0, alpha_velocity],
        }
        for time in times
    ]


def test_linear_rate_recovers_exact_slope():
    times = np.asarray([0.0, 0.1, 0.2, 0.3])
    values = 2.5 * times - 0.4
    assert abs(linear_rate(times, values) - 2.5) < 1e-12


def test_center_velocity_is_compared_with_alpha_velocity():
    result = center_velocity_alpha_diagnostic(_records(0.25, 0.25))
    assert result["relative_error_mean"] < 1e-12
    assert result["relative_error_midpoint"] < 1e-12


def test_interaction_subtraction_preserves_exact_relation():
    pair = _records(0.30, 0.30)
    control = _records(0.10, 0.10)
    result = interaction_velocity_diagnostic(pair, control)
    assert abs(result["interaction_center_velocity"] - 0.20) < 1e-12
    assert abs(result["interaction_alpha_velocity"] - 0.20) < 1e-12
    assert result["relative_error"] < 1e-12
