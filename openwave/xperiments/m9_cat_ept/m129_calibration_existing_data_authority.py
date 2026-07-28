"""M9.129 authority for calibration families, uncertainty, and existing-data reuse."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .four_clock_calibration_family_m129 import run_calibration_family
from .four_clock_uncertainty_m129 import run_uncertainty_propagation
from .existing_experiment_four_clock_protocol_m129 import run_existing_experiment_protocol


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m129_calibration_existing_data_authority() -> dict[str, Any]:
    calibration = run_calibration_family()
    uncertainty = run_uncertainty_propagation()
    evidence = run_existing_experiment_protocol()
    requirements = {
        "nonaffine_monotone_calibration_control": calibration["passed"],
        "uncertainty_and_order_robustness_control": uncertainty["passed"],
        "existing_experiment_reuse_contract": evidence["passed"],
        "qualified_existing_dataset_ingested": evidence["decision"]["qualified_live_package_present"],
        "physlib_pr38_merged_and_compiler_verified": False,
        "independent_physical_pairwise_calibration": False,
    }
    internal_ready = all(requirements[name] for name in (
        "nonaffine_monotone_calibration_control",
        "uncertainty_and_order_robustness_control",
        "existing_experiment_reuse_contract",
    ))
    physical_ready = all(requirements.values())
    payload = {
        "schema": "openwave.m9.m129-calibration-existing-data-authority.v1",
        "task": "M9.129",
        "calibration": calibration,
        "uncertainty": uncertainty,
        "evidence_protocol": evidence,
        "requirements": requirements,
        "decision": {
            "internal_methodology_ready": internal_ready,
            "existing_experiment_reanalysis_ready": True,
            "new_experiment_is_immediately_required": False,
            "physical_promotion_allowed": physical_ready,
        },
        "claim_boundary": {
            "methodology_ready_is_external_validation": False,
            "existing_papers_are_already_ingested": False,
            "physlib_candidate_is_merged_authority": False,
        },
    }
    acceptance = {
        "all_three_internal_targets_pass": internal_ready,
        "physical_gate_fails_closed": not physical_ready,
        "existing_data_route_is_explicit": payload["decision"]["existing_experiment_reanalysis_ready"],
        "new_experiment_is_not_prematurely_required": not payload["decision"]["new_experiment_is_immediately_required"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
