"""One periodic Fourier differential complex for M9 matter and Maxwell fields.

The legacy gauge-spinor stationary operator used exact Fourier derivatives while
its Maxwell inversion used centered-difference symbols ``sin(k h) / h``. This
module uses the same exact Fourier wave numbers for gradient, divergence, curl,
Laplacian, Helmholtz projection, Poisson inversion, and gauge-covariant matter
derivatives.

For real-valued Maxwell fields the reconciled campaign uses an odd number of
points on every axis. Odd grids have no self-conjugate Nyquist frequency, so the
exact Fourier derivative maps real fields to real fields and only the global
zero mode is removed. ``spectral_resample`` transports the historical even-grid
seed to this odd operational grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Any

import numpy as np

Scalar = np.ndarray
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


def spectral_resample(values: np.ndarray, new_shape: tuple[int, int, int]) -> np.ndarray:
    """Fourier-pad or crop one three-dimensional periodic complex field."""
    if values.ndim != 3 or len(new_shape) != 3 or any(points < 5 for points in new_shape):
        raise ValueError("three-dimensional field and target shape required")
    old_shape = tuple(values.shape)
    old_hat = np.fft.fftshift(np.fft.fftn(values))
    new_hat = np.zeros(new_shape, dtype=np.complex128)
    widths = tuple(min(old, new) for old, new in zip(old_shape, new_shape, strict=True))
    old_slices = tuple(
        slice((old - width) // 2, (old - width) // 2 + width)
        for old, width in zip(old_shape, widths, strict=True)
    )
    new_slices = tuple(
        slice((new - width) // 2, (new - width) // 2 + width)
        for new, width in zip(new_shape, widths, strict=True)
    )
    new_hat[new_slices] = old_hat[old_slices]
    scale = math.prod(new_shape) / math.prod(old_shape)
    return np.asarray(
        scale * np.fft.ifftn(np.fft.ifftshift(new_hat)), dtype=np.complex128
    )


@dataclass(frozen=True)
class PeriodicFourierGeometry:
    shape: tuple[int, int, int]
    spacings: tuple[float, float, float]

    def __post_init__(self) -> None:
        if len(self.shape) != 3 or len(self.spacings) != 3:
            raise ValueError("three-dimensional shape and spacings required")
        if any(points < 5 for points in self.shape):
            raise ValueError("periodic grids with at least five points required")
        if any(spacing <= 0.0 for spacing in self.spacings):
            raise ValueError("positive spacings required")

    @property
    def is_odd_grid(self) -> bool:
        return all(points % 2 == 1 for points in self.shape)

    @property
    def cell_volume(self) -> float:
        return math.prod(self.spacings)

    @property
    def volume(self) -> float:
        return math.prod(
            points * spacing
            for points, spacing in zip(self.shape, self.spacings, strict=True)
        )

    @lru_cache(maxsize=1)
    def wave_mesh(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        waves = [
            2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
            for points, spacing in zip(self.shape, self.spacings, strict=True)
        ]
        kx, ky, kz = np.meshgrid(*waves, indexing="ij")
        k2 = kx * kx + ky * ky + kz * kz
        return tuple(
            np.asarray(item, dtype=np.float64) for item in (kx, ky, kz, k2)
        )  # type: ignore[return-value]

    def _check_scalar(self, values: np.ndarray) -> None:
        if tuple(values.shape[-3:]) != self.shape:
            raise ValueError(
                f"expected trailing spatial shape {self.shape}, got {values.shape}"
            )

    def derivative(self, values: np.ndarray, axis: int) -> np.ndarray:
        self._check_scalar(values)
        if axis not in (0, 1, 2):
            raise ValueError("axis must be 0, 1, or 2")
        if np.isrealobj(values) and not self.is_odd_grid:
            raise ValueError(
                "real exact-Fourier derivatives require an odd grid to avoid a Nyquist ambiguity"
            )
        symbol = self.wave_mesh()[axis]
        prefix = (1,) * (values.ndim - 3)
        transformed = np.fft.fftn(values, axes=(-3, -2, -1))
        result = np.fft.ifftn(
            1.0j * symbol.reshape((*prefix, *self.shape)) * transformed,
            axes=(-3, -2, -1),
        )
        if np.isrealobj(values):
            return np.asarray(np.real_if_close(result, tol=1000).real, dtype=np.float64)
        return np.asarray(result, dtype=np.complex128)

    def gradient(self, values: np.ndarray) -> Vector:
        if values.ndim != 3:
            raise ValueError("three-dimensional scalar field required")
        return tuple(
            np.asarray(self.derivative(values, axis)) for axis in range(3)
        )  # type: ignore[return-value]

    def divergence(self, vector: Vector) -> np.ndarray:
        if any(tuple(component.shape) != self.shape for component in vector):
            raise ValueError("matching three-dimensional vector components required")
        result = sum(self.derivative(vector[axis], axis) for axis in range(3))
        return np.asarray(np.real_if_close(result, tol=1000).real, dtype=np.float64)

    def curl(self, vector: Vector) -> Vector:
        if any(tuple(component.shape) != self.shape for component in vector):
            raise ValueError("matching three-dimensional vector components required")
        x, y, z = vector
        return (
            np.asarray(self.derivative(z, 1) - self.derivative(y, 2), dtype=np.float64),
            np.asarray(self.derivative(x, 2) - self.derivative(z, 0), dtype=np.float64),
            np.asarray(self.derivative(y, 0) - self.derivative(x, 1), dtype=np.float64),
        )

    def laplacian(self, values: np.ndarray) -> np.ndarray:
        self._check_scalar(values)
        k2 = self.wave_mesh()[3]
        prefix = (1,) * (values.ndim - 3)
        transformed = np.fft.fftn(values, axes=(-3, -2, -1))
        result = np.fft.ifftn(
            -k2.reshape((*prefix, *self.shape)) * transformed,
            axes=(-3, -2, -1),
        )
        if np.isrealobj(values):
            return np.asarray(np.real_if_close(result, tol=1000).real, dtype=np.float64)
        return np.asarray(result, dtype=np.complex128)

    def mean_zero(self, values: np.ndarray) -> np.ndarray:
        if tuple(values.shape) != self.shape:
            raise ValueError("three-dimensional scalar field required")
        return np.asarray(values - np.mean(values), dtype=values.dtype)

    def inverse_negative_laplacian(self, source: np.ndarray) -> np.ndarray:
        """Solve ``-Delta u = source - mean(source)`` on the periodic box."""
        if tuple(source.shape) != self.shape:
            raise ValueError("three-dimensional source required")
        if np.isrealobj(source) and not self.is_odd_grid:
            raise ValueError("real Poisson fields require an odd reconciled grid")
        k2 = self.wave_mesh()[3]
        transformed = np.fft.fftn(self.mean_zero(source))
        result_hat = np.zeros_like(transformed, dtype=np.complex128)
        active = k2 > 0.0
        result_hat[active] = transformed[active] / k2[active]
        result = np.fft.ifftn(result_hat)
        if np.isrealobj(source):
            return np.asarray(np.real_if_close(result, tol=1000).real, dtype=np.float64)
        return np.asarray(result, dtype=np.complex128)

    def transverse_projection(self, vector: Vector) -> Vector:
        if any(tuple(component.shape) != self.shape for component in vector):
            raise ValueError("matching vector components required")
        if any(np.isrealobj(component) for component in vector) and not self.is_odd_grid:
            raise ValueError("real Helmholtz projection requires an odd reconciled grid")
        kx, ky, kz, k2 = self.wave_mesh()
        symbols = (kx, ky, kz)
        hats = [np.fft.fftn(component) for component in vector]
        dot = sum(symbols[index] * hats[index] for index in range(3))
        active = k2 > 0.0
        projected = []
        for symbol, component_hat in zip(symbols, hats, strict=True):
            value_hat = np.zeros_like(component_hat, dtype=np.complex128)
            value_hat[active] = (
                component_hat[active]
                - symbol[active] * dot[active] / k2[active]
            )
            value = np.fft.ifftn(value_hat)
            projected.append(
                np.asarray(np.real_if_close(value, tol=1000).real, dtype=np.float64)
            )
        return tuple(projected)  # type: ignore[return-value]

    def scalar_potential(self, charge_density: np.ndarray) -> np.ndarray:
        return self.inverse_negative_laplacian(charge_density)

    def vector_potential(self, current: Vector) -> tuple[Vector, Vector]:
        transverse = self.transverse_projection(current)
        potential = tuple(
            self.inverse_negative_laplacian(component) for component in transverse
        )
        return potential, transverse  # type: ignore[return-value]

    def static_maxwell_fields(
        self, charge_density: np.ndarray, current: Vector
    ) -> dict[str, Any]:
        scalar = self.scalar_potential(charge_density)
        electric = tuple(
            np.asarray(-component, dtype=np.float64)
            for component in self.gradient(scalar)
        )
        vector_potential, transverse_current = self.vector_potential(current)
        magnetic = self.curl(vector_potential)
        projected_charge = self.mean_zero(charge_density)
        gauss_residual = self.divergence(electric) - projected_charge
        ampere = self.curl(magnetic)
        ampere_residual = tuple(
            ampere[index] - transverse_current[index] for index in range(3)
        )
        magnetic_divergence = self.divergence(magnetic)
        charge_scale = max(float(np.linalg.norm(projected_charge)), 1.0e-30)
        current_scale = max(
            math.sqrt(
                sum(
                    float(np.sum(component * component))
                    for component in transverse_current
                )
            ),
            1.0e-30,
        )
        return {
            "potential": scalar,
            "electric": electric,
            "vector_potential": vector_potential,
            "magnetic": magnetic,
            "projected_charge": projected_charge,
            "transverse_current": transverse_current,
            "projection_loss": 0.0,
            "gauss_relative_residual": float(
                np.linalg.norm(gauss_residual) / charge_scale
            ),
            "ampere_relative_residual": math.sqrt(
                sum(
                    float(np.sum(component * component))
                    for component in ampere_residual
                )
            )
            / current_scale,
            "magnetic_divergence_max": float(
                np.max(np.abs(magnetic_divergence))
            ),
            "electric_energy": 0.5
            * self.cell_volume
            * sum(float(np.sum(component * component)) for component in electric),
            "magnetic_energy": 0.5
            * self.cell_volume
            * sum(float(np.sum(component * component)) for component in magnetic),
        }

    def covariant_laplacian(
        self, spinor: np.ndarray, vector_potential: Vector, charge: float
    ) -> np.ndarray:
        if spinor.ndim != 4 or tuple(spinor.shape[-3:]) != self.shape:
            raise ValueError("component-by-space spinor required")
        if any(tuple(component.shape) != self.shape for component in vector_potential):
            raise ValueError("matching vector potential required")
        result = np.zeros_like(spinor, dtype=np.complex128)
        for axis in range(3):
            first = self.derivative(spinor, axis)
            first -= 1.0j * charge * vector_potential[axis][None, ...] * spinor
            second = self.derivative(first, axis)
            second -= 1.0j * charge * vector_potential[axis][None, ...] * first
            result += second
        return np.asarray(result, dtype=np.complex128)

    def centered_symbol_null_count(self) -> int:
        symbols = []
        for points, spacing in zip(self.shape, self.spacings, strict=True):
            wave = 2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
            symbols.append(np.sin(wave * spacing) / spacing)
        sx, sy, sz = np.meshgrid(*symbols, indexing="ij")
        return int(
            np.count_nonzero(sx * sx + sy * sy + sz * sz <= 1.0e-28)
        )

    def fourier_symbol_null_count(self) -> int:
        return int(np.count_nonzero(self.wave_mesh()[3] == 0.0))


def analytic_identity_diagnostics(
    points: int = 17, half_width: float = 8.0
) -> dict[str, float | int]:
    if points % 2 == 0:
        raise ValueError("reconciled real-field diagnostics require an odd grid")
    spacing = 2.0 * half_width / points
    geometry = PeriodicFourierGeometry(
        (points, points, points), (spacing, spacing, spacing)
    )
    axis = -half_width + spacing * np.arange(points, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    length = 2.0 * half_width
    scalar = np.sin(2.0 * math.pi * x / length) * np.cos(
        4.0 * math.pi * y / length
    )
    vector = (
        np.sin(2.0 * math.pi * y / length),
        np.sin(2.0 * math.pi * z / length),
        np.sin(2.0 * math.pi * x / length),
    )
    curl_grad = geometry.curl(geometry.gradient(scalar))
    div_curl = geometry.divergence(geometry.curl(vector))
    lap_from_div_grad = geometry.divergence(geometry.gradient(scalar))
    lap = geometry.laplacian(scalar)
    even_reference = PeriodicFourierGeometry(
        (16, 16, 16), (1.0, 1.0, 1.0)
    )
    return {
        "points": points,
        "spacing": spacing,
        "odd_operational_grid": int(geometry.is_odd_grid),
        "curl_gradient_max": max(
            float(np.max(np.abs(component))) for component in curl_grad
        ),
        "divergence_curl_max": float(np.max(np.abs(div_curl))),
        "laplacian_identity_relative_error": float(
            np.linalg.norm(lap_from_div_grad - lap)
            / max(np.linalg.norm(lap), 1.0e-30)
        ),
        "fourier_null_mode_count": geometry.fourier_symbol_null_count(),
        "centered_null_mode_count_on_operational_grid": geometry.centered_symbol_null_count(),
        "legacy_even_centered_null_mode_count": even_reference.centered_symbol_null_count(),
    }


def result_to_json(result: dict[str, Any]) -> str:
    import json

    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
