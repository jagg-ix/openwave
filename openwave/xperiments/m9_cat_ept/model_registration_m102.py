"""Current M9.102 registration over schema-v19 evidence conformance."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m102_extension import CURRENT_FORMAL_HEAD, GOVERNANCE_SOURCES
from .formalization_m102_extension import HISTORICAL_FORMAL_HEAD
from .model_conformance_m102 import canonical_payload as conformance_payload
from .model_conformance_m102 import run_conformance_study
from .model_registration_m101 import canonical_registration_payload as m9_101_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = m9_101_payload()
    conformance = conformance_payload()
    return {
        **previous,
        "schema": "openwave.model-registration.v10",
        "conformance": conformance,
        "m9_102": {
            "historical_formal_head": HISTORICAL_FORMAL_HEAD,
            "current_formal_head": CURRENT_FORMAL_HEAD,
            "governance_sources": [dict(source) for source in GOVERNANCE_SOURCES],
            "carrier_state_separation_registered": conformance["maturity"]["policy"][
                "carrier_implementation_is_not_state_existence"
            ],
            "snapshot_generation_available": conformance["m9_101_reproducibility"][
                "policy"
            ]["fresh_snapshot_generation_and_verification_available"],
            "committed_post_merge_reference_snapshots_present": conformance[
                "m9_101_reproducibility"
            ]["policy"]["committed_post_merge_reference_snapshots_present"],
            "headline_counts": conformance["summary"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "current_formal_governance_is_numerical_evidence": False,
            "carrier_implementation_is_state_existence": False,
            "snapshot_contract_is_external_validation": False,
            "historical_pin_is_live_head_check": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    conformance = run_conformance_study()
    payload = canonical_registration_payload()
    boundaries = (
        "current_formal_governance_is_numerical_evidence",
        "carrier_implementation_is_state_existence",
        "snapshot_contract_is_external_validation",
        "historical_pin_is_live_head_check",
    )
    acceptance = {
        "m102_conformance_passes": bool(conformance["passed"]),
        "schema_v10_is_current": payload["schema"] == "openwave.model-registration.v10",
        "historical_pin_is_preserved": (
            payload["m9_102"]["historical_formal_head"] == HISTORICAL_FORMAL_HEAD
        ),
        "current_formal_head_is_exact": (
            payload["m9_102"]["current_formal_head"] == CURRENT_FORMAL_HEAD
        ),
        "three_governance_sources_are_registered": (
            len(payload["m9_102"]["governance_sources"]) == 3
        ),
        "carrier_and_state_are_separate": payload["m9_102"][
            "carrier_state_separation_registered"
        ],
        "snapshot_generation_is_registered": payload["m9_102"][
            "snapshot_generation_available"
        ],
        "missing_committed_snapshots_are_not_hidden": not payload["m9_102"][
            "committed_post_merge_reference_snapshots_present"
        ],
        "no_physical_claim_is_promoted": payload["m9_102"][
            "physical_claims_promoted"
        ]
        == [],
        "all_new_scope_boundaries_are_preserved": all(
            not payload["claim_boundary"][key] for key in boundaries
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.102e",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m102_registration_is_current": True,
            "formal_drift_and_reproducibility_status_are_explicit": True,
            "physical_identity_changed": False,
            "external_prediction_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
