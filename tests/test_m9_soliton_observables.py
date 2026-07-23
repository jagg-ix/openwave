"""Tests for the M9.5 bright-soliton observable ledger."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.soliton_observables import (
    SolitonParameters,
    numerical_ledger,
    profile,
    run_observable_study,
    state,
)


def test_m9_4_member_is_recovered_exactly() -> None:
    parameters = SolitonParameters(coupling=2.0, norm=1.0)
    assert parameters.inverse_width == pytest.approx(1.0)
    assert parameters.amplitude == pytest.approx(1.0 / math.sqrt(2.0))
    assert parameters.chemical_potential == pytest.approx(-0.5)
    assert parameters.phase_frequency == pytest.approx(0.5)
    assert parameters.energy == pytest.approx(-1.0 / 6.0)


def test_profile_has_requested_norm_and_energy() -> None:
    ledger = numerical_ledger(SolitonParameters(coupling=3.0, norm=0.5))
    assert ledger.norm_error <= 1.0e-12
    assert ledger.energy_error <= 1.0e-12
    assert ledger.radius_error <= 1.0e-12
    assert ledger.numerical_stationary_residual <= 1.0e-12


def test_radius_scales_as_inverse_gN() -> None:
    first = SolitonParameters(coupling=1.0, norm=1.0)
    second = SolitonParameters(coupling=2.0, norm=1.0)
    third = SolitonParameters(coupling=1.0, norm=2.0)
    assert second.rms_radius == pytest.approx(first.rms_radius / 2.0)
    assert third.rms_radius == pytest.approx(first.rms_radius / 2.0)


def test_energy_and_frequency_are_not_independent() -> None:
    parameters = SolitonParameters(coupling=2.0, norm=1.5)
    assert parameters.phase_frequency == pytest.approx(
        parameters.inverse_width**2 / 2.0
    )
    assert parameters.chemical_potential == pytest.approx(
        -parameters.phase_frequency
    )
    assert parameters.energy == pytest.approx(
        parameters.chemical_potential * parameters.norm / 3.0
    )


def test_time_dependence_changes_only_global_phase() -> None:
    x = np.linspace(-10.0, 10.0, 1001)
    parameters = SolitonParameters()
    initial = profile(x, parameters)
    later = state(x, 2.5, parameters)
    assert np.abs(later) == pytest.approx(np.abs(initial), abs=1.0e-14)


def test_observable_study_passes() -> None:
    result = run_observable_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError, match="coupling must be positive"):
        SolitonParameters(coupling=0.0)
    with pytest.raises(ValueError, match="norm must be positive"):
        SolitonParameters(norm=0.0)
