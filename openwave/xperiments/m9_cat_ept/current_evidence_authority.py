"""Current-tree evidence authority for CAT/EPT identity and force claims.

This module composes the current formal-tree overlay with the M9.96 charged
branch, Maxwell-source, and force-triangle studies. It is the current authority
surface for new identity decisions; the older selected PhysLib contract remains
a historical compatibility subset.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .charged_branch_feasibility import run_charged_branch_feasibility
from .charged_maxwell_source_bridge import run_charged_maxwell_source_bridge
from .field_force_triangle import run_field_force_triangle
from .formalization_force_extension import run_force_formal_extension_study


def authority_fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_current_evidence_authority() -> dict[str, Any]:
    formal = run_force_formal_extension_study()
    branch = run_charged_branch_feasibility()
    source = run_charged_maxwell_source_bridge()
    force = run_field_force_triangle()
    payload = {
        "schema": "openwave.m9.current-evidence-authority.v1",
        "task": "M9.96-authority",
        "formal": {
            "base_inventory_fingerprint": formal["base_inventory_fingerprint"],
            "force_extension_fingerprint": formal["extension_fingerprint"],
            "source_count": formal["source_count"],
        },
        "charged_branch": {
            "campaign_passed": branch["passed"],
            "passing_candidate_count": branch["passing_candidate_count"],
            "charged_stationary_branch_constructed": branch["decision"][
                "charged_stationary_branch_constructed"
            ],
        },
        "maxwell_source": {
            "passed": source["passed"],
            "same_field_supplies_charge_current_and_moment": source["decision"][
                "same_field_supplies_winding_charge_current_and_moment"
            ],
            "static_constraints_closed": source["decision"][
                "static_maxwell_source_equations_closed"
            ],
            "magnetic_response_closed": source["decision"][
                "magnetic_moment_response_closed_on_candidate"
            ],
        },
        "force_triangle": {
            "passed": force["passed"],
            "field_force_triangle_closed": force["decision"][
                "field_derived_force_triangle_closed_on_charged_candidates"
            ],
            "center_acceleration_measured": force["decision"][
                "center_acceleration_measured_from_full_pde"
            ],
        },
        "status": {
            "magnetic_moment_spin": "partial",
            "electric_force": "partial",
            "magnetic_force": "partial",
        },
    }
    acceptance = {
        "formal_current_tree_overlay_passes": bool(formal["passed"]),
        "charged_feasibility_campaign_passes_as_an_honest_audit": bool(
            branch["passed"]
        ),
        "charged_stationary_failure_is_explicit": not branch["decision"][
            "charged_stationary_branch_constructed"
        ],
        "maxwell_source_bridge_passes": bool(source["passed"]),
        "force_triangle_passes": bool(force["passed"]),
        "three_partial_statuses_are_preserved": set(payload["status"].values())
        == {"partial"},
        "no_full_pde_acceleration_is_inferred": not force["decision"][
            "center_acceleration_measured_from_full_pde"
        ],
    }
    fingerprint = authority_fingerprint(payload)
    return {
        **payload,
        "fingerprint": fingerprint,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "current_evidence_authority_complete": True,
            "historical_selected_contract_is_sufficient_for_new_identity": False,
            "physical_identity_established": False,
            "criterion_rows_promoted": [],
        },
    }


def evaluate_current_identity(
    model: Any,
    state: Any,
    evidence: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    authority = run_current_evidence_authority()
    observables = model.measure(state)
    supplied = dict(evidence or {})
    external = (
        "charge_unit_calibrated",
        "rest_energy_calibrated",
        "clock_identified",
        "spin_and_exchange_closed_on_same_branch",
        "physical_magnetic_moment_calibrated",
        "physical_force_calibrated",
        "out_of_sample_prediction",
    )
    gates = {
        "current_evidence_authority_passes": bool(authority["passed"]),
        "state_is_normalized": observables["normalization_error"] <= 2.0e-10,
        "state_is_localized": observables["boundary_fraction"] <= 2.0e-2,
        "state_sector_matches_model": (
            state.declared_winding_sector == model.spec.winding_sector
        ),
        "winding_sector_is_embedded": bool(state.winding_embedded),
        "charged_stationary_branch_is_closed": authority["charged_branch"][
            "charged_stationary_branch_constructed"
        ],
        "maxwell_source_and_moment_are_closed": authority["maxwell_source"][
            "passed"
        ],
        "field_force_triangle_is_closed": authority["force_triangle"]["passed"],
        "physical_name_is_requested": model.spec.physical_assignment is not None,
        "calibration_record_is_present": model.spec.calibration_id is not None,
        **{name: bool(supplied.get(name, False)) for name in external},
    }
    passed = all(gates.values())
    return {
        "schema": "openwave.m9.current-identity-certificate.v1",
        "particle_id": model.spec.particle_id,
        "requested_assignment": model.spec.physical_assignment,
        "authority_fingerprint": authority["fingerprint"],
        "gates": gates,
        "passed": passed,
        "decision": {
            "physical_identity_established": passed,
            "current_charged_stationary_failure_blocks_identity": not authority[
                "charged_branch"
            ]["charged_stationary_branch_constructed"],
            "historical_contract_alone_is_not_authoritative": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
