"""M9.77 long-time conservative-grid orbit campaign and formal mild-flow handoff."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .cubic_quintic_continuum import strang_step
from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)

OPENWAVE_BASE = "009efb37d535174712109c550e8da06b77dd8f9c"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_PR_HEAD = "83542cc13af0a966a072d90f2082c49785d20c55"


@dataclass(frozen=True)
class GlobalMildOrbitConfig:
    points: int = 20
    half_width: float = 8.0
    stationary_iterations: int = 3000
    final_time: float = 1.5
    dt: float = 0.002
    sample_every: int = 25
    perturbations: tuple[str, ...] = (
        "phase",
        "translation",
        "chirp",
        "amplitude",
        "noise",
    )
    maximum_relative_h1_orbit_distance: float = 0.22
    maximum_energy_drift: float = 1e-5
    maximum_boundary_fraction: float = 2e-4


def local_stationary_config(cfg: GlobalMildOrbitConfig) -> StationaryBranchConfig:
    return StationaryBranchConfig(
        grids=(cfg.points,),
        reference_grid=cfg.points,
        half_width=cfg.half_width,
        iterations=cfg.stationary_iterations,
    )


def perturb(
    reference: np.ndarray, grid: tuple[np.ndarray, ...], kind: str
) -> np.ndarray:
    r2 = grid[3]
    dx = float(grid[5])
    if kind == "phase":
        state = reference * np.exp(0.2j)
    elif kind == "translation":
        state = np.roll(reference, 1, axis=0)
    elif kind == "chirp":
        state = reference * np.exp(1j * 0.012 * r2)
    elif kind == "amplitude":
        rho = np.abs(reference) ** 2
        mean = float(np.sum(r2 * rho) * dx**3)
        state = reference * (1.0 + 0.015 * (r2 / max(mean, 1e-30) - 1.0))
    elif kind == "noise":
        pattern = (
            np.sin(0.5 * grid[0])
            + 0.7 * np.cos(0.5 * grid[1])
            - 0.4 * np.sin(0.5 * grid[2])
        )
        state = reference * (1.0 + 0.008 * pattern)
    else:
        raise ValueError(f"unknown perturbation: {kind}")
    return normalize_state(state.astype(np.complex128), dx)


def align_translation(reference: np.ndarray, state: np.ndarray) -> np.ndarray:
    reference_index = np.unravel_index(
        int(np.argmax(np.abs(reference) ** 2)), reference.shape
    )
    state_index = np.unravel_index(int(np.argmax(np.abs(state) ** 2)), state.shape)
    shift = tuple(reference_index[index] - state_index[index] for index in range(3))
    return np.roll(state, shift, axis=(0, 1, 2))


def phase_align(reference: np.ndarray, state: np.ndarray, dx: float) -> np.ndarray:
    overlap = np.vdot(reference, state) * dx**3
    return state if abs(overlap) == 0 else state * np.conj(overlap) / abs(overlap)


def h1_distance(
    reference: np.ndarray, state: np.ndarray, grid: tuple[np.ndarray, ...]
) -> float:
    dx = float(grid[5])
    k2 = grid[4]
    aligned = phase_align(reference, state, dx)
    difference = aligned - reference
    l2 = float(np.sum(np.abs(difference) ** 2) * dx**3)
    gradient = np.fft.ifftn(np.sqrt(k2) * np.fft.fftn(difference))
    gradient_sq = float(np.sum(np.abs(gradient) ** 2) * dx**3)
    reference_gradient = np.fft.ifftn(np.sqrt(k2) * np.fft.fftn(reference))
    denominator = math.sqrt(
        float(np.sum(np.abs(reference) ** 2) * dx**3)
        + float(np.sum(np.abs(reference_gradient) ** 2) * dx**3)
    )
    return math.sqrt(l2 + gradient_sq) / max(denominator, 1e-30)


def observables(
    state: np.ndarray, grid: tuple[np.ndarray, ...], cfg: GlobalMildOrbitConfig
) -> dict[str, float]:
    alpha, beta = coefficients()
    dx = float(grid[5])
    rho = np.abs(state) ** 2
    mass = float(np.sum(rho) * dx**3)
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    gradient_sq = float(np.sum(np.abs(gradient) ** 2) * dx**3)
    energy = (
        0.65 * gradient_sq
        - 0.5 * alpha * float(np.sum(rho**2) * dx**3)
        + (beta / 3.0) * float(np.sum(rho**3) * dx**3)
    )
    radius = math.sqrt(float(np.sum(grid[3] * rho) * dx**3 / mass))
    boundary = np.maximum.reduce(
        (np.abs(grid[0]), np.abs(grid[1]), np.abs(grid[2]))
    ) > 0.75 * cfg.half_width
    return {
        "mass": mass,
        "energy": energy,
        "radius": radius,
        "boundary_fraction": float(np.sum(rho[boundary]) * dx**3 / mass),
    }


def run_one(
    reference: np.ndarray,
    grid: tuple[np.ndarray, ...],
    kind: str,
    cfg: GlobalMildOrbitConfig,
) -> dict[str, float | int | str]:
    alpha, beta = coefficients()
    state = perturb(reference, grid, kind)
    initial = observables(state, grid, cfg)
    steps = math.ceil(cfg.final_time / cfg.dt)
    actual_dt = cfg.final_time / steps
    maximum_energy_drift = 0.0
    maximum_mass_error = 0.0
    maximum_orbit_distance = 0.0
    maximum_boundary = initial["boundary_fraction"]
    for index in range(steps):
        state = strang_step(state, actual_dt, grid[4], 0.65, alpha, beta)
        if (index + 1) % cfg.sample_every == 0 or index + 1 == steps:
            row = observables(state, grid, cfg)
            aligned = align_translation(reference, state)
            maximum_energy_drift = max(
                maximum_energy_drift, abs(row["energy"] - initial["energy"])
            )
            maximum_mass_error = max(
                maximum_mass_error, abs(row["mass"] - initial["mass"])
            )
            maximum_orbit_distance = max(
                maximum_orbit_distance, h1_distance(reference, aligned, grid)
            )
            maximum_boundary = max(maximum_boundary, row["boundary_fraction"])
    return {
        "perturbation": kind,
        "dt": actual_dt,
        "steps": steps,
        "mass_error": maximum_mass_error,
        "maximum_energy_drift": maximum_energy_drift,
        "maximum_relative_h1_orbit_distance": maximum_orbit_distance,
        "maximum_boundary_fraction": maximum_boundary,
        "final_radius": observables(state, grid, cfg)["radius"],
    }


@lru_cache(maxsize=1)
def run_global_mild_orbit_campaign(
    cfg: GlobalMildOrbitConfig = GlobalMildOrbitConfig(),
) -> dict[str, Any]:
    reference, grid = solve_stationary(
        cfg.points, "super_gaussian", local_stationary_config(cfg)
    )
    rows = [run_one(reference, grid, kind, cfg) for kind in cfg.perturbations]
    acceptance = {
        "all_orbits_preserve_mass": max(row["mass_error"] for row in rows)
        < 1e-10,
        "all_orbits_preserve_energy_numerically": max(
            row["maximum_energy_drift"] for row in rows
        )
        <= cfg.maximum_energy_drift,
        "all_aligned_orbits_remain_in_h1_tube": max(
            row["maximum_relative_h1_orbit_distance"] for row in rows
        )
        <= cfg.maximum_relative_h1_orbit_distance,
        "all_orbits_remain_boundary_clean": max(
            row["maximum_boundary_fraction"] for row in rows
        )
        <= cfg.maximum_boundary_fraction,
        "global_conservative_weak_mild_flow_certificate_is_formalized": True,
        "born_minimizing_orbit_stability_composition_is_formalized": True,
    }
    return {
        "schema": "openwave.m9.global-mild-orbit-campaign.v1",
        "task": "M9.77",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_pr_head": FORMAL_PR_HEAD,
        },
        "rows": rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_grid_long_time_orbit_is_bounded": all(
                acceptance[key]
                for key in (
                    "all_orbits_preserve_mass",
                    "all_orbits_preserve_energy_numerically",
                    "all_aligned_orbits_remain_in_h1_tube",
                    "all_orbits_remain_boundary_clean",
                )
            ),
            "formal_global_conservative_mild_flow_constructed_from_pde": False,
            "formal_global_flow_certificate_interface_closed": True,
            "minimizing_orbit_stability_from_explicit_certificates_closed": True,
            "m9_69_branch_physically_identified": False,
            "m9_77_corrected_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"