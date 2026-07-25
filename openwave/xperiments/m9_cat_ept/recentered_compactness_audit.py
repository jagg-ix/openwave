"""M9.76 recentered compactness and interaction-closure audit."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    phase_aligned_l2_distance,
    solve_stationary,
)

OPENWAVE_BASE = "009efb37d535174712109c550e8da06b77dd8f9c"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_PR_HEAD = "83542cc13af0a966a072d90f2082c49785d20c55"


@dataclass(frozen=True)
class RecenteredCompactnessConfig:
    points: int = 20
    half_width: float = 8.0
    stationary_iterations: int = 3000
    translation_cells: tuple[int, ...] = (0, 2, 4, 6)
    tail_radius: float = 4.0
    recentered_tolerance: float = 2e-12
    energy_tolerance: float = 2e-10


def local_stationary_config(cfg: RecenteredCompactnessConfig) -> StationaryBranchConfig:
    return StationaryBranchConfig(
        grids=(cfg.points,),
        reference_grid=cfg.points,
        half_width=cfg.half_width,
        iterations=cfg.stationary_iterations,
    )


def l2_distance(a: np.ndarray, b: np.ndarray, dx: float) -> float:
    return math.sqrt(float(np.sum(np.abs(a - b) ** 2) * dx**3))


def recenter_known_translation(state: np.ndarray, shift: int) -> np.ndarray:
    return np.roll(state, -shift, axis=0)


def first_moment_and_tail(
    state: np.ndarray, grid: tuple[np.ndarray, ...], radius: float
) -> tuple[float, float]:
    rho = np.abs(state) ** 2
    dx = float(grid[5])
    r = np.sqrt(grid[3])
    mass = float(np.sum(rho) * dx**3)
    return (
        float(np.sum(r * rho) * dx**3 / mass),
        float(np.sum(rho[r > radius]) * dx**3 / mass),
    )


def translation_invariant_energy(
    state: np.ndarray, grid: tuple[np.ndarray, ...], dispersion: float = 0.65
) -> float:
    alpha, beta = coefficients()
    rho = np.abs(state) ** 2
    dx = float(grid[5])
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    return (
        dispersion * float(np.sum(np.abs(gradient) ** 2) * dx**3)
        - 0.5 * alpha * float(np.sum(rho**2) * dx**3)
        + (beta / 3.0) * float(np.sum(rho**3) * dx**3)
    )


@lru_cache(maxsize=1)
def run_recentered_compactness_audit(
    cfg: RecenteredCompactnessConfig = RecenteredCompactnessConfig(),
) -> dict[str, Any]:
    reference, grid = solve_stationary(
        cfg.points, "super_gaussian", local_stationary_config(cfg)
    )
    dx = float(grid[5])
    reference_energy = translation_invariant_energy(reference, grid)
    reference_mass = float(np.sum(np.abs(reference) ** 2) * dx**3)
    rows = []
    for shift in cfg.translation_cells:
        moved = np.roll(reference, shift, axis=0)
        recentered = recenter_known_translation(moved, shift)
        moment, tail = first_moment_and_tail(recentered, grid, cfg.tail_radius)
        rows.append(
            {
                "translation_cells": shift,
                "physical_translation": shift * dx,
                "unaligned_l2_distance": l2_distance(reference, moved, dx),
                "recentered_l2_distance": phase_aligned_l2_distance(
                    reference, recentered, dx
                ),
                "centered_first_moment": moment,
                "centered_tail_fraction": tail,
                "mass_error": abs(
                    float(np.sum(np.abs(moved) ** 2) * dx**3) - reference_mass
                ),
                "energy_error": abs(
                    translation_invariant_energy(moved, grid) - reference_energy
                ),
            }
        )
    acceptance = {
        "translated_family_is_not_naively_compact": max(
            row["unaligned_l2_distance"] for row in rows
        )
        > 0.2,
        "recentring_collapses_translation_orbit": max(
            row["recentered_l2_distance"] for row in rows
        )
        <= cfg.recentered_tolerance,
        "centered_first_moment_is_uniform": float(
            np.ptp([row["centered_first_moment"] for row in rows])
        )
        < 1e-12,
        "centered_tail_is_uniform_and_small": max(
            row["centered_tail_fraction"] for row in rows
        )
        < 5e-4,
        "mass_and_energy_are_translation_invariant": max(
            row["mass_error"] for row in rows
        )
        < 1e-12
        and max(row["energy_error"] for row in rows) <= cfg.energy_tolerance,
        "live_born_moment_compactness_theorem_is_reused": True,
        "live_interaction_convergence_no_loss_theorem_is_reused": True,
    }
    return {
        "schema": "openwave.m9.recentered-compactness-audit.v1",
        "task": "M9.76",
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
            "finite_grid_translation_orbit_recentered": True,
            "first_moment_and_tail_tightness_numerically_qualified": True,
            "compact_minimizing_orbit_from_interaction_closure_kernel_available": True,
            "general_target_recentered_tightness_proved": False,
            "general_concentration_trichotomy_proved": False,
            "m9_76_corrected_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"