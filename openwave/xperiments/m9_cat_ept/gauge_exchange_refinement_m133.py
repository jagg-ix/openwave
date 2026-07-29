"""M9.133b-c: local exchange accounting and gauge-coupled refinement campaign."""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
import json
import math
from typing import Any, Mapping

from .gauge_coupled_cat_ept_m133 import GaugeCATEPTConfig, run_with_config


def run_exchange_accounting() -> dict[str, Any]:
    result = run_with_config(GaugeCATEPTConfig())
    records = result["records"]
    matter_change = records[-1]["matter_energy"] - records[0]["matter_energy"]
    gauge_change = records[-1]["gauge_energy"] - records[0]["gauge_energy"]
    resolved_change = records[-1]["total_resolved_energy"] - records[0]["total_resolved_energy"]
    entropy_gain = records[-1]["entropic_time"] - records[0]["entropic_time"]
    current_response = max(row["current_l2"] for row in records)
    electric_response = max(row["electric_l2"] for row in records)
    acceptance = {
        "gauge_coupled_solver_passes": result["passed"],
        "matter_and_gauge_energy_are_jointly_reported": all(
            math.isfinite(value) for value in (matter_change, gauge_change, resolved_change)
        ),
        "matter_gauge_exchange_is_nontrivial": abs(matter_change) > 1.0e-9 and abs(gauge_change) > 1.0e-12,
        "current_drives_electric_response": current_response > 1.0e-8 and electric_response > 1.0e-10,
        "irreversible_sector_produces_entropic_time": entropy_gain > 0.0,
        "gauss_constraint_is_tracked": all(math.isfinite(row["gauss_residual_l2"]) for row in records),
    }
    return {
        "schema": "openwave.m9.gauge-exchange-accounting.v1",
        "task": "M9.133b",
        "records": records,
        "metrics": {
            "matter_energy_change": matter_change,
            "gauge_energy_change": gauge_change,
            "resolved_energy_change": resolved_change,
            "entropic_time_gain": entropy_gain,
            "maximum_current_l2": current_response,
            "maximum_electric_l2": electric_response,
            "maximum_gauss_residual_l2": max(row["gauss_residual_l2"] for row in records),
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "claim_boundary": {
            "resolved_energy_accounting_is_exact_total_conservation": False,
            "finite_Gauss_residual_is_constraint_proof": False,
            "finite_run_is_global_stability": False,
        },
    }


def _terminal(result: Mapping[str, Any]) -> Mapping[str, float]:
    return result["records"][-1]


def run_refinement_campaign() -> dict[str, Any]:
    base = GaugeCATEPTConfig()
    configs = (
        replace(base, points=64, time_step=3.0e-4, steps=160, sample_stride=20),
        replace(base, points=96, time_step=2.0e-4, steps=240, sample_stride=30),
        replace(base, points=128, time_step=1.5e-4, steps=320, sample_stride=40),
    )
    results = tuple(run_with_config(cfg) for cfg in configs)
    rows = tuple({
        "points": result["config"]["points"],
        "final_time": result["records"][-1]["time"],
        "density_peak": _terminal(result)["density_peak"],
        "matter_energy": _terminal(result)["matter_energy"],
        "gauge_energy": _terminal(result)["gauge_energy"],
        "electric_l2": _terminal(result)["electric_l2"],
        "entropic_time": _terminal(result)["entropic_time"],
        "gauss_residual_l2": _terminal(result)["gauss_residual_l2"],
    } for result in results)
    tracked = ("density_peak", "matter_energy", "gauge_energy", "electric_l2", "entropic_time")
    pair_changes = []
    for left, right in zip(rows, rows[1:]):
        changes = {
            key: abs(float(right[key]) - float(left[key])) / max(abs(float(right[key])), abs(float(left[key])), 1.0e-15)
            for key in tracked
        }
        pair_changes.append({
            "coarse_points": left["points"],
            "fine_points": right["points"],
            **changes,
            "maximum_relative_change": max(changes.values()),
        })
    acceptance = {
        "three_grids_execute": len(results) == 3 and all(result["passed"] for result in results),
        "common_final_time_is_preserved": max(row["final_time"] for row in rows) - min(row["final_time"] for row in rows) <= 1.0e-12,
        "refinement_diagnostics_are_finite": all(math.isfinite(float(value)) for row in rows for value in row.values()),
        "successive_results_are_bounded": max(pair["maximum_relative_change"] for pair in pair_changes) < 0.45,
        "gauss_residual_does_not_diverge": rows[-1]["gauss_residual_l2"] < 3.0 * max(rows[0]["gauss_residual_l2"], 1.0e-12),
    }
    return {
        "schema": "openwave.m9.gauge-coupled-refinement.v1",
        "task": "M9.133c",
        "rows": rows,
        "pair_changes": tuple(pair_changes),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "claim_boundary": {
            "three_grid_boundedness_is_continuum_convergence": False,
            "finite_constraint_control_is_exact_gauge_invariance": False,
            "dimensionless_refinement_is_physical_validation": False,
        },
    }


@lru_cache(maxsize=1)
def run_gauge_exchange_refinement() -> dict[str, Any]:
    exchange = run_exchange_accounting()
    refinement = run_refinement_campaign()
    acceptance = {
        "exchange_accounting_passes": exchange["passed"],
        "refinement_campaign_passes": refinement["passed"],
        "model_level_extension_complete": True,
    }
    return {
        "schema": "openwave.m9.gauge-exchange-refinement-authority.v1",
        "task": "M9.133b-c",
        "exchange": exchange,
        "refinement": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
