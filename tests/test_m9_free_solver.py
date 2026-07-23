"""Tests for the M9.2 free Schrödinger solver and refinement gate."""

from __future__ import annotations

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.free_solver import (
    GaussianPacket,
    SolverConfig,
    analytic_gaussian_state,
    benchmark_metrics,
    discrete_norm,
    evolve_free_packet,
    run_refinement_study,
)


def test_analytic_gaussian_is_normalized_on_wide_grid() -> None:
    config = SolverConfig(half_width=20.0, points=1024, final_time=0.0)
    run = evolve_free_packet(GaussianPacket(), config)
    assert discrete_norm(run.initial_state, run.dx) == pytest.approx(1.0, abs=1.0e-12)


def test_zero_time_returns_the_initial_state() -> None:
    config = SolverConfig(points=128, final_time=0.0)
    run = evolve_free_packet(GaussianPacket(), config)
    assert run.steps == 0
    assert run.dt == 0.0
    assert np.array_equal(run.initial_state, run.final_state)


def test_crank_nicolson_conserves_discrete_norm_and_energy() -> None:
    run = evolve_free_packet(GaussianPacket(), SolverConfig(points=256))
    metrics = benchmark_metrics(run)
    assert metrics.norm_drift <= 1.0e-12
    assert metrics.discrete_energy_drift <= 1.0e-12


def test_refinement_study_passes_frozen_acceptance_gate() -> None:
    result = run_refinement_study()
    assert result.passed is True
    assert all(result.acceptance.values())
    assert min(result.observed_orders["phase_aligned_l2"]) >= 1.8
    assert min(result.observed_orders["density_l1"]) >= 1.8
    assert min(result.observed_orders["current_relative_l2"]) >= 1.8


def test_refinement_errors_decrease_monotonically() -> None:
    result = run_refinement_study()
    for field in (
        "phase_aligned_l2_error",
        "density_l1_error",
        "current_relative_l2_error",
        "continuum_energy_relative_error",
    ):
        values = [float(level[field]) for level in result.levels]
        assert values == sorted(values, reverse=True)


def test_analytic_packet_translates_at_group_velocity() -> None:
    packet = GaussianPacket(center=-2.0, wave_number=1.25, mass=2.0, hbar=3.0)
    x = np.linspace(-20.0, 20.0, 20001)
    time = 0.75
    density = np.abs(analytic_gaussian_state(x, time, packet)) ** 2
    mean = np.trapezoid(x * density, x) / np.trapezoid(density, x)
    expected = packet.center + packet.group_velocity * time
    assert mean == pytest.approx(expected, abs=1.0e-10)


def test_invalid_solver_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="points must be at least 8"):
        SolverConfig(points=4)
    with pytest.raises(ValueError, match="sigma must be positive"):
        GaussianPacket(sigma=0.0)
