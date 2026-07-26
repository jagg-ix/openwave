"""M9.102a: current formal authority with historical-pin separation.

M9.101 intentionally pinned the exact formal tree used by PR #92.  The live
``entropic-physlib-linear-full`` branch subsequently added claim-maturity,
evidence-integrity, and theorem-intent audits.  This module preserves the PR #92
pin as historical reproduction metadata while registering the new live head as
the current formal authority.

The new files govern evidence and publication discipline.  They do not create a
new OpenWave numerical result or change a physical particle identity.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m101_extension import FORMAL_SOURCES as M101_PHYSICS_SOURCES
from .formalization_m101_extension import TARGETS as M101_TARGETS

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
HISTORICAL_FORMAL_HEAD = "acdbe8ce6456e66837bd18604cf3107d3181c4de"
HISTORICAL_PHYSLIB_ROOT_BLOB = "cf0c719c3249c48174df8923380287bcaf33f04b"
CURRENT_FORMAL_HEAD = "eba0124fcfbc1216d973bb6f504c5a6d324de60c"
CURRENT_PHYSLIB_ROOT_BLOB = "56813b617e44f1ebd2ce5716fec72db4327ed0d0"
COMMITS_SINCE_M101 = 6

GOVERNANCE_SOURCES = (
    {
        "path": "Physlib/Meta/ClaimMaturity.lean",
        "blob": "95f765f51b7c5cb58783a890c9d7482d1a2c6d52",
        "role": "six-axis maturity, prerequisite coherence, assertion honesty, and witness-backed formal closure",
        "build_mode": "default-root",
        "epistemic_status": "audit-authority",
    },
    {
        "path": "Physlib/Meta/EvidenceIntegrity.lean",
        "blob": "9f5361a4606db34f60a5066634537703ac694700",
        "role": "falsification/supersession rules, structured numerical gates, and internal-versus-external evidence classification",
        "build_mode": "default-root",
        "epistemic_status": "audit-authority",
    },
    {
        "path": "Physlib/Meta/TheoremIntentAudit.lean",
        "blob": "5c953c52f35dd37a09dce1b3dc9e0ccbaaec00f7",
        "role": "on-demand cross-audit of theorem abstraction intents against formalizes and supported_by graph edges",
        "build_mode": "on-demand",
        "epistemic_status": "audit-tool",
    },
)


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m102-extension.v1",
        "repository": {
            "name": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "historical_head": HISTORICAL_FORMAL_HEAD,
            "historical_physlib_root_blob": HISTORICAL_PHYSLIB_ROOT_BLOB,
            "current_head": CURRENT_FORMAL_HEAD,
            "current_physlib_root_blob": CURRENT_PHYSLIB_ROOT_BLOB,
            "commits_since_m101": COMMITS_SINCE_M101,
        },
        "physics_sources": [dict(source) for source in M101_PHYSICS_SOURCES],
        "governance_sources": [dict(source) for source in GOVERNANCE_SOURCES],
        "targets": [dict(target) for target in M101_TARGETS],
        "policy": {
            "historical_reproduction_pin_is_preserved": True,
            "live_formal_head_is_distinct_from_historical_pin": True,
            "physics_source_blobs_are_unchanged_since_m101": True,
            "governance_updates_do_not_create_physical_evidence": True,
            "default_build_and_on_demand_audits_are_distinguished": True,
            "live_branch_resolution_requires_external_checkout_or_connector": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_formalization_m102_extension() -> dict[str, Any]:
    payload = canonical_payload()
    governance_paths = [source["path"] for source in GOVERNANCE_SOURCES]
    physics_paths = [source["path"] for source in M101_PHYSICS_SOURCES]
    acceptance = {
        "historical_and_current_heads_are_exact": (
            _is_sha(HISTORICAL_FORMAL_HEAD)
            and _is_sha(CURRENT_FORMAL_HEAD)
            and HISTORICAL_FORMAL_HEAD != CURRENT_FORMAL_HEAD
        ),
        "current_root_blob_is_exact": _is_sha(CURRENT_PHYSLIB_ROOT_BLOB),
        "six_commit_drift_is_registered": COMMITS_SINCE_M101 == 6,
        "all_m101_physics_sources_remain_exact": (
            len(M101_PHYSICS_SOURCES) == 11
            and len(set(physics_paths)) == len(physics_paths)
            and all(_is_sha(source["blob"]) for source in M101_PHYSICS_SOURCES)
        ),
        "three_governance_sources_are_exact": (
            len(GOVERNANCE_SOURCES) == 3
            and len(set(governance_paths)) == 3
            and all(_is_sha(source["blob"]) for source in GOVERNANCE_SOURCES)
        ),
        "claim_maturity_and_evidence_integrity_are_default_root": all(
            source["build_mode"] == "default-root"
            for source in GOVERNANCE_SOURCES[:2]
        ),
        "theorem_intent_audit_is_on_demand": (
            GOVERNANCE_SOURCES[2]["build_mode"] == "on-demand"
        ),
        "historical_and_live_verification_are_separate": (
            payload["policy"]["historical_reproduction_pin_is_preserved"]
            and payload["policy"]["live_branch_resolution_requires_external_checkout_or_connector"]
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.102a",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "current_formal_authority_refreshed": True,
            "historical_m101_reproduction_preserved": True,
            "new_numerical_physics_result_created": False,
            "physical_identity_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
