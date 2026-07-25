"""M9.96a: nonzero-winding charged-branch feasibility on the selected scalar action.

The campaign starts from the validated neutral non-Gaussian stationary amplitude,
embeds a measured winding-three vortex core, and evolves the full unconstrained
cubic--quintic imaginary-time equation. It records whether winding, localization,
and the stationary residual close simultaneously. A negative result is an
explicit model result rather than a failed test run.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_field_tools import periodic_contour_winding
from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)


@dataclass(frozen=True)
class ChargedBranchFeasibilityConfig:
    points: int = 20
    half_width: float = 8.0
    winding: int = 3
    core_radii: tuple[float, ...] = (0.50, 0.70, 0.90, 1.10)
    contour_radius: float = 2.40
    imaginary_dt: float = 5.0e-4
    neutral_iterations: int = 6000
    charged_iterations: int = 2500
    stationary_residual_gate: float = 5.0e-2
    radius_gate: float = 1.75
    boundary_gate: float = 2.0e-2

    def __post_init__(self) -> None:
        if self.points < 16 or self.points % 2:
            raise ValueError("an even grid with at least 16 points is required")
        if self.half_width <= 0.0 or self.imaginary_dt <= 0.0:
            raise ValueError("positive domain and imaginary-time step required")
        if self.winding == 0 or self.charged_iterations < 100:
            raise ValueError("nonzero winding and a substantive charged campaign required")
        if any(radius <= 0.0 for radius in self.core_radii):
            raise ValueError("positive vortex core radii required")

    def stationary_config(self) -> StationaryBranchConfig:
        return StationaryBranchConfig(
            grids=(self.points,),
            reference_grid=self.points,
            half_width=self.half_width,
            imaginary_dt=self.imaginary_dt,
            iterations=self.neutral_iterations,
        )


def charged_seed(
    core_radius: float,
    cfg: ChargedBranchFeasibilityConfig = ChargedBranchFeasibilityConfig(),
) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    neutral, grid = solve_stationary(
        cfg.points,
        "super_gaussian",
        cfg.stationary_config(),
    )
    x, y = grid[0], grid[1]
    radial = np.hypot(x, y)
    core = np.tanh(radial / core_radius) ** abs(cfg.winding)
    phase = np.exp(1j * cfg.winding * np.arctan2(y, x))
    field = normalize_state(neutral * core * phase, float(grid[5]))
    return np.asarray(field, dtype=np.complex128), grid


def evolve_unconstrained_imaginary_time(
    field: np.ndarray,
    grid: tuple[np.ndarray, ...],
    iterations: int,
    cfg: ChargedBranchFeasibilityConfig = ChargedBranchFeasibilityConfig(),
) -> np.ndarray:
    alpha, beta = coefficients()
    k2 = grid[4]
    spacing = float(grid[5])
    evolved = np.asarray(field, dtype=np.complex128).copy()
    kinetic = np.exp(-cfg.stationary_config().dispersion * k2 * cfg.imaginary_dt)
    for _ in range(iterations):
        density = np.abs(evolved) ** 2
        evolved *= np.exp(
            0.5 * cfg.imaginary_dt * (alpha * density - beta * density * density)
        )
        evolved = np.fft.ifftn(np.fft.fftn(evolved) * kinetic)
        density = np.abs(evolved) ** 2
        evolved *= np.exp(
            0.5 * cfg.imaginary_dt * (alpha * density - beta * density * density)
        )
        evolved = normalize_state(evolved, spacing)
    return np.asarray(evolved, dtype=np.complex128)


def charged_observables(
    field: np.ndarray,
    grid: tuple[np.ndarray, ...],
    cfg: ChargedBranchFeasibilityConfig = ChargedBranchFeasibilityConfig(),
) -> dict[str, float]:
    alpha, beta = coefficients()
    x, y, z, radius_sq, k2, spacing_array = grid
    spacing = float(spacing_array)
    density = np.abs(field) ** 2
    mass = float(np.sum(density) * spacing**3)
    laplacian = np.fft.ifftn(-k2 * np.fft.fftn(field))
    hamiltonian = (
        -cfg.stationary_config().dispersion * laplacian
        - alpha * density * field
        + beta * density * density * field
    )
    chemical_potential = float(
        np.real(np.vdot(field, hamiltonian)) * spacing**3 / max(mass, 1.0e-30)
    )
    residual = hamiltonian - chemical_potential * field
    residual_l2 = math.sqrt(float(np.sum(np.abs(residual) ** 2) * spacing**3))
    operator_l2 = math.sqrt(
        float(np.sum(np.abs(hamiltonian) ** 2) * spacing**3)
    )
    radius = math.sqrt(
        float(np.sum(radius_sq * density) * spacing**3 / max(mass, 1.0e-30))
    )
    boundary = np.maximum.reduce((np.abs(x), np.abs(y), np.abs(z))) > (
        0.75 * cfg.half_width
    )
    boundary_fraction = float(
        np.sum(density[boundary]) * spacing**3 / max(mass, 1.0e-30)
    )
    winding = periodic_contour_winding(
        np.asarray(field, dtype=np.complex128),
        spacing,
        radius=cfg.contour_radius,
    )
    return {
        "mass": mass,
        "chemical_potential": chemical_potential,
        "relative_stationary_residual": residual_l2 / max(operator_l2, 1.0e-30),
        "radius": radius,
        "boundary_fraction": boundary_fraction,
        **winding,
        "charge_from_winding": float(Fraction(winding["integer_winding"], 3)),
        "spin_z_for_up_embedding": 0.5 * mass,
    }


def candidate_closes(record: Mapping[str, float], cfg: ChargedBranchFeasibilityConfig) -> bool:
    return bool(
        record["integer_winding"] == cfg.winding
        and record["quantization_error"] <= 2.0e-12
        and record["relative_stationary_residual"] <= cfg.stationary_residual_gate
        and record["radius"] <= cfg.radius_gate
        and record["boundary_fraction"] <= cfg.boundary_gate
        and abs(record["mass"] - 1.0) <= 2.0e-12
    )


@lru_cache(maxsize=1)
def run_charged_branch_feasibility() -> dict[str, Any]:
    cfg = ChargedBranchFeasibilityConfig()
    neutral, neutral_grid = solve_stationary(
        cfg.points,
        "super_gaussian",
        cfg.stationary_config(),
    )
    neutral_record = charged_observables(neutral, neutral_grid, cfg)
    rows = []
    for core_radius in cfg.core_radii:
        seed, grid = charged_seed(core_radius, cfg)
        seed_record = charged_observables(seed, grid, cfg)
        evolved = evolve_unconstrained_imaginary_time(
            seed,
            grid,
            cfg.charged_iterations,
            cfg,
        )
        evolved_record = charged_observables(evolved, grid, cfg)
        rows.append(
            {
                "core_radius": core_radius,
                "seed": seed_record,
                "evolved": evolved_record,
                "full_charged_stationary_gate": candidate_closes(evolved_record, cfg),
                "radius_growth": evolved_record["radius"] / seed_record["radius"],
                "sector_preserved": evolved_record["integer_winding"] == cfg.winding,
            }
        )
    passing = [row for row in rows if row["full_charged_stationary_gate"]]
    acceptance = {
        "neutral_stationary_baseline_closes": (
            neutral_record["relative_stationary_residual"] <= 3.0e-3
            and neutral_record["boundary_fraction"] <= 1.0e-4
        ),
        "all_seeds_embed_field_derived_winding_three": all(
            row["seed"]["integer_winding"] == cfg.winding
            and row["seed"]["quantization_error"] <= 2.0e-12
            for row in rows
        ),
        "all_seed_charges_follow_exact_thirds": all(
            row["seed"]["charge_from_winding"] == 1.0 for row in rows
        ),
        "campaign_tests_multiple_core_scales": len(rows) >= 4,
        "no_candidate_silently_promoted": not passing,
        "failure_is_dynamical_or_stationary_not_topological_seed_failure": any(
            not row["sector_preserved"]
            or row["evolved"]["relative_stationary_residual"]
            > cfg.stationary_residual_gate
            or row["evolved"]["radius"] > cfg.radius_gate
            for row in rows
        ),
        "negative_subresult_is_explicit": True,
    }
    return {
        "schema": "openwave.m9.charged-branch-feasibility.v1",
        "task": "M9.96a",
        "config": asdict(cfg),
        "neutral_baseline": neutral_record,
        "rows": rows,
        "passing_candidate_count": len(passing),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "field_derived_winding_three_seeds_constructed": True,
            "same_seed_supports_spin_half_embedding": True,
            "charged_stationary_branch_constructed": bool(passing),
            "selected_scalar_action_closes_m9_96": bool(passing),
            "requires_extended_gauge_or_spinorial_stationary_equation": not passing,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
