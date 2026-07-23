"""Deterministic studies for M9.17 reservoir accounting."""

from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np

from .reservoir_core import ReservoirGrid, ReservoirParameters, ReservoirRun, density
from .reservoir_evolution import evolve_reservoir

def run_summary(run: ReservoirRun) -> dict[str, Any]:
    initial = run.records[0]
    matter = np.asarray([item["matter_probability"] for item in run.records])
    reservoir = np.asarray([item["reservoir_probability"] for item in run.records])
    tau = np.asarray([item["tau_ent"] for item in run.records])
    return {
        "parameters": asdict(run.parameters),
        "grid": asdict(run.grid),
        "dt": run.dt,
        "steps": run.steps,
        "initial": initial,
        "final": run.records[-1],
        "max_extended_probability_error": float(
            max(abs(item["extended_probability"] - initial["extended_probability"]) for item in run.records)
        ),
        "max_extended_charge_error": float(
            max(abs(item["extended_charge"] - initial["extended_charge"]) for item in run.records)
        ),
        "maximum_continuity_residual": float(
            max(
                max(item["plus_continuity_residual"], item["minus_continuity_residual"])
                for item in run.records
            )
        ),
        "minimum_reservoir_density": float(min(item["minimum_reservoir_density"] for item in run.records)),
        "matter_probability_monotone": bool(np.all(np.diff(matter) <= 2.0e-12)),
        "reservoir_probability_monotone": bool(np.all(np.diff(reservoir) >= -2.0e-12)),
        "tau_ent_monotone": bool(np.all(np.diff(tau) >= -2.0e-12)),
    }


def density_difference(coarse: ReservoirRun, fine: ReservoirRun) -> float:
    fine_plus = density(fine.final_plus) [::2]
    fine_minus = density(fine.final_minus)[::2]
    coarse_total = density(coarse.final_plus) + density(coarse.final_minus)
    fine_total = fine_plus + fine_minus
    return math.sqrt(coarse.dx * float(np.sum((coarse_total - fine_total) ** 2)))


def refinement_study(points: Sequence[int] = (64, 128, 256)) -> dict[str, Any]:
    runs = [
        evolve_reservoir(
            grid=ReservoirGrid(points=count, final_time=2.0, samples=31)
        )
        for count in points
    ]
    differences = [density_difference(coarse, fine) for coarse, fine in zip(runs[:-1], runs[1:], strict=True)]
    order = math.log(differences[0] / differences[1], 2.0)
    return {
        "points": list(points),
        "successive_density_l2_differences": differences,
        "observed_order": order,
        "summaries": [run_summary(run) for run in runs],
    }


def zero_loss_study() -> dict[str, Any]:
    parameters = ReservoirParameters(coupling=0.0)
    run = evolve_reservoir(parameters, ReservoirGrid(points=128, final_time=4.0, samples=41))
    summary = run_summary(run)
    return {
        "matter_probability_drift": abs(summary["final"]["matter_probability"] - 1.0),
        "reservoir_probability": summary["final"]["reservoir_probability"],
        "tau_ent": summary["final"]["tau_ent"],
        "extended_probability_error": summary["max_extended_probability_error"],
    }


@lru_cache(maxsize=1)
def run_reservoir_backreaction_study() -> dict[str, Any]:
    refinement = refinement_study()
    long_run = evolve_reservoir()
    summary = run_summary(long_run)
    zero_loss = zero_loss_study()
    acceptance = {
        "spatial_solution_converges": refinement["observed_order"] >= 1.5,
        "extended_probability_closes": summary["max_extended_probability_error"] <= 5.0e-8,
        "extended_charge_closes": summary["max_extended_charge_error"] <= 5.0e-10,
        "local_continuity_closes": summary["maximum_continuity_residual"] <= 5.0e-10,
        "reservoir_nonnegative": summary["minimum_reservoir_density"] >= -2.0e-12,
        "matter_probability_contracts": summary["matter_probability_monotone"],
        "reservoir_accumulates": summary["reservoir_probability_monotone"],
        "operational_tau_monotone": summary["tau_ent_monotone"],
        "zero_loss_reduces_to_closed_transport": (
            zero_loss["matter_probability_drift"] <= 5.0e-8
            and abs(zero_loss["reservoir_probability"]) <= 2.0e-12
            and abs(zero_loss["tau_ent"]) <= 5.0e-8
        ),
    }
    return {
        "schema": "openwave.m9.reservoir-backreaction-result.v1",
        "task": "M9.17",
        "model": "selected 1+1D Dirac sink with local probability/charge reservoir",
        "refinement": refinement,
        "long_run": summary,
        "zero_loss": zero_loss,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "spatial Dirac transport with a positive local sink",
                "extended matter-plus-reservoir probability and charge closure",
                "local continuity and a monotone operational matter-loss clock",
                "the zero-loss closed-transport limit",
            ],
            "does_not_establish": [
                "a microscopic reservoir Hamiltonian or thermodynamic bath",
                "that the operational matter-loss clock is physical time",
                "Maxwell back-reaction from the reservoir",
                "particle localization or physical calibration",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
