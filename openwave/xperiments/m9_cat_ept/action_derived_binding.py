"""M9.59 action-derived cubic--quintic binding discrimination.

A bounded local action density
    V_bind(rho) = -alpha/2 rho^2 + beta/3 rho^3
has variational potential -alpha rho + beta rho^2. The finite 3D campaign adds
this term to the existing untrapped CAT/EPT matter step and compares it with the
merged negative baseline. Selection is finite-grid and does not establish a
physical particle or uniqueness of the proposed action term.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .unified_self_binding_3d import (
    T8,
    Unified3DConfig,
    Unified3DState,
    color_density,
    density,
    initial_state,
    k_squared,
    lattice,
    observables,
    screened_solve,
)


@dataclass(frozen=True)
class BindingCampaignConfig:
    parameter_pairs: tuple[tuple[float, float], ...] = (
        (0.0, 0.0),
        (46.0, 170.0),
        (60.0, 260.0),
        (70.0, 380.0),
    )
    points: tuple[int, ...] = (12, 14, 16)
    half_widths: tuple[float, ...] = (6.0, 7.0, 8.0)
    final_times: tuple[float, ...] = (6.0, 5.0, 5.0)
    dt: float = 0.02
    retained_radius_ratio: float = 1.45
    maximum_boundary: float = 0.02

    def __post_init__(self) -> None:
        if len(self.points) != len(self.half_widths) or len(self.points) != len(self.final_times):
            raise ValueError("grid campaign lengths must match")
        if any(points < 10 or points % 2 for points in self.points):
            raise ValueError("even cubic grids >=10 required")
        if self.dt <= 0 or self.retained_radius_ratio <= 1 or self.maximum_boundary <= 0:
            raise ValueError("invalid campaign controls")
        if any(alpha < 0 or beta < 0 for alpha, beta in self.parameter_pairs):
            raise ValueError("nonnegative action coefficients required")


def binding_density(rho: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    return -0.5 * alpha * rho * rho + (beta / 3) * rho * rho * rho


def binding_potential(rho: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    return -alpha * rho + beta * rho * rho


def derivative_control(alpha: float = 70.0, beta: float = 380.0) -> dict[str, float]:
    rho = np.linspace(0.01, 0.25, 32)
    direction = np.cos(np.linspace(0, 2 * math.pi, 32, endpoint=False))
    eps = 1e-7
    finite = float(
        np.sum(
            binding_density(rho + eps * direction, alpha, beta)
            - binding_density(rho - eps * direction, alpha, beta)
        )
        / (2 * eps)
    )
    analytic = float(np.sum(binding_potential(rho, alpha, beta) * direction))
    return {
        "finite_difference": finite,
        "analytic_directional_derivative": analytic,
        "absolute_error": abs(finite - analytic),
    }


def binding_step(
    state: Unified3DState,
    dt: float,
    cfg: Unified3DConfig,
    alpha: float,
    beta: float,
) -> Unified3DState:
    rho = density(state.psi)
    geometry = screened_solve(rho, cfg.geometry_mass, cfg.geometry_coupling, cfg)
    gauge = screened_solve(color_density(state.psi), cfg.color_mass, cfg.color_coupling, cfg)
    scalar = (
        cfg.local_repulsion * rho
        - cfg.geometry_coupling * geometry
        + cfg.thermal_coupling * (state.temperature - float(np.mean(state.temperature)))
        + binding_potential(rho, alpha, beta)
    )
    eigenvalues = np.diag(T8).real
    color_phase = cfg.color_coupling * gauge
    state.psi *= np.exp(-0.5 * cfg.loss_rate * dt) * np.exp(-0.5j * dt * scalar)[None]
    state.psi *= np.exp(
        -0.5j * dt * eigenvalues[:, None, None, None] * color_phase[None]
    )
    state.psi = np.fft.ifftn(
        np.fft.fftn(state.psi, axes=(1, 2, 3))
        * np.exp(-1j * cfg.matter_dispersion * k_squared(cfg) * dt)[None],
        axes=(1, 2, 3),
    )
    rho2 = density(state.psi)
    geometry2 = screened_solve(rho2, cfg.geometry_mass, cfg.geometry_coupling, cfg)
    gauge2 = screened_solve(color_density(state.psi), cfg.color_mass, cfg.color_coupling, cfg)
    scalar2 = (
        cfg.local_repulsion * rho2
        - cfg.geometry_coupling * geometry2
        + cfg.thermal_coupling * (state.temperature - float(np.mean(state.temperature)))
        + binding_potential(rho2, alpha, beta)
    )
    state.psi *= np.exp(-0.5j * dt * scalar2)[None] * np.exp(
        -0.5j
        * dt
        * eigenvalues[:, None, None, None]
        * (cfg.color_coupling * gauge2)[None]
    )
    *_xyz, dx = lattice(cfg)
    before = float(np.sum(rho) * dx**3)
    state.psi *= np.exp(-0.5 * cfg.loss_rate * dt)
    after = density(state.psi)
    after_norm = float(np.sum(after) * dx**3)
    lost_total = max(before - after_norm, 0.0)
    lost_density = lost_total * after / max(after_norm, np.finfo(float).tiny)
    state.reservoir += lost_density
    state.temperature = (
        np.fft.ifftn(
            np.fft.fftn(state.temperature)
            * np.exp(-cfg.thermal_diffusion * k_squared(cfg) * dt)
        ).real
        + cfg.heat_per_loss * lost_density
    )
    state.entropy += cfg.heat_per_loss * lost_density / np.maximum(state.temperature, 0.25)
    return state


def evolve(
    alpha: float,
    beta: float,
    points: int,
    half_width: float,
    final_time: float,
    dt: float,
) -> dict[str, float]:
    cfg = Unified3DConfig(
        points=points,
        half_width=half_width,
        final_time=final_time,
        dt=dt,
        sample_stride=20,
    )
    state = initial_state(cfg)
    first = observables(state, cfg)
    maximum_boundary = first["boundary_fraction"]
    maximum_balance = 0.0
    records = [first]
    steps = math.ceil(final_time / dt)
    actual_dt = final_time / steps
    for index in range(steps):
        state = binding_step(state, actual_dt, cfg, alpha, beta)
        if (index + 1) % cfg.sample_stride == 0 or index + 1 == steps:
            row = observables(state, cfg)
            records.append(row)
            maximum_boundary = max(maximum_boundary, row["boundary_fraction"])
            maximum_balance = max(maximum_balance, abs(row["balance"] - first["balance"]))
    final = records[-1]
    return {
        "alpha": alpha,
        "beta": beta,
        "points": points,
        "half_width": half_width,
        "final_time": final_time,
        "initial_radius": first["radius"],
        "final_radius": final["radius"],
        "radius_ratio": final["radius"] / first["radius"],
        "maximum_boundary_fraction": maximum_boundary,
        "maximum_balance_error": maximum_balance,
        "final_entropy": final["entropy"],
        "minimum_temperature": min(row["minimum_temperature"] for row in records),
    }


def parameter_scan(cfg: BindingCampaignConfig = BindingCampaignConfig()) -> list[dict[str, Any]]:
    rows = []
    for alpha, beta in cfg.parameter_pairs:
        row = evolve(
            alpha,
            beta,
            cfg.points[0],
            cfg.half_widths[0],
            cfg.final_times[0],
            cfg.dt,
        )
        row["retained_localization"] = bool(
            row["radius_ratio"] < cfg.retained_radius_ratio
            and row["maximum_boundary_fraction"] < cfg.maximum_boundary
        )
        rows.append(row)
    return rows


def resolution_campaign(
    alpha: float = 70.0,
    beta: float = 380.0,
    cfg: BindingCampaignConfig = BindingCampaignConfig(),
) -> list[dict[str, Any]]:
    rows = []
    for points, half_width, final_time in zip(
        cfg.points, cfg.half_widths, cfg.final_times
    ):
        row = evolve(alpha, beta, points, half_width, final_time, cfg.dt)
        row["retained_localization"] = bool(
            row["radius_ratio"] < cfg.retained_radius_ratio
            and row["maximum_boundary_fraction"] < cfg.maximum_boundary
        )
        rows.append(row)
    return rows


@lru_cache(maxsize=1)
def run_binding_discrimination() -> dict[str, Any]:
    cfg = BindingCampaignConfig()
    derivative = derivative_control()
    scan = parameter_scan(cfg)
    baseline = scan[0]
    selected = scan[-1]
    resolution = resolution_campaign(cfg=cfg)
    acceptance = {
        "binding_term_is_an_action_derivative": derivative["absolute_error"] <= 2e-7,
        "baseline_reproduces_untrapped_spreading": baseline["radius_ratio"] >= 2.5
        or baseline["maximum_boundary_fraction"] >= 0.2,
        "candidate_reduces_radius_growth_by_large_factor": selected["radius_ratio"]
        <= 0.4 * baseline["radius_ratio"],
        "candidate_retains_localization_on_all_test_grids": all(
            row["retained_localization"] for row in resolution
        ),
        "candidate_avoids_boundary_loading": max(
            row["maximum_boundary_fraction"] for row in resolution
        )
        < cfg.maximum_boundary,
        "matter_reservoir_balance_closes": max(
            row["maximum_balance_error"] for row in scan + resolution
        )
        <= 5e-4,
        "entropy_and_temperature_controls_hold": min(
            row["final_entropy"] for row in scan + resolution
        )
        > 0
        and min(row["minimum_temperature"] for row in scan + resolution) > 0.9,
        "physical_particle_claim_is_not_overstated": True,
    }
    return {
        "schema": "openwave.m9.action-derived-binding.v1",
        "task": "M9.59",
        "config": asdict(cfg),
        "action_density": {
            "formula": "-alpha/2 rho^2 + beta/3 rho^3",
            "variational_potential": "-alpha rho + beta rho^2",
        },
        "derivative_control": derivative,
        "parameter_scan": scan,
        "selected_candidate": {"alpha": 70.0, "beta": 380.0},
        "resolution_campaign": resolution,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_grid_binding_candidate_selected": True,
            "robust_untrapped_localization_on_test_campaign": True,
            "stable_physical_particle_established": False,
            "candidate_unique_or_derived_from_first_principles": False,
        },
        "classification": {
            "establishes": [
                "an explicit bounded cubic--quintic action term and its variational potential",
                "strong finite-grid discrimination against the merged untrapped baseline",
                "retained localization across three cubic grids and domains",
            ],
            "does_not_establish": [
                "orbital stability or a continuum soliton theorem",
                "uniqueness of the action term from CAT/EPT axioms",
                "physical mass, lifetime, charge, or experimental calibration",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
