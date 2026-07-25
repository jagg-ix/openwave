"""Canonical M9 registration with the M9.98 ZIL runtime upgrade.

The M9.97 registration remains available in ``model_registration_current.py``.
This overlay adds an independently versioned ZIL compiler/runtime authority and
changes no comparison-row status.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_registration_current import M9_REGISTRATION
from .model_registration_current import (
    canonical_registration_payload as m9_97_registration_payload,
)
from .model_registration_current import (
    run_model_registration_study as run_m9_97_registration_study,
)
from .zil_runtime_upgrade_current import run_zil_runtime_upgrade


def canonical_registration_payload() -> dict[str, Any]:
    previous = m9_97_registration_payload()
    runtime = run_zil_runtime_upgrade()
    return {
        **previous,
        "schema": "openwave.model-registration.v5",
        "zil_runtime_fingerprint": runtime["fingerprint"],
        "zil_runtime_revision": runtime["repository"],
        "zil_runtime_roots": runtime["root_contract"],
        "zil_runtime_coverage": {
            "runtime_sources": len(runtime["runtime_sources"]),
            "openwave_native_graphs": len(runtime["openwave_graphs"]),
            "historical_pins": len(runtime["historical_pins"]),
        },
        "m9_98": {
            "zil_runtime_upgrade_passed": runtime["passed"],
            "physlib_root": runtime["root_contract"][
                "physlib_embedded_formalization"
            ]["import"],
            "openwave_graph_root": runtime["root_contract"][
                "openwave_native_graph_tooling"
            ]["import"],
            "formal_or_physical_status_changed": runtime["decision"][
                "formal_or_physical_status_changed"
            ],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "zil_runtime_current": True,
            "zil_dual_root_contract_explicit": True,
            "zil_runtime_is_lean_proof_authority": False,
            "zil_upgrade_promotes_physical_criteria": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    previous = run_m9_97_registration_study()
    runtime = run_zil_runtime_upgrade()
    payload = canonical_registration_payload()
    expected_counts = {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    acceptance = {
        "m9_97_registration_remains_valid": bool(previous["passed"]),
        "zil_runtime_upgrade_passes": bool(runtime["passed"]),
        "zil_head_is_current": payload["zil_runtime_revision"]["head"]
        == "3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc",
        "dual_root_contract_is_registered": (
            payload["m9_98"]["physlib_root"] == "Zil"
            and payload["m9_98"]["openwave_graph_root"] == "Zil.Native"
        ),
        "runtime_source_and_graph_counts_are_exact": payload[
            "zil_runtime_coverage"
        ]
        == {
            "runtime_sources": 6,
            "openwave_native_graphs": 4,
            "historical_pins": 2,
        },
        "comparison_status_counts_are_unchanged": payload["conformance"][
            "status_counts"
        ]
        == expected_counts,
        "formalization_corpus_revision_is_unchanged": payload[
            "formalization_revision"
        ]
        == previous["formalization_revision"],
        "runtime_upgrade_changes_no_formal_or_physical_status": (
            not payload["m9_98"]["formal_or_physical_status_changed"]
            and not payload["claim_boundary"][
                "zil_upgrade_promotes_physical_criteria"
            ]
        ),
        "physical_identity_remains_unassigned": (
            M9_REGISTRATION.physical_identity_default is None
            and not payload["claim_boundary"]["physical_particle_identity"]
        ),
        "registration_fingerprint_is_deterministic": (
            registration_fingerprint(payload) == registration_fingerprint(payload)
        ),
    }
    return {
        **payload,
        "task": "M9.98",
        "registration_fingerprint": registration_fingerprint(payload),
        "component_results": {
            **previous["component_results"],
            "zil_runtime_upgrade_passed": runtime["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            **previous["decision"],
            "zil_runtime_upgraded": True,
            "dual_root_contract_registered": True,
            "historical_zil_pins_are_current_authority": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
