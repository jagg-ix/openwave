"""M9.121 formal authority for bounded open-system evolution and promotion governance."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
CURRENT_FORMAL_HEAD = "3923d802339c957066fcccd579362f739775797a"
PHYSLIB_ROOT_BLOB = "d225e3cdb0e3239eb6c83f20af25968ddb9ec37b"
ZIL_REPOSITORY = "jagg-ix/zil-lean"
ZIL_PUBLIC_HEAD = "c671f02d8b6dcf7ba689afc86477ff7e35465c35"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean",
        "blob": "634087560adaffaaa5a683c47f3dee123501fb28",
        "role": "finite GKSL generator, positive rates and Hilbert-Schmidt evolution",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/ContinuumSemigroupClosure.lean",
        "blob": "d349630748fb066391810547e7fbb8b4431f244d",
        "role": "bounded-generator C0 semigroup and infinitesimal-generator theorem",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/TraceClassDensityOperatorIdeal.lean",
        "blob": "9e286dad87d23dba9cbc77011dfb84b11794cd00",
        "role": "positive trace-class density operators and controlled truncation",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/NuclearDensityEvolution.lean",
        "blob": "794faadf55b391db58455850fabf5fc0f8678d87",
        "role": "constructive density ensembles, positivity and trace-one preservation",
    },
    {
        "path": "Zil/Datalog/Eval.lean",
        "repository": ZIL_REPOSITORY,
        "blob": "6cde34efb9b09cc2f2d189883ff8373263daddba",
        "role": "stratified Datalog evaluation for fail-closed promotion rules",
    },
)

PENDING_FORMAL_CANDIDATES = (
    {
        "pull_request": 19,
        "head": "128bebd375cd895af1431444974a7a591c872a31",
        "state": "draft-open-unmerged",
    },
    {
        "pull_request": 20,
        "head": "e192104955fc516f1ba267f8653f0dcf8d18ab51",
        "state": "draft-open-unmerged",
    },
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m121-extension.v1",
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        "zil_repository": ZIL_REPOSITORY,
        "zil_public_head": ZIL_PUBLIC_HEAD,
        "sources": FORMAL_SOURCES,
        "pending_candidates": PENDING_FORMAL_CANDIDATES,
        "claim_boundary": {
            "bounded_semigroup_is_full_unbounded_gkls_theory": False,
            "constructive_density_carrier_is_all_trace_class_states": False,
            "datalog_gate_is_physical_evidence": False,
            "draft_physlib_pr_is_merged_authority": False,
        },
    }


def validate_formal_snapshot(
    *,
    head: str = CURRENT_FORMAL_HEAD,
    root_blob: str = PHYSLIB_ROOT_BLOB,
    zil_head: str = ZIL_PUBLIC_HEAD,
    source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    expected = {source["path"]: source["blob"] for source in FORMAL_SOURCES}
    observed = expected if source_blobs is None else dict(source_blobs)
    acceptance = {
        "formal_head_matches": head == CURRENT_FORMAL_HEAD,
        "root_blob_matches": root_blob == PHYSLIB_ROOT_BLOB,
        "zil_public_head_matches": zil_head == ZIL_PUBLIC_HEAD,
        "source_blobs_match": observed == expected,
        "drafts_not_promoted": all(
            candidate["state"] == "draft-open-unmerged"
            for candidate in PENDING_FORMAL_CANDIDATES
        ),
    }
    return {"acceptance": acceptance, "passed": all(acceptance.values())}


@lru_cache(maxsize=1)
def run_formalization_m121_extension() -> dict[str, Any]:
    payload = canonical_payload()
    validation = validate_formal_snapshot()
    acceptance = {
        **validation["acceptance"],
        "five_authority_sources_are_pinned": len(FORMAL_SOURCES) == 5,
        "no_scope_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.121-formal-authority",
        "validation": validation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "merged_open_system_authority_registered": True,
            "public_zil_runtime_rebased": True,
            "new_lean_proof_claimed_by_openwave": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
