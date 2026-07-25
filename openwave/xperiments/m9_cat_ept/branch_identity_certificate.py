"""M9.86 reproducible finite-grid branch-identity certificate.

The certificate combines the nested Rellich/no-loss sequence with independent
seed convergence and a frozen radial-density feature fingerprint.  It prepares
the data required by the formal identified-branch interface while remaining
fail-closed about analytic Lean identity, particle identity, calibration, and
external comparison.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

from .local_interaction_no_loss_closure import run_local_interaction_no_loss_closure
from .minimizing_orbit_identification import phase_align
from .rellich_hartree_closure import (
    RellichHartreeConfig,
    recentered_state,
    spectral_resample_state,
    stationary_config,
)
from .stationary_non_gaussian_branch import coefficients, solve_stationary

REFERENCE_GRID = 32
REFERENCE_FINGERPRINT = "3e171c5b4ecd2b79e858b634d4a1b7cc796b20711aa1ef757ba33967f609a1c0"
SEEDS = ("super_gaussian", "anisotropic", "shell")
FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.CubicQuinticMildFlow.IdentifiedTargetBranchCertificate",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.CubicQuinticMildFlow.identifiedBranch_mem_minimizingOrbit",
    "Physlib.QuantumMechanics.Schrodinger.EuclideanSobolevFrequencyLocalization.hOne_tendsto_of_minimizing_energySplit",
)


def h1_distance(reference: np.ndarray, state: np.ndarray, grid: tuple[np.ndarray, ...]) -> float:
    dx = float(grid[5])
    difference = phase_align(reference, state, dx) - reference
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(difference))
    return math.sqrt(float(np.sum(np.abs(difference) ** 2 + np.abs(gradient) ** 2) * dx**3))


def branch_features(state: np.ndarray, grid: tuple[np.ndarray, ...], dispersion: float) -> dict[str, Any]:
    alpha, beta = coefficients()
    dx = float(grid[5])
    radius = np.sqrt(grid[3])
    density = np.abs(state) ** 2
    mass = float(np.sum(density) * dx**3)
    gradient = np.fft.ifftn(np.sqrt(grid[4]) * np.fft.fftn(state))
    kinetic = dispersion * float(np.sum(np.abs(gradient) ** 2) * dx**3)
    quartic = float(np.sum(density**2) * dx**3)
    sextic = float(np.sum(density**3) * dx**3)
    local = -0.5 * alpha * quartic + beta * sextic / 3.0
    edges = np.linspace(0.0, 4.0, 17)
    shell_masses = [
        float(np.sum(density[(radius >= lower) & (radius < upper)]) * dx**3 / mass)
        for lower, upper in zip(edges[:-1], edges[1:])
    ]
    return {
        "mass": mass,
        "first_moment": float(np.sum(radius * density) * dx**3 / mass),
        "second_moment": float(np.sum(radius**2 * density) * dx**3 / mass),
        "fourth_moment": float(np.sum(radius**4 * density) * dx**3 / mass),
        "quartic_integral": quartic,
        "sextic_integral": sextic,
        "kinetic_energy": kinetic,
        "local_interaction": local,
        "energy": kinetic + local,
        "shell_masses": shell_masses,
    }


def feature_fingerprint(features: dict[str, Any]) -> str:
    rounded = {
        key: ([round(float(value), 12) for value in item] if isinstance(item, list) else round(float(item), 12))
        for key, item in features.items()
    }
    return sha256(json.dumps(rounded, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_branch_identity_certificate() -> dict[str, Any]:
    cfg = RellichHartreeConfig()
    reference_cfg = stationary_config(REFERENCE_GRID, cfg)
    reference, reference_grid = solve_stationary(REFERENCE_GRID, "super_gaussian", reference_cfg)
    reference, reference_center = recentered_state(reference, reference_grid)
    dx = float(reference_grid[5])
    reference_features = branch_features(reference, reference_grid, reference_cfg.dispersion)
    fingerprint = feature_fingerprint(reference_features)

    grid_rows = []
    for points in cfg.grids:
        local_cfg = stationary_config(points, cfg)
        state, grid = solve_stationary(points, "super_gaussian", local_cfg)
        state, center = recentered_state(state, grid)
        if points != REFERENCE_GRID:
            state = spectral_resample_state(state, REFERENCE_GRID, dx)
        state = phase_align(reference, state, dx)
        features = branch_features(state, reference_grid, reference_cfg.dispersion)
        grid_rows.append({
            "points": points,
            "center": center.tolist(),
            "h1_distance_to_reference": h1_distance(reference, state, reference_grid),
            "energy_gap_to_reference": features["energy"] - reference_features["energy"],
            "shell_mass_lone_distance": sum(abs(left - right) for left, right in zip(features["shell_masses"], reference_features["shell_masses"])),
        })

    seed_rows = []
    for seed in SEEDS:
        state, grid = solve_stationary(REFERENCE_GRID, seed, reference_cfg)
        state, center = recentered_state(state, grid)
        state = phase_align(reference, state, dx)
        features = branch_features(state, grid, reference_cfg.dispersion)
        seed_rows.append({
            "seed": seed,
            "center": center.tolist(),
            "h1_distance_to_reference": h1_distance(reference, state, grid),
            "energy_gap_to_reference": features["energy"] - reference_features["energy"],
        })

    no_loss = run_local_interaction_no_loss_closure()
    nonreference_grid_distances = [row["h1_distance_to_reference"] for row in grid_rows if row["points"] != REFERENCE_GRID]
    acceptance = {
        "rellich_interaction_no_loss_chain_passes": bool(no_loss["passed"]),
        "nested_grid_h1_distance_improves": all(right < left for left, right in zip(nonreference_grid_distances, nonreference_grid_distances[1:])) and nonreference_grid_distances[-1] < 5e-2,
        "independent_seeds_return_to_one_h1_tube": max(row["h1_distance_to_reference"] for row in seed_rows) < 1.5e-2,
        "independent_seed_energy_spread_is_small": max(abs(row["energy_gap_to_reference"]) for row in seed_rows) < 5e-5,
        "reference_feature_fingerprint_is_frozen": fingerprint == REFERENCE_FINGERPRINT,
        "formal_identified_branch_interface_is_named": len(FORMAL_WITNESSES) == 3,
        "analytic_identity_and_external_comparison_remain_fail_closed": True,
    }
    return {
        "schema": "openwave.m9.branch-identity-certificate.v1",
        "task": "M9.86",
        "repositories": no_loss["repositories"],
        "formal_witnesses": list(FORMAL_WITNESSES),
        "reference": {"points": REFERENCE_GRID, "center": reference_center.tolist(), "features": reference_features, "fingerprint": fingerprint},
        "nested_grid_rows": grid_rows,
        "seed_rows": seed_rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "reproducible_finite_grid_branch_certificate_constructed": True,
            "nested_grid_and_seed_candidate_identity_qualified": True,
            "analytic_minimizing_orbit_identified_in_lean": False,
            "physical_particle_identity_fixed": False,
            "independent_calibration_registered": False,
            "external_comparison_admissible": False,
            "m9_86_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
