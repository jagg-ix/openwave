"""Latest integrated M9 registration; stable M9.126 aliases remain unchanged."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .canonical_particle_model_m140 import (
    MILESTONE,
    SCHEMA as CONTRACT_SCHEMA,
    canonical_payload as canonical_contract_payload,
    run_canonical_model_contract,
)
from .model_registration_current import (
    CURRENT_MILESTONE as STABLE_MILESTONE,
    CURRENT_SCHEMA as STABLE_SCHEMA,
    canonical_registration_payload as stable_registration_payload,
)

LATEST_SCHEMA = "openwave.model-registration.latest.v1"
LATEST_MODULE = "openwave.xperiments.m9_cat_ept.model_registration_latest"
LATEST_CONFORMANCE_RUNNER = (
    "openwave.xperiments.m9_cat_ept.model_conformance_latest:run_conformance_study"
)


def canonical_registration_payload() -> dict[str, Any]:
    stable = stable_registration_payload()
    contract = canonical_contract_payload()
    return {
        "schema": LATEST_SCHEMA,
        "model_id": "M9",
        "model": "CAT/EPT Entropic Particle Dynamics",
        "latest_milestone": MILESTONE,
        "stable_compatibility": {
            "milestone": STABLE_MILESTONE,
            "schema": STABLE_SCHEMA,
            "module": "openwave.xperiments.m9_cat_ept.model_registration_current",
            "payload_schema": stable["schema"],
        },
        "latest_registration": {
            **stable["registration"],
            "conformance_runner": LATEST_CONFORMANCE_RUNNER,
            "canonical_model_api": contract["canonical_api"],
            "canonical_contract": (
                "openwave.xperiments.m9_cat_ept."
                "canonical_particle_model_m140:run_canonical_model_contract"
            ),
            "latest_module": LATEST_MODULE,
        },
        "canonical_contract": {
            "schema": CONTRACT_SCHEMA,
            "milestone": contract["milestone"],
            "components": contract["components"],
            "action_term_map": contract["action_term_map"],
            "next_model_gates": contract["next_model_gates"],
        },
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    contract = run_canonical_model_contract()
    acceptance = {
        "latest_milestone_is_M9_140": payload["latest_milestone"] == "M9.140",
        "stable_M9_126_alias_is_preserved": (
            payload["stable_compatibility"]["milestone"] == "M9.126"
            and payload["stable_compatibility"]["schema"]
            == "openwave.model-registration.v29"
        ),
        "canonical_contract_passes": bool(contract["passed"]),
        "latest_registration_points_to_latest_conformance": (
            payload["latest_registration"]["conformance_runner"]
            == LATEST_CONFORMANCE_RUNNER
        ),
        "canonical_api_is_registered": payload["latest_registration"][
            "canonical_model_api"
        ].endswith(":CanonicalCatEptModel"),
        "physical_identity_remains_unassigned": (
            payload["latest_registration"]["physical_identity_default"] is None
            and not payload["claim_boundary"]["physical_particle_identity"]
        ),
        "criterion_rows_are_not_promoted": payload["claim_boundary"][
            "criterion_rows_promoted"
        ]
        == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.140b",
        "fingerprint": fingerprint(payload),
        "contract_fingerprint": contract["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "latest_registration_is_available": True,
            "stable_current_alias_is_not_rewritten": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
