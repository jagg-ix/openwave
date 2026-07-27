"""M9.111a-c: synchronized weak/nonlinear gravity from one screen anchor.

The two carriers share one screen-derived Newton coupling, one Pauli matter state,
one Maxwell state, and one matter evolution time step.  Their common matter,
source, and weak-potential observables must remain equal while the nonlinear
carrier separately evolves conformal curvature, trace extrinsic curvature, lapse,
and constraint projections.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .electrogravitic_weak_field_evolution import electrogravitic_fields, rhs as matter_rhs
from .holographic_gravity_coupling import ScreenDensityAnchor, build_gravity_configs
from .nonlinear_constraint_gravity import (
    conformal_scalar_curvature,
    constraint_fields,
    metric_step,
    project_constraints,
)
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed


def _relative_l2(left: np.ndarray, right: np.ndarray) -> float:
    numerator = float(np.linalg.norm(np.asarray(left) - np.asarray(right)))
    denominator = max(
        float(np.linalg.norm(np.asarray(left))),
        float(np.linalg.norm(np.asarray(right))),
        1.0e-300,
    )
    return numerator / denominator


def _relative_scalar(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), 1.0e-300)


def run_synchronized_history(
    anchor: ScreenDensityAnchor,
    *,
    steps: int = 8,
    points: int = 17,
    half_width: float = 8.0,
) -> dict[str, Any]:
    if steps < 2:
        raise ValueError("at least two synchronized steps required")

    configs = build_gravity_configs(anchor, points=points, half_width=half_width)
    weak_cfg = configs.weak
    nonlinear_cfg = configs.nonlinear
    nonlinear_matter_cfg = nonlinear_cfg.matter_config()

    if abs(weak_cfg.time_step - nonlinear_matter_cfg.time_step) > 1.0e-18:
        raise ValueError("weak and nonlinear matter time steps must match")

    scalar = odd_grid_seed(weak_cfg.action_config().reconciled_config())
    weak_spinor = np.zeros((2, points, points, points), dtype=np.complex128)
    weak_spinor[0] = scalar
    weak_spinor = normalize_spinor(weak_spinor, weak_cfg.spacing)
    nonlinear_spinor = np.asarray(weak_spinor.copy(), dtype=np.complex128)

    weak_vector = tuple(np.zeros((points,) * 3, dtype=np.float64) for _ in range(3))
    nonlinear_vector = tuple(np.zeros((points,) * 3, dtype=np.float64) for _ in range(3))

    initial_fields = electrogravitic_fields(weak_spinor, weak_vector, weak_cfg)
    potential = np.asarray(initial_fields["gravitational_potential"], dtype=np.float64)
    u = np.asarray(0.5 * potential / weak_cfg.light_speed**2, dtype=np.float64)
    trace_k = np.zeros_like(u)

    records: list[dict[str, float]] = []
    maximum_spinor_error = 0.0
    maximum_source_error = 0.0
    maximum_potential_error = 0.0
    maximum_g00_error = 0.0
    maximum_weak_poisson_residual = 0.0
    minimum_lapse = math.inf

    for step in range(steps + 1):
        weak_fields = electrogravitic_fields(weak_spinor, weak_vector, weak_cfg)
        nonlinear_fields = electrogravitic_fields(
            nonlinear_spinor, nonlinear_vector, nonlinear_matter_cfg
        )
        weak_vector = weak_fields["vector_potential"]
        nonlinear_vector = nonlinear_fields["vector_potential"]

        geometry = nonlinear_matter_cfg.geometry()
        _, current = reconciled_charge_current(
            nonlinear_spinor,
            nonlinear_vector,
            geometry,
            nonlinear_matter_cfg.action_config().reconciled_config(),
        )

        constraints_before = constraint_fields(
            u, trace_k, nonlinear_fields, current, nonlinear_cfg
        )
        projected_u, projected_k = project_constraints(
            u, trace_k, constraints_before, nonlinear_cfg
        )
        constraints_after = constraint_fields(
            projected_u, projected_k, nonlinear_fields, current, nonlinear_cfg
        )
        next_u, next_k, lapse = metric_step(
            projected_u,
            projected_k,
            np.asarray(nonlinear_fields["total_gravitational_source"], dtype=np.float64),
            nonlinear_cfg,
        )

        spinor_error = _relative_l2(weak_spinor, nonlinear_spinor)
        source_error = _relative_l2(
            np.asarray(weak_fields["total_gravitational_source"]),
            np.asarray(nonlinear_fields["total_gravitational_source"]),
        )
        potential_error = _relative_l2(
            np.asarray(weak_fields["gravitational_potential"]),
            np.asarray(nonlinear_fields["gravitational_potential"]),
        )
        g00_error = _relative_l2(
            np.asarray(weak_fields["metric_g00"]),
            np.asarray(nonlinear_fields["metric_g00"]),
        )
        curvature = conformal_scalar_curvature(projected_u, nonlinear_cfg)

        maximum_spinor_error = max(maximum_spinor_error, spinor_error)
        maximum_source_error = max(maximum_source_error, source_error)
        maximum_potential_error = max(maximum_potential_error, potential_error)
        maximum_g00_error = max(maximum_g00_error, g00_error)
        maximum_weak_poisson_residual = max(
            maximum_weak_poisson_residual,
            float(weak_fields["einstein00_relative_residual"]),
        )
        minimum_lapse = min(minimum_lapse, float(np.min(lapse)))

        records.append(
            {
                "step": float(step),
                "time": float(step * weak_cfg.time_step),
                "spinor_relative_error": spinor_error,
                "source_relative_error": source_error,
                "potential_relative_error": potential_error,
                "weak_g00_relative_error": g00_error,
                "weak_einstein00_relative_residual": float(
                    weak_fields["einstein00_relative_residual"]
                ),
                "hamiltonian_before": float(
                    constraints_before["hamiltonian_relative"]
                ),
                "hamiltonian_after": float(
                    constraints_after["hamiltonian_relative"]
                ),
                "momentum_before": float(constraints_before["momentum_relative"]),
                "momentum_after": float(constraints_after["momentum_relative"]),
                "maximum_abs_scalar_curvature": float(np.max(np.abs(curvature))),
                "maximum_abs_u": float(np.max(np.abs(projected_u))),
                "maximum_abs_K": float(np.max(np.abs(projected_k))),
                "minimum_lapse": float(np.min(lapse)),
            }
        )

        if step == steps:
            break

        weak_derivative = matter_rhs(weak_spinor, weak_fields, weak_cfg)
        nonlinear_derivative = matter_rhs(
            nonlinear_spinor, nonlinear_fields, nonlinear_matter_cfg
        )
        weak_spinor = normalize_spinor(
            weak_spinor + weak_cfg.time_step * weak_derivative, weak_cfg.spacing
        )
        nonlinear_spinor = normalize_spinor(
            nonlinear_spinor
            + nonlinear_matter_cfg.time_step * nonlinear_derivative,
            nonlinear_matter_cfg.spacing,
        )
        u, trace_k = next_u, next_k

    projection_finite = all(
        math.isfinite(row["hamiltonian_before"])
        and math.isfinite(row["hamiltonian_after"])
        and math.isfinite(row["momentum_before"])
        and math.isfinite(row["momentum_after"])
        for row in records
    )
    nonlinear_geometry_evolved = any(
        row["maximum_abs_K"] > 0.0 or row["maximum_abs_scalar_curvature"] > 0.0
        for row in records[1:]
    )

    return {
        "screen_newton_coupling": anchor.newton_coupling,
        "weak_newton_coupling": weak_cfg.newton_coupling,
        "nonlinear_newton_coupling": nonlinear_matter_cfg.newton_coupling,
        "time_step": weak_cfg.time_step,
        "steps": steps,
        "records": records,
        "maximum_spinor_relative_error": maximum_spinor_error,
        "maximum_source_relative_error": maximum_source_error,
        "maximum_potential_relative_error": maximum_potential_error,
        "maximum_weak_g00_relative_error": maximum_g00_error,
        "maximum_weak_einstein00_relative_residual": maximum_weak_poisson_residual,
        "minimum_lapse": minimum_lapse,
        "projection_diagnostics_are_finite": projection_finite,
        "nonlinear_geometry_evolved": nonlinear_geometry_evolved,
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_synchronized_screen_gravity_evolution() -> dict[str, Any]:
    anchor = ScreenDensityAnchor(
        area=2.0,
        bits=8.0,
        evidence_class="external",
        source="synthetic synchronized-history fixture; not physical evidence",
    )
    history = run_synchronized_history(anchor)
    acceptance = {
        "one_screen_G_drives_both_histories": max(
            _relative_scalar(
                history["screen_newton_coupling"], history["weak_newton_coupling"]
            ),
            _relative_scalar(
                history["screen_newton_coupling"],
                history["nonlinear_newton_coupling"],
            ),
        )
        <= 5.0e-15,
        "shared_matter_history_closes": history["maximum_spinor_relative_error"]
        <= 5.0e-13,
        "shared_source_history_closes": history["maximum_source_relative_error"]
        <= 5.0e-13,
        "shared_weak_potential_history_closes": history[
            "maximum_potential_relative_error"
        ]
        <= 5.0e-13,
        "shared_weak_metric_history_closes": history[
            "maximum_weak_g00_relative_error"
        ]
        <= 5.0e-13,
        "weak_poisson_sector_remains_closed": history[
            "maximum_weak_einstein00_relative_residual"
        ]
        <= 1.0e-10,
        "nonlinear_constraint_diagnostics_remain_finite": history[
            "projection_diagnostics_are_finite"
        ],
        "nonlinear_geometry_adds_dynamics": history["nonlinear_geometry_evolved"],
        "lapse_remains_positive": history["minimum_lapse"] > 0.0,
    }
    payload = {
        "schema": "openwave.m9.synchronized-screen-gravity-evolution.v1",
        "task": "M9.111a-c",
        "anchor": {
            "area": anchor.area,
            "bits": anchor.bits,
            "area_per_bit": anchor.area_per_bit,
            "newton_coupling": anchor.newton_coupling,
            "epistemic_status": "synthetic-fixture-not-physical-evidence",
        },
        "history": history,
        "claim_boundary": {
            "shared_matter_history_is_full_metric_equivalence": False,
            "finite_constraints_are_constraint_closure": False,
            "nonlinear_curvature_is_experimental_validation": False,
            "synthetic_anchor_is_physical_calibration": False,
            "reduced_conformal_ADM_is_general_GR": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "synchronized_shared_matter_and_weak_fields_complete": True,
            "nonlinear_curvature_and_constraint_history_reported": True,
            "general_Einstein_time_evolution_complete": False,
            "physical_screen_density_calibrated": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
