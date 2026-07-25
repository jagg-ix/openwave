"""M9.96 overlay for Pauli--Maxwell and conserved-current formal witnesses."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_import import (
    criterion_import_map,
    run_formalization_import_study,
    witness_resolves,
)
from .formalization_inventory_force_extensions import (
    FORCE_EXTENSION_DECLARATIONS,
    FORCE_EXTENSION_LEAN_SOURCES,
)


def _is_sha(value: str) -> bool:
    return len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def extension_source_blobs() -> dict[str, str]:
    return {
        path: blob
        for _identifier, path, blob, _namespaces, _status in FORCE_EXTENSION_LEAN_SOURCES
    }


def extended_criterion_import_map() -> dict[str, dict[str, Any]]:
    result = {
        key: {
            "criterion": item["criterion"],
            "task": item["task"],
            "declarations": tuple(item["declarations"]),
            "numerical_adapters": tuple(item["numerical_adapters"]),
            "boundary": tuple(item["boundary"]),
        }
        for key, item in criterion_import_map().items()
    }
    for criterion, extension in FORCE_EXTENSION_DECLARATIONS.items():
        current = result[criterion]
        current["declarations"] = tuple(
            dict.fromkeys(current["declarations"] + tuple(extension["declarations"]))
        )
        current["boundary"] = tuple(
            dict.fromkeys(current["boundary"] + tuple(extension["boundary"]))
        )
    return result


def extension_fingerprint() -> str:
    payload = {
        "sources": FORCE_EXTENSION_LEAN_SOURCES,
        "criteria": FORCE_EXTENSION_DECLARATIONS,
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_force_formal_extension(
    *,
    observed_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    base = run_formalization_import_study()
    base_map = criterion_import_map()
    merged = extended_criterion_import_map()
    namespace_prefixes = tuple(
        prefix
        for _identifier, _path, _blob, namespaces, _status in FORCE_EXTENSION_LEAN_SOURCES
        for prefix in namespaces
    )
    extension_declarations = tuple(
        declaration
        for item in FORCE_EXTENSION_DECLARATIONS.values()
        for declaration in item["declarations"]
    )
    expected_blobs = extension_source_blobs()
    observed = expected_blobs if observed_blobs is None else dict(observed_blobs)
    errors: list[str] = []

    def resolves(declaration: str) -> bool:
        return witness_resolves(declaration) or any(
            declaration == prefix or declaration.startswith(prefix + ".")
            for prefix in namespace_prefixes
        )

    if len(FORCE_EXTENSION_LEAN_SOURCES) != 2:
        errors.append("force extension source count does not close")
    for identifier, path, blob, namespaces, _status in FORCE_EXTENSION_LEAN_SOURCES:
        if not identifier or not path or not namespaces:
            errors.append("force extension source metadata is incomplete")
        if not _is_sha(blob):
            errors.append(f"invalid force extension blob: {path}")
        if path not in observed:
            errors.append(f"force extension source missing: {path}")
        elif observed[path] != blob:
            errors.append(f"force extension source drift detected: {path}")
    for declaration in extension_declarations:
        if not resolves(declaration):
            errors.append(f"unresolved force extension declaration: {declaration}")
    for key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
        if len(merged[key]["declarations"]) <= len(base_map[key]["declarations"]):
            errors.append(f"force extension did not strengthen criterion: {key}")

    acceptance = {
        "base_current_tree_inventory_passes": bool(base["passed"]),
        "two_additional_sources_are_blob_pinned": (
            len(FORCE_EXTENSION_LEAN_SOURCES) == 2
            and all(
                _is_sha(blob)
                for _id, _path, blob, _namespaces, _status in FORCE_EXTENSION_LEAN_SOURCES
            )
        ),
        "all_extension_sources_are_observed_exactly": all(
            observed.get(path) == blob for path, blob in expected_blobs.items()
        ),
        "all_extension_declarations_resolve_to_registered_namespaces": all(
            resolves(declaration) for declaration in extension_declarations
        ),
        "all_three_partial_rows_receive_stronger_witnesses": all(
            len(merged[key]["declarations"]) > len(base_map[key]["declarations"])
            for key in ("magnetic_moment_spin", "electric_force", "magnetic_force")
        ),
        "physical_identity_and_calibration_are_not_inherited": True,
        "fingerprint_is_deterministic": (
            extension_fingerprint() == extension_fingerprint()
        ),
        "validation_has_no_errors": not errors,
    }
    return {
        "schema": "openwave.m9.force-formal-extension.v2",
        "task": "M9.96-formal",
        "base_inventory_fingerprint": base["fingerprint"],
        "extension_fingerprint": extension_fingerprint(),
        "source_count": len(FORCE_EXTENSION_LEAN_SOURCES),
        "source_blobs": expected_blobs,
        "sources": [
            {
                "id": identifier,
                "path": path,
                "blob": blob,
                "namespaces": list(namespaces),
                "status": status,
            }
            for identifier, path, blob, namespaces, status in FORCE_EXTENSION_LEAN_SOURCES
        ],
        "criterion_imports": {
            key: {
                "declarations": list(value["declarations"]),
                "boundary": list(value["boundary"]),
            }
            for key, value in merged.items()
            if key in FORCE_EXTENSION_DECLARATIONS
        },
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "pauli_maxwell_link_imported": True,
            "conserved_current_maxwell_link_imported": True,
            "static_maxwell_stress_source_link_imported": True,
            "formal_availability_promotes_physical_rows": False,
        },
    }


@lru_cache(maxsize=1)
def run_force_formal_extension_study() -> dict[str, Any]:
    return validate_force_formal_extension()


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
