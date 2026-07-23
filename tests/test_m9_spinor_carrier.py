"""Tests for the M9.7a nonlinear Dirac/Soler spinor carrier gate."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.spinor_carrier import (
    SolerParameters,
    SpinorConfig,
    analytic_stationary_residual,
    covariant_energy,
    gauge_transform,
    periodic_grid,
    run_spinor_carrier_study,
    soler_profile,
    spinor_density,
    spinor_norm,
    spinor_probability,
)


def test_exact_profile_has_even_upper_and_odd_lower_components() -> None:
    x = np.linspace(-20.0, 20.0, 2001)
    profile = soler_profile(x)
    assert profile[0] == pytest.approx(profile[0, ::-1], abs=1.0e-14)
    assert profile[1] == pytest.approx(-profile[1, ::-1], abs=1.0e-14)


def test_exact_profile_closes_stationary_equation() -> None:
    x = np.linspace(-30.0, 30.0, 20001)
    assert analytic_stationary_residual(x) <= 1.0e-12


def test_pure_gauge_transform_preserves_density_norm_and_energy() -> None:
    parameters = SolerParameters()
    config = SpinorConfig(points=1024, final_time=0.0)
    x, dx = periodic_grid(config)
    state = soler_profile(x, parameters)
    wave_number = 2.0 * math.pi / (2.0 * config.half_width) * 2.0
    phase = 0.3 * np.sin(wave_number * x)
    gradient = 0.3 * wave_number * np.cos(wave_number * x)
    transformed = gauge_transform(state, phase, parameters)

    assert spinor_density(transformed) == pytest.approx(
        spinor_density(state), abs=1.0e-14
    )
    assert spinor_norm(transformed, dx) == pytest.approx(
        spinor_norm(state, dx), abs=1.0e-13
    )
    assert covariant_energy(
        transformed,
        dx,
        parameters,
        vector_potential=gradient,
    ) == pytest.approx(covariant_energy(state, dx, parameters), abs=1.0e-11)


def test_spinor_probability_preserves_entropic_clock_interface() -> None:
    config = SpinorConfig(points=512, final_time=0.0)
    x, dx = periodic_grid(config)
    probability = spinor_probability(soler_profile(x), dx)
    assert probability.ndim == 1
    assert probability.shape == (config.points,)
    assert float(np.sum(probability)) == pytest.approx(1.0, abs=1.0e-15)
    assert np.all(probability >= 0.0)


def test_full_spinor_gate_passes() -> None:
    result = run_spinor_carrier_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())
    assert min(result["refinement"]["phase_orders"]) >= 1.8
    assert min(result["refinement"]["density_orders"]) >= 1.8
    assert result["free_dirac_control"]["variance_ratio"] >= 2.0
    assert result["perturbation"]["core_fraction_r8"] >= 0.999


def test_scope_does_not_promote_background_connection_to_maxwell() -> None:
    result = run_spinor_carrier_study()
    status = result["gauge_covariance"]["status"]
    assert "background pure-gauge" in status
    assert "no dynamical Maxwell" in status
    assert "three-dimensional localization" in result["classification"][
        "does_not_establish"
    ]


def test_invalid_parameters_and_configurations_are_rejected() -> None:
    with pytest.raises(ValueError, match="frequency must lie"):
        SolerParameters(frequency=1.0)
    with pytest.raises(ValueError, match="even integer"):
        SpinorConfig(points=511)
    with pytest.raises(ValueError, match="nonnegative"):
        SpinorConfig(nonlinear_coupling=-1.0)
