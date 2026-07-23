"""Tests for the M9.6 scalar-carrier no-go and replacement contract."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.carrier_limits import (
    CURRENT_SCALAR,
    DIRAC_U1_TARGET,
    centered_current,
    global_phase_transform,
    replacement_carrier_contract,
    run_scalar_carrier_audit,
    scalar_contraction,
    scalar_density,
    scalar_rotation_character,
    spin_half_rotation_character,
)


def test_global_phase_does_not_change_scalar_density() -> None:
    state = np.asarray([1.0 + 2.0j, -0.5j], dtype=np.complex128)
    transformed = global_phase_transform(state, 0.71)
    assert np.max(np.abs(scalar_density(transformed) - scalar_density(state))) <= 1.0e-15


def test_conjugation_reverses_probability_current() -> None:
    x = np.linspace(-5.0, 5.0, 1000, endpoint=False)
    dx = x[1] - x[0]
    state = np.exp(-x**2) * np.exp(0.8j * x)
    current = centered_current(state, dx)
    conjugate_current = centered_current(np.conj(state), dx)
    assert np.max(np.abs(current + conjugate_current)) <= 1.0e-14


def test_scalar_configuration_has_explicit_contraction_to_zero() -> None:
    state = np.asarray([1.0 + 1.0j, 2.0 - 0.5j], dtype=np.complex128)
    assert np.array_equal(scalar_contraction(state, 0.0), state)
    assert np.array_equal(scalar_contraction(state, 1.0), np.zeros_like(state))
    with pytest.raises(ValueError, match="must lie in"):
        scalar_contraction(state, -0.1)


def test_scalar_and_spinor_two_pi_characters_differ() -> None:
    assert scalar_rotation_character(2.0 * math.pi) == pytest.approx(1.0 + 0.0j)
    assert spin_half_rotation_character(2.0 * math.pi) == pytest.approx(-1.0 + 0.0j)
    assert spin_half_rotation_character(4.0 * math.pi) == pytest.approx(1.0 + 0.0j)


def test_current_scalar_capability_record_exposes_missing_structures() -> None:
    assert CURRENT_SCALAR.complex_components == 1
    assert CURRENT_SCALAR.local_u1_connection is False
    assert CURRENT_SCALAR.gauss_law_flux is False
    assert CURRENT_SCALAR.opposite_charge_sector is False
    assert CURRENT_SCALAR.intrinsic_spin_half is False


def test_dirac_u1_target_has_required_charge_and_spin_structures() -> None:
    assert DIRAC_U1_TARGET.complex_components == 4
    assert DIRAC_U1_TARGET.local_u1_connection is True
    assert DIRAC_U1_TARGET.gauss_law_flux is True
    assert DIRAC_U1_TARGET.opposite_charge_sector is True
    assert DIRAC_U1_TARGET.intrinsic_spin_half is True
    assert DIRAC_U1_TARGET.two_pi_character_real == -1.0


def test_replacement_contract_preserves_cat_ept_density_interface() -> None:
    contract = replacement_carrier_contract()
    assert contract["target_carrier"]["cat_ept_positive_density"] is True
    assert "positive density psi-dagger psi" in contract["requirements"]["cat_ept_compatibility"]
    assert len(contract["staged_path"]) == 3


def test_complete_scalar_carrier_audit_passes() -> None:
    result = run_scalar_carrier_audit()
    assert result["passed"] is True
    assert all(result["checks"].values())
