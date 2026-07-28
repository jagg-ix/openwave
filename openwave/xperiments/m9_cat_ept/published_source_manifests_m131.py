"""M9.131a: canonical manifests for published summary-level evidence.

The digests in this module cover normalized citation/extraction metadata. They are
not hashes of publisher PDF bytes. Raw-file digest verification remains a
separate promotion requirement.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


def _digest(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canonical_manifests() -> tuple[dict[str, Any], ...]:
    rows = (
        {
            "source_id": "moreva-2014-paw",
            "title": "Time from quantum entanglement: An experimental illustration",
            "doi": "10.1103/PhysRevA.89.052122",
            "arxiv": "1310.4691",
            "published": "2014-05-20",
            "carrier": "polarization-entangled-photon-pair",
            "extraction_level": "publication-metadata",
        },
        {
            "source_id": "moreva-2017-multitime",
            "title": "Quantum time: Experimental multitime correlations",
            "doi": "10.1103/PhysRevD.96.102005",
            "arxiv": "1710.00707",
            "published": "2017-11-16",
            "carrier": "single-photon-position-clock",
            "extraction_level": "published-table",
        },
        {
            "source_id": "lu-2003-dot",
            "title": "Real-time detection of electron tunnelling in a quantum dot",
            "doi": "10.1038/nature01642",
            "published": "2003-05-22",
            "carrier": "quantum-dot-charge-state",
            "extraction_level": "published-summary-bound",
        },
        {
            "source_id": "gustavsson-2016-qubit",
            "title": "Suppressing relaxation in superconducting qubits by quasiparticle pumping",
            "doi": "10.1126/science.aah5844",
            "arxiv": "1612.08462",
            "published": "2016-12-23",
            "carrier": "superconducting-flux-qubit",
            "extraction_level": "published-fit-parameters",
        },
    )
    return tuple({**row, "metadata_sha256": _digest(row)} for row in rows)


def validate_manifests(manifests: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    required = ("source_id", "title", "doi", "published", "carrier", "extraction_level", "metadata_sha256")
    errors = []
    seen = set()
    for index, row in enumerate(manifests):
        missing = tuple(key for key in required if key not in row)
        if missing:
            errors.append({"row": index, "error": "missing-fields", "fields": missing})
            continue
        source_id = str(row["source_id"])
        if source_id in seen:
            errors.append({"row": index, "error": "duplicate-source-id", "source_id": source_id})
            continue
        seen.add(source_id)
        canonical = {key: row[key] for key in row if key != "metadata_sha256"}
        if str(row["metadata_sha256"]) != _digest(canonical):
            errors.append({"row": index, "error": "metadata-digest-mismatch", "source_id": source_id})
    return {
        "schema": "openwave.m9.published-source-manifests.v1",
        "manifests": tuple(dict(row) for row in manifests),
        "errors": tuple(errors),
        "valid": bool(manifests) and not errors,
        "raw_source_file_digests_verified": False,
    }


def run_published_source_manifests() -> dict[str, Any]:
    manifests = canonical_manifests()
    result = validate_manifests(manifests)
    acceptance = {
        "four_publications_registered": len(manifests) == 4,
        "canonical_metadata_digests_verify": result["valid"],
        "table_fit_and_bound_levels_are_explicit": {row["extraction_level"] for row in manifests}
        == {"publication-metadata", "published-table", "published-summary-bound", "published-fit-parameters"},
        "raw_file_digest_is_not_overclaimed": not result["raw_source_file_digests_verified"],
    }
    return {**result, "task": "M9.131a", "acceptance": acceptance, "passed": all(acceptance.values())}
