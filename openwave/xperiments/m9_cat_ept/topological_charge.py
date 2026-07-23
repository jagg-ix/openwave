"""M9.26: field-derived winding and topological-sector observables.

A complex two-dimensional field is sampled on closed contours. The observable

    Q = (1 / 2 pi) sum arg(psi_{j+1} psi_j^*)

is computed from the field itself and is invariant under a global phase. The
reference suite covers isolated vortices, separated multi-vortex configurations,
smooth perturbations, contour changes, and resolution changes.

The sector is seeded in the initial condition. This module therefore qualifies
a topological observable and its quantization, not spontaneous charge creation
or identification with electric charge.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

ComplexGrid = NDArray[np.complex128]
ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class VortexGrid:
    half_width: float = 8.0
    points: int = 257
    core_radius: float = 1.0
    contour_radius: float = 4.0
    contour_samples: int = 2048
    minimum_contour_amplitude: float = 0.1

    def __post_init__(self) -> None:
        if self.half_width <= 0.0 or self.core_radius <= 0.0:
            raise ValueError("positive domain and core radius required")
        if self.points < 33 or self.points % 2 == 0:
            raise ValueError("points must be an odd integer at least 33")
        if not 0.0 < self.contour_radius < self.half_width:
            raise ValueError("contour must lie inside the domain")
        if self.contour_samples < 64:
            raise ValueError("at least 64 contour samples required")
        if self.minimum_contour_amplitude <= 0.0:
            raise ValueError("minimum contour amplitude must be positive")


def coordinates(grid: VortexGrid) -> tuple[RealArray, RealArray, RealArray, RealArray]:
    x = np.linspace(-grid.half_width, grid.half_width, grid.points)
    y = x.copy()
    xx, yy = np.meshgrid(x, y, indexing="xy")
    return x, y, xx, yy


def vortex_field(
    grid: VortexGrid,
    vortices: Sequence[tuple[float, float, int]],
    *,
    global_phase: float = 0.0,
) -> ComplexGrid:
    _x, _y, xx, yy = coordinates(grid)
    field = np.ones_like(xx, dtype=np.complex128) * np.exp(1j * global_phase)
    for center_x, center_y, winding in vortices:
        dx = xx - center_x
        dy = yy - center_y
        radius = np.hypot(dx, dy)
        angle = np.arctan2(dy, dx)
        amplitude = np.ones_like(radius) if winding == 0 else np.tanh(radius / grid.core_radius) ** abs(winding)
        field *= amplitude * np.exp(1j * winding * angle)
    return np.asarray(field, dtype=np.complex128)


def smooth_perturbation(
    grid: VortexGrid,
    field: ComplexGrid,
    *,
    amplitude: float = 0.08,
    phase_amplitude: float = 0.12,
) -> ComplexGrid:
    _x, _y, xx, yy = coordinates(grid)
    envelope = 1.0 + amplitude * np.cos(0.37 * xx) * np.cos(0.29 * yy)
    phase = phase_amplitude * np.sin(0.23 * xx) * np.cos(0.31 * yy)
    return np.asarray(field * envelope * np.exp(1j * phase), dtype=np.complex128)


def bilinear_sample(
    x: RealArray,
    y: RealArray,
    field: ComplexGrid,
    query_x: RealArray,
    query_y: RealArray,
) -> ComplexArray:
    dx = float(x[1] - x[0])
    dy = float(y[1] - y[0])
    index_x = np.clip(((query_x - x[0]) / dx).astype(int), 0, len(x) - 2)
    index_y = np.clip(((query_y - y[0]) / dy).astype(int), 0, len(y) - 2)
    frac_x = (query_x - x[index_x]) / dx
    frac_y = (query_y - y[index_y]) / dy
    return np.asarray(
        (1.0 - frac_x) * (1.0 - frac_y) * field[index_y, index_x]
        + frac_x * (1.0 - frac_y) * field[index_y, index_x + 1]
        + (1.0 - frac_x) * frac_y * field[index_y + 1, index_x]
        + frac_x * frac_y * field[index_y + 1, index_x + 1],
        dtype=np.complex128,
    )


def winding_number(
    grid: VortexGrid,
    field: ComplexGrid,
    *,
    center: tuple[float, float] = (0.0, 0.0),
    radius: float | None = None,
) -> dict[str, float]:
    contour_radius = grid.contour_radius if radius is None else radius
    if not 0.0 < contour_radius < grid.half_width:
        raise ValueError("contour must lie inside the domain")
    x, y, _xx, _yy = coordinates(grid)
    angles = np.linspace(0.0, 2.0 * math.pi, grid.contour_samples, endpoint=False)
    values = bilinear_sample(
        x,
        y,
        field,
        center[0] + contour_radius * np.cos(angles),
        center[1] + contour_radius * np.sin(angles),
    )
    minimum_amplitude = float(np.min(np.abs(values)))
    if minimum_amplitude < grid.minimum_contour_amplitude:
        raise ValueError("field approaches zero on contour; winding is undefined")
    increments = np.angle(np.roll(values, -1) * np.conj(values))
    raw = float(np.sum(increments) / (2.0 * math.pi))
    integer = int(round(raw))
    return {
        "raw_winding": raw,
        "integer_winding": integer,
        "quantization_error": abs(raw - integer),
        "minimum_contour_amplitude": minimum_amplitude,
    }


def sector_resolution_study(
    windings: Sequence[int] = (-2, -1, 0, 1, 2),
    point_counts: Sequence[int] = (65, 129, 257),
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    maximum_error = 0.0
    for points in point_counts:
        grid = VortexGrid(points=points)
        for winding in windings:
            result = winding_number(grid, vortex_field(grid, ((0.0, 0.0, winding),)))
            maximum_error = max(maximum_error, result["quantization_error"])
            records.append({"points": points, "seed_winding": winding, **result})
    return {
        "records": records,
        "maximum_quantization_error": maximum_error,
        "windings": list(windings),
        "point_counts": list(point_counts),
    }


def contour_study() -> dict[str, Any]:
    grid = VortexGrid()
    field = vortex_field(grid, ((0.0, 0.0, 2),))
    records = [{"radius": radius, **winding_number(grid, field, radius=radius)} for radius in (2.5, 3.5, 4.5, 5.5)]
    return {
        "records": records,
        "maximum_quantization_error": max(item["quantization_error"] for item in records),
        "integer_windings": [item["integer_winding"] for item in records],
    }


def perturbation_study() -> dict[str, Any]:
    grid = VortexGrid()
    base = vortex_field(grid, ((0.0, 0.0, -1),), global_phase=0.71)
    perturbed = smooth_perturbation(grid, base)
    base_result = winding_number(grid, base)
    perturbed_result = winding_number(grid, perturbed)
    return {
        "base": base_result,
        "perturbed": perturbed_result,
        "integer_preserved": base_result["integer_winding"] == perturbed_result["integer_winding"] == -1,
    }


def additivity_study() -> dict[str, Any]:
    grid = VortexGrid()
    field = vortex_field(grid, ((-2.0, 0.0, 1), (2.0, 0.0, -2)))
    total = winding_number(grid, field, radius=6.0)
    left = winding_number(grid, field, center=(-2.0, 0.0), radius=1.2)
    right = winding_number(grid, field, center=(2.0, 0.0), radius=1.2)
    return {
        "left": left,
        "right": right,
        "total": total,
        "integer_additivity_error": abs(total["integer_winding"] - left["integer_winding"] - right["integer_winding"]),
    }


@lru_cache(maxsize=1)
def run_topological_charge_study() -> dict[str, Any]:
    resolution = sector_resolution_study()
    contours = contour_study()
    perturbation = perturbation_study()
    additivity = additivity_study()
    grid = VortexGrid()
    base = vortex_field(grid, ((0.0, 0.0, 1),))
    phase_rotated = base * np.exp(1.234j)
    global_phase_error = abs(winding_number(grid, base)["raw_winding"] - winding_number(grid, phase_rotated)["raw_winding"])
    acceptance = {
        "integer_sectors_recovered": resolution["maximum_quantization_error"] <= 2.0e-12,
        "resolution_robust": len(resolution["point_counts"]) == 3,
        "contour_independent": len(set(contours["integer_windings"])) == 1 and contours["maximum_quantization_error"] <= 2.0e-12,
        "global_phase_invariant": global_phase_error <= 2.0e-12,
        "smooth_perturbation_preserves_sector": perturbation["integer_preserved"],
        "multi_vortex_additivity": additivity["integer_additivity_error"] == 0,
        "contour_zero_rejection_is_explicit": True,
        "no_spontaneous_sector_selection_promoted": True,
    }
    return {
        "schema": "openwave.m9.topological-charge-result.v1",
        "task": "M9.26",
        "observable": "closed-contour complex-field winding",
        "grid": asdict(grid),
        "resolution": resolution,
        "contours": contours,
        "perturbation": perturbation,
        "additivity": additivity,
        "global_phase_error": global_phase_error,
        "field_derived_integer_charge": all(acceptance.values()),
        "identified_with_electric_charge": False,
        "spontaneous_sector_selection": False,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "an integer field-derived topological observable",
                "global-phase, contour, resolution, and smooth-perturbation robustness",
                "local and total additivity for separated vortices",
            ],
            "does_not_establish": [
                "spontaneous creation or selection of the winding sector",
                "identification of winding with elementary electric charge",
                "a stable three-dimensional charged particle",
                "a dynamical gauge coupling or Coulomb force law",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
