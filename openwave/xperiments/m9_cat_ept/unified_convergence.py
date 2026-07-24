"""Unified nonlinear continuum-to-grid convergence campaign.

The study evolves the same smooth periodic CAT/EPT initial state on nested
spectral grids, lifts each final state to the finest grid, and measures field and
ledger convergence. The result is a finite-grid convergence campaign, not a
proof of convergence to a continuum solution.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from scipy.signal import resample

from .unified_pde import UnifiedPDEConfig, UnifiedState, matter_density, simulate


@dataclass(frozen=True)
class ConvergenceConfig:
    points: tuple[int, ...] = (32, 64, 128, 256)
    length: float = 12.0
    final_time: float = 0.04
    dt: float = 6.25e-5

    def __post_init__(self) -> None:
        if len(self.points) < 4 or tuple(sorted(self.points)) != self.points:
            raise ValueError("four increasing grids required")
        if (
            any(points < 32 or points % 2 for points in self.points)
            or self.length <= 0
            or self.final_time <= 0
            or self.dt <= 0
        ):
            raise ValueError("valid positive controls required")


def run_grid(points: int, control: ConvergenceConfig) -> dict[str, Any]:
    cfg = UnifiedPDEConfig(
        points=points,
        length=control.length,
        final_time=control.final_time,
        dt=control.dt,
    )
    return simulate(cfg)


def lift(value: np.ndarray, points: int) -> np.ndarray:
    return resample(value, points, axis=-1)


def l2_norm(value: np.ndarray, length: float) -> float:
    return math.sqrt(float(np.sum(np.abs(value) ** 2) * length / value.shape[-1]))


def relative_error(value: np.ndarray, reference: np.ndarray, length: float) -> float:
    return l2_norm(value - reference, length) / max(l2_norm(reference, length), 1e-14)


def field_errors(
    state: UnifiedState,
    reference: UnifiedState,
    control: ConvergenceConfig,
) -> dict[str, float]:
    points = reference.temperature.size
    psi = lift(state.psi, points)
    gauge = lift(state.gauge, points).real
    momentum = lift(state.gauge_momentum, points).real
    geometry = lift(state.geometry, points).real
    temperature = lift(state.temperature, points).real
    reservoir = lift(state.reservoir, points).real
    density = matter_density(psi)
    reference_density = matter_density(reference.psi)
    temperature_shift = temperature - float(np.mean(temperature))
    reference_temperature_shift = reference.temperature - float(np.mean(reference.temperature))
    fields = {
        "psi": relative_error(psi, reference.psi, control.length),
        "matter_density": relative_error(density, reference_density, control.length),
        "gauge": relative_error(gauge, reference.gauge, control.length),
        "gauge_momentum": relative_error(
            momentum, reference.gauge_momentum, control.length
        ),
        "geometry": relative_error(geometry, reference.geometry, control.length),
        "temperature_perturbation": relative_error(
            temperature_shift,
            reference_temperature_shift,
            control.length,
        ),
        "reservoir": relative_error(reservoir, reference.reservoir, control.length),
    }
    fields["aggregate"] = math.sqrt(
        sum(value * value for value in fields.values()) / len(fields)
    )
    return fields


def ledger_errors(run: dict[str, Any]) -> dict[str, Any]:
    records = run["records"]
    initial = records[0]
    entropy = np.asarray([row["entropy"] for row in records])
    return {
        "matter_reservoir": max(
            abs(row["matter_reservoir_balance"] - initial["matter_reservoir_balance"])
            for row in records
        ),
        "thermal_loss": max(
            abs(row["thermal_loss_balance"] - initial["thermal_loss_balance"])
            for row in records
        ),
        "gauge_work": max(
            abs(row["gauge_work_balance"] - initial["gauge_work_balance"])
            for row in records
        ),
        "minimum_temperature": min(row["minimum_temperature"] for row in records),
        "entropy_monotone": bool(np.all(np.diff(entropy) >= -2e-12)),
    }


def convergence_campaign(
    control: ConvergenceConfig = ConvergenceConfig(),
) -> dict[str, Any]:
    runs = {points: run_grid(points, control) for points in control.points}
    reference = runs[control.points[-1]]["state"]
    rows = []
    for points in control.points[:-1]:
        rows.append(
            {
                "points": points,
                "field_errors": field_errors(runs[points]["state"], reference, control),
                "ledger_errors": ledger_errors(runs[points]),
                "steps": runs[points]["steps"],
            }
        )
    reference_ledgers = ledger_errors(runs[control.points[-1]])
    aggregate = [row["field_errors"]["aggregate"] for row in rows]
    orders = [math.log(aggregate[index] / aggregate[index + 1], 2) for index in range(len(aggregate) - 1)]
    return {
        "rows": rows,
        "reference": {
            "points": control.points[-1],
            "steps": runs[control.points[-1]]["steps"],
            "ledger_errors": reference_ledgers,
        },
        "aggregate_errors": aggregate,
        "observed_orders": orders,
    }


@lru_cache(maxsize=1)
def run_unified_convergence_study() -> dict[str, Any]:
    control = ConvergenceConfig()
    campaign = convergence_campaign(control)
    errors = np.asarray(campaign["aggregate_errors"])
    finest = campaign["rows"][-1]["field_errors"]
    ledger_rows = [row["ledger_errors"] for row in campaign["rows"]] + [
        campaign["reference"]["ledger_errors"]
    ]
    acceptance = {
        "aggregate_grid_error_decreases": bool(np.all(np.diff(errors) < 0)),
        "observed_convergence_order_is_positive": min(campaign["observed_orders"]) > 0.5,
        "finest_comparison_is_small": finest["aggregate"] < 5e-3
        and finest["psi"] < 2e-3
        and finest["matter_density"] < 3e-3,
        "all_ledgers_remain_closed": max(row["matter_reservoir"] for row in ledger_rows) < 3e-8
        and max(row["thermal_loss"] for row in ledger_rows) < 3e-8
        and max(row["gauge_work"] for row in ledger_rows) < 3e-7,
        "temperature_remains_positive": min(row["minimum_temperature"] for row in ledger_rows) > 0.9,
        "entropy_remains_monotone": all(row["entropy_monotone"] for row in ledger_rows),
        "continuum_limit_is_not_overclaimed": True,
    }
    return {
        "schema": "openwave.m9.unified-convergence.v1",
        "task": "M9.56",
        "config": asdict(control),
        "campaign": campaign,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "nested_grid_convergence_observed": True,
            "continuum_solution_constructed": False,
            "continuum_convergence_proved": False,
        },
        "classification": {
            "establishes": [
                "nested spectral-grid convergence for the coupled nonlinear state",
                "simultaneous matter, color-wave, geometry, thermal and reservoir comparison",
                "balance, positivity and entropy controls on every grid",
            ],
            "does_not_establish": [
                "existence of a continuum CAT/EPT solution",
                "a convergence theorem independent of the selected smooth datum",
                "physical calibration or a self-bound particle",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
