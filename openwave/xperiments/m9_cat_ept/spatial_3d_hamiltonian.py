"""Hamiltonian, energy, and constraint helpers for the M9 3D engine."""

from __future__ import annotations

import math
import numpy as np

from .spatial_3d_types import ALPHAS, BETA, ComplexArray, RealArray, Spatial3DParameters
from .spatial_3d_operators import (
    apply_matrix, beta_expectation, curl, density, derivative, divergence,
    signed_charge_density, currents,
)

Vector = tuple[RealArray, RealArray, RealArray]

def _spinor_derivatives(
    state: ComplexArray,
    spacings: tuple[float, float, float],
) -> tuple[ComplexArray, ComplexArray, ComplexArray]:
    return tuple(
        np.asarray(derivative(state, axis + 1, spacings[axis]), dtype=np.complex128)
        for axis in range(3)
    )  # type: ignore[return-value]


def hamiltonian_action(
    state: ComplexArray,
    charge_sign: float,
    vector_potential: Vector,
    parameters: Spatial3DParameters,
    spacings: tuple[float, float, float],
) -> ComplexArray:
    derivatives = _spinor_derivatives(state, spacings)
    result = np.zeros_like(state)
    signed_charge = charge_sign * parameters.gauge_charge
    for axis, alpha in enumerate(ALPHAS):
        result += -1j * apply_matrix(alpha, derivatives[axis])
        result += -signed_charge * vector_potential[axis] * apply_matrix(alpha, state)
    scalar = beta_expectation(state)
    effective_mass = parameters.mass - parameters.soler_coupling * scalar
    result += effective_mass * apply_matrix(BETA, state)
    return np.asarray(result, dtype=np.complex128)


def _rhs(
    plus: ComplexArray,
    minus: ComplexArray,
    vector_potential: Vector,
    electric_field: Vector,
    absorber_charge: RealArray,
    sigma: RealArray,
    parameters: Spatial3DParameters,
    spacings: tuple[float, float, float],
    cell_volume: float,
    matter_enabled: bool,
) -> tuple[
    ComplexArray,
    ComplexArray,
    Vector,
    Vector,
    RealArray,
    float,
]:
    if matter_enabled:
        dplus = -1j * hamiltonian_action(
            plus, 1.0, vector_potential, parameters, spacings
        )
        dminus = -1j * hamiltonian_action(
            minus, -1.0, vector_potential, parameters, spacings
        )
        current = currents(plus, minus, parameters)
    else:
        dplus = np.zeros_like(plus)
        dminus = np.zeros_like(minus)
        current = tuple(np.zeros_like(electric_field[0]) for _ in range(3))
    magnetic_field = curl(vector_potential, spacings)
    magnetic_curl = curl(magnetic_field, spacings)
    dvector = tuple(-component for component in electric_field)
    delectric = tuple(
        np.asarray(
            magnetic_curl[axis] - current[axis] - sigma * electric_field[axis],
            dtype=np.float64,
        )
        for axis in range(3)
    )
    weighted_field = tuple(sigma * component for component in electric_field)
    dabsorber_charge = -divergence(weighted_field, spacings)
    loss_rate = cell_volume * float(
        np.sum(sigma * sum(component**2 for component in electric_field))
    )
    return (
        np.asarray(dplus),
        np.asarray(dminus),
        dvector,  # type: ignore[arg-type]
        delectric,  # type: ignore[arg-type]
        np.asarray(dabsorber_charge),
        loss_rate,
    )


def _state_add(
    state: tuple[ComplexArray, ComplexArray, Vector, Vector, RealArray],
    factor: float,
    derivative_values,
):
    plus, minus, vector_potential, electric_field, absorber_charge = state
    dplus, dminus, dvector, delectric, dcharge, _ = derivative_values
    return (
        plus + factor * dplus,
        minus + factor * dminus,
        tuple(vector_potential[i] + factor * dvector[i] for i in range(3)),
        tuple(electric_field[i] + factor * delectric[i] for i in range(3)),
        absorber_charge + factor * dcharge,
    )


def total_norm(plus: ComplexArray, minus: ComplexArray, cell_volume: float) -> float:
    return cell_volume * float(np.sum(density(plus) + density(minus)))


def field_energy(
    vector_potential: Vector,
    electric_field: Vector,
    spacings: tuple[float, float, float],
    cell_volume: float,
) -> float:
    magnetic_field = curl(vector_potential, spacings)
    energy_density = sum(component**2 for component in electric_field)
    energy_density += sum(component**2 for component in magnetic_field)
    return 0.5 * cell_volume * float(np.sum(energy_density))


def matter_energy(
    plus: ComplexArray,
    minus: ComplexArray,
    vector_potential: Vector,
    parameters: Spatial3DParameters,
    spacings: tuple[float, float, float],
    cell_volume: float,
) -> float:
    value = 0.0
    for state, sign in ((plus, 1.0), (minus, -1.0)):
        linear_parameters = Spatial3DParameters(
            mass=parameters.mass,
            gauge_charge=parameters.gauge_charge,
            packet_width=parameters.packet_width,
            offset_x=parameters.offset_x,
            offset_y=parameters.offset_y,
            offset_z=parameters.offset_z,
            momentum_x=parameters.momentum_x,
            momentum_y=parameters.momentum_y,
            momentum_z=parameters.momentum_z,
            gauge_seed_amplitude=parameters.gauge_seed_amplitude,
            gauge_seed_width=parameters.gauge_seed_width,
            soler_coupling=0.0,
            total_norm=parameters.total_norm,
        )
        action = hamiltonian_action(
            state, sign, vector_potential, linear_parameters, spacings
        )
        value += cell_volume * float(np.real(np.sum(np.conj(state) * action)))
        if parameters.soler_coupling:
            scalar = beta_expectation(state)
            value -= 0.5 * parameters.soler_coupling * cell_volume * float(
                np.sum(scalar**2)
            )
    return value


def gauss_metrics(
    electric_field: Vector,
    plus: ComplexArray,
    minus: ComplexArray,
    absorber_charge: RealArray,
    parameters: Spatial3DParameters,
    spacings: tuple[float, float, float],
) -> tuple[float, float, float]:
    matter_charge = signed_charge_density(plus, minus, parameters)
    total_charge = matter_charge + absorber_charge
    residual = divergence(electric_field, spacings) - total_charge
    absolute = float(np.max(np.abs(residual)))
    scale = max(float(np.max(np.abs(total_charge))), 1.0e-12)
    return absolute, absolute / scale, float(np.mean(residual))


def packet_moments(
    x: RealArray,
    y: RealArray,
    z: RealArray,
    state: ComplexArray,
    cell_volume: float,
) -> tuple[float, float, float, float]:
    probability = density(state)
    norm = cell_volume * float(np.sum(probability))
    if norm <= 0.0:
        return 0.0, 0.0, 0.0, 0.0
    cx = cell_volume * float(np.sum(x * probability)) / norm
    cy = cell_volume * float(np.sum(y * probability)) / norm
    cz = cell_volume * float(np.sum(z * probability)) / norm
    rms = math.sqrt(
        cell_volume
        * float(np.sum(((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2) * probability))
        / norm
    )
    return cx, cy, cz, rms
