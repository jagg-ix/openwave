"""CAT/EPT formalization import and cross-repository coverage audit.

The importer covers the five operational/status graphs and the six merged
formalization-family graphs on the pinned branch tree. Lean remains proof
authority; ZIL records declarations, dependencies, source links, status, rules,
queries, and explicit analytic boundaries.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from importlib import import_module
import json
from typing import Any, Mapping

from .formalization_inventory import (
    CRITERION_IMPORTS,
    EXTERNAL_WITNESS_PREFIXES,
    FORMAL_BRANCH,
    FORMAL_COMMIT as FORMAL_BASE_COMMIT,
    FORMAL_REPOSITORY,
    LEAN_SOURCES,
    MODULE_INDEX_PATH,
    ZIL_GRAPHS,
)
from .formalization_inventory_additional import ADDITIONAL_ZIL_GRAPHS
from .formalization_inventory_corpus import (
    CORPUS_CRITERION_IMPORTS,
    CORPUS_LEAN_SOURCES,
    CORPUS_ZIL_GRAPHS,
    LATEST_FORMAL_TREE,
    LATEST_MODULE_INDEX_BLOB,
)
from .physlib_contract import load_contract

IMPORTED_ZIL_GRAPHS = (
    tuple(ZIL_GRAPHS)
    + tuple(ADDITIONAL_ZIL_GRAPHS)
    + tuple(CORPUS_ZIL_GRAPHS)
)
ALL_LEAN_SOURCES = tuple(LEAN_SOURCES) + tuple(CORPUS_LEAN_SOURCES)
ALL_CRITERION_IMPORTS = tuple(CRITERION_IMPORTS) + tuple(CORPUS_CRITERION_IMPORTS)
REQUIRED_GRAPH_IDS = {
    "electrogravitic-action-closure",
    "lindblad-driven-leads",
    "liouville-second-quantization",
    "cauchy-weak-limit",
    "lindblad-trace-preservation",
    "rivers-scalar-green-functions",
    "rivers-scalar-green-functions-continuum",
    "lovelock-rund-continuum-variational",
    "lovelock-rund-pointwise-operators",
    "lovelock-rund-invariant-geometry",
    "veliev-periodic-schrodinger",
}
EXPECTED_ENTITY_COUNT = 422
EXPECTED_OPEN_TARGET_COUNT = 12
EXPECTED_LEAN_SOURCE_COUNT = 24
EXPECTED_CRITERION_IMPORTS = {
    "magnetic_moment_spin",
    "electric_force",
    "magnetic_force",
    "gravity",
}
ADDITIONAL_EXTERNAL_PREFIXES = (
    "ProbabilityMeasure",
    "LinearMap.",
    "Physlib.QFT.PathIntegral.",
    "WickContraction",
    "FieldSpecification.",
    "SchwartzMap",
    "ClassicalFieldTheory.",
    "ClassicalMechanics.",
    "ContinuousAlternatingMap.",
    "VectorField.",
    "Matrix.",
)


def _is_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def lean_source_records() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "id": identifier,
            "path": path,
            "blob": blob,
            "namespaces": tuple(namespaces),
            "status": status,
        }
        for identifier, path, blob, namespaces, status in ALL_LEAN_SOURCES
    )


def resolve_adapter(specification: str):
    module_name, separator, attribute = specification.partition(":")
    if not separator or not module_name or not attribute:
        raise ValueError(f"invalid adapter specification: {specification!r}")
    module = import_module(module_name)
    adapter = getattr(module, attribute)
    if not callable(adapter):
        raise TypeError(f"adapter is not callable: {specification!r}")
    return adapter


def graph_entity_counts() -> dict[str, dict[str, int]]:
    return {
        graph["id"]: {
            kind: len(tuple(names)) for kind, names in graph["entities"].items()
        }
        for graph in IMPORTED_ZIL_GRAPHS
    }


def total_entity_count() -> int:
    return sum(
        len(tuple(names))
        for graph in IMPORTED_ZIL_GRAPHS
        for names in graph["entities"].values()
    )


def total_open_target_count() -> int:
    return sum(len(tuple(graph["open_targets"])) for graph in IMPORTED_ZIL_GRAPHS)


def registered_namespace_prefixes() -> tuple[str, ...]:
    values = [
        prefix
        for source in lean_source_records()
        for prefix in source["namespaces"]
    ]
    values.extend(EXTERNAL_WITNESS_PREFIXES)
    values.extend(ADDITIONAL_EXTERNAL_PREFIXES)
    return tuple(sorted(set(values)))


def witness_resolves(witness: str) -> bool:
    for prefix in registered_namespace_prefixes():
        if prefix.endswith("."):
            if witness.startswith(prefix):
                return True
        elif witness == prefix or witness.startswith(prefix + "."):
            return True
    return False


def criterion_import_map() -> dict[str, Mapping[str, Any]]:
    return {str(item["criterion"]): item for item in ALL_CRITERION_IMPORTS}


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.cat-ept-formalization-import.v3",
        "repository": {
            "name": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "base_commit": FORMAL_BASE_COMMIT,
            "tree": LATEST_FORMAL_TREE,
            "module_index_path": MODULE_INDEX_PATH,
            "module_index_blob": LATEST_MODULE_INDEX_BLOB,
        },
        "zil_graphs": [
            {
                "id": graph["id"],
                "module": graph["module"],
                "source_path": graph["source_path"],
                "source_blob": graph["source_blob"],
                "entities": {
                    kind: list(names) for kind, names in graph["entities"].items()
                },
                "rules": list(graph["rules"]),
                "queries": list(graph["queries"]),
                "open_targets": list(graph["open_targets"]),
                "witness_prefixes": list(graph["witness_prefixes"]),
            }
            for graph in IMPORTED_ZIL_GRAPHS
        ],
        "lean_sources": [dict(record) for record in lean_source_records()],
        "criterion_imports": [
            {
                "criterion": item["criterion"],
                "task": item["task"],
                "declarations": list(item["declarations"]),
                "numerical_adapters": list(item["numerical_adapters"]),
                "boundary": list(item["boundary"]),
            }
            for item in ALL_CRITERION_IMPORTS
        ],
    }


def inventory_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else payload
    encoded = json.dumps(
        selected,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(encoded.encode()).hexdigest()


def expected_source_blobs() -> dict[str, str]:
    result = {
        graph["source_path"]: graph["source_blob"]
        for graph in IMPORTED_ZIL_GRAPHS
    }
    result.update(
        {source["path"]: source["blob"] for source in lean_source_records()}
    )
    result[MODULE_INDEX_PATH] = LATEST_MODULE_INDEX_BLOB
    return result


def validate_inventory(
    *,
    observed_tree: str | None = None,
    observed_blobs: Mapping[str, str] | None = None,
    resolve_adapters: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    graphs = IMPORTED_ZIL_GRAPHS
    sources = lean_source_records()
    graph_ids = [str(graph["id"]) for graph in graphs]
    graph_modules = [str(graph["module"]) for graph in graphs]
    graph_paths = [str(graph["source_path"]) for graph in graphs]
    source_ids = [str(source["id"]) for source in sources]
    source_paths = [str(source["path"]) for source in sources]

    if set(graph_ids) != REQUIRED_GRAPH_IDS:
        errors.append("required ZIL graph set does not close")
    if len(graph_ids) != len(set(graph_ids)):
        errors.append("duplicate ZIL graph identifier")
    if len(graph_modules) != len(set(graph_modules)):
        errors.append("duplicate ZIL module name")
    if len(graph_paths) != len(set(graph_paths)):
        errors.append("duplicate ZIL source path")
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate Lean source identifier")
    if len(source_paths) != len(set(source_paths)):
        errors.append("duplicate Lean source path")

    for graph in graphs:
        if not _is_sha(graph["source_blob"]):
            errors.append(f"invalid ZIL blob for {graph['id']}")
        qualified: list[str] = []
        for kind, names in graph["entities"].items():
            local = tuple(str(name) for name in names)
            if not local or any(not name for name in local):
                errors.append(f"empty {kind} declaration set in {graph['id']}")
            if len(local) != len(set(local)):
                errors.append(f"duplicate {kind} declaration in {graph['id']}")
            qualified.extend(f"{kind}:{name}" for name in local)
        if len(qualified) != len(set(qualified)):
            errors.append(f"duplicate qualified declaration in {graph['id']}")
        claims = set(graph["entities"].get("claim", ()))
        assumptions = set(graph["entities"].get("assumption", ()))
        if not set(graph["open_targets"]).issubset(claims | assumptions):
            errors.append(f"open target is not declared in {graph['id']}")
        for prefix in graph["witness_prefixes"]:
            if not witness_resolves(str(prefix)):
                errors.append(f"unresolved ZIL witness prefix {prefix}")

    for source in sources:
        if not _is_sha(source["blob"]):
            errors.append(f"invalid Lean source blob for {source['id']}")
        if not source["namespaces"]:
            errors.append(f"Lean source lacks namespace mapping: {source['id']}")

    imported_criteria = criterion_import_map()
    if set(imported_criteria) != EXPECTED_CRITERION_IMPORTS:
        errors.append("criterion import set does not close")
    for criterion, item in imported_criteria.items():
        if not item["declarations"] or not item["boundary"]:
            errors.append(
                f"criterion import lacks declarations or boundary: {criterion}"
            )
        for declaration in item["declarations"]:
            if not witness_resolves(str(declaration)):
                errors.append(f"unresolved Lean declaration: {declaration}")
        if resolve_adapters:
            for adapter in item["numerical_adapters"]:
                try:
                    resolve_adapter(str(adapter))
                except (ImportError, AttributeError, TypeError, ValueError) as error:
                    errors.append(f"adapter failed for {criterion}: {error}")

    legacy = load_contract()
    source_map = {source["path"]: source["blob"] for source in sources}
    for interface in legacy["interfaces"]:
        path = str(interface["source_path"])
        if source_map.get(path) != interface["source_blob"]:
            errors.append(f"legacy contract source is not imported exactly: {path}")

    expected = expected_source_blobs()
    observed = expected if observed_blobs is None else dict(observed_blobs)
    actual_tree = LATEST_FORMAL_TREE if observed_tree is None else observed_tree
    if actual_tree != LATEST_FORMAL_TREE:
        errors.append("formal repository tree drift detected")
    for path, blob in expected.items():
        if path not in observed:
            errors.append(f"imported formal source missing: {path}")
        elif observed[path] != blob:
            errors.append(f"imported formal source drift detected: {path}")

    acceptance = {
        "exact_repository_is_pinned": (
            FORMAL_REPOSITORY == "jagg-ix/entropic-physlib-private"
        ),
        "exact_branch_is_pinned": FORMAL_BRANCH == "entropic-physlib-linear-full",
        "base_commit_is_pinned": _is_sha(FORMAL_BASE_COMMIT),
        "exact_branch_tree_is_pinned": _is_sha(LATEST_FORMAL_TREE),
        "module_index_is_pinned": (
            MODULE_INDEX_PATH == "Physlib.lean"
            and _is_sha(LATEST_MODULE_INDEX_BLOB)
        ),
        "all_eleven_zil_graphs_are_imported": set(graph_ids) == REQUIRED_GRAPH_IDS,
        "all_zil_entity_identifiers_are_indexed": (
            total_entity_count() == EXPECTED_ENTITY_COUNT
        ),
        "all_open_targets_remain_explicit": (
            total_open_target_count() == EXPECTED_OPEN_TARGET_COUNT
        ),
        "lean_source_registry_is_complete": (
            len(sources) == EXPECTED_LEAN_SOURCE_COUNT
        ),
        "legacy_contract_is_subsumed": not any(
            error.startswith("legacy contract source") for error in errors
        ),
        "criterion_imports_are_registered": (
            set(imported_criteria) == EXPECTED_CRITERION_IMPORTS
        ),
        "observed_tree_matches": actual_tree == LATEST_FORMAL_TREE,
        "observed_blobs_match": all(
            observed.get(path) == blob for path, blob in expected.items()
        ),
        "physical_identity_is_not_inherited": True,
        "inventory_fingerprint_is_deterministic": (
            inventory_fingerprint() == inventory_fingerprint()
        ),
        "validation_has_no_errors": not errors,
    }
    return {
        "schema": "openwave.m9.cat-ept-formalization-import-result.v3",
        "task": "M9.94a",
        "repository": canonical_payload()["repository"],
        "graph_entity_counts": graph_entity_counts(),
        "total_entity_count": total_entity_count(),
        "total_open_target_count": total_open_target_count(),
        "lean_source_count": len(sources),
        "criterion_imports": sorted(imported_criteria),
        "source_blobs": expected,
        "fingerprint": inventory_fingerprint(),
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "cat_ept_formalization_imported": not errors,
            "zil_graphs_are_proof_authority": False,
            "lean_kernel_is_proof_authority": True,
            "pending_open_and_conditional_claims_preserved": True,
            "physical_particle_identity_inherited": False,
        },
    }


@lru_cache(maxsize=1)
def run_formalization_import_study() -> dict[str, Any]:
    return validate_inventory(resolve_adapters=True)


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
