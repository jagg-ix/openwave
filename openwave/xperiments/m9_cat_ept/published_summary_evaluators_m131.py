"""M9.131c: theorem-facing checks over published summary-level evidence."""
from __future__ import annotations

from math import isfinite
from typing import Any, Mapping, Sequence

from .published_summary_ingestion_m131 import published_summary_rows, quasiparticle_decay


def evaluate_leggett_garg(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = tuple(row for row in rows if row["domain"] == "leggett-garg-correlation")
    z_scores = tuple((float(row["y"]) - float(row["theory"])) / float(row["uncertainty"]) for row in selected)
    return {
        "count": len(selected),
        "all_observed_values_violate_classical_upper_bound": bool(selected)
        and all(float(row["y"]) > 1.0 for row in selected),
        "maximum_absolute_theory_residual_z": max((abs(value) for value in z_scores), default=float("inf")),
        "passed": bool(selected)
        and all(float(row["y"]) > 1.0 for row in selected)
        and max((abs(value) for value in z_scores), default=float("inf")) <= 3.0,
    }


def evaluate_qubit_fit_reconstruction(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = tuple(row for row in rows if row["domain"] == "quasiparticle-relaxation-fit")
    residuals = tuple(float(row["y"]) - quasiparticle_decay(float(row["x"])) for row in selected)
    values = tuple(float(row["y"]) for row in selected)
    return {
        "count": len(selected),
        "maximum_absolute_reconstruction_error": max((abs(value) for value in residuals), default=float("inf")),
        "population_is_nonincreasing": all(left >= right for left, right in zip(values, values[1:])),
        "passed": bool(selected)
        and max((abs(value) for value in residuals), default=float("inf")) <= 1.0e-15
        and all(left >= right for left, right in zip(values, values[1:])),
    }


def evaluate_quantum_dot_bound(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    selected = tuple(row for row in rows if row["domain"] == "inelastic-scattering-bound")
    return {
        "count": len(selected),
        "minimum_reported_lower_bound_us": min((float(row["y"]) for row in selected), default=0.0),
        "passed": len(selected) == 1 and float(selected[0]["y"]) >= 10.0,
    }


def run_published_summary_evaluators() -> dict[str, Any]:
    rows = published_summary_rows()
    leggett_garg = evaluate_leggett_garg(rows)
    qubit = evaluate_qubit_fit_reconstruction(rows)
    dot = evaluate_quantum_dot_bound(rows)
    acceptance = {
        "published_Leggett_Garg_table_is_evaluated": leggett_garg["passed"],
        "published_qubit_fit_is_reproduced": qubit["passed"],
        "published_quantum_dot_bound_is_preserved": dot["passed"],
        "all_summary_metrics_are_finite": all(
            isfinite(value)
            for value in (
                leggett_garg["maximum_absolute_theory_residual_z"],
                qubit["maximum_absolute_reconstruction_error"],
                dot["minimum_reported_lower_bound_us"],
            )
        ),
    }
    return {
        "schema": "openwave.m9.published-summary-evaluators.v1",
        "task": "M9.131c",
        "leggett_garg": leggett_garg,
        "qubit_fit": qubit,
        "quantum_dot_bound": dot,
        "claim_boundary": {
            "published_summary_reconstruction_is_raw_data_validation": False,
            "Leggett_Garg_violation_validates_all_Page_Wootters_claims": False,
            "fit_reproduction_is_independent_prediction": False,
            "lower_bound_is_complete_relaxation_trajectory": False,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
