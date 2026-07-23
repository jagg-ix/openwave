"""Tests for the M9.7b1 electrostatic gauge qualification gate."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.electrostatic_gauge_3d import (
    RadialGrid,
    RadialSpinorParameters,
    apply_reflecting_channel,
    boundary_flux,
    field_energy,
    gauss_shell_residuals,
    radial_clock_trajectory,
    run_electrostatic_gauge_study,
    shell_probability,
    solve_electrostatic_constraint,
    source_potential_energy,
    total_charge,
)


def test_exact_reference_formulas() -> None:
    parameters = RadialSpinorParameters()
    assert parameters.raw_norm == pytest.approx(math.pi * 1.75)
    assert parameters.exact_central_potential == pytest.approx(
        0.06252515621467317
    )
    assert parameters.exact_field_energy == pytest.approx(
        0.019301216292932542
    )


def test_finite_volume_gauss_and_flux_close() -> None:
    solution = solve_electrostatic_constraint(grid=RadialGrid(shells=1024))
    assert np.max(np.abs(gauss_shell_residuals(solution))) <= 1.0e-13
    assert boundary_flux(solution) == pytest.approx(
        total_charge(solution), abs=1.0e-13
    )
    assert field_energy(solution) == pytest.approx(
        source_potential_energy(solution), rel=5.0e-6
    )


def test_signed_charge_reverses_field_not_density() -> None:
    positive = solve_electrostatic_constraint()
    negative = solve_electrostatic_constraint(
        RadialSpinorParameters(gauge_charge=-1.0)
    )
    assert negative.number_density == pytest.approx(positive.number_density)
    assert negative.electric_field_edges == pytest.approx(
        -positive.electric_field_edges, abs=1.0e-14
    )
    assert negative.potential_edges == pytest.approx(
        -positive.potential_edges, abs=1.0e-14
    )
    assert field_energy(negative) == pytest.approx(field_energy(positive))


def test_reflecting_channel_preserves_uniform_probability() -> None:
    probability = np.full(64, 1.0 / 64.0)
    assert apply_reflecting_channel(probability) == pytest.approx(probability)


def test_radial_clock_contracts_remaining_information() -> None:
    solution = solve_electrostatic_constraint()
    trajectory = radial_clock_trajectory(shell_probability(solution))
    assert trajectory["remaining_nonincreasing"] is True
    assert trajectory["gain_nondecreasing"] is True
    assert trajectory["correlation_nonnegative"] is True
    assert trajectory["max_ledger_closure_error"] <= 1.0e-12


def test_full_electrostatic_gate_passes() -> None:
    result = run_electrostatic_gauge_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())
    assert min(result["observed_orders"]["field_energy"]) >= 1.8
    assert min(result["observed_orders"]["central_potential"]) >= 1.8


def test_invalid_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="length_scale must be positive"):
        RadialSpinorParameters(length_scale=0.0)
    with pytest.raises(ValueError, match="gauge_charge must be nonzero"):
        RadialSpinorParameters(gauge_charge=0.0)
    with pytest.raises(ValueError, match="shells must be at least 64"):
        RadialGrid(shells=32)
    with pytest.raises(ValueError, match="probability must sum to 1"):
        apply_reflecting_channel(np.asarray([0.2, 0.2]))
