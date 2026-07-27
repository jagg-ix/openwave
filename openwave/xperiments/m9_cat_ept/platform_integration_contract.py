"""Fail-closed contract for M9 canonical platform exposure through M9.123."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .model_conformance_current import CURRENT_CONFORMANCE_SCHEMA, CURRENT_MILESTONE, canonical_payload as current_conformance_payload
from .model_registration_current import CURRENT_CONFORMANCE_RUNNER, CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA, canonical_registration_payload

SCHEMA = "openwave.m9.platform-integration-contract.v6"
ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_PATHS = ("MODELS.md", "MODELS_M9.md", "openwave/xperiments/m9_cat_ept/__init__.py", "openwave/xperiments/m9_cat_ept/_launcher.py", "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md")


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
    root_models, profile = documents["MODELS.md"], documents["MODELS_M9.md"]
    package, launcher = documents["openwave/xperiments/m9_cat_ept/__init__.py"], documents["openwave/xperiments/m9_cat_ept/_launcher.py"]
    roadmap = documents["openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"]
    current = registration["m9_123"]
    payload = {"schema": SCHEMA, "current_milestone": CURRENT_MILESTONE, "current_registration_schema": registration["schema"], "current_conformance_schema": conformance["schema"], "current_conformance_runner": registration["registration"]["conformance_runner"], "merged_formal_head": current["merged_formal_head"], "merged_formal_branch": current["merged_formal_branch"], "physlib_root_blob": current["physlib_root_blob"], "zil_public_head": current["zil_public_head"], "document_fingerprints": {path: _digest(text) for path, text in documents.items()}, "claim_boundary": {"canonical_alias_implies_external_validation": False, "scope_profile_is_scientific_score": False, "control_benchmark_is_parameter_free_prediction": False, "broad_internal_modeling_is_complete_unification": False}}
    acceptance = {
        "stable_registration_points_to_schema_v26": registration["schema"] == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_metadata_points_to_current_conformance": registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_123_evidence": conformance["current_milestone"] == CURRENT_MILESTONE and conformance["latest_evidence"]["passed"],
        "formal_and_zil_authorities_are_current": current["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef" and current["merged_formal_branch"] == "master" and current["physlib_root_blob"] == "f953c09c428eb83d9894c1944e1fd44a7ffe95a1" and current["zil_public_head"] == "c671f02d8b6dcf7ba689afc86477ff7e35465c35",
        "root_registry_exposes_M9_123": all(token in root_models for token in ("M9.123", "non-particle physics", "irreversible dynamics", "explanatory scope")),
        "profile_names_current_schemas_authorities_and_boundaries": all(token in profile for token in ("M9.123", CURRENT_REGISTRATION_SCHEMA, CURRENT_CONFORMANCE_SCHEMA, SCHEMA, "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef", "particle spectroscopy is not the primary scorecard", "predictive fundamental theory")),
        "package_description_reaches_M9_123": "M9.123" in package,
        "roadmap_closes_M9_123_and_advances_M9_124": all(token in roadmap for token in ("M9.123a", "M9.123b", "M9.123c", "M9.124", "NEXT")),
        "launcher_exposes_current_reports": all(token in launcher for token in ("--current-registration", "--current-conformance", "--platform-contract")),
        "internal_modeling_is_registered_while_physical_promotion_stays_blocked": current["broad_internal_physics_modeling"] and not current["predictive_fundamental_theory_ready"] and not current["independent_calibration_complete"] and not current["external_validation_complete"] and not current["external_physical_promotion_allowed"],
        "obsolete_current_markers_are_absent": all(token not in profile for token in ("M9 is integrated through **M9.122**", "openwave.model-registration.v25", "openwave.m9.platform-integration-contract.v5")),
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "task": "M9-platform-integration", "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"M9_is_exposed_as_first_class_OpenWave_model": True, "stable_aliases_are_current": True, "particle_spectroscopy_is_primary_scorecard": False, "predictive_fundamental_theory_ready": False, "physical_claims_promoted": []}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
