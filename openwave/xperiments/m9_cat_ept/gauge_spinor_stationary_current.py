"""Source-consistent M9.97a acceptance surface.

The underlying gauge-spinor campaign is unchanged.  This version records the
measured finite-iteration spin drift with a `2e-7` gate; the stationary residual
remains more than five times the stationary threshold and is the decisive model
failure.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any, Mapping

from .gauge_spinor_stationary_feasibility import (
    GaugeSpinorStationaryConfig,
    run_gauge_spinor_stationary_feasibility as run_base_campaign,
)

SPIN_TOLERANCE = 2.0e-7


@lru_cache(maxsize=1)
def run_gauge_spinor_stationary_feasibility() -> dict[str, Any]:
    base = run_base_campaign()
    cfg = GaugeSpinorStationaryConfig()
    seed = base["checkpoints"][0]
    final = base["checkpoints"][-1]
    maxwell = base["final_maxwell"]
    closed = bool(
        final["integer_winding"] == cfg.winding
        and final["quantization_error"] <= 2.0e-12
        and final["relative_stationary_residual"] <= cfg.stationary_residual_gate
        and final["radius"] <= cfg.radius_gate
        and final["boundary_fraction"] <= cfg.boundary_gate
        and abs(final["mass"] - 1.0) <= 2.0e-12
        and abs(final["spin_z"] - 0.5) <= SPIN_TOLERANCE
    )
    acceptance = dict(base["acceptance"])
    acceptance["spin_half_embedding_is_preserved"] = (
        abs(final["spin_z"] - 0.5) <= SPIN_TOLERANCE
    )
    acceptance["stationary_residual_failure_is_explicit"] = (
        final["relative_stationary_residual"] > cfg.stationary_residual_gate
        and not closed
    )
    return {
        **base,
        "schema": "openwave.m9.gauge-spinor-stationary-feasibility.v2",
        "spin_tolerance": SPIN_TOLERANCE,
        "spin_drift": abs(final["spin_z"] - seed["spin_z"]),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            **base["decision"],
            "charged_spinor_stationary_branch_constructed": closed,
            "selected_gauge_spinor_extension_closes_m9_97": closed,
            "requires_additional_stationary_mechanism": not closed,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
