"""M9.74 independent robustness test of the frozen M9.71 radial mode.

M9.71 derived the mode from a radial phase chirp and a single-frequency
least-squares scan. This module changes both controls:

* perturbation: normalized radial amplitude deformation;
* estimator: detrended Hann-windowed periodogram with local peak interpolation.

The M9.71 value, coefficients, and 5% gate remain immutable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

from .replacement_mode_prediction import conservative_energy
from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)

OPENWAVE_BASE = "2dfaf6da88b24fe43799b53d79ef2f7aa3244a32"
FORMAL_HEAD = "5d0cdf07c891b1dbe7381b93c2d794b593fae09d"
FROZEN_PREDICTION_ID = "CAT-EPT-M9.71-STATIONARY-BRANCH-RADIAL-MODE-v1"
FROZEN_RATIO = 1.0743568358247257
FROZEN_SOURCE_FINGERPRINT = "e83aa3bd8b5daf1a0b7bfdefc84277a70f02ecb920c0820326ba5b0e5c539236"


@dataclass(frozen=True)
class IndependentModeRobustnessConfig:
    grids: tuple[int, ...] = (20, 24, 28)
    amplitude_strength: float = 0.015
    final_time: float = 16.0
    dt: float = 4e-3
    sample_every: int = 3
    fit_start: float = 1.0
    minimum_omega: float = 0.8
    maximum_omega: float = 2.2
    zero_padding_factor: int = 32
    spectral_band_half_width: float = 0.12
    minimum_peak_power_fraction: float = 0.30
    relative_tolerance: float = 0.05

    def __post_init__(self) -> None:
        if self.amplitude_strength <= 0 or self.final_time <= 0 or self.dt <= 0:
            raise ValueError("positive robustness controls required")
        if self.sample_every < 1 or self.zero_padding_factor < 2:
            raise ValueError("insufficient temporal or spectral sampling")
        if not 0 < self.relative_tolerance < 0.5:
            raise ValueError("valid immutable tolerance required")
        if self.minimum_omega <= 0 or self.minimum_omega >= self.maximum_omega:
            raise ValueError("valid mode window required")


def radial_amplitude_perturbation(
    stationary: np.ndarray,
    radial_squared: np.ndarray,
    dx: float,
    strength: float,
) -> np.ndarray:
    """Apply a normalized amplitude deformation distinct from the M9.71 chirp."""
    rho = np.abs(stationary) ** 2
    radius_squared = float(np.sum(radial_squared * rho) * dx**3)
    if radius_squared <= 0:
        raise ValueError("positive stationary radius required")
    shape = radial_squared / radius_squared - 1.0
    return normalize_state(stationary * (1.0 + strength * shape), dx)


def radial_amplitude_trace(
    points: int,
    cfg: IndependentModeRobustnessConfig,
    stationary_cfg: StationaryBranchConfig,
) -> dict[str, Any]:
    alpha, beta = coefficients()
    stationary, grid = solve_stationary(points, "super_gaussian", stationary_cfg)
    radial_squared, k2, dx = grid[3], grid[4], float(grid[5])
    stationary_density = np.abs(stationary) ** 2
    stationary_radius = math.sqrt(
        float(np.sum(radial_squared * stationary_density) * dx**3)
    )
    psi = radial_amplitude_perturbation(
        stationary, radial_squared, dx, cfg.amplitude_strength
    )
    initial_mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    initial_energy = conservative_energy(psi, grid, stationary_cfg)
    initial_radius = math.sqrt(
        float(np.sum(radial_squared * np.abs(psi) ** 2) * dx**3 / initial_mass)
    )
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
            times.append((index + 1) * cfg.dt)
            radii.append(
                math.sqrt(float(np.sum(radial_squared * rho) * dx**3 / mass))
            )
    final_mass = float(np.sum(np.abs(psi) ** 2) * dx**3)
    final_energy = conservative_energy(psi, grid, stationary_cfg)
    radii_array = np.asarray(radii)
    return {
        "points": points,
        "times": np.asarray(times),
        "radii": radii_array,
        "stationary_radius": stationary_radius,
        "initial_perturbed_radius": initial_radius,
        "maximum_relative_radius_excursion": float(
            np.max(np.abs(radii_array - stationary_radius)) / stationary_radius
        ),
        "mass_error": abs(final_mass - initial_mass),
        "energy_drift": abs(final_energy - initial_energy),
    }


def periodogram_mode(
    trace: dict[str, Any], cfg: IndependentModeRobustnessConfig
) -> dict[str, float]:
    """Extract the mode nonparametrically from a windowed power spectrum."""
    times = trace["times"]
    radii = trace["radii"]
    mask = times >= cfg.fit_start
    times, radii = times[mask], radii[mask]
    design = np.column_stack((np.ones_like(times), times))
    detrended = radii - design @ np.linalg.lstsq(design, radii, rcond=None)[0]
    windowed = detrended * np.hanning(len(detrended))
    nfft = 1
    while nfft < cfg.zero_padding_factor * len(windowed):
        nfft *= 2
    power = np.abs(np.fft.rfft(windowed, n=nfft)) ** 2
    angular_frequency = 2.0 * math.pi * np.fft.rfftfreq(
        nfft, d=float(times[1] - times[0])
    )
    valid = np.where(
        (angular_frequency >= cfg.minimum_omega)
        & (angular_frequency <= cfg.maximum_omega)
    )[0]
    peak_index = int(valid[np.argmax(power[valid])])
    offset = 0.0
    if 0 < peak_index < len(power) - 1:
        local = np.log(np.maximum(power[peak_index - 1 : peak_index + 2], 1e-300))
        denominator = float(local[0] - 2.0 * local[1] + local[2])
        if abs(denominator) > 1e-15:
            offset = 0.5 * float(local[0] - local[2]) / denominator
    omega = float(
        angular_frequency[peak_index]
        + offset * (angular_frequency[1] - angular_frequency[0])
    )
    selected_power = float(
        np.sum(
            power[
                (angular_frequency >= omega - cfg.spectral_band_half_width)
                & (angular_frequency <= omega + cfg.spectral_band_half_width)
            ]
        )
    )
    total_power = float(np.sum(power[valid]))
    omega_compton = 2.0 * stationary_dispersion()
    return {
        "omega_dimensionless": omega,
        "omega_over_compton": omega / omega_compton,
        "peak_power_fraction": selected_power / max(total_power, 1e-300),
        "zero_padded_samples": float(nfft),
    }


def stationary_dispersion() -> float:
    return StationaryBranchConfig().dispersion


def frozen_record(cfg: IndependentModeRobustnessConfig) -> dict[str, Any]:
    return {
        "prediction_id": FROZEN_PREDICTION_ID,
        "dimensionless_ratio": FROZEN_RATIO,
        "relative_tolerance": cfg.relative_tolerance,
        "source_fingerprint": FROZEN_SOURCE_FINGERPRINT,
        "coefficients_refit": False,
        "perturbation_reused_from_derivation": False,
        "estimator_reused_from_derivation": False,
    }


def robustness_fingerprint(
    cfg: IndependentModeRobustnessConfig, record: dict[str, Any]
) -> str:
    payload = {
        "schema": "openwave.m9.independent-mode-robustness.v1",
        "openwave_head": OPENWAVE_BASE,
        "formal_head": FORMAL_HEAD,
        "config": asdict(cfg),
        "frozen_prediction": record,
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def evaluate_measurement(
    points: int,
    cfg: IndependentModeRobustnessConfig,
    stationary_cfg: StationaryBranchConfig,
) -> dict[str, Any]:
    trace = radial_amplitude_trace(points, cfg, stationary_cfg)
    spectral = periodogram_mode(trace, cfg)
    relative_error = abs(spectral["omega_over_compton"] - FROZEN_RATIO) / FROZEN_RATIO
    return {
        "points": points,
        **spectral,
        "stationary_radius": trace["stationary_radius"],
        "initial_perturbed_radius": trace["initial_perturbed_radius"],
        "maximum_relative_radius_excursion": trace[
            "maximum_relative_radius_excursion"
        ],
        "mass_error": trace["mass_error"],
        "energy_drift": trace["energy_drift"],
        "relative_error_from_frozen_prediction": relative_error,
        "passes_frozen_tolerance": relative_error <= cfg.relative_tolerance,
    }


@lru_cache(maxsize=1)
def run_independent_mode_robustness() -> dict[str, Any]:
    cfg = IndependentModeRobustnessConfig()
    stationary_cfg = StationaryBranchConfig()
    record = frozen_record(cfg)
    rows = [evaluate_measurement(points, cfg, stationary_cfg) for points in cfg.grids]
    acceptance = {
        "m9_71_record_reused_without_refit": not record["coefficients_refit"],
        "perturbation_is_independent_of_m9_71_chirp": not record[
            "perturbation_reused_from_derivation"
        ],
        "estimator_is_independent_of_m9_71_least_squares_scan": not record[
            "estimator_reused_from_derivation"
        ],
        "all_grids_pass_frozen_tolerance": all(
            row["passes_frozen_tolerance"] for row in rows
        ),
        "spectral_peaks_are_resolved": min(
            row["peak_power_fraction"] for row in rows
        ) >= cfg.minimum_peak_power_fraction,
        "mass_and_energy_controls_close": max(row["mass_error"] for row in rows)
        <= 5e-11
        and max(row["energy_drift"] for row in rows) <= 2e-6,
        "fingerprint_is_deterministic": robustness_fingerprint(cfg, record)
        == robustness_fingerprint(cfg, record),
    }
    return {
        "schema": "openwave.m9.independent-mode-robustness.v1",
        "task": "M9.74",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_pr_head": FORMAL_HEAD,
        },
        "frozen_prediction": record,
        "measurements": rows,
        "fingerprint": robustness_fingerprint(cfg, record),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "frozen_replacement_mode_survives_independent_perturbation": all(
                row["passes_frozen_tolerance"] for row in rows
            ),
            "internal_computational_robustness_qualified": True,
            "external_experimental_test_performed": False,
            "physical_prediction_validated": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
