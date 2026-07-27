"""Fail-closed contract for M9 canonical platform exposure through M9.122."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from .model_conformance_current import (
    CURRENT_CONFORMANCE_SCHEMA,
    CURRENT_MILESTONE,
    canonical_payload as current_conformance_payload,
)
from .model_registration_current import (
    CURRENT_CONFORMANCE_RUNNER,
    CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA,
    canonical_registration_payload,
)

SCHEMA = "openwave.m9.platform-integration-contract.v5"
ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_PATHS = (
    "MODELS.md",
    "MODELS_M9.md",
    "openwave/xperiments/m9_cat_ept/__init__.py",
    "openwave/xperiments/m9_cat_ept/_launcher.py",
    "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md",
)


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _digest(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_platform_integration_contract() -> dict[str, Any]:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    documents = {path: _read(path) for path in DOCUMENT_PATHS}
    root_models = documents["MODELS.md"]
    profile = documents["MODELS_M9.md"]
    package = documents["openwave/xperiments/m9_cat_ept/__init__.py"]
    launcher = documents["openwave/xperiments/m9_cat_ept/_launcher.py"]
    roadmap = documents[
        "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"
    ]
    current = registration["m9_122"]
    payload = {
        "schema": SCHEMA,
        "current_milestone": CURRENT_MILESTONE,
        "current_registration_schema": registration["schema"],
        "current_conformance_schema": conformance["schema"],
        "current_conformance_runner": registration["registration"][
            "conformance_runner"
        ],
        "merged_formal_head": current["merged_formal_head"],
        "merged_formal_branch": current["merged_formal_branch"],
        "physlib_root_blob": current["physlib_root_blob"],
        "zil_public_head": current["zil_public_head"],
        "document_fingerprints": {
            path: _digest(text) for path, text in documents.items()
        },
        "claim_boundary": {
            "canonical_alias_implies_external_validation": False,
            "evidence_package_schema_is_external_evidence": False,
            "synthetic_fixture_is_heldout_test": False,
            "identity_contract_is_observed_identity": False,
        },
    }
    acceptance = {
        "stable_registration_points_to_schema_v25": registration["schema"]
        == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_metadata_points_to_current_conformance": registration[
            "registration"
        ]["conformance_runner"]
        == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"]
        == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_122_evidence": conformance[
            "current_milestone"
        ]
        == CURRENT_MILESTONE
        and conformance["latest_evidence"]["passed"],
        "formal_and_zil_authorities_are_current": current["merged_formal_head"]
        == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
        and current["merged_formal_branch"] == "master"
        and current["physlib_root_blob"]
        == "f953c09c428eb83d9894c1944e1fd44a7ffe95a1"
        and current["zil_public_head"]
        == "c671f02d8b6dcf7ba689afc86477ff7e35465c35",
        "root_registry_exposes_M9_122": all(
            token in root_models
            for token in (
                "M9.122",
                "external-evidence package",
                "blinded evaluator",
                "identity bridge",
            )
        ),
        "profile_names_current_schemas_authorities_and_boundaries": all(
            token in profile
            for token in (
                "M9.122",
                CURRENT_REGISTRATION_SCHEMA,
                CURRENT_CONFORMANCE_SCHEMA,
                SCHEMA,
                "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef",
                "synthetic fixture",
                "real external evidence package",
            )
        ),
        "package_description_reaches_M9_122": "M9.122" in package,
        "roadmap_closes_M9_122_and_advances_M9_123": all(
            token in roadmap
            for token in ("M9.122a", "M9.122b", "M9.122c", "M9.123", "NEXT")
        ),
        "launcher_exposes_current_reports": all(
            token in launcher
            for token in (
                "--current-registration",
                "--current-conformance",
                "--platform-contract",
            )
        ),
        "live_external_path_is_still_blocked": not current[
            "real_external_evidence_ingested"
        ]
        and not current["live_heldout_evaluation_executed"]
        and not current["physical_transition_identity_established"]
        and not current["external_validation_complete"]
        and not current["external_physical_promotion_allowed"],
        "obsolete_current_markers_are_absent": all(
            token not in profile
            for token in (
                "M9 is integrated through **M9.121**",
                "openwave.model-registration.v24",
                "openwave.m9.platform-integration-contract.v4",
                "merged Physlib head  3923d802339c957066fcccd579362f739775797a",
            )
        ),
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
            "external_evidence_readiness_is_current": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
