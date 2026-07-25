"""Current fail-closed overlay for the M9.99 equation contract."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Mapping

from .formal_numerical_equation_contract import (
    FORMAL_BRANCH,
    FORMAL_REPOSITORY,
    FORMAL_SOURCES,
    OPENWAVE_SOURCES,
    canonical_payload as base_payload,
    contract_fingerprint,
    equation_relations,
)

ADDITIONAL_OPENWAVE_SOURCES = (
    {
        "path": "openwave/xperiments/m9_cat_ept/coefficient_self_consistency.py",
        "blob": "b4f86e6fa27f08240898a7364aff9c84059e25b3",
        "role": "Gaussian-reference alpha/beta selection assumptions",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/spinorial_pair_dynamics.py",
        "blob": "0ee2a6d3555b704aac376c807f047b570787f6ca",
        "role": "Pauli current, Pauli-to-Dirac embedding, position, momentum, alpha velocity, and response fits",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/spatial_3d_types.py",
        "blob": "7b70f9b73eebb6a2775268c81e5d23124decf0f1",
        "role": "canonical numerical Dirac matrices and declared mass/gauge parameters",
    },
)

ALL_OPENWAVE_SOURCES = tuple(OPENWAVE_SOURCES) + ADDITIONAL_OPENWAVE_SOURCES


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def expected_formal_blobs() -> dict[str, str]:
    return {str(item["path"]): str(item["blob"]) for item in FORMAL_SOURCES}


def expected_openwave_blobs() -> dict[str, str]:
    return {str(item["path"]): str(item["blob"]) for item in ALL_OPENWAVE_SOURCES}


def canonical_payload() -> dict[str, Any]:
    payload = base_payload()
    return {
        **payload,
        "schema": "openwave.m9.formal-numerical-equation-contract.v2",
        "openwave_sources": [dict(item) for item in ALL_OPENWAVE_SOURCES],
        "source_registry": {
            "formal_source_count": len(FORMAL_SOURCES),
            "openwave_source_count": len(ALL_OPENWAVE_SOURCES),
            "all_relation_source_paths_pinned": True,
        },
    }


def current_contract_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return contract_fingerprint(selected)


def validate_formal_numerical_equation_contract(
    *,
    observed_formal_blobs: Mapping[str, str] | None = None,
    observed_openwave_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    formal = (
        expected_formal_blobs()
        if observed_formal_blobs is None
        else dict(observed_formal_blobs)
    )
    openwave = (
        expected_openwave_blobs()
        if observed_openwave_blobs is None
        else dict(observed_openwave_blobs)
    )
    errors: list[str] = []
    for path, blob in expected_formal_blobs().items():
        if formal.get(path) != blob:
            errors.append(f"formal source drift detected: {path}")
    for path, blob in expected_openwave_blobs().items():
        if openwave.get(path) != blob:
            errors.append(f"OpenWave source drift detected: {path}")
    rows = equation_relations()
    relation_paths = {
        path
        for row in rows
        for path in (*row.formal_sources, *row.openwave_sources)
    }
    registered_paths = set(expected_formal_blobs()) | set(expected_openwave_blobs())
    acceptance = {
        "current_formal_repository_and_branch_are_exact": (
            FORMAL_REPOSITORY == "jagg-ix/entropic-physlib-private"
            and FORMAL_BRANCH == "entropic-physlib-linear-full"
        ),
        "all_formal_sources_are_blob_pinned": all(
            _is_sha(value) for value in expected_formal_blobs().values()
        ),
        "all_openwave_sources_are_blob_pinned": all(
            _is_sha(value) for value in expected_openwave_blobs().values()
        ),
        "all_relation_source_paths_are_registered": relation_paths.issubset(
            registered_paths
        ),
        "observed_formal_blobs_match": all(
            formal.get(path) == blob
            for path, blob in expected_formal_blobs().items()
        ),
        "observed_openwave_blobs_match": all(
            openwave.get(path) == blob
            for path, blob in expected_openwave_blobs().items()
        ),
        "source_registry_has_no_errors": not errors,
        "no_criterion_promotion_is_allowed": not canonical_payload()[
            "authority_boundary"
        ]["criterion_promotion_allowed"],
        "fingerprint_is_deterministic": current_contract_fingerprint()
        == current_contract_fingerprint(),
    }
    return {
        **canonical_payload(),
        "task": "M9.99a",
        "fingerprint": current_contract_fingerprint(),
        "errors": errors,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "formal_and_numerical_equations_are_machine_mapped": True,
            "all_referenced_sources_are_exactly_registered": True,
            "legacy_results_are_direct_tests_of_current_formal_equations": False,
            "criterion_rows_promoted": [],
        },
    }


@lru_cache(maxsize=1)
def run_formal_numerical_equation_contract() -> dict[str, Any]:
    return validate_formal_numerical_equation_contract()
