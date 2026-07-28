from openwave.xperiments.m9_cat_ept.published_source_manifests_m131 import (
    canonical_manifests,
    run_published_source_manifests,
    validate_manifests,
)


def test_canonical_manifests_verify_metadata_digests():
    result = run_published_source_manifests()
    assert result["passed"]
    assert result["valid"]
    assert len(result["manifests"]) == 4
    assert not result["raw_source_file_digests_verified"]


def test_manifest_tampering_fails_closed():
    rows = [dict(row) for row in canonical_manifests()]
    rows[0]["title"] = "tampered"
    result = validate_manifests(rows)
    assert not result["valid"]
    assert result["errors"][0]["error"] == "metadata-digest-mismatch"
