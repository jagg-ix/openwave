"""Current M9 registration over schema-v21 conformance."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance_m108 import canonical_payload as conformance_payload
from .model_conformance_m108 import run_conformance_study
from .model_registration_m105 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    conformance = conformance_payload()
    components = conformance["evidence"]["components"]
    return {
        **previous,
        "schema": "openwave.model-registration.v12",
        "conformance": conformance,
        "m9_106_108": {
            "physlib_head": conformance["formal_authority"]["formal_repository"][
                "current_head"
            ],
            "zil_head": conformance["formal_authority"]["zil_repository"]["head"],
            "program_health": conformance["formal_authority"][
                "program_health_baseline"
            ],
            "nonlinear_gravity_campaign_registered": components[
                "nonlinear_gravity"
            ]["campaign_passed"],
            "nonlinear_gravity_constraint_gate": components[
                "nonlinear_gravity"
            ]["constraint_gate"],
            "coupled_sector_campaign_registered": components[
                "coupled_sectors"
            ]["campaign_passed"],
            "coupled_sector_gates": components["coupled_sectors"]["gates"],
            "candidate_state_campaign_registered": components[
                "candidate_states"
            ]["campaign_passed"],
            "candidate_state_gates": components["candidate_states"]["gates"],
            "headline_counts": conformance["summary"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "reduced_nonlinear_metric_is_general_einstein": False,
            "coupled_reduced_fields_are_standard_model": False,
            "stable_candidate_is_observed_particle": False,
            "program_health_passage_is_external_evidence": False,
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
    current = payload["m9_106_108"]
    boundaries = (
        "reduced_nonlinear_metric_is_general_einstein",
        "coupled_reduced_fields_are_standard_model",
        "stable_candidate_is_observed_particle",
        "program_health_passage_is_external_evidence",
    )
    acceptance = {
        "m108_conformance_passes": bool(conformance["passed"]),
        "schema_v12_is_current": payload["schema"]
        == "openwave.model-registration.v12",
        "three_campaigns_are_registered": current[
            "nonlinear_gravity_campaign_registered"
        ]
        and current["coupled_sector_campaign_registered"]
        and current["candidate_state_campaign_registered"],
        "all_subgates_are_explicit_booleans": isinstance(
            current["nonlinear_gravity_constraint_gate"], bool
        )
        and all(
            isinstance(value, bool)
            for value in current["coupled_sector_gates"].values()
        )
        and all(
            isinstance(value, bool)
            for value in current["candidate_state_gates"].values()
        ),
        "program_health_baseline_is_registered": current["program_health"][
            "untested_numerical"
        ]
        == 0,
        "no_physical_claim_is_promoted": current["physical_claims_promoted"]
        == [],
        "all_new_boundaries_are_preserved": all(
            not payload["claim_boundary"][key] for key in boundaries
        ),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.106--M9.108-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m108_registration_is_current": True,
            "physical_identity_changed": False,
            "external_validation_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
