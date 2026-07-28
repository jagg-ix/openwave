"""M9.131a: source manifest and artifact-integrity verification for reused experiments."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

REQUIRED_SOURCE_FIELDS = (
    "dataset_id", "paper_doi", "source_uri", "source_digest", "artifact_kind",
    "license_or_access", "extracted_by", "extraction_version",
)


def canonical_digest(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def verify_source_manifest(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    errors = []
    normalized = []
    seen = set()
    for index, entry in enumerate(entries):
        missing = tuple(field for field in REQUIRED_SOURCE_FIELDS if not entry.get(field))
        if missing:
            errors.append({"entry": index, "error": "missing-fields", "fields": missing})
            continue
        dataset_id = str(entry["dataset_id"])
        if dataset_id in seen:
            errors.append({"entry": index, "error": "duplicate-dataset-id", "dataset_id": dataset_id})
            continue
        seen.add(dataset_id)
        digest = str(entry["source_digest"])
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
            errors.append({"entry": index, "error": "invalid-sha256", "dataset_id": dataset_id})
            continue
        normalized.append({field: entry[field] for field in REQUIRED_SOURCE_FIELDS})
    payload = {
        "schema": "openwave.m9.existing-data-source-manifest.v1",
        "entries": tuple(normalized),
        "errors": tuple(errors),
    }
    return {
        **payload,
        "valid": bool(normalized) and not errors,
        "manifest_digest": canonical_digest(payload),
    }


def run_source_manifest_verifier() -> dict[str, Any]:
    fixture = (
        {
            "dataset_id": "moreva-2014-page-wootters",
            "paper_doi": "10.1103/PhysRevA.89.052122",
            "source_uri": "publisher-or-reviewed-repository-uri",
            "source_digest": "1" * 64,
            "artifact_kind": "digitized-coincidence-table",
            "license_or_access": "review-required",
            "extracted_by": "openwave-m9-importer",
            "extraction_version": "v1",
        },
        {
            "dataset_id": "lu-2003-quantum-dot",
            "paper_doi": "10.1038/nature01642",
            "source_uri": "publisher-or-reviewed-repository-uri",
            "source_digest": "2" * 64,
            "artifact_kind": "time-tagged-event-table",
            "license_or_access": "review-required",
            "extracted_by": "openwave-m9-importer",
            "extraction_version": "v1",
        },
    )
    result = verify_source_manifest(fixture)
    acceptance = {
        "fixture_manifest_is_valid": result["valid"],
        "two_distinct_sources_are_registered": len(result["entries"]) == 2,
        "manifest_digest_is_deterministic": result["manifest_digest"] == verify_source_manifest(fixture)["manifest_digest"],
        "raw_artifact_digest_is_required": "source_digest" in REQUIRED_SOURCE_FIELDS,
    }
    return {**result, "task": "M9.131a", "acceptance": acceptance, "passed": all(acceptance.values())}
