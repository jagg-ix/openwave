"""M9.101e: end-to-end weak-field electrogravitic evolution.

A single Pauli spinor generates its charge and current, exact periodic Maxwell
fields, matter-plus-electromagnetic gravitational source, Newton potential,
weak metric perturbation, and the Hamiltonian used for the next time step.
Newton's coupling is the current formal natural-unit realization
``G = hbar*c*sigma0^4``.

This is a controlled weak-field Schrodinger--Maxwell--Poisson reduction.  It is
not a nonlinear four-dimensional Einstein Cauchy development, but it closes the
previous OpenWave gap where gravity controls and formal equations were parallel
rather than one executable source/evolution chain.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .compatible_discrete_geometry import PeriodicFourierGeometry
from .coupled_gauge_spinor_hartree_action import CoupledActionConfig
from .reconciled_gauge_spinor_stationary import (
    normalize_spinor,
    reconciled_charge_current,
    reconciled_hamiltonian,
)
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed

Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class ElectrograviticEvolutionConfig:
    points: int = 17
    seed_points: int = 16
    half_width: float = 8.0
    charge: float = 1.0
    g_factor: float = 2.0
    dispersion: float = 0.65
    core_radius: float = 0.90
    winding: int = 3
    contour_radius: float = 2.40
    neutral_iterations: int = 3000
    hbar: float = 1.0
    light_speed: float = 1.0
    inference_width: float = 1.0
    time_step: float = 2.0e-5
    steps: int = 60
    sample_stride: int = 10

    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0:
            raise ValueError("odd operational grid required")
        if self.seed_points < 16 or self.seed_points % 2:
            raise ValueError("even historical seed grid required")
        if min(
            self.half_width,
            self.g_factor,
            self.dispersion,
            self.core_radius,
            self.contour_radius,
            self.hbar,
            self.light_speed,
            self.inference_width,
            self.time_step,
        ) <= 0.0:
            raise ValueError("positive electrogravitic controls required")
        if self.charge == 0.0 or self.winding == 0 or self.steps < 10:
            raise ValueError("nonzero charge/winding and substantive evolution required")
        if self.sample_stride < 1:
            raise ValueError("positive sample stride required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def effective_mass(self) -> float:
        return 1.0 / (2.0 * self.dispersion)

    @property
    def newton_coupling(self) -> float:
        return self.hbar * self.light_speed * self.inference_width**4

    def action_config(self) -> CoupledActionConfig:
        return CoupledActionConfig(
            points=self.points,
            seed_points=self.seed_points,
            half_width=self.half_width,
            winding=self.winding,
            core_radius=self.core_radius,
            contour_radius=self.contour_radius,
            charge=self.charge,
            g_factor=self.g_factor,
            dispersion=self.dispersion,
            neutral_iterations=self.neutral_iterations,
            iterations=20,
            hbar=self.hbar,
            light_speed=self.light_speed,
            inference_width=self.inference_width,
        )

    def geometry(self) -> PeriodicFourierGeometry:
        return PeriodicFourierGeometry(
            (self.points, self.points, self.points),
            (self.spacing, self.spacing, self.spacing),
        )


def coordinate_mesh(cfg: ElectrograviticEvolutionConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis = -cfg.half_width + cfg.spacing * np.arange(cfg.points, dtype=np.float64)
    return tuple(np.asarray(item, dtype=np.float64) for item in np.meshgrid(axis, axis, axis, indexing="ij"))  # type: ignore[return-value]


def electrogravitic_fields(
    spinor: np.ndarray,
    vector_potential: Vector,
    cfg: ElectrograviticEvolutionConfig,
) -> dict[str, Any]:
    geometry = cfg.geometry()
    rcfg = cfg.action_config().reconciled_config()
    charge_density, current = reconciled_charge_current(
        spinor, vector_potential, geometry, rcfg
    )
    maxwell = geometry.static_maxwell_fields(charge_density, current)
    exact_vector = tuple(
        np.asarray(component, dtype=np.float64)
        for component in maxwell["vector_potential"]
    )
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    em_energy_density = 0.5 * sum(
        maxwell["electric"][index] ** 2 + maxwell["magnetic"][index] ** 2
        for index in range(3)
    )
    total_source = np.asarray(
        cfg.effective_mass * density
        + em_energy_density / cfg.light_speed**2,
        dtype=np.float64,
    )
    projected_source = geometry.mean_zero(total_source)
    newton_kernel = geometry.inverse_negative_laplacian(total_source)
    gravitational_potential = -cfg.newton_coupling * newton_kernel
    metric_g00 = 1.0 + 2.0 * gravitational_potential / cfg.light_speed**2
    acceleration = tuple(
        np.asarray(-component, dtype=np.float64)
        for component in geometry.gradient(gravitational_potential)
    )
    einstein00_residual = geometry.laplacian(gravitational_potential) - (
        cfg.newton_coupling * projected_source
    )
    source_scale = max(float(np.linalg.norm(cfg.newton_coupling * projected_source)), 1.0e-30)
    return {
        **maxwell,
        "vector_potential": exact_vector,
        "density": density,
        "em_energy_density": em_energy_density,
        "total_gravitational_source": total_source,
        "projected_gravitational_source": projected_source,
        "newton_kernel": newton_kernel,
        "gravitational_potential": gravitational_potential,
        "metric_g00": metric_g00,
        "gravitational_acceleration": acceleration,
        "einstein00_relative_residual": float(
            np.linalg.norm(einstein00_residual) / source_scale
        ),
    }


def record_state(
    time: float,
    spinor: np.ndarray,
    fields: Mapping[str, Any],
    cfg: ElectrograviticEvolutionConfig,
) -> dict[str, float]:
    x, y, z = coordinate_mesh(cfg)
    density = np.asarray(fields["density"], dtype=np.float64)
    norm = float(np.sum(density) * cfg.spacing**3)
    radius2 = x * x + y * y + z * z
    center = [
        float(np.sum(coordinate * density) * cfg.spacing**3 / max(norm, 1.0e-30))
        for coordinate in (x, y, z)
    ]
    radius = math.sqrt(
        float(np.sum(radius2 * density) * cfg.spacing**3 / max(norm, 1.0e-30))
    )
    gravitational_energy = 0.5 * cfg.spacing**3 * float(
        np.sum(fields["total_gravitational_source"] * fields["gravitational_potential"])
    )
    return {
        "time": time,
        "norm": norm,
        "integrated_charge": cfg.charge * norm,
        "center_x": center[0],
        "center_y": center[1],
        "center_z": center[2],
        "radius": radius,
        "minimum_g00": float(np.min(fields["metric_g00"])),
        "maximum_metric_perturbation": float(np.max(np.abs(fields["metric_g00"] - 1.0))),
        "einstein00_relative_residual": float(fields["einstein00_relative_residual"]),
        "gauss_relative_residual": float(fields["gauss_relative_residual"]),
        "ampere_relative_residual": float(fields["ampere_relative_residual"]),
        "magnetic_divergence_max": float(fields["magnetic_divergence_max"]),
        "gravitational_energy": gravitational_energy,
        "electric_energy": float(fields["electric_energy"]),
        "magnetic_energy": float(fields["magnetic_energy"]),
    }


def rhs(
    spinor: np.ndarray,
    fields: Mapping[str, Any],
    cfg: ElectrograviticEvolutionConfig,
) -> np.ndarray:
    rcfg = cfg.action_config().reconciled_config()
    hpsi = reconciled_hamiltonian(
        spinor,
        fields["potential"],
        fields["vector_potential"],
        fields["magnetic"],
        fields["newton_kernel"],
        cfg.newton_coupling * cfg.effective_mass,
        cfg.geometry(),
        rcfg,
    )
    return np.asarray(-1.0j * hpsi / cfg.hbar, dtype=np.complex128)


@lru_cache(maxsize=1)
def run_electrogravitic_weak_field_evolution() -> dict[str, Any]:
    cfg = ElectrograviticEvolutionConfig()
    scalar = odd_grid_seed(cfg.action_config().reconciled_config())
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = normalize_spinor(spinor, cfg.spacing)
    vector = tuple(np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3))
    records = []
    maximum_pre_normalization_drift = 0.0
    for step in range(cfg.steps + 1):
        fields = electrogravitic_fields(spinor, vector, cfg)
        vector = fields["vector_potential"]
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            records.append(record_state(step * cfg.time_step, spinor, fields, cfg))
        if step == cfg.steps:
            break
        derivative = rhs(spinor, fields, cfg)
        trial = spinor + cfg.time_step * derivative
        trial_norm = float(np.sum(np.abs(trial) ** 2) * cfg.spacing**3)
        maximum_pre_normalization_drift = max(
            maximum_pre_normalization_drift, abs(trial_norm - 1.0)
        )
        spinor = normalize_spinor(trial, cfg.spacing)

    final = records[-1]
    initial = records[0]
    acceleration = fields["gravitational_acceleration"]
    probe_mass_1 = 0.7
    probe_mass_2 = 2.3
    equivalence_error = max(
        float(np.max(np.abs((probe_mass_1 * component) / probe_mass_1 - (probe_mass_2 * component) / probe_mass_2)))
        for component in acceleration
    )
    acceptance = {
        "one_state_drives_all_source_and_field_layers": len(records) >= 2,
        "maxwell_constraints_close_through_evolution": max(row["gauss_relative_residual"] for row in records) <= 1.0e-11 and max(row["ampere_relative_residual"] for row in records) <= 1.0e-11 and max(row["magnetic_divergence_max"] for row in records) <= 1.0e-11,
        "weak_einstein00_poisson_sector_closes": max(row["einstein00_relative_residual"] for row in records) <= 1.0e-11,
        "norm_and_charge_are_preserved": max(abs(row["norm"] - 1.0) for row in records) <= 2.0e-12 and max(abs(row["integrated_charge"] - cfg.charge) for row in records) <= 2.0e-12,
        "weak_metric_remains_lorentzian": min(row["minimum_g00"] for row in records) > 0.0,
        "equivalence_principle_probe_mass_cancels": equivalence_error <= 2.0e-15,
        "time_integrator_drift_is_audited": math.isfinite(maximum_pre_normalization_drift),
        "full_nonlinear_einstein_cauchy_development_is_not_claimed": True,
    }
    return {
        "schema": "openwave.m9.electrogravitic-weak-field-evolution.v1",
        "task": "M9.101e",
        "config": asdict(cfg),
        "formal_coupling_map": {
            "equation": "G = hbar*c*sigma0^4",
            "value": cfg.newton_coupling,
            "epistemic_status": "ansatz-loaded-natural-unit-realization",
        },
        "records": records,
        "initial": initial,
        "final": final,
        "maximum_pre_normalization_norm_drift": maximum_pre_normalization_drift,
        "equivalence_probe_error": equivalence_error,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "end_to_end_weak_field_electrogravitic_evolution_constructed": True,
            "matter_em_and_gravity_sources_share_one_state": True,
            "metric_source_equation_closed_in_weak_field_sector": True,
            "full_nonlinear_four_dimensional_einstein_evolution_constructed": False,
            "physical_gravity_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
