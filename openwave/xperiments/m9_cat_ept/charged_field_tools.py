"""Shared periodic charge, current, Maxwell-field, and stress-flux tools for M9.96."""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .spatial_3d_operators import curl, derivative, divergence, longitudinal_field_from_charge

ComplexField = NDArray[np.complex128]
RealField = NDArray[np.float64]
Vector = tuple[RealField, RealField, RealField]


def spacing_tuple(spacing: float | tuple[float, float, float]) -> tuple[float, float, float]:
    values = (spacing, spacing, spacing) if isinstance(spacing, (int, float)) else spacing
    if len(values) != 3 or min(values) <= 0.0:
        raise ValueError("three positive spacings required")
    return tuple(float(value) for value in values)


def periodic_axis(points: int, spacing: float) -> RealField:
    return (np.arange(points, dtype=np.float64) - points / 2.0) * spacing


def periodic_displacement(values: RealField, center: float, length: float) -> RealField:
    return np.asarray((values - center + 0.5 * length) % length - 0.5 * length, dtype=np.float64)


def centered_symbols(
    shape: tuple[int, int, int],
    spacings: tuple[float, float, float],
) -> tuple[RealField, RealField, RealField, RealField]:
    symbols = []
    for points, spacing in zip(shape, spacings, strict=True):
        wave = 2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
        symbols.append(np.sin(wave * spacing) / spacing)
    sx, sy, sz = np.meshgrid(*symbols, indexing="ij")
    denominator = sx * sx + sy * sy + sz * sz
    return (
        np.asarray(sx, dtype=np.float64),
        np.asarray(sy, dtype=np.float64),
        np.asarray(sz, dtype=np.float64),
        np.asarray(denominator, dtype=np.float64),
    )


def spectral_shift(
    values: ComplexField | RealField,
    spacings: tuple[float, float, float],
    shift: tuple[float, float, float],
) -> ComplexField:
    if values.ndim != 3:
        raise ValueError("three-dimensional scalar field required")
    waves = [
        2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
        for points, spacing in zip(values.shape, spacings, strict=True)
    ]
    kx, ky, kz = np.meshgrid(*waves, indexing="ij")
    phase = np.exp(-1j * (kx * shift[0] + ky * shift[1] + kz * shift[2]))
    return np.asarray(np.fft.ifftn(np.fft.fftn(values) * phase), dtype=np.complex128)


def periodic_contour_winding(
    field: ComplexField,
    spacing: float,
    *,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    radius: float = 2.4,
    samples: int = 720,
) -> dict[str, float]:
    if field.ndim != 3 or len(set(field.shape)) != 1:
        raise ValueError("one cubic three-dimensional field is required")
    if spacing <= 0.0 or radius <= 0.0 or samples < 64:
        raise ValueError("positive contour controls and at least 64 samples required")
    points = field.shape[0]
    length = points * spacing
    if radius >= 0.5 * length:
        raise ValueError("contour must lie inside the minimum-image half box")
    axis = periodic_axis(points, spacing)
    z_distance = np.abs(periodic_displacement(axis, center[2], length))
    z_index = int(np.argmin(z_distance))
    plane = field[:, :, z_index]
    angles = np.linspace(0.0, 2.0 * math.pi, samples, endpoint=False)
    query_x = center[0] + radius * np.cos(angles)
    query_y = center[1] + radius * np.sin(angles)
    query_x = (query_x + 0.5 * length) % length - 0.5 * length
    query_y = (query_y + 0.5 * length) % length - 0.5 * length
    index_x = (query_x - axis[0]) / spacing
    index_y = (query_y - axis[0]) / spacing
    lower_x = np.floor(index_x).astype(int) % points
    lower_y = np.floor(index_y).astype(int) % points
    frac_x = index_x - np.floor(index_x)
    frac_y = index_y - np.floor(index_y)
    upper_x = (lower_x + 1) % points
    upper_y = (lower_y + 1) % points
    values = (
        (1.0 - frac_x) * (1.0 - frac_y) * plane[lower_x, lower_y]
        + frac_x * (1.0 - frac_y) * plane[upper_x, lower_y]
        + (1.0 - frac_x) * frac_y * plane[lower_x, upper_y]
        + frac_x * frac_y * plane[upper_x, upper_y]
    )
    minimum = float(np.min(np.abs(values)))
    increments = np.angle(np.roll(values, -1) * np.conj(values))
    raw = float(np.sum(increments) / (2.0 * math.pi))
    integer = int(round(raw))
    return {
        "raw_winding": raw,
        "integer_winding": integer,
        "quantization_error": abs(raw - integer),
        "minimum_contour_amplitude": minimum,
    }


def pauli_charge_current(
    field: ComplexField,
    spacing: float | tuple[float, float, float],
    *,
    charge: float,
    spin: int,
    mass: float = 1.0,
    include_convective: bool = True,
) -> tuple[RealField, Vector, dict[str, float]]:
    spacings = spacing_tuple(spacing)
    if field.ndim != 3 or charge == 0.0 or mass <= 0.0 or spin not in (-1, 1):
        raise ValueError("charged three-dimensional field, positive mass, and spin +/-1 required")
    density = np.asarray(np.abs(field) ** 2, dtype=np.float64)
    charge_density = np.asarray(charge * density, dtype=np.float64)
    current = [np.zeros_like(density) for _ in range(3)]
    if include_convective:
        for axis in range(3):
            gradient = derivative(field, axis, spacings[axis])
            current[axis] += charge / mass * np.imag(np.conj(field) * gradient)
    magnetization = (
        np.zeros_like(density),
        np.zeros_like(density),
        np.asarray(charge * spin * density / (2.0 * mass), dtype=np.float64),
    )
    magnetization_current = curl(magnetization, spacings)
    for axis in range(3):
        current[axis] += magnetization_current[axis]
    cell_volume = math.prod(spacings)
    return charge_density, tuple(np.asarray(item, dtype=np.float64) for item in current), {
        "integrated_charge": float(np.sum(charge_density) * cell_volume),
        "current_l2": math.sqrt(
            cell_volume * sum(float(np.sum(item * item)) for item in current)
        ),
    }


def scalar_potential_from_charge(
    charge_density: RealField,
    spacings: tuple[float, float, float],
) -> tuple[RealField, RealField, float]:
    sx, sy, sz, denominator = centered_symbols(tuple(charge_density.shape), spacings)
    source_hat = np.fft.fftn(charge_density - np.mean(charge_density))
    active = denominator > 1.0e-14
    potential_hat = np.zeros_like(source_hat)
    potential_hat[active] = source_hat[active] / denominator[active]
    projected_hat = np.zeros_like(source_hat)
    projected_hat[active] = source_hat[active]
    potential = np.asarray(np.real(np.fft.ifftn(potential_hat)), dtype=np.float64)
    projected = np.asarray(np.real(np.fft.ifftn(projected_hat)), dtype=np.float64)
    source = charge_density - np.mean(charge_density)
    projection_loss = float(np.linalg.norm(source - projected) / max(np.linalg.norm(source), 1.0e-30))
    return potential, projected, projection_loss


def vector_potential_from_current(
    current: Vector,
    spacings: tuple[float, float, float],
) -> tuple[Vector, Vector]:
    shape = tuple(current[0].shape)
    if any(tuple(component.shape) != shape for component in current):
        raise ValueError("matching current components required")
    sx, sy, sz, denominator = centered_symbols(shape, spacings)
    symbols = (sx, sy, sz)
    current_hat = [np.fft.fftn(component) for component in current]
    dot = sum(symbols[index] * current_hat[index] for index in range(3))
    active = denominator > 1.0e-14
    transverse_hat = []
    potential = []
    for symbol, component_hat in zip(symbols, current_hat, strict=True):
        projected = np.zeros_like(component_hat)
        projected[active] = (
            component_hat[active]
            - symbol[active] * dot[active] / denominator[active]
        )
        transverse_hat.append(projected)
        potential_hat = np.zeros_like(component_hat)
        potential_hat[active] = projected[active] / denominator[active]
        potential.append(np.asarray(np.real(np.fft.ifftn(potential_hat)), dtype=np.float64))
    transverse = tuple(
        np.asarray(np.real(np.fft.ifftn(component)), dtype=np.float64)
        for component in transverse_hat
    )
    return tuple(potential), transverse  # type: ignore[return-value]


def static_maxwell_fields(
    charge_density: RealField,
    current: Vector,
    spacing: float | tuple[float, float, float],
) -> dict[str, Any]:
    spacings = spacing_tuple(spacing)
    potential, projected_charge, projection_loss = scalar_potential_from_charge(
        charge_density, spacings
    )
    electric = longitudinal_field_from_charge(charge_density, spacings)
    vector_potential, transverse_current = vector_potential_from_current(current, spacings)
    magnetic = curl(vector_potential, spacings)
    gauss_residual = divergence(electric, spacings) - projected_charge
    magnetic_divergence = divergence(magnetic, spacings)
    ampere = curl(magnetic, spacings)
    ampere_residual = tuple(
        np.asarray(ampere[index] - transverse_current[index], dtype=np.float64)
        for index in range(3)
    )
    gauss_scale = max(float(np.linalg.norm(projected_charge)), 1.0e-30)
    ampere_scale = max(
        math.sqrt(sum(float(np.sum(item * item)) for item in transverse_current)),
        1.0e-30,
    )
    cell_volume = math.prod(spacings)
    return {
        "potential": potential,
        "electric": electric,
        "vector_potential": vector_potential,
        "magnetic": magnetic,
        "transverse_current": transverse_current,
        "projected_charge": projected_charge,
        "projection_loss": projection_loss,
        "gauss_relative_residual": float(np.linalg.norm(gauss_residual) / gauss_scale),
        "ampere_relative_residual": math.sqrt(
            sum(float(np.sum(item * item)) for item in ampere_residual)
        )
        / ampere_scale,
        "magnetic_divergence_max": float(np.max(np.abs(magnetic_divergence))),
        "electric_energy": 0.5
        * cell_volume
        * sum(float(np.sum(item * item)) for item in electric),
        "magnetic_energy": 0.5
        * cell_volume
        * sum(float(np.sum(item * item)) for item in magnetic),
    }


def relative_mesh(
    shape: tuple[int, int, int],
    spacing: float,
    center: tuple[float, float, float],
) -> tuple[RealField, RealField, RealField]:
    axes = [periodic_axis(points, spacing) for points in shape]
    mesh = np.meshgrid(*axes, indexing="ij")
    lengths = tuple(points * spacing for points in shape)
    return tuple(
        periodic_displacement(values, selected_center, length)
        for values, selected_center, length in zip(mesh, center, lengths, strict=True)
    )  # type: ignore[return-value]


def magnetic_moment_z(
    current: Vector,
    spacing: float,
    *,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> float:
    x, y, _z = relative_mesh(tuple(current[0].shape), spacing, center)
    return 0.5 * spacing**3 * float(np.sum(x * current[1] - y * current[0]))


def uniform_b_response(
    current: Vector,
    spacing: float,
    *,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    step: float = 1.0e-4,
) -> dict[str, float]:
    x, y, _z = relative_mesh(tuple(current[0].shape), spacing, center)

    def coupling_energy(field_strength: float) -> float:
        external = (
            -0.5 * field_strength * y,
            0.5 * field_strength * x,
            np.zeros_like(x),
        )
        return -spacing**3 * float(
            np.sum(sum(current[index] * external[index] for index in range(3)))
        )

    response = -(coupling_energy(step) - coupling_energy(-step)) / (2.0 * step)
    moment = magnetic_moment_z(current, spacing, center=center)
    return {
        "current_moment": moment,
        "energy_response_moment": response,
        "absolute_error": abs(moment - response),
    }


def lorentz_force(
    charge_density: RealField,
    current: Vector,
    external_electric: Vector,
    external_magnetic: Vector,
    spacings: tuple[float, float, float],
) -> np.ndarray:
    j_cross_b = (
        current[1] * external_magnetic[2] - current[2] * external_magnetic[1],
        current[2] * external_magnetic[0] - current[0] * external_magnetic[2],
        current[0] * external_magnetic[1] - current[1] * external_magnetic[0],
    )
    cell_volume = math.prod(spacings)
    return np.asarray(
        [
            cell_volume
            * float(np.sum(charge_density * external_electric[index] + j_cross_b[index]))
            for index in range(3)
        ],
        dtype=np.float64,
    )


def cross_maxwell_stress_flux(
    first_electric: Vector,
    first_magnetic: Vector,
    second_electric: Vector,
    second_magnetic: Vector,
    spacing: float,
    *,
    center: tuple[float, float, float],
    half_width: float,
) -> np.ndarray:
    shape = tuple(first_electric[0].shape)
    if len(set(shape)) != 1 or half_width <= 0.0:
        raise ValueError("cubic grid and positive integration half width required")
    dot = sum(
        first_electric[index] * second_electric[index]
        + first_magnetic[index] * second_magnetic[index]
        for index in range(3)
    )
    stress = [
        [
            first_electric[i] * second_electric[j]
            + second_electric[i] * first_electric[j]
            + first_magnetic[i] * second_magnetic[j]
            + second_magnetic[i] * first_magnetic[j]
            - (dot if i == j else 0.0)
            for j in range(3)
        ]
        for i in range(3)
    ]
    points = shape[0]
    length = points * spacing
    axis = periodic_axis(points, spacing)
    masks = [
        np.abs(periodic_displacement(axis, center[index], length)) <= half_width
        for index in range(3)
    ]
    result = np.zeros(3, dtype=np.float64)
    area = spacing * spacing
    for normal_axis in range(3):
        values = periodic_displacement(axis, center[normal_axis], length)
        positive = int(np.argmin(np.abs(values - half_width)))
        negative = int(np.argmin(np.abs(values + half_width)))
        if normal_axis == 0:
            selection = np.ix_(masks[1], masks[2])
            for component in range(3):
                result[component] += area * (
                    float(np.sum(stress[component][0][positive, :, :][selection]))
                    - float(np.sum(stress[component][0][negative, :, :][selection]))
                )
        elif normal_axis == 1:
            selection = np.ix_(masks[0], masks[2])
            for component in range(3):
                result[component] += area * (
                    float(np.sum(stress[component][1][:, positive, :][selection]))
                    - float(np.sum(stress[component][1][:, negative, :][selection]))
                )
        else:
            selection = np.ix_(masks[0], masks[1])
            for component in range(3):
                result[component] += area * (
                    float(np.sum(stress[component][2][:, :, positive][selection]))
                    - float(np.sum(stress[component][2][:, :, negative][selection]))
                )
    return result
