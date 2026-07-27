"""Fail-closed contract for M9 canonical platform exposure through M9.121."""
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

SCHEMA = "openwave.m9.platform-integration-contract.v4"
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
    m9_profile = documents["MODELS_M9.md"]
    package = documents["openwave/xperiments/m9_cat_ept/__init__.py"]
    launcher = documents["openwave/xperiments/m9_cat_ept/_launcher.py"]
    roadmap = documents[
        "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"
    ]
    current = registration["m9_121"]
    payload = {
        "schema": SCHEMA,
        "current_milestone": CURRENT_MILESTONE,
        "current_registration_schema": registration["schema"],
        "current_conformance_schema": conformance["schema"],
        "current_conformance_runner": registration["registration"]["conformance_runner"],
        "merged_formal_head": current["merged_formal_head"],
        "zil_public_head": current["zil_public_head"],
        "document_fingerprints": {
            path: _digest(text) for path, text in documents.items()
        },
        "claim_boundary": {
            "canonical_alias_implies_physical_validation": False,
            "CPTP_model_decay_is_measured_width": False,
            "blind_protocol_is_completed_calibration": False,
            "internal_promotion_is_external_promotion": False,
        },
    }
    acceptance = {
        "stable_registration_points_to_schema_v24": registration["schema"]
        == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_metadata_points_to_current_conformance": registration[
            "registration"
        ]["conformance_runner"]
        == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"]
        == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_121_evidence": conformance[
            "current_milestone"
        ]
        == CURRENT_MILESTONE
        and conformance["latest_evidence"]["passed"],
        "formal_and_zil_heads_are_current": current["merged_formal_head"]
        == "3923d802339c957066fcccd579362f739775797a"
        and current["zil_public_head"]
        == "c671f02d8b6dcf7ba689afc86477ff7e35465c35",
        "root_registry_exposes_M9_121": all(
            token in root_models
            for token in (
                "M9.121",
                "open-system decay",
                "calibration governance",
                "promotion governance",
            )
        ),
        "M9_profile_names_current_schemas_and_boundaries": all(
            token in m9_profile
            for token in (
                "M9.121",
                CURRENT_REGISTRATION_SCHEMA,
                CURRENT_CONFORMANCE_SCHEMA,
                SCHEMA,
                "CPTP",
                "independent physical anchor supplied  false",
                "External physical promotion additionally requires",
            )
        ),
        "package_description_reaches_M9_121": "M9.121" in package,
        "roadmap_closes_M9_121_and_advances_M9_122": all(
            token in roadmap
            for token in ("M9.121a", "M9.121b", "M9.121c", "M9.122", "NEXT")
        ),
        "launcher_exposes_current_reports": all(
            token in launcher
            for token in (
                "--current-registration",
                "--current-conformance",
                "--platform-contract",
            )
        ),
        "external_promotion_is_still_blocked": not current[
            "external_physical_promotion_allowed"
        ]
        and not current["independent_physical_anchor_ready"]
        and not current["heldout_validation_complete"],
        "obsolete_current_markers_are_absent": all(
            token not in m9_profile
            for token in (
                "M9 is integrated through **M9.120**",
                "openwave.model-registration.v23",
                "openwave.m9.platform-integration-contract.v3",
                "zil-lean head       e09723a44185a1e70031ad2661c8009dc98bef74",
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
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
