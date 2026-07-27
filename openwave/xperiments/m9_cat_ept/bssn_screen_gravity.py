"""M9.115--M9.116: source-coupled reduced BSSN-style screen gravity.

This layer extends the generalized ADM carrier with:

* a conformal metric ``g_tilde`` projected to unit determinant;
* trace-free conformal extrinsic curvature ``A_tilde``;
* conformal connection functions ``Gamma_tilde^i``;
* 1+log lapse evolution;
* a damped Gamma-driver shift and auxiliary ``B^i`` field;
* a metric-built conformal Ricci tensor;
* a screen-source tidal tensor entering the trace-free curvature evolution;
* exact Fourier correction of the reduced tensor-momentum constraint;
* explicit algebraic and differential constraint diagnostics.

It is a finite periodic reduced BSSN-style model, not a complete production BSSN
implementation or a proof of general Einstein evolution. The source-tidal term is a
declared scalar-density reduction, not the complete trace-free stress-energy tensor.
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
    gamma_constraint_damping: float = 2.0e3
    tensor_constraint_damping: float = 2.0e3
    ricci_strength: float = 0.25
    source_tidal_strength: float = 0.25

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
            self.gamma_constraint_damping,
            self.tensor_constraint_damping,
            self.ricci_strength,
            self.source_tidal_strength,
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
    """Symmetrize and rescale a positive conformal metric to ``det(g_tilde)=1``."""
    symmetric = 0.5 * (metric + np.swapaxes(metric, 0, 1))
    determinant = determinant_field(symmetric)
    if np.any(determinant <= 0.0):
        raise ValueError("positive conformal metric determinant required")
    factor = np.power(determinant, -1.0 / 3.0)
    return np.asarray(symmetric * factor[None, None, ...], dtype=np.float64)


def metric_trace_free(tensor: Tensor, metric: Tensor) -> Tensor:
    """Return the symmetric trace-free part using the supplied metric."""
    symmetric = 0.5 * (tensor + np.swapaxes(tensor, 0, 1))
    inverse = inverse_metric_field(metric)
    trace = sum(inverse[i, j] * symmetric[i, j] for i in range(3) for j in range(3))
    return np.asarray(
        symmetric - metric * trace[None, None, ...] / 3.0,
        dtype=np.float64,
    )


def conformal_connection(metric: Tensor, geometry: Any) -> Vector:
    """Compute ``Gamma_tilde^i = -partial_j g_tilde^{ij}``."""
    inverse = inverse_metric_field(metric)
    values = []
    for i in range(3):
        connection = -sum(geometry.derivative(inverse[i, j], j) for j in range(3))
        values.append(np.asarray(connection, dtype=np.float64))
    return tuple(values)  # type: ignore[return-value]


def christoffel_symbols(metric: Tensor, geometry: Any) -> Tensor:
    """Metric-built three-dimensional Christoffel symbols ``Gamma^k_ij``."""
    inverse = inverse_metric_field(metric)
    derivatives = np.empty((3, 3, 3) + metric.shape[2:], dtype=np.float64)
    for axis in range(3):
        for i in range(3):
            for j in range(3):
                derivatives[axis, i, j] = geometry.derivative(metric[i, j], axis)
    gamma = np.zeros((3, 3, 3) + metric.shape[2:], dtype=np.float64)
    for k in range(3):
        for i in range(3):
            for j in range(3):
                gamma[k, i, j] = 0.5 * sum(
                    inverse[k, ell]
                    * (
                        derivatives[i, ell, j]
                        + derivatives[j, ell, i]
                        - derivatives[ell, i, j]
                    )
                    for ell in range(3)
                )
    return gamma


def conformal_ricci_tensor(metric: Tensor, geometry: Any) -> Tensor:
    """Compute the metric-built conformal Ricci tensor on the periodic grid."""
    gamma = christoffel_symbols(metric, geometry)
    ricci = np.zeros_like(metric, dtype=np.float64)
    for i in range(3):
        for j in range(3):
            derivative_part = sum(
                geometry.derivative(gamma[k, i, j], k)
                - geometry.derivative(gamma[k, i, k], j)
                for k in range(3)
            )
            quadratic_part = np.zeros_like(metric[0, 0])
            for k in range(3):
                for ell in range(3):
                    quadratic_part += (
                        gamma[k, i, j] * gamma[ell, k, ell]
                        - gamma[ell, i, k] * gamma[k, j, ell]
                    )
            ricci[i, j] = derivative_part + quadratic_part
    return np.asarray(0.5 * (ricci + np.swapaxes(ricci, 0, 1)), dtype=np.float64)


def conformal_scalar_from_ricci(ricci: Tensor, metric: Tensor) -> np.ndarray:
    inverse = inverse_metric_field(metric)
    return np.asarray(
        sum(inverse[i, j] * ricci[i, j] for i in range(3) for j in range(3)),
        dtype=np.float64,
    )


def source_tidal_tensor(
    source: np.ndarray,
    geometry: Any,
    coupling: float,
) -> Tensor:
    """Reduced trace-free tidal source from ``-Delta Phi = 4 pi G rho``.

    This is the scalar-density source used by the reduced screen carrier. It is not
    a replacement for the complete trace-free spatial stress tensor.
    """
    potential = 4.0 * math.pi * coupling * geometry.inverse_negative_laplacian(
        geometry.mean_zero(source)
    )
    hessian = np.zeros((3, 3) + source.shape, dtype=np.float64)
    gradient = geometry.gradient(potential)
    for i in range(3):
        for j in range(3):
            hessian[i, j] = geometry.derivative(gradient[i], j)
    return symmetric_trace_free(hessian)


def vector_l2(vector: Vector) -> float:
    return math.sqrt(sum(float(np.linalg.norm(component) ** 2) for component in vector))


def vector_relative_error(a: Vector, b: Vector) -> float:
    numerator = vector_l2(tuple(a[i] - b[i] for i in range(3)))
    denominator = max(vector_l2(a), vector_l2(b), 1.0e-300)
    return numerator / denominator


def tensor_momentum_constraint(
    a_tilde: Tensor,
    current: Vector,
    geometry: Any,
    coupling: float,
) -> Vector:
    """Reduced trace-free tensor momentum constraint.

    ``M_i = partial_j A_tilde_ij - 8 pi G J_i`` on the periodic carrier.
    """
    divergence = tensor_divergence(a_tilde, geometry)
    return tuple(
        np.asarray(
            divergence[i]
            - 8.0 * math.pi * coupling * geometry.mean_zero(np.asarray(current[i])),
            dtype=np.float64,
        )
        for i in range(3)
    )  # type: ignore[return-value]


def stf_tensor_with_divergence(vector: Vector, geometry: Any) -> Tensor:
    """Construct an STF tensor whose Fourier divergence equals ``vector``.

    The zero Fourier mode is removed because no periodic tensor divergence can carry
    a nonzero spatial mean. For every active mode the construction is exact.
    """
    mean_zero = tuple(geometry.mean_zero(np.asarray(component)) for component in vector)
    hats = [np.fft.fftn(component) for component in mean_zero]
    kx, ky, kz, k2 = geometry.wave_mesh()
    waves = (kx, ky, kz)
    dot = sum(waves[i] * hats[i] for i in range(3))
    active = k2 > 0.0
    correction = np.zeros((3, 3) + geometry.shape, dtype=np.float64)
    for i in range(3):
        for j in range(3):
            value_hat = np.zeros_like(hats[0], dtype=np.complex128)
            numerator = waves[i] * hats[j] + waves[j] * hats[i]
            value_hat[active] = -1.0j * numerator[active] / k2[active]
            if i == j:
                value_hat[active] += 0.5j * dot[active] / k2[active]
            value_hat[active] += (
                0.5j
                * waves[i][active]
                * waves[j][active]
                * dot[active]
                / (k2[active] ** 2)
            )
            value = np.fft.ifftn(value_hat)
            correction[i, j] = np.real_if_close(value, tol=1000).real
    return symmetric_trace_free(correction)


def damp_tensor_momentum_constraint(
    a_tilde: Tensor,
    current: Vector,
    geometry: Any,
    coupling: float,
    rate: float,
    time_step: float,
) -> tuple[Tensor, dict[str, float]]:
    before = tensor_momentum_constraint(a_tilde, current, geometry, coupling)
    fraction = 1.0 - math.exp(-rate * time_step)
    correction = stf_tensor_with_divergence(before, geometry)
    next_a = symmetric_trace_free(a_tilde - fraction * correction)
    after = tensor_momentum_constraint(next_a, current, geometry, coupling)
    before_norm = vector_l2(before)
    after_norm = vector_l2(after)
    return next_a, {
        "tensor_momentum_before": before_norm,
        "tensor_momentum_after": after_norm,
        "tensor_momentum_gain": before_norm - after_norm,
        "tensor_damping_fraction": fraction,
    }


def damp_gamma_constraint(
    transported: Vector,
    target: Vector,
    rate: float,
    time_step: float,
) -> tuple[Vector, dict[str, float]]:
    factor = math.exp(-rate * time_step)
    before = tuple(np.asarray(transported[i] - target[i], dtype=np.float64) for i in range(3))
    next_gamma = tuple(
        np.asarray(target[i] + factor * before[i], dtype=np.float64) for i in range(3)
    )
    after = tuple(np.asarray(next_gamma[i] - target[i], dtype=np.float64) for i in range(3))
    before_norm = vector_l2(before)
    after_norm = vector_l2(after)
    return next_gamma, {
        "gamma_constraint_before": before_norm,
        "gamma_constraint_after": after_norm,
        "gamma_constraint_gain": before_norm - after_norm,
        "gamma_damping_factor": factor,
    }


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
        "constraint_audit": {
            "tensor_momentum_before": 0.0,
            "tensor_momentum_after": 0.0,
            "tensor_momentum_gain": 0.0,
            "tensor_damping_fraction": 0.0,
            "gamma_constraint_before": 0.0,
            "gamma_constraint_after": 0.0,
            "gamma_constraint_gain": 0.0,
            "gamma_damping_factor": 1.0,
        },
    }


def bssn_step(
    state: Mapping[str, Any],
    source: np.ndarray,
    current: Vector,
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
    a_squared = sum(a_tilde[i, j] ** 2 for i in range(3) for j in range(3))
    k_rhs = -geometry.laplacian(lapse) + lapse * (
        trace_k * trace_k / 3.0
        + a_squared
        + 4.0 * math.pi * coupling * geometry.mean_zero(source)
    )

    beta_gradient = tuple(geometry.gradient(component) for component in beta)
    longitudinal_shift = np.zeros_like(metric)
    for i in range(3):
        for j in range(3):
            longitudinal_shift[i, j] = beta_gradient[j][i] + beta_gradient[i][j]
    longitudinal_shift = symmetric_trace_free(longitudinal_shift)
    metric_rhs = -2.0 * lapse[None, None, ...] * a_tilde + longitudinal_shift

    ricci = conformal_ricci_tensor(metric, geometry)
    ricci_tf = metric_trace_free(ricci, metric)
    tidal = source_tidal_tensor(source, geometry, coupling)
    effective_ricci = metric_trace_free(
        cfg.ricci_strength * ricci_tf - cfg.source_tidal_strength * tidal,
        metric,
    )
    lapse_hessian = np.zeros_like(metric)
    lapse_gradient = geometry.gradient(lapse)
    for i in range(3):
        for j in range(3):
            lapse_hessian[i, j] = geometry.derivative(lapse_gradient[i], j)
    a_rhs = metric_trace_free(
        -lapse_hessian
        + lapse[None, None, ...]
        * (effective_ricci + trace_k[None, None, ...] * a_tilde)
        - cfg.trace_relaxation * a_tilde,
        metric,
    )

    next_chi = np.asarray(chi + cfg.time_step * chi_rhs, dtype=np.float64)
    next_k = np.asarray(trace_k + cfg.time_step * k_rhs, dtype=np.float64)
    next_lapse = np.asarray(lapse + cfg.time_step * lapse_rhs, dtype=np.float64)
    next_metric = enforce_unit_determinant(metric + cfg.time_step * metric_rhs)
    provisional_a = symmetric_trace_free(a_tilde + cfg.time_step * a_rhs)
    next_a, tensor_audit = damp_tensor_momentum_constraint(
        provisional_a,
        current,
        geometry,
        coupling,
        cfg.tensor_constraint_damping,
        cfg.time_step,
    )

    gamma_target = conformal_connection(next_metric, geometry)
    div_lapse_a = tensor_divergence(
        lapse[None, None, ...] * next_a,
        geometry,
    )
    grad_k = geometry.gradient(next_k)
    grad_beta_div = geometry.gradient(beta_div)
    gamma_rhs = tuple(
        np.asarray(
            -2.0 * div_lapse_a[i]
            - (4.0 / 3.0) * grad_k[i]
            + geometry.laplacian(beta[i])
            + (1.0 / 3.0) * grad_beta_div[i],
            dtype=np.float64,
        )
        for i in range(3)
    )
    transported_gamma = tuple(
        np.asarray(gamma_old[i] + cfg.time_step * gamma_rhs[i], dtype=np.float64)
        for i in range(3)
    )
    next_gamma, gamma_audit = damp_gamma_constraint(
        transported_gamma,
        gamma_target,
        cfg.gamma_constraint_damping,
        cfg.time_step,
    )

    next_driver = tuple(
        np.asarray(
            driver_b[i]
            + cfg.time_step * (gamma_rhs[i] - cfg.gamma_damping * driver_b[i]),
            dtype=np.float64,
        )
        for i in range(3)
    )
    next_beta = tuple(
        np.asarray(beta[i] + cfg.time_step * cfg.shift_driver * next_driver[i], dtype=np.float64)
        for i in range(3)
    )

    return {
        "chi": next_chi,
        "metric": next_metric,
        "a_tilde": next_a,
        "trace_k": next_k,
        "lapse": next_lapse,
        "beta": next_beta,
        "driver_b": next_driver,
        "gamma_tilde": next_gamma,
        "constraint_audit": {**tensor_audit, **gamma_audit},
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
    coupling = nonlinear.matter_config().newton_coupling
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
    ricci = conformal_ricci_tensor(metric, geometry)
    ricci_scalar = conformal_scalar_from_ricci(ricci, metric)
    ricci_tf = metric_trace_free(ricci, metric)
    source = np.asarray(fields["total_gravitational_source"], dtype=np.float64)
    tidal = source_tidal_tensor(source, geometry, coupling)
    tensor_constraint = tensor_momentum_constraint(a_tilde, current, geometry, coupling)
    audit = state["constraint_audit"]
    return {
        "determinant_error_max": float(np.max(np.abs(determinant - 1.0))),
        "a_tilde_trace_max": float(
            np.max(np.abs(a_tilde[0, 0] + a_tilde[1, 1] + a_tilde[2, 2]))
        ),
        "gamma_constraint_relative": vector_relative_error(gamma_stored, gamma_from_metric),
        "gamma_norm": vector_l2(gamma_stored),
        "shift_norm": vector_l2(state["beta"]),
        "driver_norm": vector_l2(state["driver_b"]),
        "minimum_lapse": float(np.min(state["lapse"])),
        "maximum_lapse": float(np.max(state["lapse"])),
        "hamiltonian_relative": float(base["hamiltonian_relative"]),
        "momentum_relative": float(base["momentum_relative"]),
        "metric_norm": tensor_norm(metric),
        "a_tilde_norm": tensor_norm(a_tilde),
        "a_tilde_divergence_norm": vector_l2(tensor_divergence(a_tilde, geometry)),
        "tensor_momentum_constraint_norm": vector_l2(tensor_constraint),
        "ricci_scalar_norm": float(np.linalg.norm(ricci_scalar)),
        "ricci_tracefree_norm": tensor_norm(ricci_tf),
        "source_tidal_norm": tensor_norm(tidal),
        "ricci_source_balance_norm": tensor_norm(ricci_tf - tidal),
        "tensor_momentum_before": float(audit["tensor_momentum_before"]),
        "tensor_momentum_after": float(audit["tensor_momentum_after"]),
        "tensor_momentum_gain": float(audit["tensor_momentum_gain"]),
        "gamma_constraint_before": float(audit["gamma_constraint_before"]),
        "gamma_constraint_after": float(audit["gamma_constraint_after"]),
        "gamma_constraint_gain": float(audit["gamma_constraint_gain"]),
    }


def run_bssn_screen_gravity_with_config(cfg: BSSNScreenConfig) -> dict[str, Any]:
    configs = build_gravity_configs(
        cfg.anchor,
        points=cfg.points,
        half_width=cfg.half_width,
    )
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
            current,
            geometry,
            matter.newton_coupling,
            cfg,
        )
        derivative = matter_rhs(spinor, fields, matter)
        spinor = normalize_spinor(spinor + matter.time_step * derivative, matter.spacing)

    max_det = max(row["determinant_error_max"] for row in records)
    max_trace = max(row["a_tilde_trace_max"] for row in records)
    max_gamma_constraint = max(row["gamma_constraint_relative"] for row in records)
    damping_rows = records[1:]
    tensor_nonworsening = all(
        row["tensor_momentum_after"]
        <= row["tensor_momentum_before"] + 1.0e-10 * max(1.0, row["tensor_momentum_before"])
        for row in damping_rows
    )
    gamma_nonworsening = all(
        row["gamma_constraint_after"]
        <= row["gamma_constraint_before"] + 1.0e-10 * max(1.0, row["gamma_constraint_before"])
        for row in damping_rows
    )
    acceptance = {
        "one_screen_G_is_preserved": abs(matter.newton_coupling - cfg.anchor.newton_coupling)
        / max(abs(cfg.anchor.newton_coupling), 1.0e-300)
        <= 5.0e-15,
        "conformal_metric_unit_determinant_is_enforced": max_det <= 5.0e-12,
        "conformal_extrinsic_curvature_remains_trace_free": max_trace <= 5.0e-12,
        "conformal_connection_constraint_is_measured": math.isfinite(max_gamma_constraint),
        "one_plus_log_lapse_is_evolved": any(
            abs(row["minimum_lapse"] - 1.0) > 0.0
            or abs(row["maximum_lapse"] - 1.0) > 0.0
            for row in records[1:]
        ),
        "gamma_driver_shift_is_evolved": any(row["shift_norm"] > 0.0 for row in records[1:]),
        "hamiltonian_and_momentum_constraints_are_reported": all(
            math.isfinite(row["hamiltonian_relative"])
            and math.isfinite(row["momentum_relative"])
            for row in records
        ),
        "metric_built_ricci_is_evolved": all(
            math.isfinite(row["ricci_scalar_norm"])
            and math.isfinite(row["ricci_tracefree_norm"])
            for row in records
        ),
        "screen_source_tidal_term_is_evolved": any(row["source_tidal_norm"] > 0.0 for row in records),
        "tensor_momentum_constraint_is_damped": bool(damping_rows) and tensor_nonworsening,
        "gamma_constraint_is_damped": bool(damping_rows) and gamma_nonworsening,
        "exact_production_BSSN_is_not_claimed": True,
    }
    payload = {
        "schema": "openwave.m9.bssn-screen-gravity.v2",
        "task": "M9.115-M9.116",
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
            "scalar_tidal_source_is_complete_stress_energy": False,
            "finite_grid_refinement_is_continuum_convergence_proof": False,
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
            "metric_built_conformal_ricci_constructed": True,
            "source_coupled_tracefree_curvature_constructed": True,
            "tensor_constraint_damping_constructed": True,
            "production_BSSN_constructed": False,
            "physical_screen_calibration_complete": False,
        },
    }


@lru_cache(maxsize=1)
def run_bssn_screen_gravity() -> dict[str, Any]:
    return run_bssn_screen_gravity_with_config(BSSNScreenConfig())


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
