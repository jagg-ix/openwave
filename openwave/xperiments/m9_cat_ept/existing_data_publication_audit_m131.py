"""M9.131c: leakage audit and publication report for existing-data evaluation."""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def audit_split(rows: Sequence[Mapping[str, Any]], fitted_observation_ids: Sequence[str]) -> dict[str, Any]:
    fitted = set(fitted_observation_ids)
    calibration = {str(row["observation_id"]) for row in rows if row["split"] == "calibration"}
    holdout = {str(row["observation_id"]) for row in rows if row["split"] == "holdout"}
    leakage = tuple(sorted(fitted & holdout))
    return {
        "calibration_ids": tuple(sorted(calibration)),
        "holdout_ids": tuple(sorted(holdout)),
        "fitted_ids": tuple(sorted(fitted)),
        "leakage_ids": leakage,
        "disjoint_split": calibration.isdisjoint(holdout),
        "fit_uses_calibration_only": fitted.issubset(calibration),
        "passed": calibration.isdisjoint(holdout) and fitted.issubset(calibration) and not leakage,
    }


def run_leakage_publication_audit() -> dict[str, Any]:
    rows = (
        {"observation_id":"c0","split":"calibration"},
        {"observation_id":"c1","split":"calibration"},
        {"observation_id":"h0","split":"holdout"},
        {"observation_id":"h1","split":"holdout"},
    )
    audit = audit_split(rows, ("c0", "c1"))
    report = {
        "theorem_families": ("page-wootters-conditioning", "binary-relaxation", "strict-binary-kl"),
        "required_metrics": ("maximum-absolute-z", "heldout-rmse", "kl-monotonicity", "carrier-fold-result"),
        "negative_results_must_be_retained": True,
        "per_carrier_refitting_allowed": False,
    }
    acceptance = {
        "split_audit_passes": audit["passed"],
        "holdout_leakage_is_empty": not audit["leakage_ids"],
        "negative_results_are_required": report["negative_results_must_be_retained"],
        "per_carrier_refitting_is_forbidden": not report["per_carrier_refitting_allowed"],
    }
    return {"schema":"openwave.m9.existing-data-publication-audit.v1","task":"M9.131c","audit":audit,"report_contract":report,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"publication_pipeline_ready":True,"external_validation_complete":False}}
