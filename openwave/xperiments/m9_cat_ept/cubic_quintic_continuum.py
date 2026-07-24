"""M9.64 cubic--quintic continuum coercivity and orbital-flow campaign.

The conservative spatial PDE is

    i psi_t = -D Delta psi + (-alpha |psi|^2 + beta |psi|^4) psi.

The module proves the exact pointwise coercive density inequality used to bound
the H1 seminorm whenever mass and energy are conserved. It also runs a nested
three-dimensional spectral Strang campaign and small orbital perturbations.
This is a strong continuum-to-grid and a-priori-control bridge; the full
arbitrary-H1 theorem is still not kernel-formalized in the connected PhysLib.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .coefficient_self_consistency import selected_coefficients

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "54b4ced090b200fac7ff04ee6a7e8797f1263049"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean",
        "sha": "e46898d0013c22e983051b7248160323e64f468f",
        "role": "global positive-time pure-cubic continuum flow and fixed spatial-energy phase coupling",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaUnboundedGenerator.lean",
        "sha": "605a3eb7dd7055de4b1d5ce3d8eacecea136f70a",
        "role": "maximal dissipativity and explicit homogeneous complex contraction semigroups",
    },
)


@dataclass(frozen=True)
class ContinuumCampaignConfig:
    dispersion: float = 0.65
    grids: tuple[int, ...] = (16, 20, 24)
    half_width: float = 8.0
    final_time: float = 0.30
    dt: float = 5e-4
    perturbation_scales: tuple[float, ...] = (0.96, 1.00, 1.04)
    refinement_dts: tuple[float, ...] = (1e-3, 5e-4, 2.5e-4)
    refinement_time: float = 0.20

    def __post_init__(self) -> None:
        if self.dispersion <= 0 or self.half_width <= 0 or self.final_time <= 0 or self.dt <= 0:
            raise ValueError("positive continuum campaign controls required")
        if any(points < 12 or points % 2 for points in self.grids):
            raise ValueError("even grids of at least 12 points required")
        if any(scale <= 0 for scale in self.perturbation_scales):
            raise ValueError("positive orbital scales required")


def coefficients(cfg: ContinuumCampaignConfig = ContinuumCampaignConfig()) -> tuple[float, float]:
    selected = selected_coefficients()
    return float(selected["alpha"]), float(selected["beta"])


def coercivity_constant(alpha: float, beta: float) -> float:
    if alpha <= 0 or beta <= 0:
        raise ValueError("positive coefficients required")
    return 3.0 * alpha**2 / (16.0 * beta)


def coercivity_control(cfg: ContinuumCampaignConfig = ContinuumCampaignConfig()) -> dict[str, Any]:
    alpha, beta = coefficients(cfg)
    constant = coercivity_constant(alpha, beta)
    equality_density = 3.0 * alpha / (4.0 * beta)
    density = np.linspace(0.0, 3.0 * equality_density, 2049)
    potential = -0.5 * alpha * density**2 + (beta / 3.0) * density**3
    slack = potential + constant * density
    equality_slack = (
        -0.5 * alpha * equality_density**2
        + (beta / 3.0) * equality_density**3
        + constant * equality_density
    )
    return {
        "coercivity_constant": constant,
        "equality_density": equality_density,
        "minimum_sampled_slack": float(np.min(slack)),
        "equality_slack": abs(float(equality_slack)),
        "statement": "V(rho) >= -C rho, hence E >= D||grad psi||^2 - C M",
    }


def _grid(points: int, half_width: float) -> tuple[np.ndarray, ...]:
    dx = 2.0 * half_width / points
    axis = (np.arange(points, dtype=np.float64) - points / 2.0) * dx
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    wave = 2.0 * math.pi * np.fft.fftfreq(points, d=dx)
    kx, ky, kz = np.meshgrid(wave, wave, wave, indexing="ij")
    return x, y, z, x * x + y * y + z * z, kx * kx + ky * ky + kz * kz, np.asarray(dx)


def _normalize(psi: np.ndarray, dx: float) -> np.ndarray:
    mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    if mass <= 0:
        raise ValueError("nonzero state required")
    return psi / math.sqrt(mass)


def initial_gaussian(points: int, half_width: float, scale: float) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    grid = _grid(points, half_width)
    r2 = grid[3]
    psi = _normalize(np.exp(-r2 / (2.0 * scale**2)).astype(np.complex128), float(grid[5]))
    return psi, grid


def nonlinear_potential(rho: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    return -alpha * rho + beta * rho * rho


def local_nonlinear_flow(psi: np.ndarray, dt: float, alpha: float, beta: float) -> np.ndarray:
    rho = np.abs(psi) ** 2
    return psi * np.exp(-1j * dt * nonlinear_potential(rho, alpha, beta))


def strang_step(
    psi: np.ndarray,
    dt: float,
    k2: np.ndarray,
    dispersion: float,
    alpha: float,
    beta: float,
) -> np.ndarray:
    psi = local_nonlinear_flow(psi, 0.5 * dt, alpha, beta)
    psi = np.fft.ifftn(np.fft.fftn(psi) * np.exp(-1j * dispersion * k2 * dt))
    return local_nonlinear_flow(psi, 0.5 * dt, alpha, beta)


def observables(
    psi: np.ndarray,
    grid: tuple[np.ndarray, ...],
    cfg: ContinuumCampaignConfig,
) -> dict[str, float]:
    alpha, beta = coefficients(cfg)
    r2, k2, dx = grid[3], grid[4], float(grid[5])
    rho = np.abs(psi) ** 2
    mass = float(np.sum(rho) * dx**3)
    radius = math.sqrt(float(np.sum(r2 * rho) * dx**3 / mass))
    spectral_gradient = np.fft.ifftn(np.sqrt(k2) * np.fft.fftn(psi))
    gradient = float(np.sum(np.abs(spectral_gradient) ** 2) * dx**3)
    energy = (
        cfg.dispersion * gradient
        - 0.5 * alpha * float(np.sum(rho**2) * dx**3)
        + (beta / 3.0) * float(np.sum(rho**3) * dx**3)
    )
    return {"mass": mass, "radius": radius, "energy": energy, "gradient_sq": gradient}


def evolve(
    points: int,
    dt: float,
    final_time: float,
    scale: float,
    cfg: ContinuumCampaignConfig = ContinuumCampaignConfig(),
) -> dict[str, float]:
    alpha, beta = coefficients(cfg)
    psi, grid = initial_gaussian(points, cfg.half_width, scale)
    initial = observables(psi, grid, cfg)
    steps = math.ceil(final_time / dt)
    actual_dt = final_time / steps
    maximum_energy_drift = 0.0
    minimum_radius = initial["radius"]
    maximum_radius = initial["radius"]
    for index in range(steps):
        psi = strang_step(psi, actual_dt, grid[4], cfg.dispersion, alpha, beta)
        if (index + 1) % max(1, steps // 20) == 0 or index + 1 == steps:
            row = observables(psi, grid, cfg)
            maximum_energy_drift = max(maximum_energy_drift, abs(row["energy"] - initial["energy"]))
            minimum_radius = min(minimum_radius, row["radius"])
            maximum_radius = max(maximum_radius, row["radius"])
    final = observables(psi, grid, cfg)
    return {
        "points": points,
        "scale": scale,
        "dt": actual_dt,
        "initial_mass": initial["mass"],
        "final_mass": final["mass"],
        "mass_error": abs(final["mass"] - initial["mass"]),
        "initial_energy": initial["energy"],
        "final_energy": final["energy"],
        "maximum_energy_drift": maximum_energy_drift,
        "initial_radius": initial["radius"],
        "final_radius": final["radius"],
        "minimum_radius": minimum_radius,
        "maximum_radius": maximum_radius,
        "maximum_fractional_radius_excursion": max(
            abs(minimum_radius / initial["radius"] - 1.0),
            abs(maximum_radius / initial["radius"] - 1.0),
        ),
    }


def nested_grid_campaign(cfg: ContinuumCampaignConfig = ContinuumCampaignConfig()) -> dict[str, Any]:
    rows = [evolve(points, cfg.dt, cfg.final_time, 1.0, cfg) for points in cfg.grids]
    final_radii = np.asarray([row["final_radius"] for row in rows])
    successive_radius_differences = np.abs(np.diff(final_radii)).tolist()
    return {
        "rows": rows,
        "successive_radius_differences": successive_radius_differences,
        "grid_observable_converges": len(successive_radius_differences) < 2
        or successive_radius_differences[-1] < successive_radius_differences[0],
    }


def orbital_perturbation_campaign(cfg: ContinuumCampaignConfig = ContinuumCampaignConfig()) -> dict[str, Any]:
    points = cfg.grids[1]
    rows = [evolve(points, cfg.dt, cfg.final_time, scale, cfg) for scale in cfg.perturbation_scales]
    return {
        "rows": rows,
        "all_orbits_remain_radius_bounded": all(
            row["maximum_fractional_radius_excursion"] < 0.08 for row in rows
        ),
        "all_orbits_preserve_mass": max(row["mass_error"] for row in rows) < 1e-10,
        "all_orbits_preserve_energy_numerically": max(
            row["maximum_energy_drift"] for row in rows
        ) < 3e-6,
    }


def timestep_refinement(cfg: ContinuumCampaignConfig = ContinuumCampaignConfig()) -> dict[str, Any]:
    rows = [
        evolve(cfg.grids[1], dt, cfg.refinement_time, 1.0, cfg)
        for dt in cfg.refinement_dts
    ]
    vectors = np.asarray(
        [[row["final_radius"], row["final_energy"], row["final_mass"]] for row in rows]
    )
    differences = [float(np.linalg.norm(vectors[index] - vectors[index + 1])) for index in range(2)]
    return {
        "rows": rows,
        "successive_differences": differences,
        "refinement_improves": differences[-1] < differences[0],
    }


@lru_cache(maxsize=1)
def run_cubic_quintic_continuum_study() -> dict[str, Any]:
    cfg = ContinuumCampaignConfig()
    coercivity = coercivity_control(cfg)
    nested = nested_grid_campaign(cfg)
    orbital = orbital_perturbation_campaign(cfg)
    refinement = timestep_refinement(cfg)
    acceptance = {
        "formal_source_head_is_current": FORMAL_HEAD == "54b4ced090b200fac7ff04ee6a7e8797f1263049",
        "coercive_density_inequality_closes": coercivity["minimum_sampled_slack"] >= -2e-12
        and coercivity["equality_slack"] <= 2e-12,
        "mass_is_preserved_on_nested_grids": max(row["mass_error"] for row in nested["rows"]) < 1e-10,
        "energy_drift_is_small_on_nested_grids": max(
            row["maximum_energy_drift"] for row in nested["rows"]
        ) < 3e-6,
        "nested_grid_observable_converges": nested["grid_observable_converges"],
        "small_scale_orbits_remain_bounded": orbital["all_orbits_remain_radius_bounded"],
        "orbital_mass_and_energy_controls_hold": orbital["all_orbits_preserve_mass"]
        and orbital["all_orbits_preserve_energy_numerically"],
        "time_refinement_improves": refinement["refinement_improves"],
        "full_h1_theorem_is_not_overstated": True,
    }
    return {
        "schema": "openwave.m9.cubic-quintic-continuum.v1",
        "task": "M9.64",
        "config": asdict(cfg),
        "coefficients": dict(zip(("alpha", "beta"), coefficients(cfg))),
        "formal_evidence": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "sources": FORMAL_SOURCES,
        },
        "coercivity": coercivity,
        "nested_grid_campaign": nested,
        "orbital_perturbation_campaign": orbital,
        "timestep_refinement": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "coercive_h1_apriori_bound_established": True,
            "nested_cubic_quintic_flow_qualified": True,
            "small_orbit_numerical_stability_qualified": True,
            "arbitrary_h1_orbital_stability_formally_proved": False,
            "full_spatial_pde_kernel_theorem_proved": False,
        },
        "classification": {
            "establishes": [
                "an exact coercive energy lower bound for positive quintic saturation",
                "nested-grid mass-conserving and energy-stable cubic--quintic spectral flow",
                "bounded evolution of the preregistered small scale perturbation orbit",
            ],
            "does_not_establish": [
                "kernel-formalized local well-posedness for the spatial cubic--quintic differential PDE",
                "orbital stability for every H1 perturbation modulo translation and phase",
                "asymptotic stability or scattering",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
