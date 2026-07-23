"""Tests for the M9.6 scalar-carrier capability audit."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.carrier_audit import (
    audit_scalar_carrier,
    discrete_norm,
    global_phase_transform,
    local_phase_transform,
    scalar_rotation_factor,
    spectral_kinetic_energy,
    spinor_rotation_factor,
)


def test_global_phase_preserves_norm() -> None:
    x = np.linspace(-10.0, 10.0, 1024, endpoint=False)
    dx = x[1] - x[0]
    state = np.exp(-(x**2)).astype(np.complex128)
    transformed = global_phase_transform(state, 0.73)
    assert discrete_norm(transformed, dx) == pytest.approx(discrete_norm(state, dx))


def test_local_phase_is_not_a_symmetry_without_gauge_field() -> None:
    x = np.linspace(-20.0, 20.0, 2048, endpoint=False)
    dx = x[1] - x[0]
    state = np.exp(-(x**2) / 2.0).astype(np.complex128)
    transformed = local_phase_transform(x, state, 1.25)
    assert discrete_norm(transformed, dx) == pytest.approx(discrete_norm(state, dx))
    assert spectral_kinetic_energy(transformed, dx) > spectral_kinetic_energy(state, dx)


def test_scalar_rotation_is_trivial() -> None:
    assert scalar_rotation_factor(2.0 * math.pi) == pytest.approx(1.0 + 0.0j)
    assert scalar_rotation_factor(4.0 * math.pi) == pytest.approx(1.0 + 0.0j)


def test_spinor_reference_exposes_missing_double_cover() -> None:
    assert spinor_rotation_factor(2.0 * math.pi) == pytest.approx(-1.0 + 0.0j)
    assert spinor_rotation_factor(4.0 * math.pi) == pytest.approx(1.0 + 0.0j)


def test_audit_passes_and_keeps_charge_distinction() -> None:
    result = audit_scalar_carrier()
    assert result["passed"] is True
    capabilities = {item["name"]: item for item in result["capabilities"]}
    assert capabilities["global_u1_phase_symmetry"]["present"] is True
    assert capabilities["electric_charge_derivation"]["present"] is False
    assert capabilities["intrinsic_spin_half_representation"]["present"] is False


def test_invalid_grid_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="dx must be positive"):
        discrete_norm(np.ones(4, dtype=np.complex128), 0.0)
    with pytest.raises(ValueError, match="same shape"):
        local_phase_transform(
            np.ones(3, dtype=np.float64),
            np.ones(4, dtype=np.complex128),
            1.0,
        )
