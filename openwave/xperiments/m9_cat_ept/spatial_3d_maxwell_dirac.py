"""M9.13 coupled three-dimensional Maxwell--Dirac qualification."""

from __future__ import annotations

from functools import lru_cache
import math
from typing import Any, Sequence

import numpy as np

from .spatial_3d import (
    ComplexArray,
    Spatial3DGrid,
    Spatial3DParameters,
    evolve_spatial_3d,
    run_summary,
)

def _relative_spinor_l2(
    actual_plus: ComplexArray,
    actual_minus: ComplexArray,
    expected_plus: ComplexArray,
    expected_minus: ComplexArray,
    cell_volume: float,
) -> float:
    numerator = np.sum(np.abs(actual_plus - expected_plus) ** 2)
    numerator += np.sum(np.abs(actual_minus - expected_minus) ** 2)
    denominator = np.sum(np.abs(expected_plus) ** 2)
    denominator += np.sum(np.abs(expected_minus) ** 2)
    return math.sqrt(cell_volume * float(numerator)) / math.sqrt(
        cell_volume * float(denominator)
    )


def _downsample_state(state: ComplexArray, factor: int) -> ComplexArray:
    return state[:, ::factor, ::factor, ::factor]


def run_coupled_refinement(
    points: Sequence[int] = (10, 20, 40),
) -> dict[str, Any]:
    runs = []
    for count in points:
        runs.append(
            evolve_spatial_3d(
                Spatial3DParameters(),
                Spatial3DGrid(
                    points_x=count,
                    points_y=count,
                    points_z=count,
                    final_time=0.5,
                    samples=9,
                ),
            )
        )
    differences = []
    for coarse, fine in zip(runs[:-1], runs[1:], strict=True):
        factor = fine.grid.points_x // coarse.grid.points_x
        differences.append(
            _relative_spinor_l2(
                coarse.final_plus,
                coarse.final_minus,
                _downsample_state(fine.final_plus, factor),
                _downsample_state(fine.final_minus, factor),
                coarse.dx * coarse.dy * coarse.dz,
            )
        )
    return {
        "summaries": [run_summary(run) for run in runs],
        "successive_spinor_l2_differences": differences,
        "observed_order": math.log(differences[0] / differences[1], 2.0),
    }


def run_domain_shape_study() -> dict[str, Any]:
    cases = (
        (16, 14, 12, 12.0, 10.5, 9.0),
        (16, 16, 14, 12.0, 12.0, 10.5),
        (16, 18, 16, 12.0, 13.5, 12.0),
    )
    records = []
    for nx, ny, nz, hx, hy, hz in cases:
        run = evolve_spatial_3d(
            Spatial3DParameters(),
            Spatial3DGrid(
                half_width_x=hx,
                half_width_y=hy,
                half_width_z=hz,
                points_x=nx,
                points_y=ny,
                points_z=nz,
                final_time=1.2,
                samples=17,
            ),
        )
        summary = run_summary(run)
        records.append(
            {
                "shape": [nx, ny, nz],
                "half_widths": [hx, hy, hz],
                "final_separation": summary["final_separation"],
                "emitted_energy": summary["emitted_energy"],
                "max_energy_drift": summary["max_corrected_energy_relative_drift"],
                "max_gauss_relative": summary["max_gauss_residual_relative"],
            }
        )
    separation = np.asarray([record["final_separation"] for record in records])
    emission = np.asarray([record["emitted_energy"] for record in records])
    return {
        "records": records,
        "relative_spreads": {
            "final_separation": float((np.max(separation) - np.min(separation)) / np.mean(np.abs(separation))),
            "emitted_energy": float((np.max(emission) - np.min(emission)) / max(np.mean(np.abs(emission)), 1.0e-30)),
        },
    }


@lru_cache(maxsize=1)
def run_spatial_3d_transport_study() -> dict[str, Any]:
    refinement = run_coupled_refinement()
    long_run = evolve_spatial_3d(
        Spatial3DParameters(),
        Spatial3DGrid(
            points_x=20,
            points_y=20,
            points_z=20,
            final_time=2.5,
            samples=31,
        ),
    )
    summary = run_summary(long_run)
    domain = run_domain_shape_study()
    initial = summary["initial"]
    final = summary["final"]
    initial_direction = np.asarray(
        [
            initial["minus_center_x"] - initial["plus_center_x"],
            initial["minus_center_y"] - initial["plus_center_y"],
            initial["minus_center_z"] - initial["plus_center_z"],
        ]
    )
    final_direction = np.asarray(
        [
            final["minus_center_x"] - final["plus_center_x"],
            final["minus_center_y"] - final["plus_center_y"],
            final["minus_center_z"] - final["plus_center_z"],
        ]
    )
    direction_change = float(
        math.acos(
            np.clip(
                np.dot(initial_direction, final_direction)
                / (np.linalg.norm(initial_direction) * np.linalg.norm(final_direction)),
                -1.0,
                1.0,
            )
        )
    )
    acceptance = {
        "coupled_refinement_converges": refinement["observed_order"] >= 1.2,
        "norm_conserved": summary["max_norm_drift"] <= 3.0e-6,
        "energy_balance_closes": summary["max_corrected_energy_relative_drift"] <= 3.0e-5,
        "dynamic_gauss_closes": (
            summary["final"]["gauss_residual_absolute"] <= 5.0e-4
            and summary["final"]["gauss_residual_relative"] <= 2.5e-1
        ),
        "net_charge_neutral": summary["max_net_total_charge"] <= 2.0e-8,
        "packets_transport": summary["final_separation"] <= 0.90 * summary["initial_separation"],
        "magnetic_field_nonzero": summary["final"]["max_magnetic_field"] >= 1.0e-4,
        "three_axis_motion": direction_change >= 1.0e-3,
        "radiation_recorded": summary["emitted_energy"] > 0.0,
        "domain_shape_stable": (
            domain["relative_spreads"]["final_separation"] <= 1.0e-3
            and max(record["max_energy_drift"] for record in domain["records"]) <= 1.0e-6
            and max(record["max_gauss_relative"] for record in domain["records"]) <= 2.0e-1
        ),
    }
    return {
        "schema": "openwave.m9.spatial-3d-maxwell-dirac-result.v1",
        "task": "M9.13",
        "model": "bounded 3+1D opposite-charge Maxwell-Dirac transport",
        "refinement": refinement,
        "long_run": summary,
        "direction_change": direction_change,
        "domain_shape_study": domain,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "coupled transport of four-component Dirac packets in three dimensions",
                "three-component electric and magnetic Maxwell back-reaction",
                "dynamic Gauss, absorber-charge, Poynting, and energy ledgers",
                "bounded refinement and domain-shape checks",
            ],
            "does_not_establish": [
                "a stable localized charged particle",
                "orbital or asymptotic stability",
                "physical calibration or fermionic quantization",
            ],
        },
    }
