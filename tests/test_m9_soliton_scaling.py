"""Tests for the M9.5 exact soliton scaling and clock ledger."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.soliton_scaling import (
    SolitonParameters,
    conditional_clock_bridge,
    run_scaling_study,
    soliton_state,
)


def test_reference_member_matches_m9_4_candidate() -> None:
    parameters = SolitonParameters()
    assert parameters.inverse_width == pytest.approx(1.0)
    assert parameters.amplitude == pytest.approx(1.0 / math.sqrt(2.0))
    assert parameters.chemical_potential == pytest.approx(-0.5)
    assert parameters.phase_frequency == pytest.approx(0.5)
    assert parameters.energy == pytest.approx(-1.0 / 6.0)


def test_exact_family_state_has_expected_phase_rotation() -> None:
    parameters = SolitonParameters(coupling=3.0, norm=1.25)
    x = np.linspace(-4.0, 4.0, 101)
    state0 = soliton_state(x, 0.0, parameters)
    state1 = soliton_state(x, 0.7, parameters)
    ratio = state1 / state0
    expected = np.exp(1j * parameters.phase_frequency * 0.7)
    assert np.max(np.abs(ratio - expected)) <= 1.0e-14


def test_radius_quantile_formula() -> None:
    parameters = SolitonParameters(coupling=2.0, norm=1.0)
    radius = parameters.enclosed_radius(0.9)
    assert math.tanh(parameters.inverse_width * radius) == pytest.approx(0.9)
    with pytest.raises(ValueError, match="strictly between"):
        parameters.enclosed_radius(1.0)


def test_scaling_study_passes_all_frozen_checks() -> None:
    result = run_scaling_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())


def test_scaling_exponents_are_exact() -> None:
    slopes = run_scaling_study()["observed_norm_scaling_slopes"]
    assert slopes["inverse_width_vs_norm"] == pytest.approx(1.0, abs=1.0e-12)
    assert slopes["phase_frequency_vs_norm"] == pytest.approx(2.0, abs=1.0e-12)
    assert slopes["absolute_energy_vs_norm"] == pytest.approx(3.0, abs=1.0e-12)
    assert slopes["rms_radius_vs_norm"] == pytest.approx(-1.0, abs=1.0e-12)


def test_phase_radius_product_is_scale_invariant() -> None:
    for coupling in (0.75, 2.0, 5.0):
        for norm in (0.4, 1.0, 2.5):
            parameters = SolitonParameters(coupling=coupling, norm=norm)
            product = parameters.phase_frequency * parameters.rms_radius**2
            assert product == pytest.approx(math.pi**2 / 24.0, abs=1.0e-14)


def test_clock_bridge_is_conditional_and_mass_free() -> None:
    bridge = conditional_clock_bridge(SolitonParameters())
    assert bridge["status"] == "conditional_identification_not_prediction"
    assert bridge["compton_hypothesis_Rrms_over_lambdaC"] == pytest.approx(
        math.pi / math.sqrt(24.0)
    )
    assert bridge["zitter_hypothesis_Rrms_over_lambdaC"] == pytest.approx(
        math.pi / math.sqrt(48.0)
    )


def test_invalid_family_parameters_are_rejected() -> None:
    with pytest.raises(ValueError, match="coupling must be positive"):
        SolitonParameters(coupling=0.0)
    with pytest.raises(ValueError, match="norm must be positive"):
        SolitonParameters(norm=-1.0)
