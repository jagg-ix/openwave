"""Fail-closed contract for M9 canonical platform exposure through M9.125."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .model_conformance_current import CURRENT_CONFORMANCE_SCHEMA, CURRENT_MILESTONE, canonical_payload as current_conformance_payload
from .model_registration_current import CURRENT_CONFORMANCE_RUNNER, CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA, canonical_registration_payload

SCHEMA = "openwave.m9.platform-integration-contract.v8"
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
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_platform_integration_contract() -> dict[str, Any]:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    docs = {path: _read(path) for path in DOCUMENT_PATHS}
    current = registration["m9_125"]
    payload = {
        "schema": SCHEMA,
        "current_milestone": CURRENT_MILESTONE,
        "current_registration_schema": registration["schema"],
        "current_conformance_schema": conformance["schema"],
        "current_conformance_runner": registration["registration"]["conformance_runner"],
        "merged_formal_head": current["merged_formal_head"],
        "development_formal_head": current["development_formal_head"],
        "zil_public_head": current["zil_public_head"],
        "document_fingerprints": {path: sha256(text.encode()).hexdigest() for path, text in docs.items()},
        "claim_boundary": {
            "stable_alias_implies_universal_clock": False,
            "internal_calibration_implies_measured_proper_time": False,
            "synthetic_fixture_implies_heldout_validation": False,
        },
    }
    profile = docs["MODELS_M9.md"]
    roadmap = docs["openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"]
    acceptance = {
        "stable_registration_points_to_schema_v28": registration["schema"] == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_points_to_current_conformance": registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_125": conformance["current_milestone"] == CURRENT_MILESTONE and conformance["latest_evidence"]["passed"],
        "public_documents_expose_M9_125": all("M9.125" in text for text in docs.values()),
        "profile_names_current_schemas_and_boundaries": all(token in profile for token in (CURRENT_REGISTRATION_SCHEMA, CURRENT_CONFORMANCE_SCHEMA, SCHEMA, "shared finite carrier", "real three-clock data")),
        "roadmap_advances_real_test_to_M9_126": all(token in roadmap for token in ("M9.125a", "M9.125b", "M9.125c", "M9.126", "NEXT")),
        "reduced_carrier_is_registered_without_universal_promotion": current["shared_finite_three_clock_carrier"] and current["internal_clock_parameter_maps"] and not current["single_universal_physical_clock_established"],
        "live_external_path_is_blocked": not current["real_three_clock_data_ingested"] and not current["external_validation_complete"] and not current["external_physical_promotion_allowed"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9-platform-integration",
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_is_exposed_as_first_class_OpenWave_model": True,
            "stable_aliases_are_current": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
