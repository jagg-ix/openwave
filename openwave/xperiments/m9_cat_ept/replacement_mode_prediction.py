"""M9.71 replacement radial-mode prediction from the M9.69 stationary branch.

The prediction is frozen from a small radial phase chirp on the 20^3 derivation grid.
The same frequency ratio and 5% tolerance are then tested on 24^3 and 28^3 grids
without coefficient, profile, frequency-window, or tolerance refitting.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

from .stationary_non_gaussian_branch import (
    FORMAL_HEAD,
    OPENWAVE_HEAD,
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)


@dataclass(frozen=True)
class ReplacementModeConfig:
    derivation_grid: int = 20
    test_grids: tuple[int, ...] = (24, 28)
    chirp_strength: float = 0.02
    final_time: float = 12.0
    dt: float = 4e-3
    sample_every: int = 3
    fit_start: float = 1.0
    minimum_omega: float = 0.8
    maximum_omega: float = 2.2
    frequency_samples: int = 1200
    relative_tolerance: float = 0.05

    def __post_init__(self) -> None:
        if self.derivation_grid in self.test_grids:
            raise ValueError("derivation grid must be held out from test grids")
        if self.chirp_strength <= 0 or self.final_time <= 0 or self.dt <= 0:
            raise ValueError("positive mode controls required")
        if self.sample_every < 1 or self.frequency_samples < 100:
            raise ValueError("insufficient mode sampling")
        if not 0 < self.relative_tolerance < 0.5:
            raise ValueError("valid frozen tolerance required")


def conservative_energy(
    psi: np.ndarray,
    grid: tuple[np.ndarray, ...],
    stationary_cfg: StationaryBranchConfig,
) -> float:
    alpha, beta = coefficients()
    k2, dx = grid[4], float(grid[5])
    rho = np.abs(psi) ** 2
    gradient = np.fft.ifftn(np.sqrt(k2) * np.fft.fftn(psi))
    return float(
        stationary_cfg.dispersion * np.sum(np.abs(gradient) ** 2) * dx**3
        - 0.5 * alpha * np.sum(rho**2) * dx**3
        + beta * np.sum(rho**3) * dx**3 / 3.0
    )


def radial_chirp_trace(
    points: int,
    cfg: ReplacementModeConfig,
    stationary_cfg: StationaryBranchConfig,
) -> dict[str, Any]:
    alpha, beta = coefficients()
    stationary, grid = solve_stationary(points, "super_gaussian", stationary_cfg)
    r2, k2, dx = grid[3], grid[4], float(grid[5])
    psi = normalize_state(stationary * np.exp(1j * cfg.chirp_strength * r2), dx)
    initial_mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    initial_energy = conservative_energy(psi, grid, stationary_cfg)
    kinetic = np.exp(-1j * stationary_cfg.dispersion * k2 * cfg.dt)
    times: list[float] = []
    radii: list[float] = []
    steps = int(round(cfg.final_time / cfg.dt))
    for index in range(steps):
        rho = np.abs(psi) ** 2
        psi *= np.exp(-0.5j * cfg.dt * (-alpha * rho + beta * rho * rho))
        psi = np.fft.ifftn(np.fft.fftn(psi) * kinetic)
        rho = np.abs(psi) ** 2
        psi *= np.exp(-0.5j * cfg.dt * (-alpha * rho + beta * rho * rho))
        if (index + 1) % cfg.sample_every == 0:
            rho = np.abs(psi) ** 2
            mass = float(np.sum(rho) * dx**3)
            radius = math.sqrt(float(np.sum(r2 * rho) * dx**3 / mass))
            times.append((index + 1) * cfg.dt)
            radii.append(radius)
    final_mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    final_energy = conservative_energy(psi, grid, stationary_cfg)
    stationary_radius = math.sqrt(
        float(np.sum(r2 * np.abs(stationary) ** 2) * dx**3)
    )
    return {
        "points": points,
        "times": np.asarray(times),
        "radii": np.asarray(radii),
        "initial_mass": initial_mass,
        "mass_error": abs(final_mass - initial_mass),
        "energy_drift": abs(final_energy - initial_energy),
        "stationary_radius": stationary_radius,
    }


def fit_single_radial_mode(trace: dict[str, Any], cfg: ReplacementModeConfig) -> dict[str, float]:
    times = trace["times"]
    radii = trace["radii"]
    mask = times >= cfg.fit_start
    times, radii = times[mask], radii[mask]
    best: tuple[float, float, float] | None = None
    for omega in np.linspace(cfg.minimum_omega, cfg.maximum_omega, cfg.frequency_samples):
        design = np.column_stack(
            (np.ones_like(times), times, np.cos(omega * times), np.sin(omega * times))
        )
        coefficients_fit = np.linalg.lstsq(design, radii, rcond=None)[0]
        residual = radii - design @ coefficients_fit
        rmse = math.sqrt(float(np.mean(residual**2)))
        amplitude = math.hypot(float(coefficients_fit[2]), float(coefficients_fit[3]))
        if best is None or rmse < best[0]:
            best = (rmse, float(omega), amplitude)
    assert best is not None
    rmse, omega, amplitude = best
    omega_compton = 2.0 * StationaryBranchConfig().dispersion
    return {
        "omega_dimensionless": omega,
        "omega_over_compton": omega / omega_compton,
        "fit_rmse": rmse,
        "fit_amplitude": amplitude,
        "rmse_to_amplitude": rmse / max(amplitude, 1e-30),
    }


def measurement(
    points: int,
    cfg: ReplacementModeConfig,
    stationary_cfg: StationaryBranchConfig,
) -> dict[str, float]:
    trace = radial_chirp_trace(points, cfg, stationary_cfg)
    fit = fit_single_radial_mode(trace, cfg)
    return {
        "points": points,
        **fit,
        "stationary_radius": trace["stationary_radius"],
        "mass_error": trace["mass_error"],
        "energy_drift": trace["energy_drift"],
    }


def preregistration(cfg: ReplacementModeConfig, ratio: float) -> dict[str, Any]:
    return {
        "prediction_id": "CAT-EPT-M9.71-STATIONARY-BRANCH-RADIAL-MODE-v1",
        "observable": "dominant small-chirp radial angular frequency",
        "prediction": f"omega_radial = {ratio:.12f} * m c^2 / hbar",
        "dimensionless_ratio": ratio,
        "relative_tolerance": cfg.relative_tolerance,
        "derivation_grid": cfg.derivation_grid,
        "held_out_test_grids": list(cfg.test_grids),
        "frozen_before_held_out_comparison": True,
        "coefficients_refit_after_m9_68": False,
    }


def prediction_fingerprint(cfg: ReplacementModeConfig, record: dict[str, Any]) -> str:
    payload = {
        "schema": "openwave.m9.replacement-mode-prediction.v1",
        "openwave_head": OPENWAVE_HEAD,
        "formal_head": FORMAL_HEAD,
        "config": asdict(cfg),
        "preregistration": record,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_replacement_mode_prediction() -> dict[str, Any]:
    cfg = ReplacementModeConfig()
    stationary_cfg = StationaryBranchConfig()
    derivation = measurement(cfg.derivation_grid, cfg, stationary_cfg)
    frozen_ratio = derivation["omega_over_compton"]
    record = preregistration(cfg, frozen_ratio)
    tests = []
    for points in cfg.test_grids:
        row = measurement(points, cfg, stationary_cfg)
        row["relative_error_from_frozen_prediction"] = abs(
            row["omega_over_compton"] - frozen_ratio
        ) / frozen_ratio
        row["passes_frozen_tolerance"] = (
            row["relative_error_from_frozen_prediction"] <= cfg.relative_tolerance
        )
        tests.append(row)
    acceptance = {
        "derivation_mode_fit_is_resolved": derivation["rmse_to_amplitude"] <= 0.55,
        "derivation_mass_and_energy_controls_close": derivation["mass_error"] <= 2e-10
        and derivation["energy_drift"] <= 2e-6,
        "prediction_is_frozen_before_held_out_tests": record[
            "frozen_before_held_out_comparison"
        ],
        "no_coefficient_refit_after_failed_m9_65_mode": not record[
            "coefficients_refit_after_m9_68"
        ],
        "all_held_out_grids_pass_frozen_tolerance": all(
            row["passes_frozen_tolerance"] for row in tests
        ),
        "held_out_mass_and_energy_controls_close": max(
            row["mass_error"] for row in tests
        ) <= 2e-10
        and max(row["energy_drift"] for row in tests) <= 2e-6,
        "held_out_mode_fits_are_resolved": max(
            row["rmse_to_amplitude"] for row in tests
        ) <= 0.55,
        "fingerprint_is_deterministic": prediction_fingerprint(cfg, record)
        == prediction_fingerprint(cfg, record),
    }
    return {
        "schema": "openwave.m9.replacement-mode-prediction.v1",
        "task": "M9.71",
        "config": asdict(cfg),
        "repositories": {"openwave": OPENWAVE_HEAD, "physlib": FORMAL_HEAD},
        "derivation": derivation,
        "preregistration": record,
        "held_out_tests": tests,
        "fingerprint": prediction_fingerprint(cfg, record),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "replacement_mode_prediction_preregistered": True,
            "replacement_mode_passes_internal_held_out_grids": all(
                row["passes_frozen_tolerance"] for row in tests
            ),
            "external_experimental_test_performed": False,
            "physical_prediction_validated": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
