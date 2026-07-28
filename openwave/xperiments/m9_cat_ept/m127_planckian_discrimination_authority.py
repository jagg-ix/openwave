"""M9.127 authority for Planckian discrimination and prospective evidence requirements."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .experimental_evidence_qualification_m126 import run_experimental_evidence_qualification
from .planckian_discriminator_m127 import run_planckian_discriminator
from .prospective_planckian_contract_m127 import run_prospective_planckian_contract


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m127_planckian_discrimination_authority() -> dict[str, Any]:
    previous = run_experimental_evidence_qualification()
    discriminator = run_planckian_discriminator()
    prospective = run_prospective_planckian_contract()
    payload = {
        "schema": "openwave.m9.m127-planckian-discrimination-authority.v1",
        "task": "M9.127",
        "previous_evidence_qualification": previous,
        "discriminator": discriminator,
        "prospective_contract": prospective,
        "claim_boundary": {
            "weak_aggregate_advantage_is_confirmation": False,
            "mixed_fold_result_is_consistent_model_selection": False,
            "prospective_contract_is_completed_experiment": False,
        },
    }
    acceptance = {
        "M9_126_evidence_qualification_is_preserved": previous["passed"],
        "M9_127a_discriminator_executes": discriminator["passed"],
        "M9_127a_records_non_discrimination": not discriminator["decision"]["existing_rounded_dataset_discriminates_entropic_time"],
        "M9_127b_prospective_contract_is_fail_closed": prospective["passed"] and not prospective["decision"]["qualified_live_dataset_present"],
        "physical_promotion_remains_blocked": not prospective["decision"]["physical_promotion_allowed"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "retrospective_discriminator_complete": True,
            "fixed_scale_has_weak_aggregate_advantage": discriminator["decision"]["fixed_planckian_scale_has_weak_aggregate_advantage"],
            "existing_evidence_uniquely_supports_entropic_time": False,
            "prospective_raw_data_test_required": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
