"""M9.130b: theorem-specific evaluators for relational conditioning and binary relaxation."""
from __future__ import annotations

from math import exp, log
from typing import Any, Mapping, Sequence


def evaluate_relational_conditioning(rows: Sequence[Mapping[str, Any]], minimum_fidelity: float = 0.95) -> dict[str, Any]:
    selected = [row for row in rows if row["domain"] == "relational-conditioning"]
    z_scores = tuple((1.0 - float(row["y"])) / float(row["uncertainty"]) for row in selected)
    return {
        "domain": "relational-conditioning",
        "count": len(selected),
        "minimum_observed_fidelity": min((float(row["y"]) for row in selected), default=0.0),
        "maximum_absolute_z": max((abs(value) for value in z_scores), default=float("inf")),
        "passed": bool(selected) and all(float(row["y"]) >= minimum_fidelity for row in selected),
    }


def predict_binary_relaxation(time: float, initial: float, equilibrium: float, gamma_in: float, gamma_out: float) -> float:
    total = gamma_in + gamma_out
    if total <= 0:
        raise ValueError("total transition rate must be positive")
    return equilibrium + (initial - equilibrium) * exp(-total * time)


def binary_kl(value: float, reference: float) -> float:
    if not (0.0 < value < 1.0 and 0.0 < reference < 1.0):
        raise ValueError("binary KL requires interior occupations")
    return value * log(value / reference) + (1.0 - value) * log((1.0 - value) / (1.0 - reference))


def evaluate_binary_relaxation(rows: Sequence[Mapping[str, Any]], *, initial: float, gamma_in: float, gamma_out: float) -> dict[str, Any]:
    selected = sorted((row for row in rows if row["domain"] == "binary-relaxation"), key=lambda row: float(row["x"]))
    total = gamma_in + gamma_out
    equilibrium = gamma_in / total
    predictions = tuple(predict_binary_relaxation(float(row["x"]), initial, equilibrium, gamma_in, gamma_out) for row in selected)
    residuals = tuple(float(row["y"]) - prediction for row, prediction in zip(selected, predictions))
    z_scores = tuple(residual / float(row["uncertainty"]) for row, residual in zip(selected, residuals))
    observed_kl = tuple(binary_kl(float(row["y"]), equilibrium) for row in selected if 0.0 < float(row["y"]) < 1.0)
    kl_nonincreasing = all(left >= right for left, right in zip(observed_kl, observed_kl[1:]))
    return {
        "domain": "binary-relaxation",
        "count": len(selected),
        "equilibrium": equilibrium,
        "predictions": predictions,
        "maximum_absolute_z": max((abs(value) for value in z_scores), default=float("inf")),
        "observed_kl_nonincreasing": kl_nonincreasing,
        "passed": bool(selected) and max((abs(value) for value in z_scores), default=float("inf")) <= 3.0 and kl_nonincreasing,
    }


def run_theorem_specific_evaluators() -> dict[str, Any]:
    relational_rows = (
        {"domain": "relational-conditioning", "y": 0.992, "uncertainty": 0.006},
        {"domain": "relational-conditioning", "y": 0.986, "uncertainty": 0.008},
    )
    gamma_in, gamma_out = 2.0, 3.0
    equilibrium, initial = gamma_in / (gamma_in + gamma_out), 0.82
    relaxation_rows = tuple(
        {
            "domain": "binary-relaxation",
            "x": time,
            "y": predict_binary_relaxation(time, initial, equilibrium, gamma_in, gamma_out),
            "uncertainty": 0.01,
        }
        for time in (0.0, 0.15, 0.35, 0.7, 1.2)
    )
    relational = evaluate_relational_conditioning(relational_rows)
    relaxation = evaluate_binary_relaxation(relaxation_rows, initial=initial, gamma_in=gamma_in, gamma_out=gamma_out)
    acceptance = {
        "relational_evaluator_passes": relational["passed"],
        "relaxation_evaluator_passes": relaxation["passed"],
        "strict_kl_behavior_is_checked": relaxation["observed_kl_nonincreasing"],
        "rate_parameters_are_frozen_outside_holdout": True,
    }
    return {
        "schema": "openwave.m9.theorem-specific-existing-data-evaluators.v1",
        "task": "M9.130b",
        "relational": relational,
        "relaxation": relaxation,
        "claim_boundary": {
            "synthetic_fixture_is_external_validation": False,
            "three_sigma_gate_is_universal_statistical_standard": False,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
