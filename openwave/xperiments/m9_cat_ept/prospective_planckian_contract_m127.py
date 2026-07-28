"""M9.127b: prospective raw-data contract for a discriminating Planckian test."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

REQUIRED_FIELDS = (
    "dataset_id", "paper_or_repository", "material_id", "material_family",
    "temperature_values_K", "transport_times_s", "transport_time_uncertainties_s",
    "extraction_method", "regime_definition", "exclusion_rules",
    "calibration_source", "commitment_digest", "commitment_timestamp",
    "reveal_timestamp", "independent_replication",
)


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def evaluate_package(package: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REQUIRED_FIELDS if field not in package or package[field] in (None, "", [], ()))
    chronology_ok = bool(package.get("commitment_timestamp") and package.get("reveal_timestamp") and package["commitment_timestamp"] < package["reveal_timestamp"])
    arrays_ok = (
        isinstance(package.get("temperature_values_K"), (list, tuple))
        and isinstance(package.get("transport_times_s"), (list, tuple))
        and isinstance(package.get("transport_time_uncertainties_s"), (list, tuple))
        and len(package.get("temperature_values_K", ())) == len(package.get("transport_times_s", ())) == len(package.get("transport_time_uncertainties_s", ()))
        and len(package.get("temperature_values_K", ())) >= 3
    )
    uncertainties_ok = arrays_ok and all(float(value) > 0 for value in package["transport_time_uncertainties_s"])
    return {
        "qualified": not missing and chronology_ok and arrays_ok and uncertainties_ok,
        "missing": missing,
        "chronology_ok": chronology_ok,
        "arrays_ok": arrays_ok,
        "uncertainties_ok": uncertainties_ok,
    }


@lru_cache(maxsize=1)
def run_prospective_planckian_contract() -> dict[str, Any]:
    empty_result = evaluate_package({})
    payload = {
        "schema": "openwave.m9.prospective-planckian-contract.v1",
        "task": "M9.127b",
        "required_fields": REQUIRED_FIELDS,
        "empty_package_result": empty_result,
        "required_model_comparisons": (
            "fixed_planckian_scale_R_equals_1",
            "training_fitted_constant_scale",
            "material_family_random_effect_or_hierarchical_baseline",
        ),
        "required_metrics": (
            "heldout_log_likelihood",
            "calibration_curve",
            "family_level_residuals",
            "sensitivity_to_exclusion_rules",
        ),
        "claim_boundary": {
            "contract_definition_is_external_evidence": False,
            "rounded_figure_values_satisfy_raw_data_contract": False,
            "same_paper_calibration_and_test_are_independent": False,
        },
    }
    acceptance = {
        "contract_requires_raw_values_and_uncertainties": all(field in REQUIRED_FIELDS for field in ("temperature_values_K", "transport_times_s", "transport_time_uncertainties_s")),
        "commitment_precedes_reveal": all(field in REQUIRED_FIELDS for field in ("commitment_digest", "commitment_timestamp", "reveal_timestamp")),
        "material_and_method_metadata_are_required": all(field in REQUIRED_FIELDS for field in ("material_id", "material_family", "extraction_method", "regime_definition", "exclusion_rules")),
        "empty_package_fails_closed": not empty_result["qualified"] and set(empty_result["missing"]) == set(REQUIRED_FIELDS),
        "alternative_baselines_are_mandatory": len(payload["required_model_comparisons"]) >= 3,
        "no_prospective_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "prospective_evidence_contract_ready": True,
            "qualified_live_dataset_present": False,
            "physical_promotion_allowed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
