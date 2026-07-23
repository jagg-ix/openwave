"""M9.10 bounded two-dimensional transported Maxwell--Dirac qualification."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class Planar2DParameters:
    mass: float = 1.0
    gauge_charge: float = 0.20
    packet_width: float = 2.2
    packet_offset_x: float = 5.0
    packet_offset_y: float = 2.0
    momentum_x: float = 0.95
    momentum_y: float = 0.35
    gauge_seed_amplitude: float = 0.006
    gauge_seed_width: float = 4.0
    soler_coupling: float = 0.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.gauge_charge < 0.0:
            raise ValueError("gauge_charge must be nonnegative")
        if self.packet_width <= 0.0 or self.gauge_seed_width <= 0.0:
            raise ValueError("widths must be positive")
        if self.packet_offset_x <= 0.0:
            raise ValueError("packet_offset_x must be positive")
        if self.soler_coupling < 0.0:
            raise ValueError("soler_coupling must be nonnegative")


@dataclass(frozen=True)
class Planar2DGrid:
    half_width_x: float = 18.0
    half_width_y: float = 18.0
    points_x: int = 64
    points_y: int = 64
    final_time: float = 4.0
    dt_over_spacing: float = 0.055
    absorber_fraction: float = 0.18
    absorber_strength: float = 0.30
    samples: int = 41

    def __post_init__(self) -> None:
        if self.half_width_x <= 0.0 or self.half_width_y <= 0.0:
            raise ValueError("half widths must be positive")
        if self.points_x < 16 or self.points_y < 16:
            raise ValueError("grid dimensions must be at least 16")
        if self.points_x % 2 or self.points_y % 2:
            raise ValueError("grid dimensions must be even")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_spacing <= 0.12:
            raise ValueError("dt_over_spacing must lie in (0, 0.12]")
        if not 0.05 <= self.absorber_fraction <= 0.30:
            raise ValueError("absorber_fraction must lie in [0.05, 0.30]")
        if self.absorber_strength < 0.0:
            raise ValueError("absorber_strength must be nonnegative")
        if self.samples < 2:
            raise ValueError("samples must be at least two")


@dataclass
class Planar2DRun:
    x: RealArray
    y: RealArray
    dx: float
    dy: float
    dt: float
    steps: int
    parameters: Planar2DParameters
    grid: Planar2DGrid
    initial_plus: ComplexArray
    initial_minus: ComplexArray
    final_plus: ComplexArray
    final_minus: ComplexArray
    initial_ax: RealArray
    initial_ay: RealArray
    initial_ex: RealArray
    initial_ey: RealArray
    final_ax: RealArray
    final_ay: RealArray
    final_ex: RealArray
    final_ey: RealArray
    initial_absorber_charge: RealArray
    final_absorber_charge: RealArray
    absorbed_energy: float
    emitted_energy: float
    records: tuple[dict[str, float], ...]


def planar_grid(grid: Planar2DGrid) -> tuple[RealArray, RealArray, float, float]:
    dx = 2.0 * grid.half_width_x / grid.points_x
    dy = 2.0 * grid.half_width_y / grid.points_y
    x = -grid.half_width_x + dx * np.arange(grid.points_x, dtype=np.float64)
    y = -grid.half_width_y + dy * np.arange(grid.points_y, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    return xx, yy, dx, dy


def wave_numbers(grid: Planar2DGrid, dx: float, dy: float) -> tuple[RealArray, RealArray]:
    kx = 2.0 * math.pi * np.fft.fftfreq(grid.points_x, d=dx)
    ky = 2.0 * math.pi * np.fft.fftfreq(grid.points_y, d=dy)
    return np.meshgrid(kx, ky)


def derivative_x(values, kx: RealArray):
    return np.fft.ifft2(1j * kx * np.fft.fft2(values, axes=(-2, -1)), axes=(-2, -1))


def derivative_y(values, ky: RealArray):
    return np.fft.ifft2(1j * ky * np.fft.fft2(values, axes=(-2, -1)), axes=(-2, -1))


def absorber_profile(xx: RealArray, yy: RealArray, grid: Planar2DGrid) -> RealArray:
    start_x = grid.half_width_x * (1.0 - grid.absorber_fraction)
    start_y = grid.half_width_y * (1.0 - grid.absorber_fraction)
    scaled_x = np.clip(
        (np.abs(xx) - start_x) / (grid.half_width_x - start_x),
        0.0,
        1.0,
    )
    scaled_y = np.clip(
        (np.abs(yy) - start_y) / (grid.half_width_y - start_y),
        0.0,
        1.0,
    )
    return grid.absorber_strength * (scaled_x**4 + scaled_y**4)


def density(state: ComplexArray) -> RealArray:
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def pauli_expectations(state: ComplexArray) -> tuple[RealArray, RealArray, RealArray]:
    upper, lower = state
    sx = 2.0 * np.real(np.conj(upper) * lower)
    sy = 2.0 * np.imag(np.conj(upper) * lower)
    sz = np.abs(upper) ** 2 - np.abs(lower) ** 2
    return np.asarray(sx), np.asarray(sy), np.asarray(sz)


def positive_energy_spinor(px: float, py: float, mass: float) -> ComplexArray:
    energy = math.sqrt(mass**2 + px**2 + py**2)
    vector = np.asarray([energy + mass, px + 1j * py], dtype=np.complex128)
    return vector / np.linalg.norm(vector)


def gaussian_packet(
    xx: RealArray,
    yy: RealArray,
    center_x: float,
    center_y: float,
    px: float,
    py: float,
    width: float,
    mass: float,
    norm: float,
    cell_area: float,
) -> ComplexArray:
    envelope = np.exp(
        -0.5 * (((xx - center_x) / width) ** 2 + ((yy - center_y) / width) ** 2)
    )
    phase = np.exp(1j * (px * xx + py * yy))
    state = positive_energy_spinor(px, py, mass)[:, None, None] * envelope * phase
    scale = math.sqrt(norm / (cell_area * float(np.sum(density(state)))))
    return np.asarray(scale * state, dtype=np.complex128)


def signed_charge_density(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: Planar2DParameters,
) -> RealArray:
    return parameters.gauge_charge * (density(plus) - density(minus))


def currents(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: Planar2DParameters,
) -> tuple[RealArray, RealArray]:
    plus_x, plus_y, _ = pauli_expectations(plus)
    minus_x, minus_y, _ = pauli_expectations(minus)
    q = parameters.gauge_charge
    return q * (plus_x - minus_x), q * (plus_y - minus_y)


def longitudinal_field_from_charge(
    charge: RealArray,
    kx: RealArray,
    ky: RealArray,
) -> tuple[RealArray, RealArray]:
    charge_hat = np.fft.fft2(charge - np.mean(charge))
    k2 = kx**2 + ky**2
    potential_hat = np.zeros_like(charge_hat)
    nonzero = k2 > 1.0e-14
    potential_hat[nonzero] = charge_hat[nonzero] / k2[nonzero]
    ex = np.real(np.fft.ifft2(-1j * kx * potential_hat))
    ey = np.real(np.fft.ifft2(-1j * ky * potential_hat))
    return np.asarray(ex), np.asarray(ey)


def initial_state(
    parameters: Planar2DParameters,
    grid: Planar2DGrid,
) -> tuple[
    RealArray,
    RealArray,
    float,
    float,
    ComplexArray,
    ComplexArray,
    RealArray,
    RealArray,
    RealArray,
    RealArray,
]:
    xx, yy, dx, dy = planar_grid(grid)
    area = dx * dy
    plus = gaussian_packet(
        xx,
        yy,
        -parameters.packet_offset_x,
        -parameters.packet_offset_y,
        parameters.momentum_x,
        parameters.momentum_y,
        parameters.packet_width,
        parameters.mass,
        0.5,
        area,
    )
    minus = gaussian_packet(
        xx,
        yy,
        parameters.packet_offset_x,
        parameters.packet_offset_y,
        -parameters.momentum_x,
        -0.65 * parameters.momentum_y,
        parameters.packet_width,
        parameters.mass,
        0.5,
        area,
    )
    kx, ky = wave_numbers(grid, dx, dy)
    ex, ey_longitudinal = longitudinal_field_from_charge(
        signed_charge_density(plus, minus, parameters),
        kx,
        ky,
    )
    radius2 = xx**2 + yy**2
    seed = parameters.gauge_seed_amplitude * np.exp(
        -radius2 / parameters.gauge_seed_width**2
    )
    ax = -yy / parameters.gauge_seed_width * seed
    ay = xx / parameters.gauge_seed_width * seed
    ey = ey_longitudinal
    return xx, yy, dx, dy, plus, minus, ax, ay, ex, ey
