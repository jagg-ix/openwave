"""Run the deterministic M9.11 localization decision and print its summary."""

from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.planar_2d_localization_decision import (
    run_localization_decision,
)


def summarize(result):
    all_runs = (
        result["survey"]["records"]
        + [result["fixed_perturbation"], result["long_time_candidate"]]
    )
    return {
        "schema": "openwave.m9.planar-2d-localization-summary.v1",
        "task": "M9.11",
        "passed": result["passed"],
        "acceptance": result["acceptance"],
        "decision": result["decision"],
        "accepted_particle_candidate": result["accepted_particle_candidate"],
        "finite_time_reduced_spreading_candidate": result[
            "finite_time_reduced_spreading_candidate"
        ],
        "spreading_improvement": result["spreading_improvement"],
        "survey": [
            {
                "soler_coupling": item["soler_coupling"],
                "maximum_rms_ratio": item["maximum_rms_ratio"],
                "minimum_peak_ratio": item["minimum_peak_ratio"],
                "minimum_core_fraction": item["minimum_core_fraction"],
                "emitted_energy": item["run"]["emitted_energy"],
                "max_norm_drift": item["run"]["max_norm_drift"],
                "max_energy_drift": item["run"][
                    "max_corrected_energy_relative_drift"
                ],
                "final_gauss_relative": item["run"]["final"][
                    "gauss_residual_relative"
                ],
            }
            for item in result["survey"]["records"]
        ],
        "fixed_perturbation": {
            key: result["fixed_perturbation"][key]
            for key in (
                "maximum_rms_ratio",
                "minimum_peak_ratio",
                "minimum_core_fraction",
            )
        },
        "long_time": {
            key: result["long_time_candidate"][key]
            for key in (
                "maximum_rms_ratio",
                "minimum_peak_ratio",
                "minimum_core_fraction",
            )
        },
        "ledger_maxima": {
            "norm_drift": max(item["run"]["max_norm_drift"] for item in all_runs),
            "energy_drift": max(
                item["run"]["max_corrected_energy_relative_drift"]
                for item in all_runs
            ),
            "final_gauss_relative": max(
                item["run"]["final"]["gauss_residual_relative"]
                for item in all_runs
            ),
        },
        "classification": result["classification"],
    }


def main() -> int:
    summary = summarize(run_localization_decision())
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
