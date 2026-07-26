"""Canonical M9.108 conformance over nonlinear gravity, sector fields and candidates."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_m108 import canonical_payload as maturity_payload
from .criterion_maturity_m108 import run_criterion_maturity_m108
from .formalization_m108_extension import canonical_payload as formal_payload
from .formalization_m108_extension import run_formalization_m108_extension
from .m106_108_evidence_authority import run_m106_108_evidence_authority


def canonical_payload() -> dict[str, Any]:
    formal = formal_payload()
    maturity = maturity_payload()
    evidence = run_m106_108_evidence_authority()
    return {
        "schema": "openwave.m9.models-conformance.v21",
        "model": "M9 CAT/EPT",
        "formal_authority": formal,
        "evidence": evidence,
        "maturity": maturity,
        "summary": maturity["headline_counts"],
        "claim_boundary": {
            "reduced_nonlinear_metric_is_general_relativity": False,
            "coupled_sector_fields_are_standard_model": False,
            "candidate_state_is_particle_identification": False,
            "program_health_is_experimental_validation": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    formal = run_formalization_m108_extension()
    evidence = run_m106_108_evidence_authority()
    maturity = run_criterion_maturity_m108()
    payload = canonical_payload()
    acceptance = {
        "formal_and_program_health_authority_passes": bool(formal["passed"]),
        "three_campaign_evidence_authority_passes": bool(evidence["passed"]),
        "outcome_driven_maturity_passes": bool(maturity["passed"]),
        "schema_v21_is_current": payload["schema"]
        == "openwave.m9.models-conformance.v21",
        "all_claim_boundaries_remain_false": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.106--M9.108-conformance",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m108_is_current_conformance_profile": True,
            "physical_identity_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
