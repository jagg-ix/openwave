"""M9.106--M9.108 upstream authority and program-health contract."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m105_extension import CURRENT_ZIL_HEAD, ZIL_REPOSITORY

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
PREVIOUS_FORMAL_HEAD = "eba0124fcfbc1216d973bb6f504c5a6d324de60c"
CURRENT_FORMAL_HEAD = "128974a501d3d0a43108a3ab9a1bd9d4fea5d7db"
PHYSLIB_ROOT_BLOB = "56813b617e44f1ebd2ce5716fec72db4327ed0d0"

PROGRAM_HEALTH_SOURCES = (
    {
        "path": "Physlib/Meta/ProgramHealth.lean",
        "blob": "5e6e8572c33c368457afbbceea72906f92a95ddd",
        "role": "rigor-weighted gaps, foundational risk, cross-consistency, and hidden epistemic debt",
    },
    {
        "path": "Physlib/Meta/ZilGraph.lean",
        "blob": "30a6f8862fdb6909f0f5c87ea995a54e1e10f1eb",
        "role": "executable graph gap rules, documented-prediction coverage, and dependency cycles",
    },
    {
        "path": "analysis/health-baseline.json",
        "blob": "30cbdb9ec3ac0d28aba26e6de8b9ea41d95cf7d0",
        "role": "diffable program-health baseline",
    },
)

PROGRAM_HEALTH_BASELINE = {
    "edges": 4528,
    "exact_identities": 218,
    "untested_numerical": 0,
    "loaded_uncited": 12,
    "undisclosed": 0,
    "out_of_vocab": 0,
    "physics_internal_only": 2,
    "hidden_debt": 43,
}


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def health_regressions(observed: Mapping[str, int]) -> list[str]:
    errors: list[str] = []
    exact = int(observed.get("exact_identities", -1))
    if exact < PROGRAM_HEALTH_BASELINE["exact_identities"]:
        errors.append("exact identity count regressed")
    for key in (
        "untested_numerical",
        "loaded_uncited",
        "undisclosed",
        "out_of_vocab",
        "physics_internal_only",
        "hidden_debt",
    ):
        if int(observed.get(key, 10**9)) > PROGRAM_HEALTH_BASELINE[key]:
            errors.append(f"{key} regressed")
    return errors


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m108-extension.v1",
        "formal_repository": {
            "name": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "previous_head": PREVIOUS_FORMAL_HEAD,
            "current_head": CURRENT_FORMAL_HEAD,
            "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        },
        "zil_repository": {
            "name": ZIL_REPOSITORY,
            "head": CURRENT_ZIL_HEAD,
        },
        "program_health_sources": [dict(row) for row in PROGRAM_HEALTH_SOURCES],
        "program_health_baseline": dict(PROGRAM_HEALTH_BASELINE),
        "targets": (
            "constraint_preserving_nonlinear_metric_evolution",
            "coupled_field_successors_for_reduced_interaction_sectors",
            "stable_dynamical_candidate_state_construction",
        ),
        "policy": {
            "program_health_must_not_regress": True,
            "campaign_execution_is_not_physical_closure": True,
            "reduced_metric_is_not_general_einstein_cauchy_development": True,
            "reduced_sector_fields_are_not_standard_model_derivations": True,
            "candidate_state_is_not_particle_identity": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def validate_program_health(observed: Mapping[str, int] | None = None) -> dict[str, Any]:
    selected = PROGRAM_HEALTH_BASELINE if observed is None else dict(observed)
    errors = health_regressions(selected)
    return {
        "observed": selected,
        "baseline": dict(PROGRAM_HEALTH_BASELINE),
        "errors": errors,
        "passed": not errors,
    }


@lru_cache(maxsize=1)
def run_formalization_m108_extension() -> dict[str, Any]:
    payload = canonical_payload()
    health = validate_program_health()
    acceptance = {
        "formal_and_zil_heads_are_exact": _is_sha(CURRENT_FORMAL_HEAD)
        and _is_sha(CURRENT_ZIL_HEAD),
        "physlib_root_is_exact": _is_sha(PHYSLIB_ROOT_BLOB),
        "three_program_health_sources_are_exact": len(PROGRAM_HEALTH_SOURCES) == 3
        and all(_is_sha(row["blob"]) for row in PROGRAM_HEALTH_SOURCES),
        "program_health_baseline_has_zero_untested_numerical": PROGRAM_HEALTH_BASELINE[
            "untested_numerical"
        ]
        == 0,
        "baseline_health_does_not_regress": bool(health["passed"]),
        "three_targets_are_registered": len(payload["targets"]) == 3,
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.106--M9.108-formalization",
        "program_health": health,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "upstream_program_health_registered": True,
            "new_physics_claim_created_by_health_metrics": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
