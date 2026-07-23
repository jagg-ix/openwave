"""Core types and initialization for M9.17 reservoir accounting.

Two oppositely labelled 1+1D Dirac packets evolve under

    d psi_s/dt = -sigma_x d_x psi_s - i m sigma_z psi_s
                 - (kappa g(x)/2) psi_s,

while local reservoir densities satisfy

    d r_s/dt = kappa g(x) |psi_s|^2.

The extended probability and charge ledgers include matter plus reservoir.  The
model is a selected sink/reservoir interface; it is not a microscopic environment
or a derivation of CAT/EPT dynamics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]

SIGMA_X = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
SIGMA_Z = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


@dataclass(frozen=True)
class ReservoirParameters:
    mass: float = 1.0
    coupling: float = 0.12
    charge: float = 0.3
    packet_width: float = 2.4
    packet_offset: float = 6.0
    plus_momentum: float = 0.8
    minus_momentum: float = -0.65

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.coupling < 0.0:
            raise ValueError("coupling must be nonnegative")
        if self.packet_width <= 0.0:
            raise ValueError("packet_width must be positive")


@dataclass(frozen=True)
class ReservoirGrid:
    half_width: float = 20.0
    points: int = 256
    final_time: float = 6.0
    dt_over_dx: float = 0.06
    samples: int = 81

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 32 or self.points % 2:
            raise ValueError("points must be an even integer at least 32")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_dx <= 0.2:
            raise ValueError("dt_over_dx must lie in (0,0.2]")
        if self.samples < 2:
            raise ValueError("samples must be at least two")


@dataclass
class ReservoirRun:
    x: RealArray
    dx: float
    dt: float
    steps: int
    parameters: ReservoirParameters
    grid: ReservoirGrid
    initial_plus: ComplexArray
    initial_minus: ComplexArray
    final_plus: ComplexArray
    final_minus: ComplexArray
    final_reservoir_plus: RealArray
    final_reservoir_minus: RealArray
    records: tuple[dict[str, float], ...]


def periodic_grid(grid: ReservoirGrid) -> tuple[RealArray, float]:
    dx = 2.0 * grid.half_width / grid.points
    x = -grid.half_width + dx * np.arange(grid.points, dtype=np.float64)
    return x, dx


def spectral_derivative(values: NDArray, dx: float) -> NDArray:
    points = values.shape[-1]
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(points, d=dx)
    transformed = np.fft.fft(values, axis=-1)
    return np.fft.ifft(1j * wave_numbers * transformed, axis=-1)


def density(state: ComplexArray) -> RealArray:
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def current(state: ComplexArray) -> RealArray:
    return np.asarray(
        np.real(np.sum(np.conj(state) * (SIGMA_X @ state), axis=0)),
        dtype=np.float64,
    )


def positive_energy_spinor(momentum: float, mass: float) -> ComplexArray:
    energy = math.sqrt(momentum**2 + mass**2)
    vector = np.asarray([energy + mass, momentum], dtype=np.complex128)
    return vector / np.linalg.norm(vector)


def gaussian_packet(
    x: RealArray,
    *,
    center: float,
    momentum: float,
    width: float,
    mass: float,
    target_norm: float,
    dx: float,
) -> ComplexArray:
    envelope = np.exp(-0.5 * ((x - center) / width) ** 2)
    phase = np.exp(1j * momentum * x)
    state = positive_energy_spinor(momentum, mass)[:, None] * envelope[None, :] * phase[None, :]
    scale = math.sqrt(target_norm / (dx * float(np.sum(density(state)))))
    return np.asarray(scale * state, dtype=np.complex128)


def loss_profile(x: RealArray, half_width: float) -> RealArray:
    profile = 1.0 + 0.35 * np.cos(math.pi * x / half_width)
    return np.asarray(profile, dtype=np.float64)


def initial_state(
    parameters: ReservoirParameters,
    grid: ReservoirGrid,
) -> tuple[RealArray, float, ComplexArray, ComplexArray, RealArray, RealArray]:
    x, dx = periodic_grid(grid)
    plus = gaussian_packet(
        x,
        center=-parameters.packet_offset,
        momentum=parameters.plus_momentum,
        width=parameters.packet_width,
        mass=parameters.mass,
        target_norm=0.5,
        dx=dx,
    )
    minus = gaussian_packet(
        x,
        center=parameters.packet_offset,
        momentum=parameters.minus_momentum,
        width=parameters.packet_width,
        mass=parameters.mass,
        target_norm=0.5,
        dx=dx,
    )
    return x, dx, plus, minus, np.zeros_like(x), np.zeros_like(x)


