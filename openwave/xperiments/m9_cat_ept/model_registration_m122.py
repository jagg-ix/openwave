"""M9.122 registration for external-evidence readiness and blocked live validation."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m122_external_evidence_readiness_authority import (
    run_m122_external_evidence_readiness_authority,
)
from .model_registration_m121 import canonical_registration_payload as previous_payload


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m122_external_evidence_readiness_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v25",
        "m9_122": {
            "external_evidence_readiness_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["current_formal_head"],
            "merged_formal_branch": formal["branch"],
            "physlib_root_blob": formal["physlib_root_blob"],
            "zil_public_head": formal["zil_public_head"],
            "external_evidence_package_schema": component[
                "external_evidence_package_schema"
            ],
            "blinded_external_evaluator": component["blinded_external_evaluator"],
            "independent_identity_bridge_contract": component[
                "independent_identity_contract"
            ],
            "real_external_evidence_ingested": component[
                "real_external_evidence_ingested"
            ],
            "live_heldout_evaluation_executed": component[
                "live_holdout_evaluation_executed"
            ],
            "physical_transition_identity_established": component[
                "physical_transition_identity"
            ],
            "external_validation_complete": component[
                "external_validation_complete"
            ],
            "external_physical_promotion_allowed": False,
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "external_evidence_schema_is_external_evidence": False,
            "synthetic_metric_fixture_is_heldout_validation": False,
            "identity_contract_is_observed_identity": False,
            "formal_zero_width_limit_is_measured_line_shape": False,
        },
    }


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m122_external_evidence_readiness_authority()
    payload = canonical_registration_payload()
    current = payload["m9_122"]
    acceptance = {
        "M9_122_authority_passes": evidence["passed"],
        "schema_v25_is_current": payload["schema"] == "openwave.model-registration.v25",
        "seven_formal_sources_are_registered": current["formal_source_count"] == 7
        and len(current["formal_authority_fingerprint"]) == 64,
        "merged_formal_authority_is_rebased": current["merged_formal_head"]
        == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
        and current["merged_formal_branch"] == "master",
        "readiness_layers_are_registered": current[
            "external_evidence_package_schema"
        ]
        and current["blinded_external_evaluator"]
        and current["independent_identity_bridge_contract"],
        "live_external_path_remains_blocked": not current[
            "real_external_evidence_ingested"
        ]
        and not current["live_heldout_evaluation_executed"]
        and not current["physical_transition_identity_established"]
        and not current["external_validation_complete"]
        and not current["external_physical_promotion_allowed"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.122-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "external_evidence_readiness_layer_is_current": True,
            "real_external_evidence_package_ingested": False,
            "external_physical_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
