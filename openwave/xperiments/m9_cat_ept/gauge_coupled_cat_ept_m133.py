"""M9.133a: reduced gauge-coupled CAT/EPT matter, geometry, and entropy evolution.

This extends M9.132 with a one-dimensional periodic U(1) vector potential and
its conjugate electric field. The charged matter field uses a covariant finite
spectral derivative. The model is reduced and dimensionless; it is not a full
Maxwell-Einstein-CAT/EPT system.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class GaugeCATEPTConfig:
    points: int = 96
    half_width: float = 10.0
    time_step: float = 2.0e-4
    steps: int = 240
    sample_stride: int = 20
    mass: float = 1.0
    hbar: float = 1.0
    charge: float = 0.35
    self_coupling: float = 0.45
    gravity_coupling: float = 0.18
    geometry_relaxation: float = 1.4
    dissipation: float = 0.08
    gauge_damping: float = 0.04
    gauge_speed: float = 1.0

    def __post_init__(self) -> None:
        if self.points < 48 or self.points % 2:
            raise ValueError("even periodic grid with at least 48 points required")
        if min(self.half_width, self.time_step, self.mass, self.hbar, self.gauge_speed) <= 0:
            raise ValueError("positive scales required")
        if self.steps < 20 or self.sample_stride < 1:
            raise ValueError("substantive run required")


@dataclass
class GaugeCATEPTState:
    psi: np.ndarray
    potential: np.ndarray
    vector_potential: np.ndarray
    electric_field: np.ndarray
    entropic_time: float = 0.0


def grid(cfg: GaugeCATEPTConfig) -> tuple[np.ndarray, np.ndarray, float]:
    length = 2.0 * cfg.half_width
    dx = length / cfg.points
    x = -cfg.half_width + dx * np.arange(cfg.points)
    k = 2.0 * math.pi * np.fft.fftfreq(cfg.points, d=dx)
    return x, k, dx


def derivative(values: np.ndarray, k: np.ndarray) -> np.ndarray:
    return np.fft.ifft(1j * k * np.fft.fft(values))


def laplacian(values: np.ndarray, k: np.ndarray) -> np.ndarray:
    return np.fft.ifft(-(k * k) * np.fft.fft(values))


def inverse_negative_laplacian(source: np.ndarray, k: np.ndarray) -> np.ndarray:
    hat = np.fft.fft(source - np.mean(source))
    result = np.zeros_like(hat)
    active = k != 0
    result[active] = hat[active] / (k[active] ** 2)
    return np.real_if_close(np.fft.ifft(result)).real


def normalize(psi: np.ndarray, dx: float) -> np.ndarray:
    norm = math.sqrt(dx * float(np.sum(np.abs(psi) ** 2)))
    if norm <= 0 or not math.isfinite(norm):
        raise ValueError("nonzero finite state required")
    return psi / norm


def initial_state(cfg: GaugeCATEPTConfig) -> GaugeCATEPTState:
    x, _, dx = grid(cfg)
    left = np.exp(-0.5 * ((x + 2.2) / 1.05) ** 2) * np.exp(0.55j * x)
    right = 0.82 * np.exp(-0.5 * ((x - 2.0) / 1.20) ** 2) * np.exp(-0.42j * x)
    psi = normalize(left + right, dx)
    seed_a = 0.035 * np.exp(-0.5 * (x / 2.8) ** 2)
    return GaugeCATEPTState(
        psi=psi,
        potential=np.zeros(cfg.points),
        vector_potential=seed_a,
        electric_field=np.zeros(cfg.points),
    )


def covariant_gradient(psi: np.ndarray, vector_potential: np.ndarray, k: np.ndarray, cfg: GaugeCATEPTConfig) -> np.ndarray:
    return derivative(psi, k) - 1j * cfg.charge * vector_potential * psi / cfg.hbar


def covariant_laplacian(psi: np.ndarray, vector_potential: np.ndarray, k: np.ndarray, cfg: GaugeCATEPTConfig) -> np.ndarray:
    first = covariant_gradient(psi, vector_potential, k, cfg)
    return derivative(first, k) - 1j * cfg.charge * vector_potential * first / cfg.hbar


def charge_current(state: GaugeCATEPTState, k: np.ndarray, cfg: GaugeCATEPTConfig) -> np.ndarray:
    dpsi = covariant_gradient(state.psi, state.vector_potential, k, cfg)
    return cfg.charge * cfg.hbar / cfg.mass * np.imag(np.conj(state.psi) * dpsi)


def hamiltonian_action(state: GaugeCATEPTState, k: np.ndarray, cfg: GaugeCATEPTConfig) -> np.ndarray:
    density = np.abs(state.psi) ** 2
    kinetic = -(cfg.hbar**2 / (2.0 * cfg.mass)) * covariant_laplacian(
        state.psi, state.vector_potential, k, cfg
    )
    local = (cfg.mass * state.potential + cfg.self_coupling * density) * state.psi
    return kinetic + local


def step(state: GaugeCATEPTState, cfg: GaugeCATEPTConfig) -> GaugeCATEPTState:
    _, k, dx = grid(cfg)
    density = np.abs(state.psi) ** 2
    target_phi = -4.0 * math.pi * cfg.gravity_coupling * inverse_negative_laplacian(density, k)
    next_phi = state.potential + cfg.time_step * cfg.geometry_relaxation * (target_phi - state.potential)

    hpsi = hamiltonian_action(state, k, cfg)
    mean_h = dx * float(np.real(np.vdot(state.psi, hpsi)))
    centered = hpsi - mean_h * state.psi
    gamma = cfg.dissipation * (0.35 + density / max(float(np.max(density)), 1.0e-15))
    production = dx * float(np.sum(gamma * np.abs(centered) ** 2)) / (cfg.hbar**2)
    psi_rhs = -1j * hpsi / cfg.hbar - gamma * centered / cfg.hbar

    current = charge_current(state, k, cfg)
    a_rhs = -state.electric_field
    e_rhs = (
        cfg.gauge_speed**2 * np.real_if_close(laplacian(state.vector_potential, k)).real
        - current
        - cfg.gauge_damping * state.electric_field
    )
    next_a = np.real_if_close(state.vector_potential + cfg.time_step * a_rhs).real
    next_e = np.real_if_close(state.electric_field + cfg.time_step * e_rhs).real
    next_psi = normalize(state.psi + cfg.time_step * psi_rhs, dx)
    return GaugeCATEPTState(
        psi=next_psi,
        potential=np.real_if_close(next_phi).real,
        vector_potential=next_a,
        electric_field=next_e,
        entropic_time=state.entropic_time + cfg.time_step * max(production, 0.0),
    )


def diagnostics(state: GaugeCATEPTState, cfg: GaugeCATEPTConfig) -> dict[str, float]:
    _, k, dx = grid(cfg)
    density = np.abs(state.psi) ** 2
    current = charge_current(state, k, cfg)
    hpsi = hamiltonian_action(state, k, cfg)
    matter_energy = dx * float(np.real(np.vdot(state.psi, hpsi)))
    magnetic_like = np.real_if_close(derivative(state.vector_potential, k)).real
    gauge_energy = 0.5 * dx * float(np.sum(state.electric_field**2 + cfg.gauge_speed**2 * magnetic_like**2))
    gauss_residual = derivative(state.electric_field, k) - cfg.charge * (density - np.mean(density))
    return {
        "norm": dx * float(np.sum(density)),
        "matter_energy": matter_energy,
        "gauge_energy": gauge_energy,
        "total_resolved_energy": matter_energy + gauge_energy,
        "density_peak": float(np.max(density)),
        "current_l2": math.sqrt(dx * float(np.sum(current**2))),
        "electric_l2": math.sqrt(dx * float(np.sum(state.electric_field**2))),
        "vector_potential_l2": math.sqrt(dx * float(np.sum(state.vector_potential**2))),
        "gauss_residual_l2": math.sqrt(dx * float(np.sum(np.abs(gauss_residual) ** 2))),
        "geometry_l2": math.sqrt(dx * float(np.sum(state.potential**2))),
        "entropic_time": state.entropic_time,
    }


def run_with_config(cfg: GaugeCATEPTConfig) -> dict[str, Any]:
    state = initial_state(cfg)
    records: list[dict[str, float]] = []
    min_entropy_increment = float("inf")
    for index in range(cfg.steps + 1):
        if index % cfg.sample_stride == 0 or index == cfg.steps:
            records.append({"time": index * cfg.time_step, **diagnostics(state, cfg)})
        if index == cfg.steps:
            break
        old_tau = state.entropic_time
        state = step(state, cfg)
        min_entropy_increment = min(min_entropy_increment, state.entropic_time - old_tau)
    acceptance = {
        "norm_is_preserved": max(abs(row["norm"] - 1.0) for row in records) <= 2.0e-10,
        "gauge_field_is_dynamical": any(row["electric_l2"] > 1.0e-10 for row in records[1:]),
        "charged_current_is_nonzero": any(row["current_l2"] > 1.0e-8 for row in records),
        "geometry_is_dynamical": any(row["geometry_l2"] > 1.0e-10 for row in records[1:]),
        "entropic_time_is_monotone": min_entropy_increment >= -1.0e-14,
        "all_diagnostics_are_finite": all(math.isfinite(value) for row in records for value in row.values()),
        "gauss_residual_is_reported": all(math.isfinite(row["gauss_residual_l2"]) for row in records),
    }
    payload = {
        "schema": "openwave.m9.gauge-coupled-cat-ept.v1",
        "task": "M9.133a",
        "config": asdict(cfg),
        "records": records,
        "acceptance": acceptance,
        "claim_boundary": {
            "reduced_U1_carrier_is_full_Maxwell_theory": False,
            "scalar_geometry_is_general_relativity": False,
            "dimensionless_parameters_are_physical_calibration": False,
        },
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "decision": {
            "charged_matter_gauge_geometry_entropy_evolved_together": True,
            "full_relativistic_gauge_gravity_constructed": False,
            "physical_calibration_complete": False,
        },
    }


@lru_cache(maxsize=1)
def run_gauge_coupled_cat_ept() -> dict[str, Any]:
    return run_with_config(GaugeCATEPTConfig())


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
