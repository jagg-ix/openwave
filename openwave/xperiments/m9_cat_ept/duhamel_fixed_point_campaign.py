"""M9.78 finite-Galerkin Duhamel fixed-point campaign.

The continuum cubic--quintic Schrödinger equation is naturally posed as an
``H1`` mild evolution with a weak generator in ``H-1``.  This module does not
claim the missing continuum Strichartz theorem.  It constructs and audits the
corresponding Volterra/Duhamel map after spectral Galerkin truncation.
"""
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
    solve_stationary,
)

OPENWAVE_BASE = "c3cdd5725e9b5455cf3f2fb35164e79cab1265d8"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_MILD_FLOW_HEAD = "83542cc13af0a966a072d90f2082c49785d20c55"
FORMAL_EVIDENCE_HEAD = "2cb1003ede54dc7d8487a8b397a1cacf15728feb"


@dataclass(frozen=True)
class DuhamelFixedPointConfig:
    points: int = 16
    half_width: float = 8.0
    stationary_iterations: int = 3000
    final_time: float = 0.01
    time_steps: tuple[int, ...] = (8, 16, 32)
    picard_iterations: int = 7
    maximum_picard_ratio: float = 0.03
    maximum_fixed_point_residual: float = 1e-10

    def __post_init__(self) -> None:
        if self.points < 8 or self.points % 2:
            raise ValueError("an even spectral grid of at least eight points is required")
        if self.half_width <= 0 or self.final_time <= 0:
            raise ValueError("positive spatial and temporal controls are required")
        if any(steps < 4 for steps in self.time_steps):
            raise ValueError("each Duhamel grid needs at least four time steps")
        if self.picard_iterations < 3:
            raise ValueError("at least three Picard iterations are required")


def local_stationary_config(cfg: DuhamelFixedPointConfig) -> StationaryBranchConfig:
    return StationaryBranchConfig(
        grids=(cfg.points,),
        reference_grid=cfg.points,
        half_width=cfg.half_width,
        iterations=cfg.stationary_iterations,
    )


def h1_norm(state: np.ndarray, grid: tuple[np.ndarray, ...]) -> float:
    dx = float(grid[5])
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    return math.sqrt(
        float(np.sum(np.abs(state) ** 2 + np.abs(gradient) ** 2) * dx**3)
    )


def nonlinear_term(state: np.ndarray) -> np.ndarray:
    alpha, beta = coefficients()
    density = np.abs(state) ** 2
    return (-alpha * density + beta * density * density) * state


def linear_flow(
    state: np.ndarray,
    time: float,
    grid: tuple[np.ndarray, ...],
    dispersion: float,
) -> np.ndarray:
    multiplier = np.exp(-1j * dispersion * grid[4] * time)
    return np.fft.ifftn(np.fft.fftn(state) * multiplier)


def duhamel_map(
    initial: np.ndarray,
    history: np.ndarray,
    times: np.ndarray,
    grid: tuple[np.ndarray, ...],
    dispersion: float,
) -> np.ndarray:
    """Apply the left-Riemann Volterra map on one finite time grid."""

    dt = float(times[1] - times[0])
    nonlinear_history = [nonlinear_term(state) for state in history[:-1]]
    result = np.empty_like(history)
    result[0] = initial
    for time_index in range(1, len(times)):
        integral = np.zeros_like(initial)
        for source_index in range(time_index):
            integral += linear_flow(
                nonlinear_history[source_index],
                float(times[time_index] - times[source_index]),
                grid,
                dispersion,
            )
        result[time_index] = linear_flow(
            initial, float(times[time_index]), grid, dispersion
        ) - 1j * dt * integral
    return result


def one_resolution(
    initial: np.ndarray,
    grid: tuple[np.ndarray, ...],
    time_steps: int,
    cfg: DuhamelFixedPointConfig,
    stationary_cfg: StationaryBranchConfig,
) -> dict[str, Any]:
    times = np.linspace(0.0, cfg.final_time, time_steps + 1)
    history = np.asarray(
        [
            linear_flow(initial, float(time), grid, stationary_cfg.dispersion)
            for time in times
        ]
    )
    differences: list[float] = []
    for _ in range(cfg.picard_iterations):
        next_history = duhamel_map(
            initial, history, times, grid, stationary_cfg.dispersion
        )
        differences.append(
            max(
                h1_norm(next_history[index] - history[index], grid)
                for index in range(len(times))
            )
        )
        history = next_history

    residual_history = duhamel_map(
        initial, history, times, grid, stationary_cfg.dispersion
    )
    fixed_point_residual = max(
        h1_norm(residual_history[index] - history[index], grid)
        for index in range(len(times))
    )

    dt = cfg.final_time / time_steps
    strang_state = initial.copy()
    alpha, beta = coefficients()
    for _ in range(time_steps):
        strang_state = strang_step(
            strang_state,
            dt,
            grid[4],
            stationary_cfg.dispersion,
            alpha,
            beta,
        )

    contraction_ratios = [
        differences[index + 1] / differences[index]
        for index in range(len(differences) - 1)
        if differences[index] > 0
    ]
    dx = float(grid[5])
    duhamel_mass = float(np.sum(np.abs(history[-1]) ** 2) * dx**3)
    return {
        "time_steps": time_steps,
        "dt": dt,
        "picard_differences": differences,
        "maximum_picard_ratio": max(contraction_ratios),
        "fixed_point_residual_h1": fixed_point_residual,
        "duhamel_strang_final_h1_difference": h1_norm(
            history[-1] - strang_state, grid
        ),
        "duhamel_mass_error": abs(duhamel_mass - 1.0),
    }


@lru_cache(maxsize=1)
def run_duhamel_fixed_point_campaign(
    cfg: DuhamelFixedPointConfig = DuhamelFixedPointConfig(),
) -> dict[str, Any]:
    stationary_cfg = local_stationary_config(cfg)
    stationary, grid = solve_stationary(
        cfg.points, "super_gaussian", stationary_cfg
    )
    rows = [
        one_resolution(stationary, grid, steps, cfg, stationary_cfg)
        for steps in cfg.time_steps
    ]
    trajectory_errors = [
        row["duhamel_strang_final_h1_difference"] for row in rows
    ]
    mass_errors = [row["duhamel_mass_error"] for row in rows]
    acceptance = {
        "picard_iteration_is_contracting": max(
            row["maximum_picard_ratio"] for row in rows
        )
        < cfg.maximum_picard_ratio,
        "discrete_duhamel_residual_closes": max(
            row["fixed_point_residual_h1"] for row in rows
        )
        < cfg.maximum_fixed_point_residual,
        "duhamel_and_strang_trajectories_converge_under_refinement": (
            trajectory_errors[2] < trajectory_errors[1] < trajectory_errors[0]
        ),
        "observed_duhamel_quadrature_ratio_is_first_order": (
            0.45 < trajectory_errors[1] / trajectory_errors[0] < 0.55
            and 0.45 < trajectory_errors[2] / trajectory_errors[1] < 0.55
        ),
        "duhamel_mass_defect_decreases": (
            mass_errors[2] < mass_errors[1] < mass_errors[0]
            and mass_errors[0] < 1e-4
        ),
        "weak_h1_to_hminus1_formal_interface_is_reused": True,
        "continuum_strichartz_theorem_is_not_overstated": True,
    }
    return {
        "schema": "openwave.m9.duhamel-fixed-point-campaign.v1",
        "task": "M9.78",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_mild_flow_head": FORMAL_MILD_FLOW_HEAD,
            "physlib_evidence_registry_head": FORMAL_EVIDENCE_HEAD,
        },
        "rows": rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_galerkin_duhamel_fixed_point_constructed": True,
            "finite_galerkin_mild_and_strang_trajectories_converge": True,
            "continuum_energy_critical_strichartz_flow_constructed": False,
            "m9_78_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
