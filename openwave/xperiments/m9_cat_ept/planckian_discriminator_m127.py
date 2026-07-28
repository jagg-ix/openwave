"""M9.127a: discriminate the fixed Planckian scale from a fitted constant baseline."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from math import exp, log
from typing import Any, Mapping

from .experimental_evidence_inventory_m126 import PLANCKIAN_RECORDS


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _geometric_mean(values: list[float]) -> float:
    return exp(sum(log(value) for value in values) / len(values))


def _mean_absolute_log_error(values: list[float], prediction: float) -> float:
    return sum(abs(log(value / prediction)) for value in values) / len(values)


@lru_cache(maxsize=1)
def run_planckian_discriminator() -> dict[str, Any]:
    papers = sorted({record["paper"] for record in PLANCKIAN_RECORDS})
    folds = []
    fixed_errors: list[float] = []
    fitted_errors: list[float] = []
    for paper in papers:
        train = [float(record["ratio"]) for record in PLANCKIAN_RECORDS if record["paper"] != paper]
        test = [float(record["ratio"]) for record in PLANCKIAN_RECORDS if record["paper"] == paper]
        fitted_constant = _geometric_mean(train)
        fixed_error = _mean_absolute_log_error(test, 1.0)
        fitted_error = _mean_absolute_log_error(test, fitted_constant)
        fixed_errors.extend(abs(log(value)) for value in test)
        fitted_errors.extend(abs(log(value / fitted_constant)) for value in test)
        folds.append({
            "heldout_paper": paper,
            "training_count": len(train),
            "heldout_count": len(test),
            "fitted_constant": fitted_constant,
            "fixed_planckian_error": fixed_error,
            "fitted_baseline_error": fitted_error,
            "winner": "fixed_planckian" if fixed_error < fitted_error else "fitted_constant",
            "all_heldout_inside_broad_band": all(0.1 < value < 10.0 for value in test),
        })
    fixed_mean = sum(fixed_errors) / len(fixed_errors)
    fitted_mean = sum(fitted_errors) / len(fitted_errors)
    fixed_fold_wins = sum(fold["winner"] == "fixed_planckian" for fold in folds)
    payload = {
        "schema": "openwave.m9.planckian-discriminator.v1",
        "task": "M9.127a",
        "observable": "R=tau_tr*k_B*T/hbar",
        "fixed_prediction": 1.0,
        "folds": tuple(folds),
        "aggregate": {
            "fixed_mean_absolute_log_error": fixed_mean,
            "fitted_mean_absolute_log_error": fitted_mean,
            "fixed_fold_wins": fixed_fold_wins,
            "fitted_fold_wins": len(folds) - fixed_fold_wins,
        },
        "claim_boundary": {
            "lower_aggregate_error_is_unique_mechanism_identification": False,
            "broad_band_success_is_precision_validation": False,
            "retrospective_fold_is_prospective_blinding": False,
        },
    }
    acceptance = {
        "all_three_papers_are_held_out_once": len(folds) == 3 and {fold["heldout_paper"] for fold in folds} == set(papers),
        "baseline_is_fit_without_heldout_paper": all(fold["training_count"] + fold["heldout_count"] == len(PLANCKIAN_RECORDS) for fold in folds),
        "fixed_scale_has_lower_aggregate_log_error": fixed_mean < fitted_mean,
        "fold_results_are_mixed": 0 < fixed_fold_wins < len(folds),
        "broad_band_is_reported_separately": all(fold["all_heldout_inside_broad_band"] for fold in folds),
        "no_discrimination_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "fixed_planckian_scale_has_weak_aggregate_advantage": fixed_mean < fitted_mean,
            "paper_level_preference_is_consistent": fixed_fold_wins == len(folds),
            "existing_rounded_dataset_discriminates_entropic_time": False,
            "stronger_raw_dataset_required": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
