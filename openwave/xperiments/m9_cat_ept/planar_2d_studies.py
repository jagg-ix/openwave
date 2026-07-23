"""Deterministic studies for the M9.10 two-dimensional reduction."""

from __future__ import annotations

from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np

from .planar_2d_core import Planar2DGrid, Planar2DRun
from .planar_2d_dynamics import evolve_planar_2d, run_summary


def _spinor_difference(coarse: Planar2DRun, fine: Planar2DRun) -> float:
    fine_plus = fine.final_plus[:, ::2, ::2]
    fine_minus = fine.final_minus[:, ::2, ::2]
    value = np.sum(np.abs(coarse.final_plus - fine_plus) ** 2)
    value += np.sum(np.abs(coarse.final_minus - fine_minus) ** 2)
    return math.sqrt(coarse.dx * coarse.dy * float(value))


def run_refinement(
    points: Sequence[int] = (32, 64, 128),
    final_time: float = 2.0,
) -> dict[str, Any]:
    runs = [
        evolve_planar_2d(
            grid=Planar2DGrid(
                points_x=count,
                points_y=count,
                final_time=final_time,
                samples=25,
            )
        )
        for count in points
    ]
    differences = [
        _spinor_difference(coarse, fine)
        for coarse, fine in zip(runs[:-1], runs[1:], strict=True)
    ]
    return {
        "summaries": [run_summary(run) for run in runs],
        "successive_spinor_l2_differences": differences,
        "observed_order": math.log(
            differences[0] / differences[1], 2.0
        ),
    }


def run_domain_shape_study() -> dict[str, Any]:
    cases = (
        (18.0, 15.0, 72, 60),
        (18.0, 18.0, 72, 72),
        (18.0, 21.0, 72, 84),
    )
    records: list[dict[str, float]] = []
    for half_x, half_y, points_x, points_y in cases:
        run = evolve_planar_2d(
            grid=Planar2DGrid(
                half_width_x=half_x,
                half_width_y=half_y,
                points_x=points_x,
                points_y=points_y,
                final_time=5.0,
                samples=31,
            )
        )
        summary = run_summary(run)
        records.append(
            {
                "half_width_x": half_x,
                "half_width_y": half_y,
                "points_x": points_x,
                "points_y": points_y,
                "final_separation": summary["final_separation"],
                "emitted_energy": summary["emitted_energy"],
                "max_norm_drift": summary["max_norm_drift"],
                "max_energy_drift": summary[
                    "max_corrected_energy_relative_drift"
                ],
            }
        )
    separation = np.asarray([item["final_separation"] for item in records])
    emitted = np.asarray([item["emitted_energy"] for item in records])
    return {
        "records": records,
        "relative_spreads": {
            "final_separation": float(
                np.ptp(separation) / np.mean(np.abs(separation))
            ),
            "emitted_energy": float(
                np.ptp(emitted) / max(np.mean(np.abs(emitted)), 1.0e-30)
            ),
        },
    }


@lru_cache(maxsize=1)
def run_planar_2d_study() -> dict[str, Any]:
    refinement = run_refinement()
    long_run = evolve_planar_2d(
        grid=Planar2DGrid(
            points_x=96,
            points_y=96,
            final_time=8.0,
            samples=65,
        )
    )
    summary = run_summary(long_run)
    shape = run_domain_shape_study()
    initial_direction = math.atan2(
        summary["initial"]["minus_center_y"]
        - summary["initial"]["plus_center_y"],
        summary["initial"]["minus_center_x"]
        - summary["initial"]["plus_center_x"],
    )
    final_direction = math.atan2(
        summary["final"]["minus_center_y"]
        - summary["final"]["plus_center_y"],
        summary["final"]["minus_center_x"]
        - summary["final"]["plus_center_x"],
    )
    acceptance = {
        "two_dimensional_convergence": refinement["observed_order"] >= 3.0,
        "norm_conserved": summary["max_norm_drift"] <= 2.0e-8,
        "energy_balance_closes": (
            summary["max_corrected_energy_relative_drift"] <= 5.0e-5
        ),
        "dynamic_gauss_closes": (
            summary["final"]["gauss_residual_absolute"] <= 2.0e-4
            and summary["final"]["gauss_residual_relative"] <= 5.0e-2
        ),
        "net_charge_neutral": summary["max_net_charge"] <= 1.0e-10,
        "packets_transport": (
            summary["final_separation"] < summary["initial_separation"]
        ),
        "magnetic_field_nonzero": (
            summary["final"]["max_magnetic_field"] >= 1.0e-4
        ),
        "non_axis_aligned_transport": (
            abs(final_direction - initial_direction) >= 1.0e-3
        ),
        "domain_shape_stable": (
            shape["relative_spreads"]["final_separation"] <= 0.08
            and shape["relative_spreads"]["emitted_energy"] <= 0.30
        ),
    }
    return {
        "schema": "openwave.m9.planar-2d-maxwell-dirac-result.v1",
        "task": "M9.10",
        "model": "bounded 2+1D opposite-charge Maxwell-Dirac reduction",
        "refinement": refinement,
        "long_run": summary,
        "domain_shape_study": shape,
        "transport_angles": {
            "initial": initial_direction,
            "final": final_direction,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "two-dimensional transport of opposite-charge Dirac packets",
                "two-component electric fields and magnetic curl back-reaction",
                "dynamic two-dimensional Gauss monitoring and net neutrality",
                "non-axis-aligned Poynting-capable transport",
                "bounded refinement and domain-shape ledgers",
            ],
            "does_not_establish": [
                "a stable localized charged particle",
                "full three-dimensional Maxwell-Dirac dynamics",
                "electron identity, calibrated units, or fermionic quantization",
                "unique CAT/EPT derivation of the 2D reduction",
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
