"""Tests for the M9.6 scalar-carrier capability audit."""

from __future__ import annotations

import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.carrier_audit import (
    audit_scalar_carrier,
    conjugate_state,
    contraction_state,
    discrete_norm,
    global_phase_transform,
    local_phase_transform,
    probability_current,
    scalar_energy,
    scalar_rotation_factor,
    spinor_density,
    spinor_density_embedding,
    spinor_rotation_factor,
)


def _state() -> tuple[np.ndarray, np.ndarray, float]:
    x = np.linspace(-20.0, 20.0, 2048, endpoint=False)
    dx = x[1] - x[0]
    state = np.exp(-(x**2) / 2.0 + 0.7j * x).astype(np.complex128)
    return x, state, dx


def test_global_phase_preserves_norm_and_energy() -> None:
    _, state, dx = _state()
    transformed = global_phase_transform(state, 0.73)
    assert discrete_norm(transformed, dx) == pytest.approx(discrete_norm(state, dx))
    assert scalar_energy(transformed, dx) == pytest.approx(scalar_energy(state, dx))


def test_local_phase_is_not_a_symmetry_without_gauge_field() -> None:
    x, state, dx = _state()
    transformed = local_phase_transform(x, state, 1.25)
    assert discrete_norm(transformed, dx) == pytest.approx(discrete_norm(state, dx))
    assert abs(scalar_energy(transformed, dx) - scalar_energy(state, dx)) >= 1.0e-3


def test_conjugation_preserves_norm_energy_and_reverses_current() -> None:
    _, state, dx = _state()
    conjugate = conjugate_state(state)
    assert discrete_norm(conjugate, dx) == pytest.approx(discrete_norm(state, dx))
    assert scalar_energy(conjugate, dx) == pytest.approx(scalar_energy(state, dx))
    assert probability_current(conjugate, dx) == pytest.approx(
        -probability_current(state, dx), abs=1.0e-12
    )


def test_profile_contracts_continuously_to_zero_vacuum() -> None:
    _, state, dx = _state()
    norms = [
        discrete_norm(contraction_state(state, parameter), dx)
        for parameter in np.linspace(0.0, 1.0, 11)
    ]
    assert norms[0] == pytest.approx(0.0)
    assert norms[-1] == pytest.approx(discrete_norm(state, dx))
    assert norms == sorted(norms)


def test_scalar_rotation_is_trivial_but_spinor_is_double_covered() -> None:
    assert scalar_rotation_factor(2.0 * math.pi) == pytest.approx(1.0 + 0.0j)
    assert scalar_rotation_factor(4.0 * math.pi) == pytest.approx(1.0 + 0.0j)
    assert spinor_rotation_factor(2.0 * math.pi) == pytest.approx(-1.0 + 0.0j)
    assert spinor_rotation_factor(4.0 * math.pi) == pytest.approx(1.0 + 0.0j)


def test_spinor_embedding_preserves_density_interface() -> None:
    _, state, _ = _state()
    embedded = spinor_density_embedding(state)
    assert spinor_density(embedded) == pytest.approx(np.abs(state) ** 2)


def test_audit_passes_and_keeps_charge_distinction() -> None:
    result = audit_scalar_carrier()
    assert result["passed"] is True
    assert all(result["acceptance"].values())
    capabilities = {item["name"]: item for item in result["capabilities"]}
    assert capabilities["global_u1_phase_symmetry"]["present"] is True
    assert capabilities["electric_charge_derivation"]["present"] is False
    assert capabilities["intrinsic_spin_half_representation"]["present"] is False
    assert capabilities["topological_charge_certificate"]["present"] is False


def test_invalid_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="dx must be positive"):
        discrete_norm(np.ones(4, dtype=np.complex128), 0.0)
    with pytest.raises(ValueError, match="same shape"):
        local_phase_transform(
            np.ones(3, dtype=np.float64),
            np.ones(4, dtype=np.complex128),
            1.0,
        )
    with pytest.raises(ValueError, match="parameter must lie"):
        contraction_state(np.ones(4, dtype=np.complex128), 1.1)
    with pytest.raises(ValueError, match="shape"):
        spinor_density(np.ones((4, 3), dtype=np.complex128))
