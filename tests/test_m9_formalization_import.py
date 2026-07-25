from openwave.xperiments.m9_cat_ept.formalization_import import (
    EXPECTED_CRITERION_IMPORTS,
    IMPORTED_ZIL_GRAPHS,
    REQUIRED_GRAPH_IDS,
    criterion_import_map,
    expected_source_blobs,
    graph_entity_counts,
    inventory_fingerprint,
    lean_source_records,
    run_formalization_import_study,
    total_entity_count,
    total_open_target_count,
    validate_inventory,
    witness_resolves,
)
from openwave.xperiments.m9_cat_ept.formalization_inventory import (
    FORMAL_BRANCH,
    FORMAL_COMMIT,
    FORMAL_REPOSITORY,
)
from openwave.xperiments.m9_cat_ept.formalization_inventory_corpus import (
    LATEST_FORMAL_TREE,
    LATEST_MODULE_INDEX_BLOB,
)


def test_exact_formal_repository_revision_is_imported():
    assert FORMAL_REPOSITORY == "jagg-ix/entropic-physlib-private"
    assert FORMAL_BRANCH == "entropic-physlib-linear-full"
    assert FORMAL_COMMIT == "e10af9a3b47bf90afc0a88167a5d495b6935f4dc"
    assert LATEST_FORMAL_TREE == "239a663a3192a3144fb998e7bb200e09689a3bb9"
    assert LATEST_MODULE_INDEX_BLOB == "182a06e0f50314ec54436da602b4ac86eba4ee08"


def test_all_zil_declarations_are_indexed_with_open_targets_preserved():
    assert {graph["id"] for graph in IMPORTED_ZIL_GRAPHS} == REQUIRED_GRAPH_IDS
    assert total_entity_count() == 422
    assert total_open_target_count() == 12
    assert graph_entity_counts() == {
        "electrogravitic-action-closure": {
            "component": 38,
            "claim": 16,
            "inspection": 2,
            "policy": 1,
        },
        "lindblad-driven-leads": {
            "component": 8,
            "source": 13,
            "claim": 16,
            "proof": 18,
        },
        "liouville-second-quantization": {
            "component": 7,
            "source": 6,
            "assumption": 5,
            "claim": 13,
            "proof": 9,
        },
        "cauchy-weak-limit": {
            "component": 4,
            "source": 3,
            "claim": 4,
            "proof": 3,
        },
        "lindblad-trace-preservation": {
            "component": 4,
            "source": 2,
            "claim": 4,
            "proof": 4,
        },
        "rivers-scalar-green-functions": {
            "component": 12,
            "source": 9,
            "claim": 26,
            "proof": 21,
        },
        "rivers-scalar-green-functions-continuum": {
            "component": 12,
            "source": 5,
            "claim": 23,
            "proof": 20,
        },
        "lovelock-rund-continuum-variational": {
            "component": 14,
            "source": 5,
            "claim": 17,
        },
        "lovelock-rund-pointwise-operators": {
            "component": 4,
            "source": 2,
            "claim": 5,
        },
        "lovelock-rund-invariant-geometry": {
            "component": 11,
            "source": 10,
            "claim": 16,
        },
        "veliev-periodic-schrodinger": {
            "source": 1,
            "component": 7,
            "claim": 22,
        },
    }


def test_blob_pinned_lean_registry_and_criterion_imports_close():
    assert len(lean_source_records()) == 24
    assert set(criterion_import_map()) == EXPECTED_CRITERION_IMPORTS == {
        "magnetic_moment_spin",
        "electric_force",
        "magnetic_force",
        "gravity",
    }
    assert all(len(source["blob"]) == 40 for source in lean_source_records())
    for item in criterion_import_map().values():
        assert item["declarations"]
        assert item["numerical_adapters"]
        assert item["boundary"]
        assert all(witness_resolves(declaration) for declaration in item["declarations"])


def test_import_subsumes_legacy_contract_and_resolves_adapters():
    result = validate_inventory(resolve_adapters=True)
    assert result["passed"], result["errors"]
    assert result["acceptance"]["legacy_contract_is_subsumed"]
    assert result["acceptance"]["criterion_imports_are_registered"]
    assert result["acceptance"]["all_eleven_zil_graphs_are_imported"]
    assert result["decision"]["lean_kernel_is_proof_authority"]
    assert not result["decision"]["zil_graphs_are_proof_authority"]


def test_import_detects_tree_blob_and_missing_source_drift():
    tree_result = validate_inventory(
        observed_tree="0" * 40,
        resolve_adapters=False,
    )
    assert not tree_result["passed"]
    assert "formal repository tree drift detected" in tree_result["errors"]

    expected = expected_source_blobs()
    path = next(iter(expected))
    stale = dict(expected)
    stale[path] = "0" * 40
    stale_result = validate_inventory(observed_blobs=stale, resolve_adapters=False)
    assert not stale_result["passed"]
    assert any("source drift detected" in error for error in stale_result["errors"])

    missing = dict(expected)
    missing.pop(path)
    missing_result = validate_inventory(
        observed_blobs=missing,
        resolve_adapters=False,
    )
    assert not missing_result["passed"]
    assert any("source missing" in error for error in missing_result["errors"])


def test_inventory_fingerprint_and_full_study_are_deterministic():
    assert len(inventory_fingerprint()) == 64
    assert inventory_fingerprint() == inventory_fingerprint()
    result = run_formalization_import_study()
    assert result["schema"] == "openwave.m9.cat-ept-formalization-import-result.v3"
    assert result["passed"] and all(result["acceptance"].values())
    assert result["total_entity_count"] == 422
    assert result["total_open_target_count"] == 12
    assert result["lean_source_count"] == 24
    assert result["repository"]["tree"] == LATEST_FORMAL_TREE
    assert not result["decision"]["physical_particle_identity_inherited"]
