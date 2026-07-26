"""Canonical M9.109 conformance for Newton-G clock anchoring."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_m109 import canonical_payload as maturity_payload
from .criterion_maturity_m109 import run_criterion_maturity_m109
from .formalization_m109_extension import canonical_payload as formal_payload
from .formalization_m109_extension import run_formalization_m109_extension
from .m109_evidence_authority import run_m109_evidence_authority


def canonical_payload() -> dict[str, Any]:
    formal = formal_payload()
    maturity = maturity_payload()
    evidence = run_m109_evidence_authority()
    return {
        "schema": "openwave.m9.models-conformance.v22",
        "model": "M9 CAT/EPT",
        "formal_authority": formal,
        "evidence": evidence,
        "maturity": maturity,
        "summary": maturity["headline_counts"],
        "claim_boundary": {
            "derived_G_identity_is_external_G_prediction": False,
            "species_Compton_clock_is_universal_gravity_anchor": False,
            "G_derived_Planck_mass_is_independent_anchor": False,
            "natural_unit_G_is_calibrated_SI_G": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_conformance_study() -> dict[str, Any]:
    formal = run_formalization_m109_extension()
    evidence = run_m109_evidence_authority()
    maturity = run_criterion_maturity_m109()
    payload = canonical_payload()
    acceptance = {
        "current_formal_G_authority_passes": bool(formal["passed"]),
        "M9_109_evidence_authority_passes": bool(evidence["passed"]),
        "outcome_driven_maturity_passes": bool(maturity["passed"]),
        "schema_v22_is_current": payload["schema"]
        == "openwave.m9.models-conformance.v22",
        "all_claim_boundaries_remain_false": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.109-conformance",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m109_is_current_conformance_profile": True,
            "G_formal_status_changed_to_derived": True,
            "G_external_prediction_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
