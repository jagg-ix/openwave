from copy import deepcopy

from openwave.xperiments.m9_cat_ept.physlib_contract import (
    EXPECTED_BRANCH,
    EXPECTED_COMMIT,
    contract_fingerprint,
    load_contract,
    run_physlib_contract_study,
    validate_contract,
)


def test_contract_pins_live_entropic_physlib_branch():
    contract = load_contract()
    assert contract["repository"]["branch"] == EXPECTED_BRANCH
    assert contract["repository"]["commit"] == EXPECTED_COMMIT
    assert contract["repository"]["name"] == "jagg-ix/entropic-physlib-private"


def test_contract_is_complete_and_preserves_claim_boundaries():
    result = validate_contract(resolve_adapters=True)
    assert result["passed"], result["errors"]
    assert result["interface_count"] >= 6
    assert result["acceptance"]["all_sources_are_blob_pinned"]
    assert result["acceptance"]["physical_identity_is_not_inherited"]
    assert result["acceptance"]["lean_is_not_a_runtime_dependency"]


def test_contract_detects_commit_drift_fail_closed():
    result = validate_contract(observed_commit="0" * 40)
    assert not result["passed"]
    assert not result["acceptance"]["observed_commit_matches"]
    assert "formal repository commit drift detected" in result["errors"]


def test_contract_detects_blob_drift_and_missing_sources():
    contract = load_contract()
    path = contract["interfaces"][0]["source_path"]
    expected = {
        item["source_path"]: item["source_blob"]
        for item in contract["interfaces"]
    }
    stale = dict(expected)
    stale[path] = "0" * 40
    stale_result = validate_contract(observed_blobs=stale)
    assert not stale_result["passed"]
    assert any("formal source drift detected" in error for error in stale_result["errors"])

    missing = dict(expected)
    missing.pop(path)
    missing_result = validate_contract(observed_blobs=missing)
    assert not missing_result["passed"]
    assert any("formal source missing" in error for error in missing_result["errors"])


def test_contract_rejects_physical_identity_inheritance():
    contract = deepcopy(load_contract())
    contract["policy"]["physical_identity_inherited"] = True
    result = validate_contract(contract)
    assert not result["passed"]
    assert not result["acceptance"]["physical_identity_is_not_inherited"]


def test_contract_fingerprint_and_study_are_deterministic():
    assert len(contract_fingerprint()) == 64
    assert contract_fingerprint() == contract_fingerprint()
    result = run_physlib_contract_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["cross_repository_drift_is_fail_closed"]
