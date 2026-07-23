"""M9.27: rest-energy and scale-selection qualification for a topological ansatz.

The selected dimensionless O(3) / baby-Skyrme reference sector uses

    E = E2 + kappa E4 + mu2 E0,

with a degree-one radial profile. Under scale R,

    E(R) = 4 pi + 8 pi kappa / (3 R^2) + 4 pi mu2 R^2.

The quartic and potential sectors balance at an interior radius. The module
checks that minimum numerically, verifies Derrick controls, and evolves the
collective scale by dissipative gradient flow.

This is a selected topological ansatz and scale-selection mechanism. It is not
the full CAT/EPT field theory, a three-dimensional particle, or a physical mass.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ScaleParameters:
    skyrme_strength: float = 0.6
    potential_strength: float = 0.4
    scale_min: float = 0.45
    scale_max: float = 2.2
    scan_points: int = 141
    radial_extent_factor: float = 40.0
    radial_points: int = 6001
    mobility: float = 0.12
    relaxation_time: float = 30.0
    relaxation_dt: float = 0.02

    def __post_init__(self) -> None:
        if self.skyrme_strength < 0.0 or self.potential_strength < 0.0:
            raise ValueError("energy coefficients must be nonnegative")
        if not 0.0 < self.scale_min < self.scale_max:
            raise ValueError("invalid scale interval")
        if self.scan_points < 21 or self.radial_points < 501:
            raise ValueError("insufficient scan or radial resolution")
        if self.radial_extent_factor <= 5.0:
            raise ValueError("radial extent factor must resolve the far field")
        if self.mobility <= 0.0 or self.relaxation_time <= 0.0 or self.relaxation_dt <= 0.0:
            raise ValueError("positive relaxation controls required")


def profile_components(radius: np.ndarray, scale: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    denominator = radius**2 + scale**2
    derivative = -2.0 * scale / denominator
    sine = 2.0 * scale * radius / denominator
    cosine = (radius**2 - scale**2) / denominator
    return derivative, sine, cosine


def numerical_energy_components(scale: float, p: ScaleParameters, *, radial_points: int | None = None) -> dict[str, float]:
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    points = p.radial_points if radial_points is None else radial_points
    maximum_radius = p.radial_extent_factor * scale
    radius = np.linspace(0.0, maximum_radius, points)
    safe_radius = radius.copy()
    safe_radius[0] = maximum_radius / (points - 1) * 0.5
    derivative, sine, cosine = profile_components(safe_radius, scale)
    sigma_density = 0.5 * (derivative**2 + sine**2 / safe_radius**2)
    skyrme_density = 0.5 * (sine * derivative / safe_radius) ** 2
    potential_density = (1.0 - cosine) ** 2
    measure = 2.0 * math.pi * safe_radius
    sigma = float(np.trapezoid(measure * sigma_density, safe_radius))
    skyrme = float(np.trapezoid(measure * skyrme_density, safe_radius))
    potential = float(np.trapezoid(measure * potential_density, safe_radius))
    total = sigma + p.skyrme_strength * skyrme + p.potential_strength * potential
    return {
        "sigma": sigma,
        "skyrme_unweighted": skyrme,
        "potential_unweighted": potential,
        "skyrme_weighted": p.skyrme_strength * skyrme,
        "potential_weighted": p.potential_strength * potential,
        "total": total,
    }


def analytic_energy(scale: float, p: ScaleParameters) -> float:
    return 4.0 * math.pi + 8.0 * math.pi * p.skyrme_strength / (3.0 * scale**2) + 4.0 * math.pi * p.potential_strength * scale**2


def analytic_derivative(scale: float, p: ScaleParameters) -> float:
    return -16.0 * math.pi * p.skyrme_strength / (3.0 * scale**3) + 8.0 * math.pi * p.potential_strength * scale


def analytic_second_derivative(scale: float, p: ScaleParameters) -> float:
    return 16.0 * math.pi * p.skyrme_strength / scale**4 + 8.0 * math.pi * p.potential_strength


def selected_scale(p: ScaleParameters) -> float | None:
    if p.skyrme_strength <= 0.0 or p.potential_strength <= 0.0:
        return None
    return (2.0 * p.skyrme_strength / (3.0 * p.potential_strength)) ** 0.25


def scale_scan(p: ScaleParameters) -> dict[str, Any]:
    scales = np.linspace(p.scale_min, p.scale_max, p.scan_points)
    analytic = np.asarray([analytic_energy(float(scale), p) for scale in scales])
    numerical = np.asarray([numerical_energy_components(float(scale), p)["total"] for scale in scales])
    index = int(np.argmin(numerical))
    exact = selected_scale(p)
    return {
        "scales": scales.tolist(),
        "analytic_energies": analytic.tolist(),
        "numerical_energies": numerical.tolist(),
        "minimum_index": index,
        "numerical_minimum_scale": float(scales[index]),
        "analytic_selected_scale": exact,
        "minimum_is_interior": 0 < index < len(scales) - 1,
        "maximum_relative_energy_error": float(np.max(np.abs(numerical - analytic) / np.maximum(np.abs(analytic), 1.0e-15))),
    }


def resolution_study(p: ScaleParameters) -> dict[str, Any]:
    scale = selected_scale(p)
    if scale is None:
        raise ValueError("selected scale requires both energy sectors")
    point_counts = (751, 1501, 3001, 6001)
    records = [{"radial_points": points, **numerical_energy_components(scale, p, radial_points=points)} for points in point_counts]
    exact = analytic_energy(scale, p)
    exact_errors = [abs(item["total"] - exact) for item in records]
    successive_differences = [abs(records[index]["total"] - records[index + 1]["total"]) for index in range(len(records) - 1)]
    orders = [math.log(successive_differences[index] / successive_differences[index + 1], 2.0) for index in range(len(successive_differences) - 1)]
    return {
        "records": records,
        "exact_energy": exact,
        "absolute_errors": exact_errors,
        "successive_differences": successive_differences,
        "observed_orders": orders,
    }


def derrick_controls(p: ScaleParameters) -> dict[str, Any]:
    scales = np.linspace(p.scale_min, p.scale_max, p.scan_points)
    no_skyrme = ScaleParameters(**{**asdict(p), "skyrme_strength": 0.0})
    no_potential = ScaleParameters(**{**asdict(p), "potential_strength": 0.0})
    no_skyrme_energy = np.asarray([analytic_energy(float(scale), no_skyrme) for scale in scales])
    no_potential_energy = np.asarray([analytic_energy(float(scale), no_potential) for scale in scales])
    return {
        "no_skyrme_minimum_at_lower_boundary": int(np.argmin(no_skyrme_energy)) == 0,
        "no_potential_minimum_at_upper_boundary": int(np.argmin(no_potential_energy)) == len(scales) - 1,
        "no_skyrme_selected_scale": selected_scale(no_skyrme),
        "no_potential_selected_scale": selected_scale(no_potential),
    }


def relax_scale(initial_scale: float, p: ScaleParameters) -> dict[str, Any]:
    if initial_scale <= 0.0:
        raise ValueError("initial scale must be positive")
    steps = math.ceil(p.relaxation_time / p.relaxation_dt)
    dt = p.relaxation_time / steps
    scale = initial_scale
    energies = [analytic_energy(scale, p)]
    scales = [scale]

    def flow(value: float) -> float:
        return -p.mobility * analytic_derivative(value, p)

    for _ in range(steps):
        k1 = flow(scale)
        k2 = flow(scale + 0.5 * dt * k1)
        k3 = flow(scale + 0.5 * dt * k2)
        k4 = flow(scale + dt * k3)
        scale = max(1.0e-8, scale + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
        scales.append(scale)
        energies.append(analytic_energy(scale, p))
    return {
        "initial_scale": initial_scale,
        "final_scale": scale,
        "initial_energy": energies[0],
        "final_energy": energies[-1],
        "energy_nonincreasing": bool(np.all(np.diff(np.asarray(energies)) <= 2.0e-12)),
        "scales": scales,
        "energies": energies,
    }


@lru_cache(maxsize=1)
def run_scale_selection_study() -> dict[str, Any]:
    p = ScaleParameters()
    exact_scale = selected_scale(p)
    if exact_scale is None:
        raise RuntimeError("reference parameters must select a scale")
    scan = scale_scan(p)
    resolution = resolution_study(p)
    controls = derrick_controls(p)
    relaxation_large = relax_scale(1.7, p)
    relaxation_small = relax_scale(0.6, p)
    derivative_at_minimum = abs(analytic_derivative(exact_scale, p))
    curvature = analytic_second_derivative(exact_scale, p)
    maximum_relaxation_error = max(abs(relaxation_large["final_scale"] - exact_scale), abs(relaxation_small["final_scale"] - exact_scale))
    acceptance = {
        "interior_minimum_found": scan["minimum_is_interior"],
        "numerical_scan_matches_analytic_scale": abs(scan["numerical_minimum_scale"] - exact_scale) <= 0.02,
        "energy_quadrature_agrees": scan["maximum_relative_energy_error"] <= 2.5e-3,
        "radial_quadrature_converges": min(resolution["observed_orders"]) >= 1.7,
        "stationary_derivative_closes": derivative_at_minimum <= 2.0e-12,
        "positive_curvature": curvature > 0.0,
        "both_scale_directions_relax": relaxation_large["energy_nonincreasing"] and relaxation_small["energy_nonincreasing"] and maximum_relaxation_error <= 2.0e-4,
        "derrick_boundary_controls_pass": controls["no_skyrme_minimum_at_lower_boundary"] and controls["no_potential_minimum_at_upper_boundary"] and controls["no_skyrme_selected_scale"] is None and controls["no_potential_selected_scale"] is None,
        "no_physical_mass_or_particle_promoted": True,
    }
    return {
        "schema": "openwave.m9.scale-selection-result.v1",
        "task": "M9.27",
        "model": "degree-one baby-Skyrme radial ansatz",
        "parameters": asdict(p),
        "analytic_selected_scale": exact_scale,
        "analytic_energy_at_selected_scale": analytic_energy(exact_scale, p),
        "derivative_at_selected_scale": derivative_at_minimum,
        "curvature_at_selected_scale": curvature,
        "scan": scan,
        "resolution": resolution,
        "derrick_controls": controls,
        "relaxation_from_large_scale": relaxation_large,
        "relaxation_from_small_scale": relaxation_small,
        "selected_dimensionless_scale": all(acceptance.values()),
        "physical_rest_mass_established": False,
        "accepted_three_dimensional_particle": False,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "an interior scale minimum for the selected topological ansatz",
                "Derrick balance between quartic and potential energy sectors",
                "convergent radial quadrature and dissipative scale relaxation",
                "failure of scale selection when either balancing sector is removed",
            ],
            "does_not_establish": [
                "the full CAT/EPT energy functional",
                "a stable three-dimensional particle",
                "a physical rest mass or unit conversion",
                "that the selected baby-Skyrme ansatz is Nature's particle sector",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    compact = dict(result)
    for key in ("scan", "relaxation_from_large_scale", "relaxation_from_small_scale"):
        compact[key] = dict(compact[key])
        compact[key].pop("scales", None)
        compact[key].pop("energies", None)
        compact[key].pop("analytic_energies", None)
        compact[key].pop("numerical_energies", None)
    return json.dumps(compact, indent=2, sort_keys=True, default=float) + "\n"
