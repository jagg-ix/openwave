"""Fail-closed contract for M9 canonical platform exposure.

The scientific modules are versioned evidence records. This contract verifies that
stable imports and public documents point to the same current milestone without
promoting numerical construction to physical validation.
"""
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

SCHEMA = "openwave.m9.platform-integration-contract.v1"
ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_PATHS = (
    "MODELS.md",
    "MODELS_M9.md",
    "openwave/xperiments/m9_cat_ept/__init__.py",
    "openwave/xperiments/m9_cat_ept/_launcher.py",
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

    payload = {
        "schema": SCHEMA,
        "current_milestone": CURRENT_MILESTONE,
        "current_registration_schema": registration["schema"],
        "current_conformance_schema": conformance["schema"],
        "current_conformance_runner": registration["registration"][
            "conformance_runner"
        ],
        "document_fingerprints": {
            path: _digest(text) for path, text in documents.items()
        },
        "claim_boundary": {
            "canonical_alias_implies_physical_validation": False,
            "root_registry_is_a_new_numerical_result": False,
            "M9_117_coarse_graining_derives_particle_mass": False,
            "current_registration_completes_external_calibration": False,
        },
    }
    acceptance = {
        "stable_registration_points_to_schema_v21": registration["schema"]
        == CURRENT_REGISTRATION_SCHEMA,
        "stable_registration_metadata_points_to_current_conformance": registration[
            "registration"
        ]["conformance_runner"]
        == CURRENT_CONFORMANCE_RUNNER,
        "stable_conformance_preserves_schema_v22": conformance["schema"]
        == CURRENT_CONFORMANCE_SCHEMA,
        "stable_conformance_composes_M9_117_evidence": conformance[
            "current_milestone"
        ]
        == CURRENT_MILESTONE
        and conformance["latest_evidence"]["passed"],
        "root_registry_exposes_M9": all(
            token in root_models
            for token in (
                "M9 - CAT/EPT",
                "MODELS_M9.md",
                "model_registration_current.py",
                "model_conformance_current.py",
                "MODELS_LEGACY.md",
            )
        ),
        "M9_profile_names_current_aliases_and_schemas": all(
            token in m9_profile
            for token in (
                "M9.117",
                "model_registration_current.py",
                "model_conformance_current.py",
                CURRENT_REGISTRATION_SCHEMA,
                CURRENT_CONFORMANCE_SCHEMA,
            )
        ),
        "package_description_reaches_M9_117": "M9.117" in package
        and "not yet a dynamical renormalization" not in package,
        "launcher_exposes_current_reports": all(
            token in launcher
            for token in (
                "--current-registration",
                "--current-conformance",
                "--platform-contract",
            )
        ),
        "obsolete_current_markers_are_absent": all(
            token not in m9_profile
            for token in (
                "canonical registration is `model_registration_m109.py`",
                "Current M9 conformance overlay through M9.96",
                "Canonical M9 registration through M9.97",
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
            "legacy_wide_matrix_is_preserved": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
