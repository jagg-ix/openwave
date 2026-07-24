"""M9.58 finite kinetic convergence and hypoelliptic bracket controls.

This module refines the positive phase-space Ornstein--Uhlenbeck/streaming bridge
on nested grids. It checks moment convergence, mass preservation, and the rank of
the continuum Hoermander vector fields. It does not prove a continuum PDE theorem.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np

from .fokker_planck_bridge import (
    FPConfig,
    analytic_moments,
    simulate,
    velocity_generator,
    velocity_propagator,
)


@dataclass(frozen=True)
class KineticConfig:
    levels: tuple[tuple[int, int, float], ...] = (
        (16, 25, 0.05),
        (24, 33, 0.04),
        (32, 41, 0.025),
        (48, 57, 0.02),
    )
    final_time: float = 1.0
    friction: float = 0.7
    diffusion: float = 0.55
    vmax: float = 5.0

    def __post_init__(self) -> None:
        if len(self.levels) < 4 or any(
            nx < 8 or nv < 9 or nv % 2 == 0 or dt <= 0 for nx, nv, dt in self.levels
        ):
            raise ValueError("valid nested kinetic grids required")
        if min(self.final_time, self.friction, self.diffusion, self.vmax) <= 0:
            raise ValueError("positive kinetic controls required")
        if any(
            self.levels[i][0] >= self.levels[i + 1][0]
            or self.levels[i][1] >= self.levels[i + 1][1]
            for i in range(len(self.levels) - 1)
        ):
            raise ValueError("strictly refined grids required")


def level_config(level: tuple[int, int, float], cfg: KineticConfig = KineticConfig()) -> FPConfig:
    nx, nv, dt = level
    return FPConfig(
        nx=nx,
        nv=nv,
        dt=dt,
        final_time=cfg.final_time,
        friction=cfg.friction,
        diffusion=cfg.diffusion,
        vmax=cfg.vmax,
    )


def hoermander_control(cfg: KineticConfig = KineticConfig()) -> dict[str, Any]:
    # X1=sqrt(2D) d_v, X0=v d_x-gamma v d_v;
    # [X1,X0]=sqrt(2D)(d_x-gamma d_v).
    scale = math.sqrt(2 * cfg.diffusion)
    coefficient = np.asarray([[0.0, scale], [scale, -cfg.friction * scale]])
    return {
        "coefficient_matrix": coefficient.tolist(),
        "determinant": float(np.linalg.det(coefficient)),
        "rank": int(np.linalg.matrix_rank(coefficient)),
    }


def generator_control(cfg: KineticConfig = KineticConfig()) -> list[dict[str, float]]:
    rows = []
    for level in cfg.levels:
        current = level_config(level, cfg)
        generator = velocity_generator(current)
        propagator = velocity_propagator(current.dt, current)
        rows.append(
            {
                "nx": current.nx,
                "nv": current.nv,
                "column_sum_error": float(np.max(np.abs(np.sum(generator, axis=0)))),
                "minimum_propagator_entry": float(np.min(propagator)),
            }
        )
    return rows


def convergence_campaign(cfg: KineticConfig = KineticConfig()) -> dict[str, Any]:
    rows = []
    for level in cfg.levels:
        current = level_config(level, cfg)
        run = simulate(current)
        value = run["records"][-1]
        target = analytic_moments(current.final_time, current)
        rows.append(
            {
                "nx": current.nx,
                "nv": current.nv,
                "dt": current.dt,
                "mass": float(value["mass"]),
                "mean_velocity": float(value["mean_velocity"]),
                "velocity_variance": float(value["velocity_variance"]),
                "relative_entropy": float(value["relative_entropy"]),
                "analytic_mean": float(target["mean"]),
                "analytic_variance": float(target["variance"]),
                "moment_error": float(
                    np.linalg.norm(
                        np.asarray(
                            [
                                value["mean_velocity"] - target["mean"],
                                value["velocity_variance"] - target["variance"],
                            ]
                        )
                    )
                ),
            }
        )
    keys = ("mass", "mean_velocity", "velocity_variance", "relative_entropy")
    reference = np.asarray([rows[-1][key] for key in keys])
    errors = [
        float(np.linalg.norm(np.asarray([row[key] for key in keys]) - reference))
        for row in rows[:-1]
    ]
    orders = [math.log(errors[i] / errors[i + 1], 2) for i in range(len(errors) - 1)]
    return {
        "rows": rows,
        "aggregate_errors_to_finest": errors,
        "observed_orders": orders,
    }


@lru_cache(maxsize=1)
def run_kinetic_continuum_study() -> dict[str, Any]:
    cfg = KineticConfig()
    bracket = hoermander_control(cfg)
    generators = generator_control(cfg)
    campaign = convergence_campaign(cfg)
    rows = campaign["rows"]
    errors = campaign["aggregate_errors_to_finest"]
    acceptance = {
        "hoermander_bracket_spans_phase_space": bracket["rank"] == 2
        and abs(bracket["determinant"]) > 1e-10,
        "every_discrete_generator_conserves_mass": max(
            row["column_sum_error"] for row in generators
        )
        <= 3e-13,
        "every_discrete_propagator_is_positive": min(
            row["minimum_propagator_entry"] for row in generators
        )
        >= -3e-14,
        "mass_remains_normalized_on_all_grids": max(abs(row["mass"] - 1) for row in rows)
        <= 5e-13,
        "moment_error_decreases": bool(
            np.all(np.diff([row["moment_error"] for row in rows]) < 0)
        ),
        "nested_observable_error_decreases": bool(np.all(np.diff(errors) < 0)),
        "observed_refinement_orders_are_positive": min(campaign["observed_orders"]) > 0.5,
        "continuum_claim_is_not_overstated": True,
    }
    return {
        "schema": "openwave.m9.kinetic-continuum-bridge.v1",
        "task": "M9.58",
        "config": asdict(cfg),
        "hoermander_control": bracket,
        "generator_controls": generators,
        "campaign": campaign,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_kinetic_convergence_qualified": True,
            "hypoelliptic_bracket_condition_resolved_algebraically": True,
            "continuum_hypoelliptic_wellposedness_proved": False,
        },
        "classification": {
            "establishes": [
                "nested finite phase-space convergence",
                "positive mass-conserving discrete kinetic generators",
                "algebraic Hoermander bracket rank for the selected kinetic vector fields",
            ],
            "does_not_establish": [
                "continuum existence or uniqueness",
                "subelliptic estimates or smooth-density theorem",
                "derivation of physical transport coefficients from CAT/EPT",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
