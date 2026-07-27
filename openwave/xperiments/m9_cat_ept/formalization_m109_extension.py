"""M9.109a: current Newton-G clock authority and scope contract."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m108_extension import (
    PROGRAM_HEALTH_BASELINE,
    canonical_payload as previous_payload,
    run_formalization_m108_extension,
)
from .formalization_m105_extension import CURRENT_ZIL_HEAD, ZIL_REPOSITORY

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
PREVIOUS_FORMAL_HEAD = "128974a501d3d0a43108a3ab9a1bd9d4fea5d7db"
CURRENT_FORMAL_HEAD = "398ba1976ce7602e30ed05ecbd0f228027335584"
PHYSLIB_ROOT_BLOB = "38e3e4d5b1fcdebf5a4335fb4741a57774a6c0d1"

G_AUTHORITY_SOURCES = (
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/ComptonClock/"
            "EntropicClockComptonAnchor.lean"
        ),
        "blob": "3c2992f8f122a3792f1b167f46f3c878cb27b95d",
        "role": (
            "Compton-anchored entropic clock, rest-energy action rate, proper-time "
            "identity, and G = c^5/(hbar*omega0^2)"
        ),
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/ComptonClock/"
            "ComptonCellNewtonConstant.lean"
        ),
        "blob": "535738543f0259aae3f6f36e772ec4bf160317b8",
        "role": "G-free Compton-cell derivation G = hbar*c/m^2 = hbar*c*sigma0^4",
    },
    {
        "path": "Physlib/Meta/ZilGraph.lean",
        "blob": "6d4a06d6443af94fd683f34a18c07efd54852a08",
        "role": (
            "canonical cross-module primitive-versus-derived guard seeded for "
            "constant:newton-G"
        ),
    },
    {
        "path": "analysis/AUDIT.md",
        "blob": "7b9bd8e6acc77178d664f7d1f41ebd7f457f98f7",
        "role": "formal-graph scope, canonical-name convention, and honesty boundary",
    },
)

G_EQUIVALENCE = {
    "mass": "G = hbar*c/m_anchor^2",
    "clock": "G = c^5/(hbar*omega_anchor^2)",
    "inference_width": "G = hbar*c*sigma0_anchor^4",
    "clock_mass": "omega_anchor = m_anchor*c^2/hbar",
}

SCOPE = {
    "newton_G_is_canonical_derived_quantity": True,
    "particle_mass_value_is_derived": False,
    "clock_anchor_removes_free_omega_parameter": True,
    "clock_anchor_predicts_mass_value": False,
    "three_origin_mass_coincidence_is_unconditional": False,
    "G_derivation_is_conditional_on_mass_or_inference_anchor": True,
    "formal_theorem_proves_species_independent_G": False,
    "universal_gravity_anchor_requires_separate_numerical_audit": True,
}


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def expected_source_blobs() -> dict[str, str]:
    return {str(row["path"]): str(row["blob"]) for row in G_AUTHORITY_SOURCES}


def canonical_payload() -> dict[str, Any]:
    previous = previous_payload()
    return {
        "schema": "openwave.m9.formalization-m109-extension.v1",
        "previous_authority": previous,
        "formal_repository": {
            "name": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "previous_head": PREVIOUS_FORMAL_HEAD,
            "current_head": CURRENT_FORMAL_HEAD,
            "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        },
        "zil_repository": {"name": ZIL_REPOSITORY, "head": CURRENT_ZIL_HEAD},
        "g_authority_sources": [dict(row) for row in G_AUTHORITY_SOURCES],
        "g_equivalence": dict(G_EQUIVALENCE),
        "scope": dict(SCOPE),
        "program_health_baseline": dict(PROGRAM_HEALTH_BASELINE),
        "policy": {
            "canonical_newton_G_must_not_be_declared_primitive": True,
            "algebraic_elimination_is_not_an_external_prediction": True,
            "species_specific_particle_clock_is_not_universal_gravity_clock": True,
            "natural_unit_identity_is_not_physical_calibration": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def validate_formalization_m109(
    *,
    observed_head: str | None = None,
    observed_root_blob: str | None = None,
    observed_source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    head = CURRENT_FORMAL_HEAD if observed_head is None else observed_head
    root = PHYSLIB_ROOT_BLOB if observed_root_blob is None else observed_root_blob
    sources = (
        expected_source_blobs()
        if observed_source_blobs is None
        else dict(observed_source_blobs)
    )
    errors: list[str] = []
    if head != CURRENT_FORMAL_HEAD:
        errors.append("formal head drift detected")
    if root != PHYSLIB_ROOT_BLOB:
        errors.append("Physlib root drift detected")
    for path, blob in expected_source_blobs().items():
        if sources.get(path) != blob:
            errors.append(f"G authority source drift detected: {path}")
    return {"errors": errors, "passed": not errors}


@lru_cache(maxsize=1)
def run_formalization_m109_extension() -> dict[str, Any]:
    previous = run_formalization_m108_extension()
    validation = validate_formalization_m109()
    payload = canonical_payload()
    acceptance = {
        "previous_program_health_authority_passes": bool(previous["passed"]),
        "current_formal_and_zil_heads_are_exact": _is_sha(CURRENT_FORMAL_HEAD)
        and _is_sha(CURRENT_ZIL_HEAD),
        "current_physlib_root_is_exact": _is_sha(PHYSLIB_ROOT_BLOB),
        "four_G_authority_sources_are_blob_pinned": len(G_AUTHORITY_SOURCES) == 4
        and all(_is_sha(str(row["blob"])) for row in G_AUTHORITY_SOURCES),
        "newton_G_is_derived_not_primitive": SCOPE[
            "newton_G_is_canonical_derived_quantity"
        ],
        "mass_value_and_universality_remain_open": not SCOPE[
            "particle_mass_value_is_derived"
        ]
        and not SCOPE["formal_theorem_proves_species_independent_G"],
        "source_validation_has_no_errors": bool(validation["passed"]),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.109a",
        "source_validation": validation,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "current_G_clock_authority_registered": True,
            "G_may_be_treated_as_primitive": False,
            "particle_clock_universality_established": False,
            "physical_G_prediction_executed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
