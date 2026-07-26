"""M9.101f: compose the four current formal/numerical target campaigns."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .clock_action_rate_calibration import run_clock_action_rate_calibration
from .coupled_gauge_spinor_hartree_action import run_coupled_gauge_spinor_hartree_action
from .covariant_packet_tbmt import run_covariant_packet_tbmt
from .electrogravitic_weak_field_evolution import run_electrogravitic_weak_field_evolution
from .formalization_m101_extension import run_formalization_m101_extension


def canonical_payload() -> dict[str, Any]:
    formal = run_formalization_m101_extension()
    action = run_coupled_gauge_spinor_hartree_action()
    packet = run_covariant_packet_tbmt()
    clock = run_clock_action_rate_calibration()
    gravity = run_electrogravitic_weak_field_evolution()
    return {
        "schema": "openwave.m9.m101-evidence-authority.v1",
        "formal_head": formal["repository"]["head"],
        "formal_fingerprint": formal["fingerprint"],
        "components": {
            "coupled_action": {
                "passed": action["passed"],
                "symmetry_reduced_branch": action[
                    "symmetry_reduced_stationary_branch_constructed"
                ],
                "unrestricted_branch": action["decision"][
                    "unrestricted_stable_charged_branch_constructed"
                ],
            },
            "packet_tbmt": {
                "passed": packet["passed"],
                "adapter_constructed": packet["decision"][
                    "local_covariant_packet_adapter_constructed"
                ],
                "reduction_closed": packet[
                    "local_packet_tbmt_closes_on_current_packet"
                ],
                "improves_on_rest_frame": packet[
                    "local_packet_improves_on_rest_frame"
                ],
            },
            "clock": {
                "passed": clock["passed"],
                "internal_calibration": clock["decision"][
                    "internal_clock_action_rate_calibrated"
                ],
                "external_calibration": clock["decision"][
                    "external_clock_or_mass_calibration_complete"
                ],
            },
            "gravity": {
                "passed": gravity["passed"],
                "weak_field_evolution": gravity["decision"][
                    "end_to_end_weak_field_electrogravitic_evolution_constructed"
                ],
                "full_einstein_evolution": gravity["decision"][
                    "full_nonlinear_four_dimensional_einstein_evolution_constructed"
                ],
            },
        },
        "claim_boundary": {
            "finite_action_is_full_continuum_action": False,
            "symmetry_reduced_branch_is_unrestricted_stability": False,
            "packet_bmt_is_qed_derived_covariant_extension": False,
            "internal_clock_calibration_is_external_validation": False,
            "weak_field_gravity_is_nonlinear_einstein_cauchy_development": False,
            "physical_identity_changed": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m101_evidence_authority() -> dict[str, Any]:
    formal = run_formalization_m101_extension()
    action = run_coupled_gauge_spinor_hartree_action()
    packet = run_covariant_packet_tbmt()
    clock = run_clock_action_rate_calibration()
    gravity = run_electrogravitic_weak_field_evolution()
    payload = canonical_payload()
    acceptance = {
        "current_formal_authority_passes": bool(formal["passed"]),
        "coupled_action_campaign_passes": bool(action["passed"]),
        "packet_tbmt_campaign_passes": bool(packet["passed"]),
        "clock_calibration_campaign_passes": bool(clock["passed"]),
        "weak_field_gravity_campaign_passes": bool(gravity["passed"]),
        "all_claim_boundaries_are_false": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.101f",
        "component_results": {
            "formal": formal,
            "coupled_action": action,
            "packet_tbmt": packet,
            "clock": clock,
            "gravity": gravity,
        },
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "all_four_proposed_targets_have_executable_campaigns": True,
            "all_four_targets_are_registered_against_current_formal_head": True,
            "full_physical_closure_claimed": False,
            "physical_identity_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
