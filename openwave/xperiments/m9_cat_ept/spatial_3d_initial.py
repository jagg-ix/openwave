"""Initial data for the bounded M9 3D engine."""

from __future__ import annotations

import numpy as np

from .spatial_3d_types import ComplexArray, RealArray, Spatial3DGrid, Spatial3DParameters
from .spatial_3d_operators import (
    derivative, gaussian_packet, longitudinal_field_from_charge, periodic_mesh,
    signed_charge_density,
)

def initial_state(
    parameters: Spatial3DParameters,
    grid: Spatial3DGrid,
) -> tuple[
    RealArray,
    RealArray,
    RealArray,
    float,
    float,
    float,
    ComplexArray,
    ComplexArray,
    tuple[RealArray, RealArray, RealArray],
    tuple[RealArray, RealArray, RealArray],
]:
    x, y, z, dx, dy, dz = periodic_mesh(grid)
    cell_volume = dx * dy * dz
    plus_center = (-parameters.offset_x, -parameters.offset_y, -parameters.offset_z)
    minus_center = (parameters.offset_x, parameters.offset_y, parameters.offset_z)
    plus_momentum = (parameters.momentum_x, parameters.momentum_y, parameters.momentum_z)
    minus_momentum = (
        -parameters.momentum_x,
        -0.80 * parameters.momentum_y,
        -1.20 * parameters.momentum_z,
    )
    plus = gaussian_packet(
        x, y, z, plus_center, plus_momentum, parameters.packet_width,
        parameters.mass, 0.5 * parameters.total_norm, cell_volume,
    )
    minus = gaussian_packet(
        x, y, z, minus_center, minus_momentum, parameters.packet_width,
        parameters.mass, 0.5 * parameters.total_norm, cell_volume,
    )
    spacings = (dx, dy, dz)
    scalar_seed = parameters.gauge_seed_amplitude * np.exp(
        -(x**2 + y**2 + z**2) / parameters.gauge_seed_width**2
    )
    ax = np.asarray(derivative(scalar_seed, 1, dy), dtype=np.float64)
    ay = np.asarray(-derivative(scalar_seed, 0, dx), dtype=np.float64)
    az = np.zeros_like(ax)
    vector_potential = (ax, ay, az)
    electric_field = longitudinal_field_from_charge(
        signed_charge_density(plus, minus, parameters), spacings
    )
    return x, y, z, dx, dy, dz, plus, minus, vector_potential, electric_field


Vector = tuple[RealArray, RealArray, RealArray]
