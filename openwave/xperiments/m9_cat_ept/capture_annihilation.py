"""Reduced opposite-sector capture, annihilation, and radiation ledger.

This module is dimensionless simulation infrastructure. A signed separation
coordinate evolves under a regularized Coulomb kernel. Mechanical damping and
overlap-triggered matter loss are transferred explicitly into a radiation ledger,
so the full reduced energy closes by construction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

RealVector = NDArray[np.float64]


@dataclass(frozen=True)
class CaptureConfig:
    coupling: float = 1.0
    softening: float = 0.25
    reduced_mass: float = 0.5
    damping: float = 0.12
    annihilation_rate: float = 2.4
    overlap_width: float = 0.55
    capture_radius: float = 0.75
    initial_separation: float = 5.0
    initial_velocity: float = -0.05
    initial_sector_mass: float = 1.0
    final_time: float = 30.0
    dt: float = 0.0025

    def __post_init__(self) -> None:
        positive = (
            self.coupling, self.softening, self.reduced_mass,
            self.annihilation_rate, self.overlap_width, self.capture_radius,
            self.initial_sector_mass, self.final_time, self.dt,
        )
        if any(value <= 0.0 for value in positive):
            raise ValueError("positive model parameters required")
        if self.damping < 0.0:
            raise ValueError("nonnegative damping required")


def potential(separation: float, charge_product: float, cfg: CaptureConfig) -> float:
    return charge_product * cfg.coupling / math.sqrt(
        separation * separation + cfg.softening * cfg.softening
    )


def radial_force(separation: float, charge_product: float, cfg: CaptureConfig) -> float:
    denominator = (separation * separation + cfg.softening * cfg.softening) ** 1.5
    return charge_product * cfg.coupling * separation / denominator


def overlap(separation: float, cfg: CaptureConfig) -> float:
    return math.exp(-0.5 * (separation / cfg.overlap_width) ** 2)


def total_energy(state: RealVector, charge_product: float, cfg: CaptureConfig) -> float:
    separation, velocity, sector_mass, radiation = map(float, state)
    kinetic = 0.5 * cfg.reduced_mass * velocity * velocity
    rest = 2.0 * sector_mass
    return kinetic + potential(separation, charge_product, cfg) + rest + radiation


def rhs(state: RealVector, charge_product: float, cfg: CaptureConfig) -> RealVector:
    separation, velocity, sector_mass, _radiation = map(float, state)
    force = radial_force(separation, charge_product, cfg)
    local_overlap = overlap(separation, cfg) if charge_product < 0.0 else 0.0
    annihilation_flux = cfg.annihilation_rate * local_overlap * max(sector_mass, 0.0)
    damping_power = cfg.damping * velocity * velocity
    return np.asarray([
        velocity,
        (force - cfg.damping * velocity) / cfg.reduced_mass,
        -annihilation_flux,
        damping_power + 2.0 * annihilation_flux,
    ], dtype=np.float64)


def rk4_step(state: RealVector, charge_product: float, cfg: CaptureConfig, dt: float) -> RealVector:
    k1 = rhs(state, charge_product, cfg)
    k2 = rhs(state + 0.5 * dt * k1, charge_product, cfg)
    k3 = rhs(state + 0.5 * dt * k2, charge_product, cfg)
    k4 = rhs(state + dt * k3, charge_product, cfg)
    out = state + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    out[2] = max(out[2], 0.0)
    return out


def simulate(charge_product: float = -1.0, cfg: CaptureConfig = CaptureConfig()) -> dict[str, Any]:
    state = np.asarray([
        cfg.initial_separation, cfg.initial_velocity,
        cfg.initial_sector_mass, 0.0,
    ], dtype=np.float64)
    steps = math.ceil(cfg.final_time / cfg.dt)
    dt = cfg.final_time / steps
    initial_energy = total_energy(state, charge_product, cfg)
    records: list[dict[str, float]] = []
    minimum_abs_separation = abs(float(state[0]))
    first_capture_time: float | None = None
    sample_stride = max(1, steps // 1200)

    for step in range(steps + 1):
        time = step * dt
        abs_separation = abs(float(state[0]))
        minimum_abs_separation = min(minimum_abs_separation, abs_separation)
        if first_capture_time is None and abs_separation <= cfg.capture_radius:
            first_capture_time = time
        if step % sample_stride == 0 or step == steps:
            records.append({
                "time": time,
                "separation": float(state[0]),
                "velocity": float(state[1]),
                "sector_mass": float(state[2]),
                "radiation": float(state[3]),
                "overlap": overlap(float(state[0]), cfg),
                "total_energy": total_energy(state, charge_product, cfg),
            })
        if step < steps:
            state = rk4_step(state, charge_product, cfg, dt)

    energies = np.asarray([row["total_energy"] for row in records])
    radiations = np.asarray([row["radiation"] for row in records])
    return {
        "config": asdict(cfg),
        "charge_product": charge_product,
        "records": records,
        "initial_energy": initial_energy,
        "final_energy": float(energies[-1]),
        "maximum_energy_error": float(np.max(np.abs(energies - initial_energy))),
        "minimum_abs_separation": minimum_abs_separation,
        "first_capture_time": first_capture_time,
        "final_sector_mass": float(state[2]),
        "final_radiation": float(state[3]),
        "radiation_monotone": bool(np.all(np.diff(radiations) >= -2e-12)),
    }


def timestep_refinement() -> dict[str, Any]:
    dts = (0.01, 0.005, 0.0025)
    runs = [simulate(cfg=CaptureConfig(dt=dt)) for dt in dts]
    masses = [run["final_sector_mass"] for run in runs]
    radiation = [run["final_radiation"] for run in runs]
    return {
        "dts": dts,
        "final_sector_mass": masses,
        "final_radiation": radiation,
        "mass_successive_differences": [
            abs(masses[index] - masses[index + 1]) for index in range(2)
        ],
        "radiation_successive_differences": [
            abs(radiation[index] - radiation[index + 1]) for index in range(2)
        ],
    }


@lru_cache(maxsize=1)
def run_capture_annihilation_study() -> dict[str, Any]:
    opposite = simulate(-1.0)
    same = simulate(+1.0, CaptureConfig(initial_velocity=0.0))
    refinement = timestep_refinement()
    acceptance = {
        "opposite_sector_captures": opposite["first_capture_time"] is not None,
        "opposite_sector_annihilates": opposite["final_sector_mass"] <= 1e-3,
        "radiation_accumulates": opposite["final_radiation"] >= 1.5,
        "full_energy_ledger_closes": opposite["maximum_energy_error"] <= 5e-8,
        "radiation_is_monotone": opposite["radiation_monotone"],
        "same_sector_does_not_capture": same["first_capture_time"] is None,
        "same_sector_does_not_annihilate": abs(same["final_sector_mass"] - 1.0) <= 1e-12,
        "timestep_converges": (
            refinement["mass_successive_differences"][1]
            <= refinement["mass_successive_differences"][0] + 1e-10
            and refinement["radiation_successive_differences"][1]
            <= refinement["radiation_successive_differences"][0] + 1e-10
        ),
    }
    return {
        "schema": "openwave.m9.capture-annihilation-result.v1",
        "task": "M9.31",
        "opposite_sector": {k: v for k, v in opposite.items() if k != "records"},
        "same_sector_control": {k: v for k, v in same.items() if k != "records"},
        "refinement": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "reduced opposite-sector capture",
                "overlap-triggered annihilation",
                "mechanical-plus-rest-energy transfer into radiation",
                "same-sector no-annihilation control",
            ],
            "does_not_establish": [
                "annihilation from the full CAT/EPT field PDE",
                "physical photons or cross sections",
                "a stable three-dimensional particle-antiparticle pair",
                "physical units or couplings",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
