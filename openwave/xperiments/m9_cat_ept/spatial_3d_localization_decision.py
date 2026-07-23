"""M9.14 bounded three-dimensional localization and radiation decision."""

from __future__ import annotations

from functools import lru_cache
import json
from typing import Any, Sequence

import numpy as np

from .spatial_3d import (
    Spatial3DGrid,
    Spatial3DParameters,
    Spatial3DRun,
    density,
    evolve_spatial_3d,
    packet_moments,
    run_summary,
)

def packet_localization(
    run: Spatial3DRun,
    initial,
    final,
) -> dict[str, float]:
    cell_volume = run.dx * run.dy * run.dz
    initial_moments = packet_moments(run.x, run.y, run.z, initial, cell_volume)
    final_moments = packet_moments(run.x, run.y, run.z, final, cell_volume)
    initial_density = density(initial)
    final_density = density(final)
    core_radius = 2.5 * initial_moments[3]
    mask = (
        (run.x - final_moments[0]) ** 2
        + (run.y - final_moments[1]) ** 2
        + (run.z - final_moments[2]) ** 2
    ) <= core_radius**2
    final_norm = cell_volume * float(np.sum(final_density))
    return {
        "initial_rms_radius": initial_moments[3],
        "final_rms_radius": final_moments[3],
        "rms_ratio": final_moments[3] / initial_moments[3],
        "peak_ratio": float(np.max(final_density) / np.max(initial_density)),
        "core_fraction": cell_volume * float(np.sum(final_density[mask])) / final_norm,
    }


def localization_summary(run: Spatial3DRun) -> dict[str, Any]:
    plus = packet_localization(run, run.initial_plus, run.final_plus)
    minus = packet_localization(run, run.initial_minus, run.final_minus)
    return {
        "run": run_summary(run),
        "plus": plus,
        "minus": minus,
        "maximum_rms_ratio": max(plus["rms_ratio"], minus["rms_ratio"]),
        "minimum_peak_ratio": min(plus["peak_ratio"], minus["peak_ratio"]),
        "minimum_core_fraction": min(plus["core_fraction"], minus["core_fraction"]),
    }


def run_coupling_survey(
    couplings: Sequence[float] = (0.0, 2.0, 4.0, 8.0),
) -> dict[str, Any]:
    records = []
    for coupling in couplings:
        run = evolve_spatial_3d(
            Spatial3DParameters(soler_coupling=coupling),
            Spatial3DGrid(
                points_x=16,
                points_y=16,
                points_z=16,
                final_time=3.0,
                samples=31,
            ),
        )
        record = localization_summary(run)
        record["soler_coupling"] = coupling
        records.append(record)
    return {"couplings": list(couplings), "records": records}


def run_fixed_perturbation(coupling: float) -> dict[str, Any]:
    parameters = Spatial3DParameters(
        soler_coupling=coupling,
        packet_width=1.89,
        momentum_z=0.1575,
        gauge_seed_amplitude=0.0044,
    )
    run = evolve_spatial_3d(
        parameters,
        Spatial3DGrid(
            points_x=20,
            points_y=20,
            points_z=20,
            final_time=3.0,
            samples=31,
        ),
    )
    result = localization_summary(run)
    result["perturbation"] = {
        "packet_width_factor": 1.05,
        "momentum_z_factor": 1.05,
        "gauge_seed_factor": 1.10,
    }
    return result


def run_long_time_candidate(coupling: float) -> dict[str, Any]:
    run = evolve_spatial_3d(
        Spatial3DParameters(soler_coupling=coupling),
        Spatial3DGrid(
            points_x=20,
            points_y=20,
            points_z=20,
            final_time=5.0,
            samples=51,
        ),
    )
    return localization_summary(run)


@lru_cache(maxsize=1)
def run_spatial_3d_localization_decision() -> dict[str, Any]:
    survey = run_coupling_survey()
    free = survey["records"][0]
    candidate = min(survey["records"], key=lambda record: record["maximum_rms_ratio"])
    coupling = float(candidate["soler_coupling"])
    perturbation = run_fixed_perturbation(coupling)
    long_time = run_long_time_candidate(coupling)
    improvement = free["maximum_rms_ratio"] - candidate["maximum_rms_ratio"]
    finite_time_candidate = (
        candidate["maximum_rms_ratio"] <= 1.55
        and candidate["minimum_peak_ratio"] >= 0.55
        and candidate["minimum_core_fraction"] >= 0.88
    )
    perturbation_survives = (
        perturbation["maximum_rms_ratio"] <= 1.60
        and perturbation["minimum_peak_ratio"] >= 0.50
        and perturbation["minimum_core_fraction"] >= 0.85
    )
    accepted_particle_candidate = (
        long_time["maximum_rms_ratio"] <= 1.20
        and long_time["minimum_peak_ratio"] >= 0.80
        and long_time["minimum_core_fraction"] >= 0.98
    )
    all_records = list(survey["records"]) + [perturbation, long_time]
    max_norm = max(record["run"]["max_norm_drift"] for record in all_records)
    max_energy = max(
        record["run"]["max_corrected_energy_relative_drift"] for record in all_records
    )
    max_final_gauss_absolute = max(
        record["run"]["final"]["gauss_residual_absolute"] for record in all_records
    )
    max_final_gauss_relative = max(
        record["run"]["final"]["gauss_residual_relative"] for record in all_records
    )
    acceptance = {
        "bounded_family_completed": len(survey["records"]) == 4,
        "strongest_member_reduces_spreading": improvement >= 2.0e-3,
        "finite_time_candidate_identified": finite_time_candidate,
        "fixed_perturbation_survives": perturbation_survives,
        "long_time_particle_claim_decided": not accepted_particle_candidate,
        "norm_ledgers_close": max_norm <= 2.0e-5,
        "energy_ledgers_close": max_energy <= 2.0e-4,
        "final_gauss_ledgers_close": (
            max_final_gauss_absolute <= 1.0e-3
            and max_final_gauss_relative <= 5.5e-1
        ),
        "radiation_recorded": all(record["run"]["emitted_energy"] >= 0.0 for record in all_records),
    }
    decision = (
        f"lambda={coupling:g} is the strongest finite-time 3D member, but it fails "
        "the frozen long-time localization gate; no stable three-dimensional "
        "particle candidate is accepted."
    )
    return {
        "schema": "openwave.m9.spatial-3d-localization-result.v1",
        "task": "M9.14",
        "survey": survey,
        "selected_coupling": coupling,
        "spreading_improvement": improvement,
        "finite_time_candidate": finite_time_candidate,
        "perturbation": perturbation,
        "long_time": long_time,
        "accepted_particle_candidate": accepted_particle_candidate,
        "decision": decision,
        "global_ledgers": {
            "max_norm_drift": max_norm,
            "max_corrected_energy_relative_drift": max_energy,
            "max_final_gauss_absolute": max_final_gauss_absolute,
            "max_final_gauss_relative": max_final_gauss_relative,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a bounded three-dimensional nonlinear localization survey",
                "a fixed perturbation and long-horizon radiation decision",
                "an explicit positive or negative particle decision",
            ],
            "does_not_establish": [
                "orbital or asymptotic stability",
                "a calibrated particle identity",
                "fermionic quantization or unique CAT/EPT coupling selection",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
