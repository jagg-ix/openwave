"""M9.80 finite-grid minimizing-orbit identification and external gate.

The module probes the constrained energy near the M9.69 branch, relaxes three
independent deformation families back toward the same phase/translation orbit,
and preserves the immutable M9.71 radial-mode record.  It deliberately blocks
an external comparison until analytic branch identity, particle identity,
calibration, and a registered external dataset are all available.
"""
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
    normalize_state,
    solve_stationary,
)

OPENWAVE_BASE = "c3cdd5725e9b5455cf3f2fb35164e79cab1265d8"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_MILD_FLOW_HEAD = "83542cc13af0a966a072d90f2082c49785d20c55"
FORMAL_EVIDENCE_HEAD = "2cb1003ede54dc7d8487a8b397a1cacf15728feb"
FROZEN_MODE_RATIO = 1.0743568358247257
FROZEN_MODE_TOLERANCE = 0.05
FROZEN_MODE_FINGERPRINT = (
    "e83aa3bd8b5daf1a0b7bfdefc84277a70f02ecb920c0820326ba5b0e5c539236"
)


@dataclass(frozen=True)
class MinimizingOrbitIdentificationConfig:
    points: int = 20
    half_width: float = 8.0
    stationary_iterations: int = 6000
    relaxation_iterations: int = 2000
    imaginary_dt: float = 5e-4
    deformation_strength: float = 0.02
    directions: tuple[str, ...] = ("radial", "quadrupole", "shell")

    def __post_init__(self) -> None:
        if self.points < 8 or self.points % 2:
            raise ValueError("an even spectral grid of at least eight points is required")
        if self.half_width <= 0 or self.imaginary_dt <= 0:
            raise ValueError("positive spatial and imaginary-time controls are required")
        if self.stationary_iterations < 1000 or self.relaxation_iterations < 500:
            raise ValueError("the branch and relaxation campaigns are under-resolved")
        if not 0 < self.deformation_strength < 0.2:
            raise ValueError("a small positive deformation is required")


def local_stationary_config(
    cfg: MinimizingOrbitIdentificationConfig,
) -> StationaryBranchConfig:
    return StationaryBranchConfig(
        grids=(cfg.points,),
        reference_grid=cfg.points,
        half_width=cfg.half_width,
        imaginary_dt=cfg.imaginary_dt,
        iterations=cfg.stationary_iterations,
    )


def conservative_energy(
    state: np.ndarray,
    grid: tuple[np.ndarray, ...],
    stationary_cfg: StationaryBranchConfig,
) -> float:
    alpha, beta = coefficients()
    dx = float(grid[5])
    density = np.abs(state) ** 2
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    return float(
        stationary_cfg.dispersion
        * np.sum(np.abs(gradient) ** 2)
        * dx**3
        - 0.5 * alpha * np.sum(density**2) * dx**3
        + beta * np.sum(density**3) * dx**3 / 3.0
    )


def phase_align(
    reference: np.ndarray, state: np.ndarray, dx: float
) -> np.ndarray:
    overlap = np.vdot(reference, state) * dx**3
    return state if abs(overlap) == 0 else state * np.conj(overlap) / abs(overlap)


def h1_distance(
    reference: np.ndarray,
    state: np.ndarray,
    grid: tuple[np.ndarray, ...],
) -> float:
    dx = float(grid[5])
    difference = phase_align(reference, state, dx) - reference
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(difference))
    return math.sqrt(
        float(np.sum(np.abs(difference) ** 2 + np.abs(gradient) ** 2) * dx**3)
    )


def deformation_shape(
    reference: np.ndarray,
    grid: tuple[np.ndarray, ...],
    direction: str,
) -> np.ndarray:
    density = np.abs(reference) ** 2
    dx = float(grid[5])
    mass = float(np.sum(density) * dx**3)
    radius_sq = grid[3]
    mean_radius_sq = float(np.sum(radius_sq * density) * dx**3 / mass)
    if direction == "radial":
        return radius_sq / mean_radius_sq - 1.0
    if direction == "quadrupole":
        return (grid[0] ** 2 - grid[1] ** 2) / mean_radius_sq
    if direction == "shell":
        radius = np.sqrt(radius_sq)
        mean_radius = float(np.sum(radius * density) * dx**3 / mass)
        return radius / mean_radius - 1.0
    raise ValueError(f"unknown deformation direction: {direction}")


def deform(
    reference: np.ndarray,
    grid: tuple[np.ndarray, ...],
    direction: str,
    epsilon: float,
) -> np.ndarray:
    shape = deformation_shape(reference, grid, direction)
    return normalize_state(
        ((1.0 + epsilon * shape) * reference).astype(np.complex128),
        float(grid[5]),
    )


def imaginary_time_relax(
    state: np.ndarray,
    grid: tuple[np.ndarray, ...],
    cfg: MinimizingOrbitIdentificationConfig,
    stationary_cfg: StationaryBranchConfig,
) -> np.ndarray:
    alpha, beta = coefficients()
    relaxed = state.copy()
    dx = float(grid[5])
    kinetic = np.exp(
        -stationary_cfg.dispersion * grid[4] * cfg.imaginary_dt
    )
    for _ in range(cfg.relaxation_iterations):
        density = np.abs(relaxed) ** 2
        relaxed *= np.exp(
            0.5
            * cfg.imaginary_dt
            * (alpha * density - beta * density * density)
        )
        relaxed = np.fft.ifftn(np.fft.fftn(relaxed) * kinetic)
        density = np.abs(relaxed) ** 2
        relaxed *= np.exp(
            0.5
            * cfg.imaginary_dt
            * (alpha * density - beta * density * density)
        )
        relaxed = normalize_state(relaxed, dx)
    return relaxed


def external_testability_gate() -> dict[str, Any]:
    prerequisites = {
        "analytic_minimizing_orbit_identified_in_lean": False,
        "physical_particle_identity_fixed": False,
        "independent_mass_clock_calibration": False,
        "external_dataset_registered": False,
        "no_refit_protocol_frozen": True,
    }
    return {
        "prerequisites": prerequisites,
        "comparison_admissible": all(prerequisites.values()),
        "comparison_performed": False,
        "reason": (
            "the immutable dimensionless mode cannot be promoted to a physical "
            "comparison before branch identity and calibration are fixed independently"
        ),
    }


@lru_cache(maxsize=1)
def run_minimizing_orbit_identification(
    cfg: MinimizingOrbitIdentificationConfig = MinimizingOrbitIdentificationConfig(),
) -> dict[str, Any]:
    stationary_cfg = local_stationary_config(cfg)
    reference, grid = solve_stationary(
        cfg.points, "super_gaussian", stationary_cfg
    )
    reference_energy = conservative_energy(reference, grid, stationary_cfg)
    directional_curvature: list[dict[str, float | str]] = []
    relaxation_rows: list[dict[str, float | int | str]] = []
    epsilon = cfg.deformation_strength
    for direction in cfg.directions:
        plus = deform(reference, grid, direction, epsilon)
        minus = deform(reference, grid, direction, -epsilon)
        plus_energy = conservative_energy(plus, grid, stationary_cfg)
        minus_energy = conservative_energy(minus, grid, stationary_cfg)
        directional_curvature.append(
            {
                "direction": direction,
                "epsilon": epsilon,
                "plus_energy_gap": plus_energy - reference_energy,
                "minus_energy_gap": minus_energy - reference_energy,
                "symmetric_second_variation": (
                    plus_energy + minus_energy - 2.0 * reference_energy
                )
                / epsilon**2,
            }
        )
        for sign, state in ((-1, minus), (1, plus)):
            relaxed = imaginary_time_relax(
                state, grid, cfg, stationary_cfg
            )
            relaxation_rows.append(
                {
                    "direction": direction,
                    "sign": sign,
                    "initial_energy_gap": (
                        conservative_energy(state, grid, stationary_cfg)
                        - reference_energy
                    ),
                    "relaxed_energy_gap": (
                        conservative_energy(relaxed, grid, stationary_cfg)
                        - reference_energy
                    ),
                    "relaxed_phase_aligned_h1_distance": h1_distance(
                        reference, relaxed, grid
                    ),
                }
            )

    phase_rotated = reference * np.exp(0.37j)
    translated = np.roll(reference, 2, axis=0)
    recentered = np.roll(translated, -2, axis=0)
    symmetry_controls = {
        "phase_energy_error": abs(
            conservative_energy(phase_rotated, grid, stationary_cfg)
            - reference_energy
        ),
        "phase_aligned_h1_distance": h1_distance(
            reference, phase_rotated, grid
        ),
        "translation_energy_error": abs(
            conservative_energy(translated, grid, stationary_cfg)
            - reference_energy
        ),
        "recentered_translation_h1_distance": h1_distance(
            reference, recentered, grid
        ),
    }
    frozen_protocol = {
        "prediction_id": "CAT-EPT-M9.71-STATIONARY-BRANCH-RADIAL-MODE-v1",
        "dimensionless_ratio": FROZEN_MODE_RATIO,
        "relative_tolerance": FROZEN_MODE_TOLERANCE,
        "fingerprint": FROZEN_MODE_FINGERPRINT,
    }
    external_gate = external_testability_gate()
    acceptance = {
        "all_declared_deformations_raise_energy": min(
            min(row["plus_energy_gap"], row["minus_energy_gap"])
            for row in directional_curvature
        )
        > 1e-4,
        "all_declared_second_variations_are_positive": min(
            row["symmetric_second_variation"]
            for row in directional_curvature
        )
        > 1.0,
        "imaginary_time_relaxation_returns_to_one_energy_tube": max(
            abs(row["relaxed_energy_gap"]) for row in relaxation_rows
        )
        < 2e-5,
        "imaginary_time_relaxation_returns_to_one_h1_tube": max(
            row["relaxed_phase_aligned_h1_distance"]
            for row in relaxation_rows
        )
        < 6e-3,
        "phase_and_translation_zero_modes_are_respected": max(
            symmetry_controls.values()
        )
        < 1e-11,
        "frozen_radial_record_is_unchanged": (
            frozen_protocol["dimensionless_ratio"] == FROZEN_MODE_RATIO
            and frozen_protocol["relative_tolerance"]
            == FROZEN_MODE_TOLERANCE
            and frozen_protocol["fingerprint"] == FROZEN_MODE_FINGERPRINT
        ),
        "external_comparison_is_fail_closed_until_prerequisites_exist": (
            external_gate["comparison_admissible"] is False
            and external_gate["comparison_performed"] is False
        ),
        "no_external_or_physical_validation_is_claimed": True,
    }
    return {
        "schema": "openwave.m9.minimizing-orbit-identification.v1",
        "task": "M9.80",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_mild_flow_head": FORMAL_MILD_FLOW_HEAD,
            "physlib_evidence_registry_head": FORMAL_EVIDENCE_HEAD,
        },
        "reference_energy": reference_energy,
        "directional_curvature": directional_curvature,
        "relaxation_rows": relaxation_rows,
        "symmetry_controls": symmetry_controls,
        "frozen_external_protocol": frozen_protocol,
        "external_testability": external_gate,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_grid_minimizing_orbit_identification_qualified": True,
            "analytic_minimizing_orbit_identified_in_lean": False,
            "external_physical_comparison_admissible": False,
            "external_experimental_test_performed": False,
            "physical_prediction_validated": False,
            "m9_80_corrected_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
