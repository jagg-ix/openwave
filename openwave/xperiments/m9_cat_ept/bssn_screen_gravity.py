"""M9.115: reduced BSSN-style gravity with one holographic screen coupling.

This layer extends the generalized ADM carrier with:

* a conformal metric ``g_tilde`` projected to unit determinant;
* trace-free conformal extrinsic curvature ``A_tilde``;
* conformal connection functions ``Gamma_tilde^i``;
* 1+log lapse evolution;
* a damped Gamma-driver shift and auxiliary ``B^i`` field;
* explicit algebraic and differential constraint diagnostics.

It is a finite periodic reduced BSSN-style model, not a complete production BSSN
implementation or a proof of general Einstein evolution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .electrogravitic_weak_field_evolution import electrogravitic_fields, rhs as matter_rhs
from .generalized_screen_adm_gravity import symmetric_trace_free, tensor_divergence, tensor_norm
from .holographic_gravity_coupling import ScreenDensityAnchor, build_gravity_configs
from .nonlinear_constraint_gravity import constraint_fields
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed

Tensor = np.ndarray
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class BSSNScreenConfig:
    points: int = 17
    half_width: float = 8.0
    time_step: float = 5.0e-5
    steps: int = 40
    sample_stride: int = 5
    screen_area: float = 2.0
    screen_bits: float = 8.0
    hbar: float = 1.0
    light_speed: float = 1.0
    gamma_damping: float = 0.8
    shift_driver: float = 0.75
    trace_relaxation: float = 0.05

    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0:
            raise ValueError("odd operational grid with at least 17 points required")
        if self.steps < 10 or self.sample_stride < 1:
            raise ValueError("substantive evolution and positive sampling required")
        if min(
            self.half_width,
            self.time_step,
            self.screen_area,
            self.screen_bits,
            self.hbar,
            self.light_speed,
            self.gamma_damping,
            self.shift_driver,
            self.trace_relaxation,
        ) <= 0.0:
            raise ValueError("positive BSSN controls required")

    @property
    def anchor(self) -> ScreenDensityAnchor:
        return ScreenDensityAnchor(
            area=self.screen_area,
            bits=self.screen_bits,
            hbar=self.hbar,
            c=self.light_speed,
            evidence_class="external",
            source="synthetic BSSN fixture; not physical evidence",
        )


def determinant_field(metric: Tensor) -> np.ndarray:
    """Pointwise determinant of a 3x3 metric field."""
    moved = np.moveaxis(metric, (0, 1), (-2, -1))
    return np.asarray(np.linalg.det(moved), dtype=np.float64)


def inverse_metric_field(metric: Tensor) -> Tensor:
    moved = np.moveaxis(metric, (0, 1), (-2, -1))
    inverse = np.linalg.inv(moved)
    return np.asarray(np.moveaxis(inverse, (-2, -1), (0, 1)), dtype=np.float64)


def enforce_unit_determinant(metric: Tensor) -> Tensor:
    """Symmetrize and rescale a positive conformal metric to det(g_tilde)=1."""
    symmetric = 0.5 * (metric + np.swapaxes(metric, 0, 1))
    determinant = determinant_field(symmetric)
    if np.any(determinant <= 0.0):
        raise ValueError("positive conformal metric determinant required")
    factor = np.power(determinant, -1.0 / 3.0)
    return np.asarray(symmetric * factor[None, None, ...], dtype=np.float64)


def conformal_connection(metric: Tensor, geometry: Any) -> Vector:
    """Compute Gamma_tilde^i = -partial_j g_tilde^{ij}."""
    inverse = inverse_metric_field(metric)
    values = []
    for i in range(3):
        connection = np.zeros_like(metric[0, 0])
        for j in range(3):
            connection -= geometry.gradient(inverse[i, j])[j]
        values.append(np.asarray(connection, dtype=np.float64))
    return tuple(values)  # type: ignore[return-value]


def vector_relative_error(a: Vector, b: Vector) -> float:
    numerator = math.sqrt(sum(float(np.linalg.norm(a[i] - b[i]) ** 2) for i in range(3)))
    denominator = max(
        math.sqrt(sum(float(np.linalg.norm(a[i]) ** 2) for i in range(3))),
        math.sqrt(sum(float(np.linalg.norm(b[i]) ** 2) for i in range(3))),
        1.0e-300,
    )
    return numerator / denominator


def initialize_bssn_state(phi: np.ndarray, geometry: Any) -> dict[str, Any]:
    chi = np.exp(np.clip(-2.0 * phi, -20.0, 20.0))
    metric = np.zeros((3, 3) + phi.shape, dtype=np.float64)
    for i in range(3):
        metric[i, i] = 1.0
    seed = 1.0e-4 * geometry.mean_zero(phi)
    metric[0, 0] += seed
    metric[1, 1] -= seed
    metric = enforce_unit_determinant(metric)
    a_tilde = np.zeros_like(metric)
    trace_k = np.zeros_like(phi)
    lapse = np.ones_like(phi)
    beta: Vector = tuple(np.zeros_like(phi) for _ in range(3))  # type: ignore[assignment]
    driver_b: Vector = tuple(np.zeros_like(phi) for _ in range(3))  # type: ignore[assignment]
    gamma_tilde = conformal_connection(metric, geometry)
    return {
        "chi": chi,
        "metric": metric,
        "a_tilde": a_tilde,
        "trace_k": trace_k,
        "lapse": lapse,
        "beta": beta,
        "driver_b": driver_b,
        "gamma_tilde": gamma_tilde,
    }


def bssn_step(
    state: Mapping[str, Any],
    source: np.ndarray,
    geometry: Any,
    coupling: float,
    cfg: BSSNScreenConfig,
) -> dict[str, Any]:
    chi = np.asarray(state["chi"], dtype=np.float64)
    metric = np.asarray(state["metric"], dtype=np.float64)
    a_tilde = np.asarray(state["a_tilde"], dtype=np.float64)
    trace_k = np.asarray(state["trace_k"], dtype=np.float64)
    lapse = np.asarray(state["lapse"], dtype=np.float64)
    beta: Vector = state["beta"]
    driver_b: Vector = state["driver_b"]
    gamma_old: Vector = state["gamma_tilde"]

    beta_div = geometry.divergence(beta)
    chi_rhs = (2.0 / 3.0) * chi * (lapse * trace_k - beta_div)
    lapse_rhs = -2.0 * lapse * trace_k
    k_rhs = -geometry.laplacian(lapse) + lapse * (
        trace_k * trace_k / 3.0 + 4.0 * math.pi * coupling * geometry.mean_zero(source)
    )

    metric_rhs = -2.0 * lapse[None, None, ...] * a_tilde
    a_rhs = np.zeros_like(a_tilde)
    for i in range(3):
        for j in range(3):
            a_rhs[i, j] = (
                0.5 * geometry.laplacian(metric[i, j])
                - cfg.trace_relaxation * a_tilde[i, j]
            )
    a_rhs = symmetric_trace_free(a_rhs)

    next_chi = np.asarray(chi + cfg.time_step * chi_rhs, dtype=np.float64)
    next_k = np.asarray(trace_k + cfg.time_step * k_rhs, dtype=np.float64)
    next_lapse = np.asarray(lapse + cfg.time_step * lapse_rhs, dtype=np.float64)
    next_metric = enforce_unit_determinant(metric + cfg.time_step * metric_rhs)
    next_a = symmetric_trace_free(a_tilde + cfg.time_step * a_rhs)
    gamma_target = conformal_connection(next_metric, geometry)

    next_driver = tuple(
        np.asarray(
            driver_b[i]
            + cfg.time_step
            * (gamma_target[i] - gamma_old[i] - cfg.gamma_damping * driver_b[i]),
            dtype=np.float64,
        )
        for i in range(3)
    )
    next_beta = tuple(
        np.asarray(beta[i] + cfg.time_step * cfg.shift_driver * next_driver[i], dtype=np.float64)
        for i in range(3)
    )
    next_gamma = conformal_connection(next_metric, geometry)

    return {
        "chi": next_chi,
        "metric": next_metric,
        "a_tilde": next_a,
        "trace_k": next_k,
        "lapse": next_lapse,
        "beta": next_beta,
        "driver_b": next_driver,
        "gamma_tilde": next_gamma,
    }


def bssn_diagnostics(
    state: Mapping[str, Any],
    fields: Mapping[str, Any],
    current: Vector,
    nonlinear: Any,
) -> dict[str, float]:
    metric = np.asarray(state["metric"], dtype=np.float64)
    a_tilde = np.asarray(state["a_tilde"], dtype=np.float64)
    geometry = nonlinear.matter_config().geometry()
    determinant = determinant_field(metric)
    gamma_from_metric = conformal_connection(metric, geometry)
    gamma_stored: Vector = state["gamma_tilde"]
    base = constraint_fields(
        -0.5 * np.log(np.maximum(np.asarray(state["chi"]), 1.0e-300)),
        np.asarray(state["trace_k"]),
        fields,
        current,
        nonlinear,
    )
    return {
        "determinant_error_max": float(np.max(np.abs(determinant - 1.0))),
        "a_tilde_trace_max": float(
            np.max(np.abs(a_tilde[0, 0] + a_tilde[1, 1] + a_tilde[2, 2]))
        ),
        "gamma_constraint_relative": vector_relative_error(gamma_stored, gamma_from_metric),
        "gamma_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in gamma_stored)),
        "shift_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in state["beta"])),
        "driver_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in state["driver_b"])),
        "minimum_lapse": float(np.min(state["lapse"])),
        "maximum_lapse": float(np.max(state["lapse"])),
        "hamiltonian_relative": float(base["hamiltonian_relative"]),
        "momentum_relative": float(base["momentum_relative"]),
        "metric_norm": tensor_norm(metric),
        "a_tilde_norm": tensor_norm(a_tilde),
        "a_tilde_divergence_norm": math.sqrt(
            sum(float(np.linalg.norm(v) ** 2) for v in tensor_divergence(a_tilde, geometry))
        ),
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
    phi = np.asarray(fields["gravitational_potential"], dtype=np.float64) / matter.light_speed**2
    state = initialize_bssn_state(phi, geometry)
    records: list[dict[str, float]] = []

    for step in range(cfg.steps + 1):
        fields = electrogravitic_fields(spinor, vector, matter)
        vector = fields["vector_potential"]
        _, current = reconciled_charge_current(
            spinor, vector, geometry, matter.action_config().reconciled_config()
        )
        diagnostics = bssn_diagnostics(state, fields, current, nonlinear)
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            records.append({"time": step * cfg.time_step, **diagnostics})
        if step == cfg.steps:
            break
        state = bssn_step(
            state,
            np.asarray(fields["total_gravitational_source"], dtype=np.float64),
            geometry,
            matter.newton_coupling,
            cfg,
        )
        derivative = matter_rhs(spinor, fields, matter)
        spinor = normalize_spinor(spinor + matter.time_step * derivative, matter.spacing)

    max_det = max(row["determinant_error_max"] for row in records)
    max_trace = max(row["a_tilde_trace_max"] for row in records)
    max_gamma_constraint = max(row["gamma_constraint_relative"] for row in records)
    acceptance = {
        "one_screen_G_is_preserved": abs(matter.newton_coupling - cfg.anchor.newton_coupling)
        / max(abs(cfg.anchor.newton_coupling), 1.0e-300)
        <= 5.0e-15,
        "conformal_metric_unit_determinant_is_enforced": max_det <= 5.0e-12,
        "conformal_extrinsic_curvature_remains_trace_free": max_trace <= 5.0e-12,
        "conformal_connection_constraint_is_measured": math.isfinite(max_gamma_constraint),
        "one_plus_log_lapse_is_evolved": any(
            abs(row["minimum_lapse"] - 1.0) > 0.0 or abs(row["maximum_lapse"] - 1.0) > 0.0
            for row in records[1:]
        ),
        "gamma_driver_shift_is_evolved": any(row["shift_norm"] > 0.0 for row in records[1:]),
        "hamiltonian_and_momentum_constraints_are_reported": all(
            math.isfinite(row["hamiltonian_relative"])
            and math.isfinite(row["momentum_relative"])
            for row in records
        ),
        "exact_production_BSSN_is_not_claimed": True,
    }
    payload = {
        "schema": "openwave.m9.bssn-screen-gravity.v1",
        "task": "M9.115",
        "config": asdict(cfg),
        "screen_newton_coupling": cfg.anchor.newton_coupling,
        "records": records,
        "maximum_determinant_error": max_det,
        "maximum_tracefree_error": max_trace,
        "maximum_gamma_constraint_relative": max_gamma_constraint,
        "claim_boundary": {
            "reduced_BSSN_is_production_numerical_relativity": False,
            "finite_constraints_are_general_constraint_closure": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
            "gauge_evolution_is_unique_physical_gauge": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "decision": {
            "conformal_connection_functions_constructed": True,
            "unit_determinant_control_constructed": True,
            "one_plus_log_and_gamma_driver_constructed": True,
            "production_BSSN_constructed": False,
            "physical_screen_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
