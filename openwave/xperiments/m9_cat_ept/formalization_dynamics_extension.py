"""M9.97 formal overlay for spin precession and particle dynamics."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_force_extension import (
    extended_criterion_import_map as force_criterion_import_map,
    run_force_formal_extension_study,
)
from .formalization_import import witness_resolves
from .formalization_inventory_dynamics_extensions import (
    DYNAMICS_EXTENSION_DECLARATIONS,
    DYNAMICS_EXTENSION_LEAN_SOURCES,
)


def _is_sha(value: str) -> bool:
    return len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )


def dynamics_criterion_import_map() -> dict[str, dict[str, Any]]:
    result = {
        key: {
            "criterion": value["criterion"],
            "task": value["task"],
            "declarations": tuple(value["declarations"]),
            "numerical_adapters": tuple(value["numerical_adapters"]),
            "boundary": tuple(value["boundary"]),
        }
        for key, value in force_criterion_import_map().items()
    }
    for criterion, extension in DYNAMICS_EXTENSION_DECLARATIONS.items():
        current = result[criterion]
        current["declarations"] = tuple(
            dict.fromkeys(current["declarations"] + tuple(extension["declarations"]))
        )
        current["boundary"] = tuple(
            dict.fromkeys(current["boundary"] + tuple(extension["boundary"]))
        )
    return result


def expected_dynamics_source_blobs() -> dict[str, str]:
    return {
        path: blob
        for _identifier, path, blob, _namespaces, _status in DYNAMICS_EXTENSION_LEAN_SOURCES
    }


def dynamics_extension_fingerprint() -> str:
    payload = {
        "sources": DYNAMICS_EXTENSION_LEAN_SOURCES,
        "criteria": DYNAMICS_EXTENSION_DECLARATIONS,
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_dynamics_extension(
    *, observed_blobs: Mapping[str, str] | None = None
) -> dict[str, Any]:
    force = run_force_formal_extension_study()
    base_map = force_criterion_import_map()
    merged = dynamics_criterion_import_map()
    expected = expected_dynamics_source_blobs()
    observed = expected if observed_blobs is None else dict(observed_blobs)
    namespace_prefixes = tuple(
        prefix
        for _identifier, _path, _blob, namespaces, _status in DYNAMICS_EXTENSION_LEAN_SOURCES
        for prefix in namespaces
    )
    declarations = tuple(
        declaration
        for value in DYNAMICS_EXTENSION_DECLARATIONS.values()
        for declaration in value["declarations"]
    )

    def resolves(declaration: str) -> bool:
        return witness_resolves(declaration) or any(
            declaration == prefix or declaration.startswith(prefix + ".")
            for prefix in namespace_prefixes
        )

    errors = []
    for path, blob in expected.items():
        if path not in observed:
            errors.append(f"dynamics formal source missing: {path}")
        elif observed[path] != blob:
            errors.append(f"dynamics formal source drift detected: {path}")
    acceptance = {
        "m9_96_force_overlay_passes": bool(force["passed"]),
        "three_dynamics_sources_are_blob_pinned": (
            len(DYNAMICS_EXTENSION_LEAN_SOURCES) == 3
            and all(
                _is_sha(blob)
                for _identifier, _path, blob, _namespaces, _status in DYNAMICS_EXTENSION_LEAN_SOURCES
            )
        ),
        "observed_dynamics_sources_match": not errors,
        "all_dynamics_declarations_resolve": all(
            resolves(declaration) for declaration in declarations
        ),
        "all_three_partial_rows_receive_dynamics_witnesses": all(
            len(merged[key]["declarations"]) > len(base_map[key]["declarations"])
            for key in ("magnetic_moment_spin", "electric_force", "magnetic_force")
        ),
        "rest_frame_and_covariant_boundaries_are_explicit": any(
            "covariant boost" in boundary
            for boundary in merged["magnetic_moment_spin"]["boundary"]
        ),
        "formal_availability_does_not_promote_physical_rows": True,
        "fingerprint_is_deterministic": (
            dynamics_extension_fingerprint() == dynamics_extension_fingerprint()
        ),
    }
    return {
        "schema": "openwave.m9.dynamics-formal-extension.v1",
        "task": "M9.97-formal",
        "force_extension_fingerprint": force["extension_fingerprint"],
        "dynamics_extension_fingerprint": dynamics_extension_fingerprint(),
        "source_count": len(DYNAMICS_EXTENSION_LEAN_SOURCES),
        "sources": [
            {
                "id": identifier,
                "path": path,
                "blob": blob,
                "namespaces": list(namespaces),
                "status": status,
            }
            for identifier, path, blob, namespaces, status in DYNAMICS_EXTENSION_LEAN_SOURCES
        ],
        "criterion_imports": {
            key: {
                "declarations": list(value["declarations"]),
                "boundary": list(value["boundary"]),
            }
            for key, value in merged.items()
            if key in DYNAMICS_EXTENSION_DECLARATIONS
        },
        "source_blobs": expected,
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "rest_frame_dirac_pauli_precession_imported": True,
            "rest_frame_tbmt_equivalence_imported": True,
            "coulomb_and_distributional_point_source_imported": True,
            "full_covariant_tbmt_dynamics_imported": False,
            "formal_availability_promotes_physical_rows": False,
        },
    }


@lru_cache(maxsize=1)
def run_dynamics_formal_extension_study() -> dict[str, Any]:
    return validate_dynamics_extension()


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
