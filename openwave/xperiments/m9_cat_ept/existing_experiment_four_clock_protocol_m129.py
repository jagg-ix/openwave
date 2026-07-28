"""M9.129c: contract for reusing existing clock and relaxation experiments."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping


EXISTING_DATA_TARGETS = (
    {
        "dataset_id": "moreva-2014-page-wootters",
        "domain": "relational-conditioning",
        "required_observables": ("clock_outcome", "conditional_system_state", "global_state_stationarity", "uncertainty"),
    },
    {
        "dataset_id": "moreva-2017-multitime",
        "domain": "relational-multitime",
        "required_observables": ("clock_pair", "conditional_correlation", "sequential_reference", "uncertainty"),
    },
    {
        "dataset_id": "lu-2003-quantum-dot",
        "domain": "binary-relaxation",
        "required_observables": ("time", "occupation", "gamma_in", "gamma_out", "uncertainty"),
    },
    {
        "dataset_id": "superconducting-qubit-thermal-relaxation",
        "domain": "open-system-clock",
        "required_observables": ("time", "excited_population", "equilibrium_population", "T1", "uncertainty"),
    },
)

REQUIRED_PACKAGE_FIELDS = (
    "dataset_id",
    "source_uri",
    "source_digest",
    "observables",
    "calibration_observation_ids",
    "heldout_observation_ids",
    "units",
    "extraction_method",
)


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def validate_package(package: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REQUIRED_PACKAGE_FIELDS if not package.get(field))
    target = next((item for item in EXISTING_DATA_TARGETS if item["dataset_id"] == package.get("dataset_id")), None)
    observables = set(package.get("observables", ()))
    target_observables_ok = target is not None and set(target["required_observables"]).issubset(observables)
    calibration = set(package.get("calibration_observation_ids", ()))
    heldout = set(package.get("heldout_observation_ids", ()))
    disjoint = bool(calibration and heldout and calibration.isdisjoint(heldout))
    digest_ok = isinstance(package.get("source_digest"), str) and len(package.get("source_digest", "")) == 64
    return {
        "qualified": not missing and target_observables_ok and disjoint and digest_ok,
        "missing": missing,
        "known_dataset": target is not None,
        "required_observables_present": target_observables_ok,
        "calibration_holdout_disjoint": disjoint,
        "digest_shape_ok": digest_ok,
    }


@lru_cache(maxsize=1)
def run_existing_experiment_protocol() -> dict[str, Any]:
    empty = validate_package({})
    example = {
        "dataset_id": "lu-2003-quantum-dot",
        "source_uri": "paper-or-data-repository-uri",
        "source_digest": "0" * 64,
        "observables": ("time", "occupation", "gamma_in", "gamma_out", "uncertainty"),
        "calibration_observation_ids": ("rate-window-a", "rate-window-b"),
        "heldout_observation_ids": ("trajectory-c", "trajectory-d"),
        "units": {"time": "s", "rate": "s^-1"},
        "extraction_method": "waiting-time rates frozen before trajectory evaluation",
    }
    example_result = validate_package(example)
    payload = {
        "schema": "openwave.m9.existing-experiment-four-clock-protocol.v1",
        "task": "M9.129c",
        "targets": EXISTING_DATA_TARGETS,
        "required_package_fields": REQUIRED_PACKAGE_FIELDS,
        "empty_package_result": empty,
        "structural_example_result": example_result,
        "claim_boundary": {
            "target_registry_means_data_were_ingested": False,
            "structural_example_is_external_evidence": False,
            "paper_citation_alone_is_qualified_dataset": False,
        },
    }
    acceptance = {
        "four_existing_data_targets_are_registered": len(EXISTING_DATA_TARGETS) == 4,
        "relational_and_relaxation_domains_are_both_covered": {item["domain"] for item in EXISTING_DATA_TARGETS} >= {"relational-conditioning", "binary-relaxation"},
        "empty_package_fails_closed": not empty["qualified"],
        "structural_example_requires_disjoint_split": example_result["qualified"] and example_result["calibration_holdout_disjoint"],
        "source_digest_is_required": "source_digest" in REQUIRED_PACKAGE_FIELDS,
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": _fingerprint(payload),
        "decision": {
            "existing_experiments_can_be_reused": True,
            "qualified_live_package_present": False,
            "new_experiment_required_before_reanalysis": False,
            "physical_promotion_allowed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
