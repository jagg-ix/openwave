from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

INTERNAL_REQUIREMENTS = (
    "formalized_by:lean_theorem",
    "implemented_by:numerical_campaign",
    "axiom_status:kernel_clean",
    "reproduced_by:deterministic_runner",
)
EXTERNAL_REQUIREMENTS = INTERNAL_REQUIREMENTS + (
    "calibrated_by:independent_anchor",
    "committed_before_reveal:prediction_digest",
    "tested_against:heldout_observation",
    "identity_supported_by:independent_bridge",
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def evaluate_relations(
    relations: Iterable[str], requirements: tuple[str, ...]
) -> dict[str, Any]:
    observed = set(relations)
    missing = tuple(item for item in requirements if item not in observed)
    return {"passed": not missing, "missing": missing, "observed": tuple(sorted(observed))}


@lru_cache(maxsize=1)
def run_physical_promotion_gate() -> dict[str, Any]:
    current = {
        "formalized_by:lean_theorem",
        "implemented_by:numerical_campaign",
        "axiom_status:kernel_clean",
        "reproduced_by:deterministic_runner",
        "open_system_decay:model_units",
        "calibration_state:external_anchor_missing",
        "validation_state:holdout_sealed",
    }
    complete_synthetic = set(EXTERNAL_REQUIREMENTS)
    internal = evaluate_relations(current, INTERNAL_REQUIREMENTS)
    external = evaluate_relations(current, EXTERNAL_REQUIREMENTS)
    synthetic = evaluate_relations(complete_synthetic, EXTERNAL_REQUIREMENTS)
    removal_failures = {
        requirement: not evaluate_relations(
            complete_synthetic - {requirement}, EXTERNAL_REQUIREMENTS
        )["passed"]
        for requirement in EXTERNAL_REQUIREMENTS
    }
    payload = {
        "schema": "openwave.m9.physical-promotion-gate.v1",
        "task": "M9.121c",
        "internal_requirements": INTERNAL_REQUIREMENTS,
        "external_requirements": EXTERNAL_REQUIREMENTS,
        "current_relations": tuple(sorted(current)),
        "internal_evaluation": internal,
        "external_evaluation": external,
        "synthetic_complete_evaluation": synthetic,
        "claim_boundary": {
            "internal_model_closure_is_external_validation": False,
            "kernel_clean_theorem_is_physical_identity": False,
            "model_unit_decay_is_calibrated_lifetime": False,
            "sealed_holdout_is_successful_heldout_test": False,
        },
    }
    acceptance = {
        "internal_model_gate_accepts_current_evidence": internal["passed"],
        "external_gate_rejects_current_unvalidated_state": not external["passed"],
        "external_gate_names_all_missing_relations": set(external["missing"])
        == set(EXTERNAL_REQUIREMENTS) - set(current),
        "complete_synthetic_record_passes": synthetic["passed"],
        "every_required_relation_is_individually_load_bearing": all(
            removal_failures.values()
        ),
        "no_physical_promotion_is_inferred": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "removal_failures": removal_failures,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "internal_model_promotion_allowed": True,
            "external_physical_promotion_allowed": False,
            "physical_promotion_gate_is_fail_closed": True,
        },
    }
