"""M9.12 three-dimensional Dirac representation and numerical controls.

The module also provides the reusable bounded 3D evolution engine consumed by
M9.13 and M9.14. It is a selected dimensionless classical field model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math
from typing import Any, Final, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

_SIGMA_X: Final[ComplexArray] = np.asarray([[0, 1], [1, 0]], dtype=np.complex128)
_SIGMA_Y: Final[ComplexArray] = np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128)
_SIGMA_Z: Final[ComplexArray] = np.asarray([[1, 0], [0, -1]], dtype=np.complex128)
_ZERO_2: Final[ComplexArray] = np.zeros((2, 2), dtype=np.complex128)
_ID_2: Final[ComplexArray] = np.eye(2, dtype=np.complex128)

ALPHA_X: Final[ComplexArray] = np.block([[_ZERO_2, _SIGMA_X], [_SIGMA_X, _ZERO_2]])
ALPHA_Y: Final[ComplexArray] = np.block([[_ZERO_2, _SIGMA_Y], [_SIGMA_Y, _ZERO_2]])
ALPHA_Z: Final[ComplexArray] = np.block([[_ZERO_2, _SIGMA_Z], [_SIGMA_Z, _ZERO_2]])
BETA: Final[ComplexArray] = np.block([[_ID_2, _ZERO_2], [_ZERO_2, -_ID_2]])
ALPHAS: Final[tuple[ComplexArray, ComplexArray, ComplexArray]] = (
    ALPHA_X,
    ALPHA_Y,
    ALPHA_Z,
)


@dataclass(frozen=True)
class Spatial3DParameters:
    mass: float = 1.0
    gauge_charge: float = 0.15
    packet_width: float = 1.8
    offset_x: float = 4.0
    offset_y: float = 1.5
    offset_z: float = 0.75
    momentum_x: float = 0.80
    momentum_y: float = 0.25
    momentum_z: float = 0.15
    gauge_seed_amplitude: float = 0.004
    gauge_seed_width: float = 3.5
    soler_coupling: float = 0.0
    total_norm: float = 1.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.gauge_charge < 0.0:
            raise ValueError("gauge_charge must be nonnegative")
        if self.packet_width <= 0.0 or self.gauge_seed_width <= 0.0:
            raise ValueError("widths must be positive")
        if min(self.offset_x, self.offset_y, self.offset_z) < 0.0:
            raise ValueError("packet offsets must be nonnegative")
        if self.soler_coupling < 0.0:
            raise ValueError("soler_coupling must be nonnegative")
        if self.total_norm <= 0.0:
            raise ValueError("total_norm must be positive")


@dataclass(frozen=True)
class Spatial3DGrid:
    half_width_x: float = 12.0
    half_width_y: float = 12.0
    half_width_z: float = 12.0
    points_x: int = 24
    points_y: int = 24
    points_z: int = 24
    final_time: float = 3.0
    dt_over_spacing: float = 0.04
    absorber_fraction: float = 0.18
    absorber_strength: float = 0.25
    samples: int = 49

    def __post_init__(self) -> None:
        if min(self.half_width_x, self.half_width_y, self.half_width_z) <= 0.0:
            raise ValueError("half widths must be positive")
        if min(self.points_x, self.points_y, self.points_z) < 10:
            raise ValueError("each axis must contain at least 10 points")
        if any(value % 2 for value in (self.points_x, self.points_y, self.points_z)):
            raise ValueError("all grid sizes must be even")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_spacing <= 0.12:
            raise ValueError("dt_over_spacing must lie in (0, 0.12]")
        if not 0.05 <= self.absorber_fraction <= 0.35:
            raise ValueError("absorber_fraction must lie in [0.05, 0.35]")
        if self.absorber_strength < 0.0:
            raise ValueError("absorber_strength must be nonnegative")
        if self.samples < 2:
            raise ValueError("samples must be at least two")


@dataclass
class Spatial3DRun:
    x: RealArray
    y: RealArray
    z: RealArray
    dx: float
    dy: float
    dz: float
    dt: float
    steps: int
    parameters: Spatial3DParameters
    grid: Spatial3DGrid
    initial_plus: ComplexArray
    initial_minus: ComplexArray
    final_plus: ComplexArray
    final_minus: ComplexArray
    initial_a: tuple[RealArray, RealArray, RealArray]
    initial_e: tuple[RealArray, RealArray, RealArray]
    final_a: tuple[RealArray, RealArray, RealArray]
    final_e: tuple[RealArray, RealArray, RealArray]
    final_absorber_charge: RealArray
    absorbed_energy: float
    emitted_energy: float
    records: tuple[dict[str, float], ...]


def clifford_residuals() -> dict[str, float]:
    identity = np.eye(4, dtype=np.complex128)
    alpha_square = max(float(np.max(np.abs(alpha @ alpha - identity))) for alpha in ALPHAS)
    beta_square = float(np.max(np.abs(BETA @ BETA - identity)))
    alpha_pairs = 0.0
    for i, left in enumerate(ALPHAS):
        for j, right in enumerate(ALPHAS):
            if i < j:
                alpha_pairs = max(alpha_pairs, float(np.max(np.abs(left @ right + right @ left))))
    alpha_beta = max(float(np.max(np.abs(alpha @ BETA + BETA @ alpha))) for alpha in ALPHAS)
    return {
        "alpha_square": alpha_square,
        "beta_square": beta_square,
        "alpha_pair_anticommutator": alpha_pairs,
        "alpha_beta_anticommutator": alpha_beta,
    }
