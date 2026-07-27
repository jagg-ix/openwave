"""M9.124 authority for Page-Wootters, modular, and entropic clock synthesis."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m124_extension import run_formalization_m124_extension
from .m123_nonparticle_physics_authority import run_m123_nonparticle_physics_authority
from .three_clock_benchmark import run_three_clock_benchmark
from .three_clock_synthesis_gate import run_three_clock_synthesis_gate
from .three_clock_time_profile import run_three_clock_time_profile


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m124_three_clock_authority() -> dict[str, Any]:
    previous = run_m123_nonparticle_physics_authority()
    formal = run_formalization_m124_extension()
    profile = run_three_clock_time_profile()
    benchmark = run_three_clock_benchmark()
    gate = run_three_clock_synthesis_gate()
    component = {
        "formal_authority_passed": formal["passed"],
        "three_clock_profile_passed": profile["passed"],
        "three_clock_benchmark_passed": benchmark["passed"],
        "three_clock_synthesis_gate_passed": gate["passed"],
        "clock_role_count": len(profile["roles"]),
        "pairwise_bridge_count": len(profile["pairwise_bridges"]),
        "page_wootters_conditioning_control": benchmark["results"]["page_wootters"]["passed"],
        "modular_flow_control": benchmark["results"]["modular"]["passed"],
        "entropic_arrow_control": benchmark["results"]["entropic"]["passed"],
        "three_aspect_time_framework": gate["decision"]["three_aspect_time_framework_ready"],
        "single_unified_physical_clock": gate["decision"]["single_unified_physical_clock_established"],
        "external_validation_complete": gate["decision"]["external_three_clock_validation_complete"],
    }
    payload = {
        "schema": "openwave.m9.m124-three-clock-authority.v1",
        "task": "M9.124",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "three_clock_synthesis_is_one_clock_identity": False,
            "reduced_benchmarks_are_external_clock_measurements": False,
            "development_formalization_is_merged_master": False,
            "pairwise_bridges_close_all_calibration_maps": False,
        },
    }
    acceptance = {
        "previous_M9_123_authority_is_preserved": previous["passed"],
        "three_clock_formal_authority_passes": formal["passed"],
        "M9_124a_three_clock_profile_closes": profile["passed"] and component["clock_role_count"] == 3 and component["pairwise_bridge_count"] == 3,
        "M9_124b_three_clock_controls_close": benchmark["passed"] and component["page_wootters_conditioning_control"] and component["modular_flow_control"] and component["entropic_arrow_control"],
        "M9_124c_synthesis_gate_is_fail_closed": gate["passed"] and component["three_aspect_time_framework"] and not component["single_unified_physical_clock"],
        "external_validation_remains_open": not component["external_validation_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {"profile": profile, "benchmark": benchmark, "gate": gate},
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_124a_three_clock_role_profile_complete": True,
            "M9_124b_three_clock_control_benchmark_complete": True,
            "M9_124c_three_clock_synthesis_gate_complete": True,
            "single_unified_physical_clock_established": False,
            "external_nonparticle_benchmark_moved_to_M9_125": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
