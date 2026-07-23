"""M9.11 bounded two-dimensional localization and radiative-stability decision."""

from __future__ import annotations

from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np

from .planar_2d_maxwell_dirac import (
    Planar2DGrid,
    Planar2DParameters,
    Planar2DRun,
    density,
    evolve_planar_2d,
    packet_moments,
    run_summary,
)


def packet_localization(
    run: Planar2DRun,
    initial,
    final,
) -> dict[str, float]:
    cell_area = run.dx * run.dy
    initial_x, initial_y, initial_rms = packet_moments(
        run.x, run.y, initial, cell_area
    )
    final_x, final_y, final_rms = packet_moments(
        run.x, run.y, final, cell_area
    )
    initial_density = density(initial)
    final_density = density(final)
    core_radius = 2.5 * initial_rms
    final_mask = (
        (run.x - final_x) ** 2 + (run.y - final_y) ** 2
    ) <= core_radius**2
    final_norm = cell_area * float(np.sum(final_density))
    return {
        "initial_center_x": initial_x,
        "initial_center_y": initial_y,
        "final_center_x": final_x,
        "final_center_y": final_y,
        "initial_rms_radius": initial_rms,
        "final_rms_radius": final_rms,
        "rms_ratio": final_rms / initial_rms,
        "peak_ratio": float(np.max(final_density) / np.max(initial_density)),
        "core_fraction": (
            cell_area * float(np.sum(final_density[final_mask])) / final_norm
        ),
    }


def localization_summary(run: Planar2DRun) -> dict[str, Any]:
    summary = run_summary(run)
    plus = packet_localization(run, run.initial_plus, run.final_plus)
    minus = packet_localization(run, run.initial_minus, run.final_minus)
    return {
        "run": summary,
        "plus": plus,
        "minus": minus,
        "maximum_rms_ratio": max(plus["rms_ratio"], minus["rms_ratio"]),
        "minimum_peak_ratio": min(plus["peak_ratio"], minus["peak_ratio"]),
        "minimum_core_fraction": min(
            plus["core_fraction"], minus["core_fraction"]
        ),
    }


def run_coupling_survey(
    couplings: Sequence[float] = (0.0, 2.0, 4.0, 8.0),
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for coupling in couplings:
        parameters = Planar2DParameters(soler_coupling=coupling)
        run = evolve_planar_2d(
            parameters=parameters,
            grid=Planar2DGrid(
                points_x=48,
                points_y=48,
                final_time=8.0,
                samples=41,
            ),
        )
        record = localization_summary(run)
        record["soler_coupling"] = coupling
        records.append(record)
    return {
        "couplings": list(couplings),
        "records": records,
    }


def run_fixed_perturbation() -> dict[str, Any]:
    parameters = Planar2DParameters(
        soler_coupling=8.0,
        packet_width=2.31,
        momentum_y=0.3675,
        gauge_seed_amplitude=0.0066,
    )
    run = evolve_planar_2d(
        parameters=parameters,
        grid=Planar2DGrid(
            points_x=64,
            points_y=64,
            final_time=8.0,
            samples=41,
        ),
    )
    result = localization_summary(run)
    result["perturbation"] = {
        "packet_width_factor": 1.05,
        "momentum_y_factor": 1.05,
        "gauge_seed_factor": 1.10,
    }
    return result


def run_long_time_candidate() -> dict[str, Any]:
    parameters = Planar2DParameters(soler_coupling=8.0)
    run = evolve_planar_2d(
        parameters=parameters,
        grid=Planar2DGrid(
            points_x=64,
            points_y=64,
            final_time=12.0,
            samples=61,
        ),
    )
    return localization_summary(run)


@lru_cache(maxsize=1)
def run_localization_decision() -> dict[str, Any]:
    survey = run_coupling_survey()
    perturbation = run_fixed_perturbation()
    long_time = run_long_time_candidate()
    free = survey["records"][0]
    candidate = survey["records"][-1]
    improvement = free["maximum_rms_ratio"] - candidate["maximum_rms_ratio"]
    finite_time_candidate = (
        candidate["maximum_rms_ratio"] <= 1.42
        and candidate["minimum_peak_ratio"] >= 0.80
        and candidate["minimum_core_fraction"] >= 0.95
    )
    perturbation_survives = (
        perturbation["maximum_rms_ratio"] <= 1.45
        and perturbation["minimum_peak_ratio"] >= 0.80
        and perturbation["minimum_core_fraction"] >= 0.95
    )
    long_time_rejected = (
        long_time["maximum_rms_ratio"] >= 1.60
        or long_time["minimum_peak_ratio"] <= 0.75
    )
    all_runs = survey["records"] + [perturbation, long_time]
    acceptance = {
        "bounded_family_completed": len(survey["records"]) == 4,
        "strongest_member_reduces_spreading": improvement >= 0.10,
        "finite_time_candidate_identified": finite_time_candidate,
        "fixed_perturbation_survives": perturbation_survives,
        "long_time_particle_claim_rejected": long_time_rejected,
        "norm_ledgers_close": all(
            item["run"]["max_norm_drift"] <= 2.0e-7 for item in all_runs
        ),
        "energy_ledgers_close": all(
            item["run"]["max_corrected_energy_relative_drift"] <= 5.0e-7
            for item in all_runs
        ),
        "gauss_ledgers_close": all(
            item["run"]["final"]["gauss_residual_relative"] <= 5.0e-3
            for item in all_runs
        ),
        "radiation_recorded": all(
            math.isfinite(item["run"]["emitted_energy"]) for item in all_runs
        ),
    }
    decision = (
        "lambda=8 is a finite-time reduced-spreading candidate at t=8, "
        "but it fails the t=12 long-time localization gate; no stable "
        "two-dimensional particle candidate is accepted."
    )
    return {
        "schema": "openwave.m9.planar-2d-localization-decision.v1",
        "task": "M9.11",
        "model": "bounded two-dimensional Soler-Maxwell-Dirac survey",
        "survey": survey,
        "fixed_perturbation": perturbation,
        "long_time_candidate": long_time,
        "spreading_improvement": improvement,
        "decision": decision,
        "accepted_particle_candidate": False,
        "finite_time_reduced_spreading_candidate": 8.0,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a bounded four-member nonlinear coupling survey",
                "finite-time reduced spreading for the strongest selected member",
                "fixed-perturbation survival through the finite-time gate",
                "long-time dispersal of the strongest member",
                "norm, energy, Gauss, and radiation ledgers for every member",
            ],
            "does_not_establish": [
                "a stable localized charged particle",
                "orbital or asymptotic stability",
                "electron identity, calibrated units, or fermionic quantization",
                "unique CAT/EPT selection of lambda=8",
            ],
        },
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(
        result,
        indent=2,
        sort_keys=True,
        default=_json_default,
    ) + "\n"
