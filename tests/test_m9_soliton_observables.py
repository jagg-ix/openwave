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
    assert parameters.eta == pytest.approx(1.0)
    assert parameters.amplitude == pytest.approx(1.0 / math.sqrt(2.0))
    assert parameters.chemical_potential == pytest.approx(-0.5)
    assert parameters.phase_frequency == pytest.approx(0.5)
    assert parameters.energy == pytest.approx(-1.0 / 6.0)
    assert parameters.rms_radius == pytest.approx(math.pi / (2.0 * math.sqrt(3.0)))


def test_profile_has_requested_norm_energy_radius_and_probabilities() -> None:
    ledger = numerical_ledger(SolitonParameters(coupling=3.0, norm=0.5))
    assert ledger.norm_relative_error <= 1.0e-10
    assert ledger.energy_relative_error <= 1.0e-10
    assert ledger.radius_relative_error <= 1.0e-10
    assert ledger.stationary_residual_relative_l2 <= 1.0e-12
    assert ledger.enclosed_probability_90_error <= 2.0e-3
    assert ledger.enclosed_probability_99_error <= 2.0e-3


def test_radius_scales_as_inverse_gN() -> None:
    first = SolitonParameters(coupling=1.0, norm=1.0)
    second = SolitonParameters(coupling=2.0, norm=1.0)
    third = SolitonParameters(coupling=1.0, norm=2.0)
    assert second.rms_radius == pytest.approx(first.rms_radius / 2.0)
    assert third.rms_radius == pytest.approx(first.rms_radius / 2.0)


def test_energy_frequency_and_radius_are_linked() -> None:
    parameters = SolitonParameters(coupling=2.0, norm=1.5)
    assert parameters.phase_frequency == pytest.approx(parameters.eta**2 / 2.0)
    assert parameters.chemical_potential == pytest.approx(
        -parameters.phase_frequency
    )
    assert parameters.energy == pytest.approx(
        parameters.chemical_potential * parameters.norm / 3.0
    )
    assert parameters.phase_frequency * parameters.rms_radius**2 == pytest.approx(
        math.pi**2 / 24.0
    )


def test_enclosed_probability_radius_is_exact() -> None:
    parameters = SolitonParameters(coupling=4.0, norm=2.0)
    for probability in (0.5, 0.9, 0.99):
        radius = parameters.radius_for_probability(probability)
        assert math.tanh(parameters.eta * radius) == pytest.approx(probability)


def test_time_dependence_changes_only_global_phase() -> None:
    x = np.linspace(-10.0, 10.0, 1001)
    parameters = SolitonParameters()
    initial = profile(x, parameters)
    later = state(x, 2.5, parameters)
    assert np.abs(later) == pytest.approx(np.abs(initial), abs=1.0e-14)


def test_observable_study_passes_nine_case_gate() -> None:
    result = run_observable_study()
    assert result["passed"] is True
    assert len(result["cases"]) == 9
    assert all(result["acceptance"].values())
    for name, target in result["scaling_targets"].items():
        assert result["scaling_exponents"][name] == pytest.approx(
            [target, target, target],
            abs=1.0e-12,
        )


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError, match="coupling must be positive"):
        SolitonParameters(coupling=0.0)
    with pytest.raises(ValueError, match="norm must be positive"):
        SolitonParameters(norm=0.0)
    with pytest.raises(ValueError, match="probability must lie"):
        SolitonParameters().radius_for_probability(1.0)
