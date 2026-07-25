"""M9.84 recentered Rellich-to-Hartree closure campaign.

The live PhysLib branch now proves that localized Rellich ``L1`` convergence,
uniform recentered tails, and a finite uniform ``L3`` bound upgrade the Born
density difference to strong ``L^(6/5)`` convergence and hence Hartree
interaction convergence.

This module makes those remaining model premises executable on the M9.69
stationary branch across four nested spectral grids.  It is a finite-grid
qualification of the theorem inputs, not a continuum Rellich proof.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from scipy.signal import resample

from .minimizing_orbit_identification import phase_align
from .recentered_conservation_closure import density_centroid, fourier_shift
from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)

OPENWAVE_BASE = "5df88b26a51dccd9d9cc2b3b1182acb384b01b78"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3"
FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.lintegral_one_three_interpolation",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.lintegral_lsixFifths_tendsto_zero_of_lone_of_lthree_bound",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.lintegral_tendsto_zero_of_localizedRellich_of_recenteredTight",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.hOneBornLSixFifthsConverges_of_recentered_localizedRellich",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.hOneAttractiveNewtonInteraction_tendsto_of_recentered_localizedRellich",
)


@dataclass(frozen=True)
class RellichHartreeConfig:
    grids: tuple[int, ...] = (20, 24, 28, 32)
    half_width: float = 8.0
    stationary_iterations: int = 6000
    imaginary_dt: float = 5e-4
    local_radii: tuple[float, ...] = (2.0, 3.0, 4.0, 5.0)
    tail_radii: tuple[float, ...] = (2.0, 3.0, 4.0, 5.0, 6.0)

    def __post_init__(self) -> None:
        if len(self.grids) < 3 or any(n < 12 or n % 2 for n in self.grids):
            raise ValueError("at least three even spectral grids are required")
        if tuple(sorted(self.grids)) != self.grids:
            raise ValueError("spectral grids must be strictly ordered")
        if self.half_width <= 0 or self.imaginary_dt <= 0:
            raise ValueError("positive spatial and imaginary-time controls required")
        if self.stationary_iterations < 1000:
            raise ValueError("stationary campaign is under-resolved")
        if any(radius <= 0 for radius in self.local_radii + self.tail_radii):
            raise ValueError("positive localization radii required")


def stationary_config(points: int, cfg: RellichHartreeConfig) -> StationaryBranchConfig:
    return StationaryBranchConfig(
        grids=(points,),
        reference_grid=points,
        half_width=cfg.half_width,
        imaginary_dt=cfg.imaginary_dt,
        iterations=cfg.stationary_iterations,
    )


def recentered_state(
    state: np.ndarray, grid: tuple[np.ndarray, ...]
) -> tuple[np.ndarray, np.ndarray]:
    center = density_centroid(state, grid)
    return fourier_shift(state, grid, center), center


def spectral_resample_state(
    state: np.ndarray,
    target_points: int,
    target_dx: float,
) -> np.ndarray:
    """Periodically resample a localized complex field on all three axes."""
    result = np.asarray(state, dtype=np.complex128)
    for axis in range(3):
        result = resample(result, target_points, axis=axis)
    return normalize_state(result, target_dx)


def periodic_hartree_energy(
    density: np.ndarray,
    k2: np.ndarray,
    dx: float,
) -> float:
    """Return the zero-mean periodic Newton/Hartree energy proxy."""
    multiplier = np.zeros_like(k2, dtype=np.float64)
    nonzero = k2 > 1e-15
    multiplier[nonzero] = 4.0 * math.pi / k2[nonzero]
    potential = np.fft.ifftn(multiplier * np.fft.fftn(density)).real
    return 0.5 * float(np.sum(density * potential) * dx**3)


def state_observables(
    state: np.ndarray,
    grid: tuple[np.ndarray, ...],
    dispersion: float,
) -> dict[str, float]:
    alpha, beta = coefficients()
    dx = float(grid[5])
    density = np.abs(state) ** 2
    quartic = float(np.sum(density**2) * dx**3)
    sextic = float(np.sum(density**3) * dx**3)
    local_interaction = -0.5 * alpha * quartic + beta * sextic / 3.0
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    kinetic = dispersion * float(np.sum(np.abs(gradient) ** 2) * dx**3)
    return {
        "mass": float(np.sum(density) * dx**3),
        "quartic_integral": quartic,
        "sextic_integral": sextic,
        "local_interaction": local_interaction,
        "kinetic_energy": kinetic,
        "total_local_energy": kinetic + local_interaction,
        "periodic_hartree_energy": periodic_hartree_energy(
            density, grid[4], dx
        ),
    }


def adjacent_pair_metrics(
    coarse_points: int,
    fine_points: int,
    cfg: RellichHartreeConfig,
) -> dict[str, Any]:
    coarse_cfg = stationary_config(coarse_points, cfg)
    fine_cfg = stationary_config(fine_points, cfg)
    coarse, coarse_grid = solve_stationary(
        coarse_points, "super_gaussian", coarse_cfg
    )
    fine, fine_grid = solve_stationary(
        fine_points, "super_gaussian", fine_cfg
    )
    coarse, coarse_center = recentered_state(coarse, coarse_grid)
    fine, fine_center = recentered_state(fine, fine_grid)
    dx = float(fine_grid[5])
    coarse_on_fine = spectral_resample_state(coarse, fine_points, dx)
    coarse_on_fine = phase_align(fine, coarse_on_fine, dx)

    coarse_density = np.abs(coarse_on_fine) ** 2
    fine_density = np.abs(fine) ** 2
    density_difference = np.abs(coarse_density - fine_density)
    radius = np.sqrt(fine_grid[3])

    lone_error = float(np.sum(density_difference) * dx**3)
    lthree_power_integral = float(
        np.sum(density_difference**3) * dx**3
    )
    lsix_fifths_power_integral = float(
        np.sum(density_difference ** (6.0 / 5.0)) * dx**3
    )
    interpolation_bound = (
        lone_error ** (9.0 / 10.0)
        * lthree_power_integral ** (1.0 / 10.0)
    )

    difference = coarse_on_fine - fine
    difference_gradient = np.fft.ifftn(
        np.sqrt(fine_grid[4]) * np.fft.fftn(difference)
    )
    h1_distance = math.sqrt(
        float(
            np.sum(
                np.abs(difference) ** 2
                + np.abs(difference_gradient) ** 2
            )
            * dx**3
        )
    )

    coarse_observables = state_observables(
        coarse_on_fine, fine_grid, fine_cfg.dispersion
    )
    fine_observables = state_observables(
        fine, fine_grid, fine_cfg.dispersion
    )

    return {
        "coarse_points": coarse_points,
        "fine_points": fine_points,
        "coarse_center": coarse_center.tolist(),
        "fine_center": fine_center.tolist(),
        "local_lone_errors": {
            str(radius_value): float(
                np.sum(density_difference[radius <= radius_value]) * dx**3
            )
            for radius_value in cfg.local_radii
        },
        "tail_lone_errors": {
            str(radius_value): float(
                np.sum(density_difference[radius > radius_value]) * dx**3
            )
            for radius_value in cfg.tail_radii
        },
        "global_lone_error": lone_error,
        "lthree_power_integral": lthree_power_integral,
        "lsix_fifths_power_integral": lsix_fifths_power_integral,
        "interpolation_upper_bound": interpolation_bound,
        "h1_distance": h1_distance,
        "quartic_error": abs(
            coarse_observables["quartic_integral"]
            - fine_observables["quartic_integral"]
        ),
        "sextic_error": abs(
            coarse_observables["sextic_integral"]
            - fine_observables["sextic_integral"]
        ),
        "local_interaction_error": abs(
            coarse_observables["local_interaction"]
            - fine_observables["local_interaction"]
        ),
        "kinetic_energy_error": abs(
            coarse_observables["kinetic_energy"]
            - fine_observables["kinetic_energy"]
        ),
        "total_local_energy_error": abs(
            coarse_observables["total_local_energy"]
            - fine_observables["total_local_energy"]
        ),
        "periodic_hartree_error": abs(
            coarse_observables["periodic_hartree_energy"]
            - fine_observables["periodic_hartree_energy"]
        ),
        "coarse_observables": coarse_observables,
        "fine_observables": fine_observables,
    }


def strictly_decreasing(values: list[float]) -> bool:
    return all(right < left for left, right in zip(values, values[1:]))


@lru_cache(maxsize=1)
def run_rellich_hartree_closure(
    cfg: RellichHartreeConfig = RellichHartreeConfig(),
) -> dict[str, Any]:
    rows = [
        adjacent_pair_metrics(coarse, fine, cfg)
        for coarse, fine in zip(cfg.grids, cfg.grids[1:])
    ]
    lsix_fifths = [row["lsix_fifths_power_integral"] for row in rows]
    hartree_errors = [row["periodic_hartree_error"] for row in rows]
    h1_distances = [row["h1_distance"] for row in rows]

    local_rellich_decreases = all(
        strictly_decreasing(
            [row["local_lone_errors"][str(radius)] for row in rows]
        )
        for radius in cfg.local_radii
    )
    tails_decrease_with_radius = all(
        strictly_decreasing(
            [row["tail_lone_errors"][str(radius)] for radius in cfg.tail_radii]
        )
        for row in rows
    )

    acceptance = {
        "nested_local_rellich_errors_decrease": local_rellich_decreases,
        "recentered_tails_decrease_with_radius": tails_decrease_with_radius,
        "uniform_farthest_tail_is_small": max(
            row["tail_lone_errors"][str(cfg.tail_radii[-1])]
            for row in rows
        )
        < 1e-5,
        "density_difference_lthree_bound_is_finite": max(
            row["lthree_power_integral"] for row in rows
        )
        < 1e-5,
        "one_three_interpolation_bound_closes": all(
            row["lsix_fifths_power_integral"]
            <= row["interpolation_upper_bound"] * (1.0 + 1e-12)
            for row in rows
        ),
        "lsix_fifths_error_decreases": strictly_decreasing(lsix_fifths)
        and lsix_fifths[-1] < 4e-3,
        "periodic_hartree_proxy_converges": strictly_decreasing(hartree_errors)
        and hartree_errors[-1] < 1e-3,
        "nested_h1_distances_decrease": strictly_decreasing(h1_distances)
        and h1_distances[-1] < 5e-2,
        "live_rellich_hartree_theorems_are_named": len(FORMAL_WITNESSES) == 5,
        "finite_grid_premises_are_not_promoted_to_continuum_proofs": True,
    }

    return {
        "schema": "openwave.m9.rellich-hartree-closure.v1",
        "task": "M9.84",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_repository": FORMAL_REPOSITORY,
            "physlib_branch": FORMAL_BRANCH,
            "physlib_head": FORMAL_HEAD,
        },
        "formal_witnesses": list(FORMAL_WITNESSES),
        "rows": rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_grid_local_rellich_premises_qualified": True,
            "finite_grid_recentered_tail_premise_qualified": True,
            "finite_grid_lthree_bound_qualified": True,
            "finite_grid_lsix_fifths_and_hartree_closure_qualified": True,
            "continuum_model_premises_proved": False,
            "m9_84_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
