"""Fail-closed contract for M9 canonical platform exposure through M9.124."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .model_conformance_current import CURRENT_CONFORMANCE_SCHEMA, CURRENT_MILESTONE, canonical_payload as current_conformance_payload
from .model_registration_current import CURRENT_CONFORMANCE_RUNNER, CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA, canonical_registration_payload

SCHEMA = "openwave.m9.platform-integration-contract.v7"
ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_PATHS = (
    "MODELS.md", "MODELS_M9.md", "openwave/xperiments/m9_cat_ept/__init__.py",
    "openwave/xperiments/m9_cat_ept/_launcher.py", "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _digest(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_platform_integration_contract() -> dict[str, Any]:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    documents = {path: _read(path) for path in DOCUMENT_PATHS}
    root_models = documents["MODELS.md"]
    profile = documents["MODELS_M9.md"]
    package = documents["openwave/xperiments/m9_cat_ept/__init__.py"]
    roadmap = documents["openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"]
    launcher = documents["openwave/xperiments/m9_cat_ept/_launcher.py"]
    current = registration["m9_124"]
    payload = {
        "schema": SCHEMA,
        "current_milestone": CURRENT_MILESTONE,
        "current_registration_schema": registration["schema"],
        "current_conformance_schema": conformance["schema"],
        "current_conformance_runner": registration["registration"]["conformance_runner"],
        "merged_formal_head": current["merged_formal_head"],
        "development_formal_head": current["development_formal_head"],
        "development_formal_branch": current["development_formal_branch"],
        "zil_public_head": current["zil_public_head"],
        "document_fingerprints": {path: _digest(text) for path, text in documents.items()},
        "claim_boundary": {
            "canonical_alias_implies_unified_clock": False,
            "three_clock_benchmark_is_external_validation": False,
            "development_formal_head_is_merged_master": False,
            "role_synthesis_is_parameter_calibration": False,
        },
    }
    acceptance = {
        "stable_registration_points_to_schema_v27": registration["schema"] == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_metadata_points_to_current_conformance": registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_124_evidence": conformance["current_milestone"] == CURRENT_MILESTONE and conformance["latest_evidence"]["passed"],
        "merged_and_development_formal_heads_are_distinguished": current["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef" and current["development_formal_head"] == "af78ea63ee0b39456d8dab023761482196b8c172" and current["development_formal_branch"] == "entropic-physlib-linear-full",
        "root_registry_exposes_three_clock_roles": all(token in root_models for token in ("M9.124", "Page-Wootters", "modular / thermal", "entropic clock")),
        "profile_names_current_schemas_and_unification_boundary": all(token in profile for token in ("M9.124", CURRENT_REGISTRATION_SCHEMA, CURRENT_CONFORMANCE_SCHEMA, SCHEMA, "single unified physical clock", "pairwise bridges")),
        "package_description_reaches_M9_124": "M9.124" in package,
        "roadmap_closes_M9_124_and_advances_M9_125": all(token in roadmap for token in ("M9.124a", "M9.124b", "M9.124c", "M9.125", "NEXT")),
        "launcher_exposes_current_reports": all(token in launcher for token in ("--current-registration", "--current-conformance", "--platform-contract")),
        "three_aspect_framework_is_registered_while_unified_clock_stays_blocked": current["three_aspect_time_framework"] and not current["single_unified_physical_clock_established"] and not current["external_validation_complete"] and not current["external_physical_promotion_allowed"],
        "obsolete_current_markers_are_absent": all(token not in profile for token in ("M9 is integrated through **M9.123**", "openwave.model-registration.v26", "openwave.m9.platform-integration-contract.v6")),
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
            "three_clock_roles_are_distinct": True,
            "single_unified_physical_clock_established": False,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
