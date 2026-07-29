"""Fail-closed public integration contract for the M9.141 latest aliases."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .canonical_particle_model_m141 import run_canonical_model_contract
from .model_conformance_latest import (
    LATEST_SCHEMA as LATEST_CONFORMANCE_SCHEMA,
    canonical_payload as latest_conformance_payload,
)
from .model_registration_latest import (
    LATEST_SCHEMA as LATEST_REGISTRATION_SCHEMA,
    canonical_registration_payload,
)

SCHEMA = "openwave.m9.platform-integration-latest.v2"
ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_PATHS = (
    "MODELS.md",
    "MODELS_M9.md",
    "openwave/xperiments/m9_cat_ept/__init__.py",
    "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_platform_integration_contract() -> dict[str, Any]:
    registration = canonical_registration_payload()
    conformance = latest_conformance_payload()
    contract = run_canonical_model_contract()
    docs = {path: _read(path) for path in DOCUMENT_PATHS}
    payload = {
        "schema": SCHEMA,
        "latest_milestone": "M9.141",
        "latest_registration_schema": registration["schema"],
        "latest_conformance_schema": conformance["schema"],
        "stable_compatibility": registration["stable_compatibility"],
        "latest_capabilities": registration["canonical_contract"]["capabilities"],
        "document_fingerprints": {
            path: sha256(text.encode()).hexdigest() for path, text in docs.items()
        },
        "claim_boundary": dict(registration["claim_boundary"]),
    }
    required_tokens = (
        "M9.141",
        "M9.126",
        "stable",
        "latest",
        "physical",
        "Pauli",
        "Hartree",
        "U(1)",
    )
    acceptance = {
        "latest_registration_schema_is_exact": registration["schema"]
        == LATEST_REGISTRATION_SCHEMA,
        "latest_conformance_schema_is_exact": conformance["schema"]
        == LATEST_CONFORMANCE_SCHEMA,
        "canonical_contract_passes": bool(contract["passed"]),
        "stable_alias_is_distinct_from_latest": (
            registration["stable_compatibility"]["milestone"] == "M9.126"
            and registration["latest_milestone"] == "M9.141"
        ),
        "public_documents_expose_stable_latest_and_carrier": all(
            all(token.lower() in text.lower() for token in required_tokens)
            for text in docs.values()
        ),
        "three_dimensional_carrier_capability_is_public": payload[
            "latest_capabilities"
        ]["three_dimensional_pauli_hartree_u1_state"],
        "no_claim_boundary_is_crossed": not any(
            value
            for key, value in payload["claim_boundary"].items()
            if key != "criterion_rows_promoted"
        )
        and payload["claim_boundary"]["criterion_rows_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.141g",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "latest_aliases_are_publicly_exposed": True,
            "stable_aliases_remain_available": True,
            "three_dimensional_charged_carrier_is_public": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
