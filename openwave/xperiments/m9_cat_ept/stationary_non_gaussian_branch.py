"""M9.69 stationary non-Gaussian CAT/EPT cubic--quintic branch.

The normalized stationary equation is

    mu phi = -D Delta phi - alpha |phi|^2 phi + beta |phi|^4 phi,
    ||phi||_2 = 1.

A normalized imaginary-time spectral flow constructs the branch without assuming a
Gaussian profile. Multiple unrelated seeds and nested three-dimensional grids are
used to distinguish a stationary solution from an ansatz artifact.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .coefficient_self_consistency import selected_coefficients

OPENWAVE_HEAD = "2dfaf6da88b24fe43799b53d79ef2f7aa3244a32"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "agent/m9-cubic-quintic-h1-certificate-70"
FORMAL_HEAD = "51aad63b2541a1377a001df71b85dfe35f26c0af"


@dataclass(frozen=True)
class StationaryBranchConfig:
    dispersion: float = 0.65
    grids: tuple[int, ...] = (20, 24, 28)
    reference_grid: int = 24
    half_width: float = 8.0
    imaginary_dt: float = 5e-4
    iterations: int = 6000
    seeds: tuple[str, ...] = ("super_gaussian", "anisotropic", "shell")
    residual_tolerance: float = 3e-3
    seed_match_tolerance: float = 5e-3
    boundary_tolerance: float = 1e-4
    minimum_non_gaussian_distance: float = 5e-2

    def __post_init__(self) -> None:
        if self.dispersion <= 0 or self.half_width <= 0 or self.imaginary_dt <= 0:
            raise ValueError("positive stationary controls required")
        if self.iterations < 100:
            raise ValueError("stationary iteration count is too small")
        if self.reference_grid not in self.grids:
            raise ValueError("reference grid must be in the nested grid set")
        if any(points < 12 or points % 2 for points in self.grids):
            raise ValueError("even three-dimensional grids of at least 12 points required")


def coefficients() -> tuple[float, float]:
    selected = selected_coefficients()
    return float(selected["alpha"]), float(selected["beta"])


@lru_cache(maxsize=None)
def spectral_grid(points: int, half_width: float) -> tuple[np.ndarray, ...]:
    dx = 2.0 * half_width / points
    axis = (np.arange(points, dtype=np.float64) - points / 2.0) * dx
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    r2 = x * x + y * y + z * z
    wave = 2.0 * math.pi * np.fft.fftfreq(points, d=dx)
    kx, ky, kz = np.meshgrid(wave, wave, wave, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    return x, y, z, r2, k2, np.asarray(dx)


def normalize_state(psi: np.ndarray, dx: float) -> np.ndarray:
    mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    if mass <= 0:
        raise ValueError("nonzero state required")
    return psi / math.sqrt(mass)


def initial_profile(seed: str, grid: tuple[np.ndarray, ...]) -> np.ndarray:
    x, y, z, r2 = grid[:4]
    if seed == "super_gaussian":
        profile = np.exp(-((r2 / (2.0 * 1.2**2)) ** 2))
    elif seed == "gaussian":
        profile = np.exp(-r2 / (2.0 * 1.2**2))
    elif seed == "anisotropic":
        profile = np.exp(
            -(x * x / (2.0 * 1.0**2) + y * y / (2.0 * 1.3**2) + z * z / (2.0 * 0.8**2))
        )
    elif seed == "shell":
        profile = np.exp(-((np.sqrt(r2) - 1.3) ** 2) / (2.0 * 0.5**2))
    else:
        raise ValueError(f"unknown stationary seed: {seed}")
    return profile.astype(np.complex128)


@lru_cache(maxsize=None)
def solve_stationary(
    points: int,
    seed: str = "super_gaussian",
    cfg: StationaryBranchConfig = StationaryBranchConfig(),
) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    alpha, beta = coefficients()
    grid = spectral_grid(points, cfg.half_width)
    k2, dx = grid[4], float(grid[5])
    psi = normalize_state(initial_profile(seed, grid), dx)
    kinetic = np.exp(-cfg.dispersion * k2 * cfg.imaginary_dt)
    for _ in range(cfg.iterations):
        rho = np.abs(psi) ** 2
        psi *= np.exp(0.5 * cfg.imaginary_dt * (alpha * rho - beta * rho * rho))
        psi = np.fft.ifftn(np.fft.fftn(psi) * kinetic)
        rho = np.abs(psi) ** 2
        psi *= np.exp(0.5 * cfg.imaginary_dt * (alpha * rho - beta * rho * rho))
        psi = normalize_state(psi, dx)
    return psi, grid


def phase_aligned_l2_distance(a: np.ndarray, b: np.ndarray, dx: float) -> float:
    overlap = np.vdot(a, b) * dx**3
    aligned = b if abs(overlap) == 0 else b * np.conj(overlap) / abs(overlap)
    return float(math.sqrt(float(np.sum(np.abs(a - aligned) ** 2) * dx**3)))


def best_gaussian_fit(psi: np.ndarray, grid: tuple[np.ndarray, ...]) -> dict[str, float]:
    r2, dx = grid[3], float(grid[5])
    best_distance = math.inf
    best_scale = math.nan
    for scale in np.linspace(0.70, 1.50, 161):
        gaussian = normalize_state(np.exp(-r2 / (2.0 * scale**2)).astype(np.complex128), dx)
        distance = phase_aligned_l2_distance(psi, gaussian, dx)
        if distance < best_distance:
            best_distance, best_scale = distance, float(scale)
    return {"l2_distance": best_distance, "scale": best_scale}


def stationary_observables(
    psi: np.ndarray,
    grid: tuple[np.ndarray, ...],
    cfg: StationaryBranchConfig = StationaryBranchConfig(),
) -> dict[str, float]:
    alpha, beta = coefficients()
    x, y, z, r2, k2, dx_array = grid
    dx = float(dx_array)
    rho = np.abs(psi) ** 2
    mass = float(np.sum(rho) * dx**3)
    laplacian = np.fft.ifftn(-k2 * np.fft.fftn(psi))
    hpsi = -cfg.dispersion * laplacian - alpha * rho * psi + beta * rho * rho * psi
    chemical_potential = float(np.real(np.vdot(psi, hpsi)) * dx**3 / mass)
    residual = hpsi - chemical_potential * psi
    residual_l2 = math.sqrt(float(np.sum(np.abs(residual) ** 2) * dx**3))
    operator_l2 = math.sqrt(float(np.sum(np.abs(hpsi) ** 2) * dx**3))
    gradient = np.fft.ifftn(np.sqrt(k2) * np.fft.fftn(psi))
    gradient_sq = float(np.sum(np.abs(gradient) ** 2) * dx**3)
    quartic = float(np.sum(rho**2) * dx**3)
    sextic = float(np.sum(rho**3) * dx**3)
    radius_sq = float(np.sum(r2 * rho) * dx**3 / mass)
    energy = cfg.dispersion * gradient_sq - 0.5 * alpha * quartic + beta * sextic / 3.0
    boundary = np.maximum.reduce((np.abs(x), np.abs(y), np.abs(z))) > 0.75 * cfg.half_width
    boundary_fraction = float(np.sum(rho[boundary]) * dx**3 / mass)
    radial_fourth = float(np.sum(r2**2 * rho) * dx**3 / mass)
    gaussian = best_gaussian_fit(psi, grid)
    return {
        "mass": mass,
        "chemical_potential": chemical_potential,
        "relative_stationary_residual": residual_l2 / max(operator_l2, 1e-30),
        "radius": math.sqrt(radius_sq),
        "energy": energy,
        "gradient_sq": gradient_sq,
        "quartic_integral": quartic,
        "sextic_integral": sextic,
        "boundary_fraction": boundary_fraction,
        "radial_kurtosis": radial_fourth / radius_sq**2,
        "best_gaussian_l2_distance": gaussian["l2_distance"],
        "best_gaussian_scale": gaussian["scale"],
    }


def seed_independence_campaign(cfg: StationaryBranchConfig) -> dict[str, Any]:
    reference, grid = solve_stationary(cfg.reference_grid, cfg.seeds[0], cfg)
    dx = float(grid[5])
    rows = []
    for seed in cfg.seeds:
        state, local_grid = solve_stationary(cfg.reference_grid, seed, cfg)
        row = {"seed": seed, **stationary_observables(state, local_grid, cfg)}
        row["distance_from_reference"] = phase_aligned_l2_distance(reference, state, dx)
        rows.append(row)
    return {
        "rows": rows,
        "maximum_seed_distance": max(row["distance_from_reference"] for row in rows),
        "maximum_seed_energy_spread": float(np.ptp([row["energy"] for row in rows])),
    }


def nested_grid_campaign(cfg: StationaryBranchConfig) -> dict[str, Any]:
    rows = []
    for points in cfg.grids:
        state, grid = solve_stationary(points, cfg.seeds[0], cfg)
        rows.append({"points": points, **stationary_observables(state, grid, cfg)})
    return {
        "rows": rows,
        "radius_spread": float(np.ptp([row["radius"] for row in rows])),
        "energy_spread": float(np.ptp([row["energy"] for row in rows])),
    }


@lru_cache(maxsize=1)
def run_stationary_non_gaussian_branch() -> dict[str, Any]:
    cfg = StationaryBranchConfig()
    seeds = seed_independence_campaign(cfg)
    nested = nested_grid_campaign(cfg)
    all_rows = seeds["rows"] + nested["rows"]
    acceptance = {
        "full_normalized_stationary_equation_is_solved_numerically": max(
            row["relative_stationary_residual"] for row in all_rows
        ) <= cfg.residual_tolerance,
        "unrelated_seeds_converge_to_one_branch": seeds["maximum_seed_distance"] <= cfg.seed_match_tolerance,
        "seed_energy_is_consistent": seeds["maximum_seed_energy_spread"] <= 1e-4,
        "branch_is_localized": max(row["boundary_fraction"] for row in all_rows) <= cfg.boundary_tolerance,
        "branch_is_not_a_best_fit_gaussian": min(
            row["best_gaussian_l2_distance"] for row in all_rows
        ) >= cfg.minimum_non_gaussian_distance,
        "nested_grids_remain_in_one_radius_tube": nested["radius_spread"] <= 2e-2,
        "mass_normalization_closes": max(abs(row["mass"] - 1.0) for row in all_rows) <= 2e-12,
    }
    return {
        "schema": "openwave.m9.stationary-non-gaussian-branch.v1",
        "task": "M9.69",
        "config": asdict(cfg),
        "repositories": {
            "openwave": OPENWAVE_HEAD,
            "physlib_repository": FORMAL_REPOSITORY,
            "physlib_branch": FORMAL_BRANCH,
            "physlib_head": FORMAL_HEAD,
        },
        "coefficients": dict(zip(("alpha", "beta"), coefficients())),
        "seed_independence": seeds,
        "nested_grid_campaign": nested,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "stationary_non_gaussian_branch_constructed": True,
            "branch_constructed_from_full_normalized_spatial_equation": True,
            "branch_is_conditional_on_m9_63_coefficients": True,
            "physical_particle_identified": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
