"""Spatial operators and packet primitives for the M9 3D engine."""

from __future__ import annotations

import math
import numpy as np

from .spatial_3d_types import (
    ALPHAS, BETA, ComplexArray, RealArray, Spatial3DGrid, Spatial3DParameters,
    _SIGMA_X, _SIGMA_Y, _SIGMA_Z,
)

def periodic_mesh(grid: Spatial3DGrid) -> tuple[RealArray, RealArray, RealArray, float, float, float]:
    dx = 2.0 * grid.half_width_x / grid.points_x
    dy = 2.0 * grid.half_width_y / grid.points_y
    dz = 2.0 * grid.half_width_z / grid.points_z
    x1 = -grid.half_width_x + dx * np.arange(grid.points_x, dtype=np.float64)
    y1 = -grid.half_width_y + dy * np.arange(grid.points_y, dtype=np.float64)
    z1 = -grid.half_width_z + dz * np.arange(grid.points_z, dtype=np.float64)
    x, y, z = np.meshgrid(x1, y1, z1, indexing="ij")
    return x, y, z, dx, dy, dz


def derivative(values, axis: int, spacing: float):
    return (np.roll(values, -1, axis=axis) - np.roll(values, 1, axis=axis)) / (2.0 * spacing)


def gradient(values: RealArray, spacings: tuple[float, float, float]) -> tuple[RealArray, RealArray, RealArray]:
    return tuple(np.asarray(derivative(values, axis, spacings[axis]), dtype=np.float64) for axis in range(3))  # type: ignore[return-value]


def divergence(vector: tuple[RealArray, RealArray, RealArray], spacings: tuple[float, float, float]) -> RealArray:
    return np.asarray(sum(derivative(vector[axis], axis, spacings[axis]) for axis in range(3)), dtype=np.float64)


def curl(vector: tuple[RealArray, RealArray, RealArray], spacings: tuple[float, float, float]) -> tuple[RealArray, RealArray, RealArray]:
    x, y, z = vector
    dx, dy, dz = spacings
    return (
        np.asarray(derivative(z, 1, dy) - derivative(y, 2, dz), dtype=np.float64),
        np.asarray(derivative(x, 2, dz) - derivative(z, 0, dx), dtype=np.float64),
        np.asarray(derivative(y, 0, dx) - derivative(x, 1, dy), dtype=np.float64),
    )


def apply_matrix(matrix: ComplexArray, state: ComplexArray) -> ComplexArray:
    return np.asarray(np.einsum("ab,bxyz->axyz", matrix, state, optimize=True), dtype=np.complex128)


def density(state: ComplexArray) -> RealArray:
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def expectation(state: ComplexArray, matrix: ComplexArray) -> RealArray:
    operated = apply_matrix(matrix, state)
    return np.asarray(np.real(np.sum(np.conj(state) * operated, axis=0)), dtype=np.float64)


def current_expectations(state: ComplexArray) -> tuple[RealArray, RealArray, RealArray]:
    return tuple(expectation(state, matrix) for matrix in ALPHAS)  # type: ignore[return-value]


def beta_expectation(state: ComplexArray) -> RealArray:
    return expectation(state, BETA)


def positive_energy_spinor(momentum: tuple[float, float, float], mass: float) -> ComplexArray:
    px, py, pz = momentum
    energy = math.sqrt(mass**2 + px**2 + py**2 + pz**2)
    chi = np.asarray([1.0, 0.0], dtype=np.complex128)
    sigma_dot_p = px * _SIGMA_X + py * _SIGMA_Y + pz * _SIGMA_Z
    lower = sigma_dot_p @ chi / (energy + mass)
    vector = np.concatenate((chi, lower))
    return np.asarray(vector / np.linalg.norm(vector), dtype=np.complex128)


def gaussian_packet(
    x: RealArray,
    y: RealArray,
    z: RealArray,
    center: tuple[float, float, float],
    momentum: tuple[float, float, float],
    width: float,
    mass: float,
    norm: float,
    cell_volume: float,
) -> ComplexArray:
    cx, cy, cz = center
    px, py, pz = momentum
    radius2 = (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2
    envelope = np.exp(-0.5 * radius2 / width**2)
    phase = np.exp(1j * (px * x + py * y + pz * z))
    spinor = positive_energy_spinor(momentum, mass)[:, None, None, None]
    state = spinor * envelope[None, ...] * phase[None, ...]
    scale = math.sqrt(norm / (cell_volume * float(np.sum(density(state)))))
    return np.asarray(scale * state, dtype=np.complex128)


def signed_charge_density(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: Spatial3DParameters,
) -> RealArray:
    return np.asarray(parameters.gauge_charge * (density(plus) - density(minus)), dtype=np.float64)


def currents(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: Spatial3DParameters,
) -> tuple[RealArray, RealArray, RealArray]:
    plus_values = current_expectations(plus)
    minus_values = current_expectations(minus)
    q = parameters.gauge_charge
    return tuple(np.asarray(q * (plus_values[i] - minus_values[i]), dtype=np.float64) for i in range(3))  # type: ignore[return-value]


def absorber_profile(x: RealArray, y: RealArray, z: RealArray, grid: Spatial3DGrid) -> RealArray:
    starts = (
        grid.half_width_x * (1.0 - grid.absorber_fraction),
        grid.half_width_y * (1.0 - grid.absorber_fraction),
        grid.half_width_z * (1.0 - grid.absorber_fraction),
    )
    widths = (
        grid.half_width_x - starts[0],
        grid.half_width_y - starts[1],
        grid.half_width_z - starts[2],
    )
    scaled = [
        np.clip((np.abs(values) - starts[i]) / widths[i], 0.0, 1.0)
        for i, values in enumerate((x, y, z))
    ]
    edge = np.maximum.reduce(scaled)
    return np.asarray(grid.absorber_strength * edge**4, dtype=np.float64)


def longitudinal_field_from_charge(
    charge: RealArray,
    spacings: tuple[float, float, float],
) -> tuple[RealArray, RealArray, RealArray]:
    shape = charge.shape
    symbols: list[RealArray] = []
    for count, spacing in zip(shape, spacings, strict=True):
        wave_numbers = 2.0 * math.pi * np.fft.fftfreq(count, d=spacing)
        symbols.append(np.sin(wave_numbers * spacing) / spacing)
    sx, sy, sz = np.meshgrid(*symbols, indexing="ij")
    denominator = sx**2 + sy**2 + sz**2
    source_hat = np.fft.fftn(charge - np.mean(charge))
    fields = []
    active = denominator > 1.0e-14
    for symbol in (sx, sy, sz):
        field_hat = np.zeros(shape, dtype=np.complex128)
        field_hat[active] = -1j * symbol[active] * source_hat[active] / denominator[active]
        fields.append(np.asarray(np.real(np.fft.ifftn(field_hat)), dtype=np.float64))
    return tuple(fields)  # type: ignore[return-value]
