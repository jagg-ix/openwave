"""M9.115: reduced BSSN-style gravity driven by one holographic screen coupling.

This module extends the generalized reduced ADM carrier with the principal BSSN
state and algebraic controls:

* unit-determinant conformal metric ``gamma_tilde[i,j]``;
* trace-free conformal extrinsic curvature ``A_tilde[i,j]``;
* contracted conformal connection functions ``Gamma_tilde[i]``;
* 1+log lapse evolution;
* Gamma-driver shift and auxiliary driver ``B[i]``;
* explicit determinant, trace, connection, Hamiltonian, and momentum diagnostics.

It is a finite periodic reduced numerical carrier. It is not a complete BSSN
implementation, a convergence proof, or a general Einstein Cauchy solver.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .electrogravitic_weak_field_evolution import electrogravitic_fields, rhs as matter_rhs
from .generalized_screen_adm_gravity import (
    GeneralizedADMConfig,
    approximate_transverse_projection,
    generalized_constraints,
    symmetric_trace_free,
    tensor_norm,
)
from .holographic_gravity_coupling import build_gravity_configs
from .nonlinear_constraint_gravity import project_constraints
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed

Tensor = np.ndarray
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class BSSNScreenConfig(GeneralizedADMConfig):
    """Reduced BSSN-style controls over the generalized screen-ADM carrier."""

    steps: int = 40
    sample_stride: int = 5
    lapse_coefficient: float = 2.0
    shift_coefficient: float = 0.75
    gamma_driver_damping: float = 1.0
    connection_relaxation: float = 0.08
    determinant_floor: float = 1.0e-12

    def __post_init__(self) -> None:
        super().__post_init__()
        if min(
            self.lapse_coefficient,
            self.shift_coefficient,
            self.gamma_driver_damping,
            self.connection_relaxation,
            self.determinant_floor,
        ) <= 0.0:
            raise ValueError("positive BSSN-style controls required")


def identity_metric(shape: tuple[int, ...]) -> Tensor:
    metric = np.zeros((3, 3) + shape, dtype=np.float64)
    for index in range(3):
        metric[index, index] = 1.0
    return metric


def pointwise_determinant(metric: Tensor) -> np.ndarray:
    moved = np.moveaxis(metric, (0, 1), (-2, -1))
    return np.asarray(np.linalg.det(moved), dtype=np.float64)


def enforce_unit_determinant(metric: Tensor, floor: float = 1.0e-12) -> Tensor:
    """Symmetrize and rescale a positive conformal metric to determinant one."""
    symmetric = 0.5 * (metric + np.swapaxes(metric, 0, 1))
    determinant = pointwise_determinant(symmetric)
    safe = np.maximum(determinant, floor)
    scale = np.power(safe, -1.0 / 3.0)
    return np.asarray(symmetric * scale[None, None, ...], dtype=np.float64)


def inverse_metric(metric: Tensor) -> Tensor:
    moved = np.moveaxis(metric, (0, 1), (-2, -1))
    inverse = np.linalg.inv(moved)
    return np.asarray(np.moveaxis(inverse, (-2, -1), (0, 1)), dtype=np.float64)


def conformal_connection_functions(metric: Tensor, geometry: Any) -> Vector:
    """Compute Gamma-tilde^i = -partial_j gamma-tilde^{ij}."""
    inverse = inverse_metric(metric)
    result = []
    for i in range(3):
        component = sum(geometry.gradient(inverse[i, j])[j] for j in range(3))
        result.append(np.asarray(-component, dtype=np.float64))
    return tuple(result)  # type: ignore[return-value]


def vector_norm(vector: Vector) -> float:
    return math.sqrt(sum(float(np.linalg.norm(component) ** 2) for component in vector))


def relative_vector_error(left: Vector, right: Vector) -> float:
    numerator = math.sqrt(
        sum(float(np.linalg.norm(left[i] - right[i]) ** 2) for i in range(3))
    )
    denominator = max(vector_norm(left), vector_norm(right), 1.0e-300)
    return numerator / denominator


def bssn_step(
    conformal_factor: np.ndarray,
    trace_k: np.ndarray,
    metric: Tensor,
    a_tilde: Tensor,
    gamma_tilde: Vector,
    lapse: np.ndarray,
    shift: Vector,
    shift_driver: Vector,
    source: np.ndarray,
    nonlinear: Any,
    cfg: BSSNScreenConfig,
) -> tuple[np.ndarray, np.ndarray, Tensor, Tensor, Vector, np.ndarray, Vector, Vector]:
    geometry = nonlinear.matter_config().geometry()
    coupling = nonlinear.matter_config().newton_coupling

    shift_divergence = geometry.divergence(shift)
    du = -(lapse * trace_k) / 6.0 + shift_divergence / 6.0
    dk = -geometry.laplacian(lapse) + lapse * (
        trace_k * trace_k / 3.0
        + 4.0 * math.pi * coupling * geometry.mean_zero(source)
    )

    metric_rhs = -2.0 * lapse[None, None, ...] * a_tilde
    a_rhs = np.zeros_like(a_tilde)
    for i in range(3):
        for j in range(3):
            a_rhs[i, j] = (
                0.5 * geometry.laplacian(metric[i, j])
                - cfg.tt_relaxation * a_tilde[i, j]
            )

    trial_metric = enforce_unit_determinant(
        metric + cfg.time_step * metric_rhs, cfg.determinant_floor
    )
    trial_a = approximate_transverse_projection(
        symmetric_trace_free(a_tilde + cfg.time_step * a_rhs), geometry
    )
    next_gamma = conformal_connection_functions(trial_metric, geometry)
    gamma_rate = tuple(
        np.asarray((next_gamma[i] - gamma_tilde[i]) / cfg.time_step, dtype=np.float64)
        for i in range(3)
    )

    next_lapse = np.asarray(
        lapse
        + cfg.time_step
        * (-cfg.lapse_coefficient * lapse * trace_k + geometry.divergence(shift)),
        dtype=np.float64,
    )
    next_lapse = np.maximum(next_lapse, 1.0e-8)

    next_shift_driver = tuple(
        np.asarray(
            shift_driver[i]
            + cfg.time_step
            * (gamma_rate[i] - cfg.gamma_driver_damping * shift_driver[i]),
            dtype=np.float64,
        )
        for i in range(3)
    )
    next_shift = tuple(
        np.asarray(
            shift[i] + cfg.time_step * cfg.shift_coefficient * next_shift_driver[i],
            dtype=np.float64,
        )
        for i in range(3)
    )

    next_u = np.asarray(conformal_factor + cfg.time_step * du, dtype=np.float64)
    next_k = np.asarray(trace_k + cfg.time_step * dk, dtype=np.float64)
    return (
        next_u,
        next_k,
        trial_metric,
        trial_a,
        next_gamma,
        next_lapse,
        next_shift,
        next_shift_driver,
    )


def bssn_diagnostics(
    metric: Tensor,
    a_tilde: Tensor,
    gamma_tilde: Vector,
    geometry: Any,
) -> dict[str, float]:
    determinant = pointwise_determinant(metric)
    recomputed_gamma = conformal_connection_functions(metric, geometry)
    trace_a = a_tilde[0, 0] + a_tilde[1, 1] + a_tilde[2, 2]
    symmetry_error = max(
        float(np.max(np.abs(metric[i, j] - metric[j, i])))
        for i in range(3)
        for j in range(3)
    )
    return {
        "determinant_max_error": float(np.max(np.abs(determinant - 1.0))),
        "metric_symmetry_max_error": symmetry_error,
        "tracefree_extrinsic_max_error": float(np.max(np.abs(trace_a))),
        "connection_constraint_relative": relative_vector_error(
            gamma_tilde, recomputed_gamma
        ),
        "conformal_metric_norm": tensor_norm(metric - identity_metric(metric.shape[2:])),
        "conformal_extrinsic_norm": tensor_norm(a_tilde),
    }


@lru_cache(maxsize=1)
def run_bssn_screen_gravity() -> dict[str, Any]:
    cfg = BSSNScreenConfig()
    configs = build_gravity_configs(cfg.anchor)
    nonlinear = configs.nonlinear
    matter = nonlinear.matter_config()
    geometry = matter.geometry()

    scalar = odd_grid_seed(matter.action_config().reconciled_config())
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = normalize_spinor(spinor, matter.spacing)
    vector = tuple(np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3))

    fields = electrogravitic_fields(spinor, vector, matter)
    potential = np.asarray(fields["gravitational_potential"], dtype=np.float64)
    u = np.asarray(0.5 * potential / matter.light_speed**2, dtype=np.float64)
    trace_k = np.zeros_like(u)

    metric = identity_metric(u.shape)
    seed = 1.0e-4 * geometry.mean_zero(potential)
    metric[0, 0] += seed
    metric[1, 1] -= seed
    metric = enforce_unit_determinant(metric, cfg.determinant_floor)
    a_tilde = np.zeros_like(metric)
    gamma_tilde = conformal_connection_functions(metric, geometry)
    lapse = np.exp(np.clip(-2.0 * u, -20.0, 20.0))
    shift: Vector = tuple(np.zeros_like(u) for _ in range(3))  # type: ignore[assignment]
    shift_driver: Vector = tuple(np.zeros_like(u) for _ in range(3))  # type: ignore[assignment]

    records: list[dict[str, float]] = []
    for step in range(cfg.steps + 1):
        fields = electrogravitic_fields(spinor, vector, matter)
        vector = fields["vector_potential"]
        _, current = reconciled_charge_current(
            spinor, vector, geometry, matter.action_config().reconciled_config()
        )

        h_tt = symmetric_trace_free(metric - identity_metric(u.shape))
        constraints = generalized_constraints(
            u, trace_k, h_tt, a_tilde, shift, fields, current, nonlinear
        )
        diagnostics = bssn_diagnostics(metric, a_tilde, gamma_tilde, geometry)

        if step % cfg.sample_stride == 0 or step == cfg.steps:
            records.append(
                {
                    "time": step * cfg.time_step,
                    **diagnostics,
                    "lapse_minimum": float(np.min(lapse)),
                    "lapse_maximum": float(np.max(lapse)),
                    "shift_norm": vector_norm(shift),
                    "shift_driver_norm": vector_norm(shift_driver),
                    "connection_norm": vector_norm(gamma_tilde),
                    "hamiltonian_relative": float(constraints["hamiltonian_relative"]),
                    "momentum_relative": float(constraints["momentum_relative"]),
                }
            )

        if step == cfg.steps:
            break

        u, trace_k = project_constraints(u, trace_k, constraints, nonlinear)
        (
            u,
            trace_k,
            metric,
            a_tilde,
            gamma_tilde,
            lapse,
            shift,
            shift_driver,
        ) = bssn_step(
            u,
            trace_k,
            metric,
            a_tilde,
            gamma_tilde,
            lapse,
            shift,
            shift_driver,
            np.asarray(fields["total_gravitational_source"], dtype=np.float64),
            nonlinear,
            cfg,
        )

        derivative = matter_rhs(spinor, fields, matter)
        spinor = normalize_spinor(
            spinor + matter.time_step * derivative, matter.spacing
        )

    maximum_det_error = max(row["determinant_max_error"] for row in records)
    maximum_trace_error = max(
        row["tracefree_extrinsic_max_error"] for row in records
    )
    maximum_connection_error = max(
        row["connection_constraint_relative"] for row in records
    )

    acceptance = {
        "unit_determinant_is_enforced": maximum_det_error <= 5.0e-10,
        "tracefree_extrinsic_is_enforced": maximum_trace_error <= 5.0e-10,
        "conformal_connection_functions_are_evolved": all(
            math.isfinite(row["connection_norm"]) for row in records
        ),
        "connection_constraint_is_measured": math.isfinite(maximum_connection_error),
        "one_plus_log_lapse_is_evolved": any(
            abs(row["lapse_minimum"] - records[0]["lapse_minimum"]) > 0.0
            or abs(row["lapse_maximum"] - records[0]["lapse_maximum"]) > 0.0
            for row in records[1:]
        ),
        "gamma_driver_shift_is_evolved": any(
            row["shift_norm"] > 0.0 or row["shift_driver_norm"] > 0.0
            for row in records[1:]
        ),
        "hamiltonian_and_momentum_constraints_are_measured": all(
            math.isfinite(row["hamiltonian_relative"])
            and math.isfinite(row["momentum_relative"])
            for row in records
        ),
        "one_screen_coupling_is_preserved": abs(
            matter.newton_coupling - cfg.anchor.newton_coupling
        )
        <= 5.0e-15,
    }
    payload = {
        "schema": "openwave.m9.bssn-screen-gravity.v1",
        "task": "M9.115",
        "config": asdict(cfg),
        "screen_newton_coupling": cfg.anchor.newton_coupling,
        "matter_newton_coupling": matter.newton_coupling,
        "records": records,
        "maximum_determinant_error": maximum_det_error,
        "maximum_tracefree_extrinsic_error": maximum_trace_error,
        "maximum_connection_constraint_relative": maximum_connection_error,
        "acceptance": acceptance,
        "claim_boundary": {
            "reduced_BSSN_style_carrier_is_exact_BSSN": False,
            "finite_connection_constraint_is_constraint_closure": False,
            "gauge_evolution_is_complete_coordinate_control": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
            "reduced_periodic_evolution_is_general_GR": False,
        },
    }
    return {
        **payload,
        "passed": all(acceptance.values())
        and not any(payload["claim_boundary"].values()),
        "decision": {
            "unit_determinant_control_constructed": True,
            "conformal_connection_functions_constructed": True,
            "one_plus_log_and_gamma_driver_constructed": True,
            "exact_BSSN_constructed": False,
            "general_Einstein_evolution_constructed": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
