"""M9.98: current ZIL runtime and dual-root compatibility authority.

OpenWave previously carried two bootstrap/control-plane ZIL commit pins without
validating the runtime surface behind them.  Current ``zil-lean`` deliberately
exports two different roots:

* ``Zil`` is the PhysLib-facing clause-logic/Datalog compatibility surface;
* ``Zil.Native`` is the native knowledge, query, provenance, workflow, and
  authorization stack used by standalone graph tooling.

This module pins that split by exact commit and source blobs.  The imported
PhysLib formalization corpus and its 11 ZIL declaration/status graphs remain
separate evidence: upgrading the runtime does not promote a mathematical or
physical claim.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

ZIL_REPOSITORY = "jagg-ix/zil-lean"
ZIL_BRANCH = "main"
CURRENT_ZIL_HEAD = "3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc"

HISTORICAL_ZIL_PINS = (
    {
        "head": "f39758f85ee6300b8060e4f8ea1ecf344ed32c96",
        "role": "M9.63 installation-bootstrap-era evidence pin",
    },
    {
        "head": "64462a3c5e2ffb51a7b226675491cc3a9b156a8d",
        "role": "M9.62 durable-control-event-era evidence pin",
    },
)

ZIL_RUNTIME_SOURCES = (
    {
        "id": "physlib-facing-datalog-root",
        "path": "Zil.lean",
        "blob": "faf28e701e4a02781e410491a6d3daf5d47f8879",
        "root": "Zil",
        "role": (
            "PhysLib-facing Datalog root: attachments, embedded validation, "
            "Holds semantics, tactics, theorem intents, and file contracts"
        ),
    },
    {
        "id": "native-knowledge-root",
        "path": "Zil/Native.lean",
        "blob": "2e6c87a85ef2f80d2424c8251ffe524067e27dee",
        "root": "Zil.Native",
        "role": (
            "native knowledge stack: facts, rules, parser, query engine, "
            "provenance, workflow, authorization, and audit services"
        ),
    },
    {
        "id": "datalog-compatibility-aliases",
        "path": "Zil/Datalog/Compat.lean",
        "blob": "d72fd52996eb2418037ed329b97c280e2f187b1a",
        "root": "Zil",
        "role": "source-compatible Zil.Value/Program/Holds aliases for PhysLib",
    },
    {
        "id": "formalization-contract-runtime",
        "path": "Zil/Datalog/FormalizationContract.lean",
        "blob": "b5753801f2564f17a684a1d8da77bc3b024e7c0a",
        "root": "Zil",
        "role": (
            "executable abstraction-level, theorem-intent, file-contract, "
            "requirement, witness, and forbidden-substitute validation"
        ),
    },
    {
        "id": "dual-root-lake-build",
        "path": "lakefile.lean",
        "blob": "8dc0dd81f8c3d80192f9467792a617fde5ec24b5",
        "root": "Zil,Zil.Native",
        "role": "default package build includes both public roots",
    },
    {
        "id": "physlib-native-arc-example",
        "path": "examples/lean/06_PhyslibFormalizationArc.lean",
        "blob": "91ec7daf0dd351e5de480149b77eea903a472ea3",
        "root": "Zil.Native",
        "role": "real PhysLib formalization knowledge arc using the native engine",
    },
)

OPENWAVE_ZIL_GRAPHS = (
    {
        "id": "m9-94-95-formalization-spin-force",
        "path": (
            "openwave/xperiments/m9_cat_ept/research/zil/"
            "m9_94_95_formalization_spin_force.zc"
        ),
        "blob": "d2952ca95134e67ff3cf37a46df4d630e9eb0aa1",
        "runtime_root": "Zil.Native",
    },
    {
        "id": "m9-96-charged-source-force",
        "path": (
            "openwave/xperiments/m9_cat_ept/research/zil/"
            "m9_96_charged_source_force.zc"
        ),
        "blob": "19eef18ae3869c7165e1a7880e97e3702c9015b5",
        "runtime_root": "Zil.Native",
    },
    {
        "id": "m9-97-gauge-spinor-dynamics",
        "path": (
            "openwave/xperiments/m9_cat_ept/research/zil/"
            "m9_97_gauge_spinor_dynamics.zc"
        ),
        "blob": "261de47286a0c1c7c4c4369dd8b2973b813a50a8",
        "runtime_root": "Zil.Native",
    },
)

REQUIRED_DATALOG_CAPABILITIES = (
    "declaration_attachments",
    "embedded_validation",
    "holds_semantics",
    "zil_solve_and_zil_apply",
    "theorem_intents",
    "file_contracts",
    "abstraction_levels",
    "forbidden_substitutes",
)

REQUIRED_NATIVE_CAPABILITIES = (
    "facts_and_theorem_shaped_rules",
    "program_parser",
    "query_engine",
    "provenance_trace",
    "workflow",
    "authorization",
    "impact_analysis",
    "proof_and_theorem_audits",
)


def _is_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.zil-runtime-upgrade.v1",
        "repository": {
            "name": ZIL_REPOSITORY,
            "branch": ZIL_BRANCH,
            "head": CURRENT_ZIL_HEAD,
        },
        "historical_pins": [dict(item) for item in HISTORICAL_ZIL_PINS],
        "runtime_sources": [dict(item) for item in ZIL_RUNTIME_SOURCES],
        "root_contract": {
            "physlib_embedded_formalization": {
                "import": "Zil",
                "namespace": "Zil.Datalog",
                "capabilities": list(REQUIRED_DATALOG_CAPABILITIES),
            },
            "openwave_native_graph_tooling": {
                "import": "Zil.Native",
                "namespace": "Zil",
                "capabilities": list(REQUIRED_NATIVE_CAPABILITIES),
            },
            "roots_must_not_be_selected_implicitly": True,
        },
        "openwave_graphs": [dict(item) for item in OPENWAVE_ZIL_GRAPHS],
        "claim_boundary": {
            "lean_kernel_remains_proof_authority": True,
            "zil_runtime_is_orchestration_and_validation_authority": True,
            "runtime_upgrade_promotes_formal_claims": False,
            "runtime_upgrade_promotes_physical_criteria": False,
        },
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


def expected_runtime_blobs() -> dict[str, str]:
    return {str(item["path"]): str(item["blob"]) for item in ZIL_RUNTIME_SOURCES}


def expected_graph_blobs() -> dict[str, str]:
    return {str(item["path"]): str(item["blob"]) for item in OPENWAVE_ZIL_GRAPHS}


def validate_zil_runtime_upgrade(
    *,
    observed_head: str | None = None,
    observed_runtime_blobs: Mapping[str, str] | None = None,
    observed_graph_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    head = CURRENT_ZIL_HEAD if observed_head is None else observed_head
    runtime_blobs = (
        expected_runtime_blobs()
        if observed_runtime_blobs is None
        else dict(observed_runtime_blobs)
    )
    graph_blobs = (
        expected_graph_blobs()
        if observed_graph_blobs is None
        else dict(observed_graph_blobs)
    )
    errors: list[str] = []

    if head != CURRENT_ZIL_HEAD:
        errors.append("ZIL runtime head drift detected")
    for path, blob in expected_runtime_blobs().items():
        if runtime_blobs.get(path) != blob:
            errors.append(f"ZIL runtime source drift detected: {path}")
    for path, blob in expected_graph_blobs().items():
        if graph_blobs.get(path) != blob:
            errors.append(f"OpenWave ZIL graph drift detected: {path}")

    historical_heads = {str(item["head"]) for item in HISTORICAL_ZIL_PINS}
    source_ids = [str(item["id"]) for item in ZIL_RUNTIME_SOURCES]
    source_paths = [str(item["path"]) for item in ZIL_RUNTIME_SOURCES]
    graph_paths = [str(item["path"]) for item in OPENWAVE_ZIL_GRAPHS]

    acceptance = {
        "current_zil_repository_and_branch_are_pinned": (
            ZIL_REPOSITORY == "jagg-ix/zil-lean" and ZIL_BRANCH == "main"
        ),
        "current_zil_head_is_exact": head == CURRENT_ZIL_HEAD and _is_sha(head),
        "historical_pins_are_distinct_and_not_current": (
            len(historical_heads) == len(HISTORICAL_ZIL_PINS)
            and CURRENT_ZIL_HEAD not in historical_heads
            and all(_is_sha(value) for value in historical_heads)
        ),
        "runtime_source_registry_is_unique": (
            len(source_ids) == len(set(source_ids))
            and len(source_paths) == len(set(source_paths))
        ),
        "all_runtime_sources_are_blob_pinned": all(
            _is_sha(str(item["blob"])) for item in ZIL_RUNTIME_SOURCES
        ),
        "physlib_root_is_datalog_and_native_root_is_explicit": (
            canonical_payload()["root_contract"]["physlib_embedded_formalization"][
                "import"
            ]
            == "Zil"
            and canonical_payload()["root_contract"]["openwave_native_graph_tooling"][
                "import"
            ]
            == "Zil.Native"
        ),
        "both_roots_are_default_build_targets": any(
            item["id"] == "dual-root-lake-build"
            and item["root"] == "Zil,Zil.Native"
            for item in ZIL_RUNTIME_SOURCES
        ),
        "datalog_compatibility_and_contract_surfaces_are_pinned": {
            "datalog-compatibility-aliases",
            "formalization-contract-runtime",
        }.issubset(set(source_ids)),
        "all_openwave_zc_graphs_use_native_runtime": (
            len(graph_paths) == len(set(graph_paths))
            and all(
                item["runtime_root"] == "Zil.Native"
                for item in OPENWAVE_ZIL_GRAPHS
            )
        ),
        "observed_runtime_blobs_match": all(
            runtime_blobs.get(path) == blob
            for path, blob in expected_runtime_blobs().items()
        ),
        "observed_graph_blobs_match": all(
            graph_blobs.get(path) == blob
            for path, blob in expected_graph_blobs().items()
        ),
        "runtime_upgrade_promotes_no_claim_or_criterion": not canonical_payload()[
            "claim_boundary"
        ]["runtime_upgrade_promotes_physical_criteria"],
        "fingerprint_is_deterministic": runtime_fingerprint() == runtime_fingerprint(),
        "validation_has_no_errors": not errors,
    }
    return {
        **canonical_payload(),
        "fingerprint": runtime_fingerprint(),
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "zil_runtime_upgraded": not errors,
            "physlib_uses_datalog_compatibility_root": True,
            "openwave_graphs_use_native_root": True,
            "historical_pins_remain_auditable": True,
            "formal_or_physical_status_changed": False,
        },
    }


@lru_cache(maxsize=1)
def run_zil_runtime_upgrade() -> dict[str, Any]:
    return validate_zil_runtime_upgrade()


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
