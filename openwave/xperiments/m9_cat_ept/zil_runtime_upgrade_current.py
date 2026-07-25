"""Current M9.98 ZIL authority including the migration graph itself.

The base runtime contract pins the three pre-upgrade OpenWave graphs.  This
versioned overlay additionally pins the self-describing M9.98 graph.  Its blob is
stored outside the graph to avoid an impossible self-hash fixed point.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .zil_runtime_upgrade import canonical_payload as base_payload
from .zil_runtime_upgrade import result_to_json
from .zil_runtime_upgrade import validate_zil_runtime_upgrade as validate_base

SELF_GRAPH = {
    "id": "m9-98-zil-runtime-upgrade",
    "path": (
        "openwave/xperiments/m9_cat_ept/research/zil/"
        "m9_98_zil_runtime_upgrade.zc"
    ),
    "blob": "7efb843b62c48087853cc83fead2e9fb8cdda33d",
    "runtime_root": "Zil.Native",
    "self_describing": True,
}


def canonical_payload() -> dict[str, Any]:
    previous = base_payload()
    return {
        **previous,
        "schema": "openwave.m9.zil-runtime-upgrade.v2",
        "openwave_graphs": [*previous["openwave_graphs"], dict(SELF_GRAPH)],
        "self_hash_policy": (
            "the migration graph declares its runtime role; its exact blob is "
            "pinned externally by this authority"
        ),
    }


def runtime_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(
            selected,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def validate_zil_runtime_upgrade(
    *,
    observed_head: str | None = None,
    observed_runtime_blobs: Mapping[str, str] | None = None,
    observed_graph_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    observed = None if observed_graph_blobs is None else dict(observed_graph_blobs)
    base_observed = None
    if observed is not None:
        base_observed = {
            item["path"]: observed.get(item["path"], "")
            for item in base_payload()["openwave_graphs"]
        }
    base = validate_base(
        observed_head=observed_head,
        observed_runtime_blobs=observed_runtime_blobs,
        observed_graph_blobs=base_observed,
    )
    self_blob = SELF_GRAPH["blob"] if observed is None else observed.get(
        SELF_GRAPH["path"]
    )
    errors = list(base["errors"])
    if self_blob != SELF_GRAPH["blob"]:
        errors.append(f"OpenWave ZIL graph drift detected: {SELF_GRAPH['path']}")
    payload = canonical_payload()
    acceptance = {
        **base["acceptance"],
        "base_runtime_contract_passes": bool(base["passed"]),
        "migration_graph_is_native_and_blob_pinned": (
            SELF_GRAPH["runtime_root"] == "Zil.Native"
            and len(SELF_GRAPH["blob"]) == 40
            and self_blob == SELF_GRAPH["blob"]
        ),
        "all_four_openwave_graphs_are_registered": len(payload["openwave_graphs"])
        == 4,
        "self_hash_policy_is_explicit": bool(payload["self_hash_policy"]),
        "validation_has_no_errors": not errors,
    }
    return {
        **payload,
        "fingerprint": runtime_fingerprint(),
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            **base["decision"],
            "migration_graph_is_current_authority_input": True,
        },
    }


@lru_cache(maxsize=1)
def run_zil_runtime_upgrade() -> dict[str, Any]:
    return validate_zil_runtime_upgrade()
