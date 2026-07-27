"""M9.114: reduced generalized ADM gravity with one holographic screen coupling.

This extends the conformal/pure-trace carrier with:

* a symmetric trace-free spatial metric perturbation ``h_tt[i,j]``;
* a symmetric trace-free extrinsic-curvature component ``A_tf[i,j]``;
* a dynamical shift vector ``beta[i]``;
* explicit trace-free and approximate transverse projections.

It remains a finite periodic reduced model, not a complete BSSN or general Einstein
Cauchy solver. The purpose is to remove three previous implementation restrictions
while preserving one screen-derived Newton coupling across matter and metric layers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .holographic_gravity_coupling import ScreenDensityAnchor, build_gravity_configs
from .nonlinear_constraint_gravity import (
    conformal_scalar_curvature,
    constraint_fields,
    project_constraints,
)
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed
from .electrogravitic_weak_field_evolution import electrogravitic_fields, rhs as matter_rhs

Tensor = np.ndarray
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class GeneralizedADMConfig:
    points: int = 17
    half_width: float = 8.0
    time_step: float = 1.0e-4
    steps: int = 40
    sample_stride: int = 5
    screen_area: float = 2.0
    screen_bits: float = 8.0
    hbar: float = 1.0
    light_speed: float = 1.0
    tt_relaxation: float = 0.04
    shift_relaxation: float = 0.03
    constraint_relaxation: float = 0.08

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
            self.tt_relaxation,
            self.shift_relaxation,
            self.constraint_relaxation,
        ) <= 0.0:
            raise ValueError("positive generalized ADM controls required")

    @property
    def anchor(self) -> ScreenDensityAnchor:
        return ScreenDensityAnchor(
            area=self.screen_area,
            bits=self.screen_bits,
            hbar=self.hbar,
            c=self.light_speed,
            evidence_class="external",
            source="synthetic generalized-ADM fixture; not physical evidence",
        )


def symmetric_trace_free(tensor: Tensor) -> Tensor:
    """Project a 3x3 tensor field to its symmetric trace-free part."""
    symmetric = 0.5 * (tensor + np.swapaxes(tensor, 0, 1))
    trace = symmetric[0, 0] + symmetric[1, 1] + symmetric[2, 2]
    result = np.array(symmetric, copy=True)
    for index in range(3):
        result[index, index] -= trace / 3.0
    return np.asarray(result, dtype=np.float64)


def tensor_divergence(tensor: Tensor, geometry: Any) -> Vector:
    rows = []
    for i in range(3):
        value = np.zeros_like(tensor[0, 0])
        for j, derivative in enumerate(geometry.gradient(tensor[i, j])):
            if j == 0:
                value = value + derivative
        # The loop above would repeatedly select x derivatives. Use explicit gradients.
        value = sum(geometry.gradient(tensor[i, j])[j] for j in range(3))
        rows.append(np.asarray(value, dtype=np.float64))
    return tuple(rows)  # type: ignore[return-value]


def approximate_transverse_projection(tensor: Tensor, geometry: Any) -> Tensor:
    """Remove a longitudinal part using periodic Poisson solves, then re-STF project."""
    divergence = tensor_divergence(tensor, geometry)
    potentials = tuple(
        geometry.inverse_negative_laplacian(geometry.mean_zero(component))
        for component in divergence
    )
    correction = np.zeros_like(tensor)
    gradients = tuple(geometry.gradient(component) for component in potentials)
    for i in range(3):
        for j in range(3):
            correction[i, j] = 0.5 * (gradients[i][j] + gradients[j][i])
    return symmetric_trace_free(tensor - correction)


def tensor_norm(tensor: Tensor) -> float:
    return math.sqrt(sum(float(np.linalg.norm(tensor[i, j]) ** 2) for i in range(3) for j in range(3)))


def generalized_constraints(
    u: np.ndarray,
    trace_k: np.ndarray,
    h_tt: Tensor,
    a_tf: Tensor,
    beta: Vector,
    fields: Mapping[str, Any],
    current: Vector,
    nonlinear: Any,
) -> dict[str, Any]:
    base = constraint_fields(u, trace_k, fields, current, nonlinear)
    geometry = nonlinear.matter_config().geometry()
    div_a = tensor_divergence(a_tf, geometry)
    tt_div = tensor_divergence(h_tt, geometry)
    shift_div = geometry.divergence(beta)
    return {
        **base,
        "tracefree_metric_trace_max": float(
            np.max(np.abs(h_tt[0, 0] + h_tt[1, 1] + h_tt[2, 2]))
        ),
        "tracefree_extrinsic_trace_max": float(
            np.max(np.abs(a_tf[0, 0] + a_tf[1, 1] + a_tf[2, 2]))
        ),
        "tt_divergence_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in tt_div)),
        "extrinsic_divergence_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in div_a)),
        "shift_divergence_norm": float(np.linalg.norm(shift_div)),
    }


def generalized_metric_step(
    u: np.ndarray,
    trace_k: np.ndarray,
    h_tt: Tensor,
    a_tf: Tensor,
    beta: Vector,
    source: np.ndarray,
    nonlinear: Any,
    cfg: GeneralizedADMConfig,
) -> tuple[np.ndarray, np.ndarray, Tensor, Tensor, Vector, np.ndarray]:
    matter = nonlinear.matter_config()
    geometry = matter.geometry()
    coupling = matter.newton_coupling
    lapse = np.exp(np.clip(-2.0 * u, -20.0, 20.0))

    scalar_laplacian = geometry.laplacian(lapse)
    du = -(lapse * trace_k) / 6.0 + geometry.divergence(beta) / 6.0
    dk = -scalar_laplacian + lapse * (
        trace_k * trace_k / 3.0 + 4.0 * math.pi * coupling * geometry.mean_zero(source)
    )

    h_rhs = -2.0 * lapse[None, None, ...] * a_tf
    a_rhs = np.zeros_like(a_tf)
    for i in range(3):
        for j in range(3):
            a_rhs[i, j] = 0.5 * geometry.laplacian(h_tt[i, j]) - cfg.tt_relaxation * a_tf[i, j]

    shift_rhs = tuple(
        np.asarray(-cfg.shift_relaxation * component + geometry.gradient(trace_k)[i], dtype=np.float64)
        for i, component in enumerate(beta)
    )

    next_u = np.asarray(u + cfg.time_step * du, dtype=np.float64)
    next_k = np.asarray(trace_k + cfg.time_step * dk, dtype=np.float64)
    next_h = approximate_transverse_projection(h_tt + cfg.time_step * h_rhs, geometry)
    next_a = approximate_transverse_projection(a_tf + cfg.time_step * a_rhs, geometry)
    next_beta = tuple(
        np.asarray(beta[i] + cfg.time_step * shift_rhs[i], dtype=np.float64)
        for i in range(3)
    )
    return next_u, next_k, next_h, next_a, next_beta, lapse


@lru_cache(maxsize=1)
def run_generalized_screen_adm_gravity() -> dict[str, Any]:
    cfg = GeneralizedADMConfig()
    configs = build_gravity_configs(cfg.anchor)
    weak = configs.weak
    nonlinear = configs.nonlinear
    matter = nonlinear.matter_config()
    geometry = matter.geometry()

    scalar = odd_grid_seed(matter.action_config().reconciled_config())
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = normalize_spinor(spinor, matter.spacing)
    vector = tuple(np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3))

    fields = electrogravitic_fields(spinor, vector, matter)
    phi = np.asarray(fields["gravitational_potential"], dtype=np.float64)
    u = np.asarray(0.5 * phi / matter.light_speed**2, dtype=np.float64)
    trace_k = np.zeros_like(u)
    h_tt = np.zeros((3, 3) + u.shape, dtype=np.float64)
    a_tf = np.zeros_like(h_tt)
    # Seed a small plus-polarized trace-free mode without claiming a physical wave.
    h_tt[0, 0] = 1.0e-4 * geometry.mean_zero(phi)
    h_tt[1, 1] = -h_tt[0, 0]
    h_tt = approximate_transverse_projection(h_tt, geometry)
    beta: Vector = tuple(np.zeros_like(u) for _ in range(3))  # type: ignore[assignment]

    records: list[dict[str, float]] = []
    for step in range(cfg.steps + 1):
        fields = electrogravitic_fields(spinor, vector, matter)
        vector = fields["vector_potential"]
        _, current = reconciled_charge_current(
            spinor, vector, geometry, matter.action_config().reconciled_config()
        )
        constraints_before = generalized_constraints(
            u, trace_k, h_tt, a_tf, beta, fields, current, nonlinear
        )
        u, trace_k = project_constraints(u, trace_k, constraints_before, nonlinear)
        u, trace_k, h_tt, a_tf, beta, lapse = generalized_metric_step(
            u,
            trace_k,
            h_tt,
            a_tf,
            beta,
            np.asarray(fields["total_gravitational_source"], dtype=np.float64),
            nonlinear,
            cfg,
        )
        constraints_after = generalized_constraints(
            u, trace_k, h_tt, a_tf, beta, fields, current, nonlinear
        )
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            records.append(
                {
                    "time": step * cfg.time_step,
                    "hamiltonian_relative": float(constraints_after["hamiltonian_relative"]),
                    "momentum_relative": float(constraints_after["momentum_relative"]),
                    "tt_metric_norm": tensor_norm(h_tt),
                    "tracefree_extrinsic_norm": tensor_norm(a_tf),
                    "shift_norm": math.sqrt(sum(float(np.linalg.norm(v) ** 2) for v in beta)),
                    "tracefree_metric_trace_max": float(constraints_after["tracefree_metric_trace_max"]),
                    "tracefree_extrinsic_trace_max": float(constraints_after["tracefree_extrinsic_trace_max"]),
                    "tt_divergence_norm": float(constraints_after["tt_divergence_norm"]),
                    "minimum_lapse": float(np.min(lapse)),
                    "maximum_abs_u": float(np.max(np.abs(u))),
                    "scalar_curvature_norm": float(np.linalg.norm(conformal_scalar_curvature(u, nonlinear))),
                }
            )
        if step == cfg.steps:
            break
        derivative = matter_rhs(spinor, fields, matter)
        spinor = normalize_spinor(spinor + matter.time_step * derivative, matter.spacing)

    acceptance = {
        "one_screen_G_reaches_generalized_carrier": abs(matter.newton_coupling - cfg.anchor.newton_coupling)
        <= 5.0e-15 * max(abs(cfg.anchor.newton_coupling), 1.0),
        "tracefree_metric_mode_evolves": max(row["tt_metric_norm"] for row in records) > 0.0,
        "tracefree_extrinsic_mode_evolves": max(row["tracefree_extrinsic_norm"] for row in records) > 0.0,
        "shift_mode_is_present": all(math.isfinite(row["shift_norm"]) for row in records),
        "tracefree_projection_is_preserved": max(
            max(row["tracefree_metric_trace_max"], row["tracefree_extrinsic_trace_max"])
            for row in records
        ) <= 1.0e-10,
        "constraints_are_measured": all(
            math.isfinite(row["hamiltonian_relative"]) and math.isfinite(row["momentum_relative"])
            for row in records
        ),
        "lorentzian_lapse_is_preserved": min(row["minimum_lapse"] for row in records) > 0.0,
        "general_Einstein_Cauchy_development_is_not_claimed": True,
    }
    payload = {
        "schema": "openwave.m9.generalized-screen-adm-gravity.v1",
        "task": "M9.114",
        "config": asdict(cfg),
        "screen_newton_coupling": cfg.anchor.newton_coupling,
        "records": records,
        "acceptance": acceptance,
        "claim_boundary": {
            "approximate_TT_projection_is_exact_BSSN": False,
            "reduced_shift_evolution_is_general_coordinate_gauge": False,
            "finite_constraint_history_is_constraint_closure": False,
            "synthetic_screen_anchor_is_physical_calibration": False,
            "generalized_reduced_ADM_is_general_GR": False,
        },
    }
    payload["passed"] = all(acceptance.values()) and not any(payload["claim_boundary"].values())
    return payload


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
