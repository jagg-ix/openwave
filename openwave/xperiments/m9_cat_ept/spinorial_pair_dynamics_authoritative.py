"""Canonical M9.97 pair dynamics composed with the versioned stationary audit."""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any, Mapping

from .gauge_spinor_stationary_current import (
    run_gauge_spinor_stationary_feasibility,
)
from .spinorial_pair_dynamics_current import (
    run_spinorial_pair_dynamics as run_source_consistent_dynamics,
)


@lru_cache(maxsize=1)
def run_spinorial_pair_dynamics() -> dict[str, Any]:
    stationary = run_gauge_spinor_stationary_feasibility()
    base = run_source_consistent_dynamics()
    acceptance = dict(base["acceptance"])
    acceptance["gauge_spinor_stationary_boundary_is_imported"] = (
        stationary["passed"]
        and not stationary["decision"]["charged_spinor_stationary_branch_constructed"]
    )
    return {
        **base,
        "schema": "openwave.m9.spinorial-pair-dynamics.v3",
        "stationary_authority_schema": stationary["schema"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
