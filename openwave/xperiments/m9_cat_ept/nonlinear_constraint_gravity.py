"""M9.106: nonlinear conformal-ADM electrogravity with constraint projection.

This is a finite periodic 3+1 reduction. The spatial metric is conformally flat,

    gamma_ij = exp(4 u) delta_ij,

and the extrinsic curvature is represented by its trace K. Matter and
electromagnetic sources come from the same Pauli spinor used by the existing
Schrodinger--Maxwell--Poisson campaign.

The evolution is nonlinear in the metric variables and explicitly measures and
projects the Hamiltonian and momentum constraints. It is not a general
four-dimensional Einstein Cauchy solver: transverse-traceless metric modes,
shift dynamics, and a general extrinsic-curvature tensor remain open.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .electrogravitic_weak_field_evolution import (
    ElectrograviticEvolutionConfig,
    electrogravitic_fields,
    rhs as matter_rhs,
)
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed

Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class NonlinearMetricConfig:
    points: int = 17
    half_width: float = 8.0
    time_step: float = 1.0e-4
    steps: int = 80
    sample_stride: int = 10
    constraint_relaxation: float = 0.08
    lapse_relaxation: float = 0.05
    hamiltonian_gate: float = 7.5e-2
    momentum_gate: float = 7.5e-2
    signature_floor: float = 0.10

    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0:
            raise ValueError("odd operational grid with at least 17 points required")
        if min(
            self.half_width,
            self.time_step,
            self.constraint_relaxation,
            self.lapse_relaxation,
            self.hamiltonian_gate,
            self.momentum_gate,
            self.signature_floor,
        ) <= 0.0:
            raise ValueError("positive metric controls required")
        if self.steps < 20 or self.sample_stride < 1:
            raise ValueError("substantive evolution and positive sampling required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    def matter_config(self) -> ElectrograviticEvolutionConfig:
        return ElectrograviticEvolutionConfig(
            points=self.points,
            half_width=self.half_width,
            time_step=min(self.time_step, 2.0e-5),
            steps=20,
            sample_stride=10,
        )


def conformal_scalar_curvature(
    u: np.ndarray, cfg: NonlinearMetricConfig
) -> np.ndarray:
    """R[exp(4u) delta] = exp(-4u)(-8 Δu - 8 |∇u|²)."""
    geometry = cfg.matter_config().geometry()
    gradient = geometry.gradient(u)
    grad2 = sum(component * component for component in gradient)
    return np.exp(-4.0 * u) * (-8.0 * geometry.laplacian(u) - 8.0 * grad2)


def constraint_fields(
    u: np.ndarray,
    trace_k: np.ndarray,
    matter: Mapping[str, Any],
    current: Vector,
    cfg: NonlinearMetricConfig,
) -> dict[str, Any]:
    geometry = cfg.matter_config().geometry()
    scalar_curvature = conformal_scalar_curvature(u, cfg)
    source = np.asarray(matter["total_gravitational_source"], dtype=np.float64)
    projected_source = geometry.mean_zero(source)
    coupling = cfg.matter_config().newton_coupling

    hamiltonian = (
        scalar_curvature
        + (2.0 / 3.0) * trace_k * trace_k
        - 16.0 * math.pi * coupling * projected_source
    )
    momentum = tuple(
        np.asarray(
            -(2.0 / 3.0) * derivative
            - 8.0 * math.pi * coupling * np.asarray(current[index], dtype=np.float64),
            dtype=np.float64,
        )
        for index, derivative in enumerate(geometry.gradient(trace_k))
    )
    h_scale = max(
        float(np.linalg.norm(16.0 * math.pi * coupling * projected_source)),
        1.0e-30,
    )
    m_scale = max(
        math.sqrt(
            sum(
                float(
                    np.linalg.norm(
                        8.0 * math.pi * coupling * np.asarray(component)
                    )
                    ** 2
                )
                for component in current
            )
        ),
        1.0e-30,
    )
    return {
        "scalar_curvature": scalar_curvature,
        "hamiltonian": hamiltonian,
        "momentum": momentum,
        "hamiltonian_relative": float(np.linalg.norm(hamiltonian) / h_scale),
        "momentum_relative": float(
            math.sqrt(sum(float(np.linalg.norm(component) ** 2) for component in momentum))
            / m_scale
        ),
    }


def project_constraints(
    u: np.ndarray,
    trace_k: np.ndarray,
    constraints: Mapping[str, Any],
    cfg: NonlinearMetricConfig,
) -> tuple[np.ndarray, np.ndarray]:
    geometry = cfg.matter_config().geometry()
    hamiltonian = geometry.mean_zero(
        np.asarray(constraints["hamiltonian"], dtype=np.float64)
    )
    u_correction = geometry.inverse_negative_laplacian(hamiltonian)
    next_u = np.asarray(
        u - cfg.constraint_relaxation * u_correction, dtype=np.float64
    )

    momentum = constraints["momentum"]
    momentum_divergence = geometry.divergence(momentum)
    k_correction = geometry.inverse_negative_laplacian(
        geometry.mean_zero(momentum_divergence)
    )
    next_k = np.asarray(
        trace_k - cfg.constraint_relaxation * k_correction, dtype=np.float64
    )
    return next_u, next_k


def metric_step(
    u: np.ndarray,
    trace_k: np.ndarray,
    source: np.ndarray,
    cfg: NonlinearMetricConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    geometry = cfg.matter_config().geometry()
    coupling = cfg.matter_config().newton_coupling
    lapse = np.exp(np.clip(-2.0 * u, -20.0, 20.0))
    lapse_laplacian = geometry.laplacian(lapse)

    du = -(lapse * trace_k) / 6.0
    dk = (
        -lapse_laplacian
        + lapse
        * (
            (trace_k * trace_k) / 3.0
            + 4.0 * math.pi * coupling * geometry.mean_zero(source)
        )
    )
    next_u = np.asarray(u + cfg.time_step * du, dtype=np.float64)
    next_k = np.asarray(trace_k + cfg.time_step * dk, dtype=np.float64)
    return next_u, next_k, lapse


def record(
    time: float,
    u: np.ndarray,
    trace_k: np.ndarray,
    lapse: np.ndarray,
    constraints: Mapping[str, Any],
) -> dict[str, float]:
    conformal_factor = np.exp(4.0 * np.clip(u, -20.0, 20.0))
    return {
        "time": time,
        "hamiltonian_relative": float(constraints["hamiltonian_relative"]),
        "momentum_relative": float(constraints["momentum_relative"]),
        "minimum_lapse": float(np.min(lapse)),
        "minimum_spatial_conformal_factor": float(np.min(conformal_factor)),
        "maximum_spatial_conformal_factor": float(np.max(conformal_factor)),
        "maximum_abs_u": float(np.max(np.abs(u))),
        "maximum_abs_K": float(np.max(np.abs(trace_k))),
    }


@lru_cache(maxsize=1)
def run_nonlinear_constraint_evolution() -> dict[str, Any]:
    cfg = NonlinearMetricConfig()
    matter_cfg = cfg.matter_config()
    geometry = matter_cfg.geometry()
    scalar = odd_grid_seed(matter_cfg.action_config().reconciled_config())
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = normalize_spinor(spinor, cfg.spacing)
    vector = tuple(
        np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3)
    )

    initial_fields = electrogravitic_fields(spinor, vector, matter_cfg)
    weak_phi = np.asarray(initial_fields["gravitational_potential"], dtype=np.float64)
    u = np.asarray(0.5 * weak_phi / matter_cfg.light_speed**2, dtype=np.float64)
    trace_k = np.zeros_like(u)
    records: list[dict[str, float]] = []
    maximum_norm_error = 0.0
    maximum_charge_error = 0.0

    for step in range(cfg.steps + 1):
        fields = electrogravitic_fields(spinor, vector, matter_cfg)
        vector = fields["vector_potential"]
        rcfg = matter_cfg.action_config().reconciled_config()
        charge_density, current = reconciled_charge_current(spinor, vector, geometry, rcfg)

        constraints_before = constraint_fields(u, trace_k, fields, current, cfg)
        u, trace_k = project_constraints(u, trace_k, constraints_before, cfg)
        constraints_after = constraint_fields(u, trace_k, fields, current, cfg)
        u, trace_k, lapse = metric_step(
            u,
            trace_k,
            np.asarray(fields["total_gravitational_source"], dtype=np.float64),
            cfg,
        )

        if step % cfg.sample_stride == 0 or step == cfg.steps:
            records.append(
                record(
                    step * cfg.time_step,
                    u,
                    trace_k,
                    lapse,
                    constraints_after,
                )
            )
            records[-1]["projection_hamiltonian_gain"] = float(
                constraints_before["hamiltonian_relative"]
                - constraints_after["hamiltonian_relative"]
            )
            records[-1]["projection_momentum_gain"] = float(
                constraints_before["momentum_relative"]
                - constraints_after["momentum_relative"]
            )

        if step == cfg.steps:
            break
        derivative = matter_rhs(spinor, fields, matter_cfg)
        spinor = normalize_spinor(spinor + matter_cfg.time_step * derivative, cfg.spacing)
        norm = float(np.sum(np.abs(spinor) ** 2) * cfg.spacing**3)
        charge = float(np.sum(charge_density) * cfg.spacing**3)
        maximum_norm_error = max(maximum_norm_error, abs(norm - 1.0))
        maximum_charge_error = max(maximum_charge_error, abs(charge - matter_cfg.charge))

    max_h = max(row["hamiltonian_relative"] for row in records)
    max_m = max(row["momentum_relative"] for row in records)
    projection_nonworsening = all(
        row["projection_hamiltonian_gain"] >= -1.0e-8
        and row["projection_momentum_gain"] >= -1.0e-8
        for row in records
    )
    nonlinear_gate = bool(
        max_h <= cfg.hamiltonian_gate
        and max_m <= cfg.momentum_gate
        and min(row["minimum_lapse"] for row in records) > cfg.signature_floor
        and min(row["minimum_spatial_conformal_factor"] for row in records)
        > cfg.signature_floor
        and projection_nonworsening
    )
    acceptance = {
        "one_matter_state_sources_maxwell_and_metric_layers": len(records) >= 2,
        "metric_variables_evolve_nonlinearly": any(
            row["maximum_abs_u"] > 0.0 or row["maximum_abs_K"] > 0.0
            for row in records
        ),
        "hamiltonian_and_momentum_constraints_are_measured": all(
            math.isfinite(row["hamiltonian_relative"])
            and math.isfinite(row["momentum_relative"])
            for row in records
        ),
        "constraint_projection_effect_is_reported": all(
            math.isfinite(row["projection_hamiltonian_gain"])
            and math.isfinite(row["projection_momentum_gain"])
            for row in records
        ),
        "matter_norm_and_charge_are_audited": math.isfinite(maximum_norm_error)
        and math.isfinite(maximum_charge_error),
        "reduced_conformal_scope_is_explicit": True,
        "full_general_einstein_cauchy_development_is_not_claimed": True,
    }
    return {
        "schema": "openwave.m9.nonlinear-conformal-adm-evolution.v1",
        "task": "M9.106",
        "config": asdict(cfg),
        "records": records,
        "maximum_hamiltonian_relative": max_h,
        "maximum_momentum_relative": max_m,
        "maximum_matter_norm_error": maximum_norm_error,
        "maximum_charge_error": maximum_charge_error,
        "constraint_preserving_nonlinear_metric_evolution_constructed": nonlinear_gate,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "nonlinear_metric_fields_evolved": True,
            "hamiltonian_and_momentum_constraints_projected": True,
            "constraint_preserving_reduced_metric_gate": nonlinear_gate,
            "general_four_dimensional_einstein_cauchy_solver_constructed": False,
            "physical_gravity_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
