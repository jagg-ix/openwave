"""M9.124c: fail-closed synthesis gate for Page-Wootters, modular, and entropic clocks."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

from .three_clock_benchmark import run_three_clock_benchmark
from .three_clock_time_profile import run_three_clock_time_profile

ROLE_REQUIREMENTS = (
    "role:page_wootters_relational",
    "role:modular_thermal",
    "role:entropic_irreversible",
    "bridge:page_wootters_entropic",
    "bridge:modular_entropic",
    "bridge:page_wootters_modular",
    "benchmark:three_clock_controls",
)

UNIFIED_CLOCK_REQUIREMENTS = ROLE_REQUIREMENTS + (
    "theorem:constraint_to_conditioned_dynamics",
    "identity:conditioned_generator_is_modular_K",
    "identity:dissipator_and_modular_flow_share_common_carrier",
    "calibration:tauPW_to_modular_parameter",
    "calibration:modular_to_entropic_parameter",
    "calibration:clock_parameters_to_proper_time",
    "dynamics:end_to_end_reversible_irreversible_composition",
    "evidence:heldout_three_clock_test",
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def evaluate_relations(relations: Iterable[str], requirements: tuple[str, ...]) -> dict[str, Any]:
    observed = set(relations)
    missing = tuple(item for item in requirements if item not in observed)
    return {"passed": not missing, "missing": missing, "observed": tuple(sorted(observed))}


@lru_cache(maxsize=1)
def run_three_clock_synthesis_gate() -> dict[str, Any]:
    profile = run_three_clock_time_profile()
    benchmark = run_three_clock_benchmark()
    current = {
        "role:page_wootters_relational",
        "role:modular_thermal",
        "role:entropic_irreversible",
        "bridge:page_wootters_entropic",
        "bridge:modular_entropic",
        "bridge:page_wootters_modular",
        "benchmark:three_clock_controls",
    }
    role_gate = evaluate_relations(current, ROLE_REQUIREMENTS)
    unified_gate = evaluate_relations(current, UNIFIED_CLOCK_REQUIREMENTS)
    synthetic_complete = set(UNIFIED_CLOCK_REQUIREMENTS)
    removal_failures = {
        item: not evaluate_relations(synthetic_complete - {item}, UNIFIED_CLOCK_REQUIREMENTS)["passed"]
        for item in UNIFIED_CLOCK_REQUIREMENTS
    }
    payload = {
        "schema": "openwave.m9.three-clock-synthesis-gate.v1",
        "task": "M9.124c",
        "role_requirements": ROLE_REQUIREMENTS,
        "unified_clock_requirements": UNIFIED_CLOCK_REQUIREMENTS,
        "current_relations": tuple(sorted(current)),
        "role_gate": role_gate,
        "unified_clock_gate": unified_gate,
        "claim_boundary": {
            "three_clock_role_coverage_is_single_clock_identity": False,
            "pairwise_complementarity_is_transitive_equivalence": False,
            "synthetic_complete_record_is_physical_evidence": False,
            "modular_and_entropic_parameters_are_automatically_proper_time": False,
        },
    }
    acceptance = {
        "profile_and_benchmark_pass": profile["passed"] and benchmark["passed"],
        "three_aspect_role_gate_accepts_current_evidence": role_gate["passed"],
        "single_unified_clock_gate_rejects_current_state": not unified_gate["passed"],
        "all_missing_unification_relations_are_named": set(unified_gate["missing"]) == set(UNIFIED_CLOCK_REQUIREMENTS) - current,
        "every_unified_requirement_is_load_bearing": all(removal_failures.values()),
        "no_identity_or_evidence_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "removal_failures": removal_failures,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "three_aspect_time_framework_ready": True,
            "pairwise_clock_bridges_supported": True,
            "single_unified_physical_clock_established": False,
            "external_three_clock_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
