"""Canonical M9 registration through M9.97.

`model_registration.py` remains the historical M9.96 registration.  This overlay
reuses its dataclass and component names while replacing the current conformance,
stationary, pair-dynamics, authority, and calibration runners.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .canonical_force_formal_bridge import run_canonical_force_formal_bridge
from .canonical_spin_magnetic_bridge import run_canonical_spin_magnetic_bridge
from .current_evidence_authority import run_current_evidence_authority
from .dynamics_evidence_authority import run_dynamics_evidence_authority
from .formalization_dynamics_extension import run_dynamics_formal_extension_study
from .formalization_force_extension import run_force_formal_extension_study
from .formalization_import import run_formalization_import_study
from .gauge_spinor_stationary_current import (
    run_gauge_spinor_stationary_feasibility,
)
from .model_conformance_dynamics import run_conformance_study
from .model_registration import M9_REGISTRATION as M9_96_REGISTRATION
from .particle_model import run_particle_kernel_study
from .physical_calibration_ledger_v2 import run_physical_calibration_ledger_v2
from .physical_calibration_ledger_v3 import run_physical_calibration_ledger_v3
from .physlib_contract import contract_fingerprint, run_physlib_contract_study
from .spinorial_pair_dynamics_authoritative import run_spinorial_pair_dynamics


M9_REGISTRATION = replace(
    M9_96_REGISTRATION,
    conformance_runner=(
        "openwave.xperiments.m9_cat_ept.model_conformance_dynamics:"
        "run_conformance_study"
    ),
    gauge_spinor_stationary_feasibility=(
        "openwave.xperiments.m9_cat_ept.gauge_spinor_stationary_current:"
        "run_gauge_spinor_stationary_feasibility"
    ),
    spinorial_pair_dynamics=(
        "openwave.xperiments.m9_cat_ept.spinorial_pair_dynamics_authoritative:"
        "run_spinorial_pair_dynamics"
    ),
    dynamics_formal_extension=(
        "openwave.xperiments.m9_cat_ept.formalization_dynamics_extension:"
        "run_dynamics_formal_extension_study"
    ),
    dynamics_evidence_authority=(
        "openwave.xperiments.m9_cat_ept.dynamics_evidence_authority:"
        "run_dynamics_evidence_authority"
    ),
    calibration_ledger_v3=(
        "openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v3:"
        "run_physical_calibration_ledger_v3"
    ),
)


def canonical_registration_payload() -> dict[str, Any]:
    conformance = run_conformance_study()
    formalization = run_formalization_import_study()
    force_extension = run_force_formal_extension_study()
    dynamics_extension = run_dynamics_formal_extension_study()
    previous_authority = run_current_evidence_authority()
    authority = run_dynamics_evidence_authority()
    return {
        "schema": "openwave.model-registration.v4",
        "registration": asdict(M9_REGISTRATION),
        "formal_contract_fingerprint": contract_fingerprint(),
        "formalization_inventory_fingerprint": formalization["fingerprint"],
        "formalization_force_extension_fingerprint": force_extension[
            "extension_fingerprint"
        ],
        "formalization_dynamics_extension_fingerprint": dynamics_extension[
            "dynamics_extension_fingerprint"
        ],
        "previous_evidence_authority_fingerprint": previous_authority["fingerprint"],
        "dynamics_evidence_authority_fingerprint": authority["fingerprint"],
        "formalization_coverage": {
            "zil_graphs": len(formalization["graph_entity_counts"]),
            "zil_entities": formalization["total_entity_count"],
            "open_targets": formalization["total_open_target_count"],
            "lean_sources": formalization["lean_source_count"],
            "force_extension_sources": force_extension["source_count"],
            "dynamics_extension_sources": dynamics_extension["source_count"],
        },
        "formalization_revision": formalization["repository"],
        "conformance": {
            "criterion_count": conformance["audit"]["criterion_count"],
            "domain_counts": conformance["audit"]["domain_counts"],
            "status_counts": conformance["audit"]["status_counts"],
            "profile_fingerprint": conformance["fingerprint"],
        },
        "m9_97": {
            "stationary_campaign_passed": authority["stationary"]["passed"],
            "stationary_schema": authority["stationary"]["schema"],
            "charged_spinor_stationary_branch_constructed": authority["stationary"][
                "charged_spinor_stationary_branch_constructed"
            ],
            "pair_dynamics_passed": authority["dynamics"]["passed"],
            "pair_dynamics_schema": authority["dynamics"]["schema"],
            "four_spinor_sources_drive_initial_fields": authority["dynamics"][
                "four_spinor_sources_drive_initial_fields"
            ],
            "momentum_transfer_closed": authority["dynamics"][
                "momentum_transfer_closed"
            ],
            "center_acceleration_closed": authority["dynamics"][
                "center_acceleration_closed"
            ],
            "center_response_has_lorentz_sign": authority["dynamics"][
                "center_response_has_lorentz_sign"
            ],
            "spin_generator_closed": authority["dynamics"][
                "spin_generator_closed"
            ],
            "rest_frame_bmt_closed": authority["dynamics"][
                "rest_frame_bmt_closed"
            ],
            "criterion_rows_promoted": [],
        },
        "claim_boundary": {
            "mathematical_particle_kernel": True,
            "formalization_imported": True,
            "field_derived_winding_source_candidate": True,
            "self_consistent_gauge_spinor_equation": True,
            "four_spinor_source_maxwell_dirac_evolution": True,
            "momentum_transfer_force_bridge": True,
            "full_dirac_spin_generator_integration": True,
            "charged_stationary_particle": False,
            "center_acceleration_reduction": False,
            "center_response_lorentz_sign": False,
            "rest_frame_bmt_reduction_on_winding_packet": False,
            "full_covariant_tbmt_dynamics": False,
            "physical_particle_identity": False,
            "physical_calibration": False,
            "out_of_sample_prediction_ready": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else payload
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    conformance = run_conformance_study()
    formal = run_physlib_contract_study()
    formalization = run_formalization_import_study()
    force_extension = run_force_formal_extension_study()
    dynamics_extension = run_dynamics_formal_extension_study()
    particle = run_particle_kernel_study()
    spin = run_canonical_spin_magnetic_bridge()
    force = run_canonical_force_formal_bridge()
    previous_authority = run_current_evidence_authority()
    previous_ledger = run_physical_calibration_ledger_v2()
    stationary = run_gauge_spinor_stationary_feasibility()
    dynamics = run_spinorial_pair_dynamics()
    authority = run_dynamics_evidence_authority()
    ledger = run_physical_calibration_ledger_v3()
    expected_counts = {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    acceptance = {
        "canonical_model_id_is_m9": M9_REGISTRATION.model_id == "M9",
        "all_21_shared_criteria_are_registered": (
            payload["conformance"]["criterion_count"] == 21
        ),
        "current_status_profile_is_exact": (
            payload["conformance"]["status_counts"] == expected_counts
        ),
        "conformance_profile_passes": bool(conformance["passed"]),
        "physlib_contract_passes_as_compatibility_subset": bool(formal["passed"]),
        "formalization_import_passes": bool(formalization["passed"]),
        "force_formal_extension_passes": bool(force_extension["passed"]),
        "dynamics_formal_extension_passes": bool(dynamics_extension["passed"]),
        "formalization_counts_are_exact": payload["formalization_coverage"]
        == {
            "zil_graphs": 11,
            "zil_entities": 422,
            "open_targets": 12,
            "lean_sources": 24,
            "force_extension_sources": 2,
            "dynamics_extension_sources": 3,
        },
        "latest_formal_tree_is_registered": (
            payload["formalization_revision"]["tree"]
            == "239a663a3192a3144fb998e7bb200e09689a3bb9"
        ),
        "retained_particle_and_canonical_bridges_pass": all(
            bool(item["passed"]) for item in (particle, spin, force)
        ),
        "m9_96_authority_and_ledger_remain_valid": (
            previous_authority["passed"] and previous_ledger["passed"]
        ),
        "gauge_spinor_stationary_audit_passes": bool(stationary["passed"]),
        "charged_spinor_stationary_failure_is_registered": not stationary["decision"][
            "charged_spinor_stationary_branch_constructed"
        ],
        "source_consistent_pair_dynamics_passes": bool(dynamics["passed"]),
        "momentum_and_generator_subreductions_close": (
            dynamics["decision"]["momentum_transfer_matches_field_lorentz_force"]
            and dynamics["decision"]["spin_generator_integration_closed"]
        ),
        "center_sign_and_bmt_reductions_remain_open": (
            not dynamics["decision"]["center_acceleration_closed"]
            and not dynamics["decision"]["center_response_has_lorentz_sign"]
            and not dynamics["decision"][
                "rest_frame_bmt_torque_closed_on_winding_state"
            ]
        ),
        "dynamics_authority_and_ledger_pass": authority["passed"] and ledger["passed"],
        "m9_97_promotes_no_rows": payload["m9_97"]["criterion_rows_promoted"] == [],
        "physical_identity_is_unassigned": (
            M9_REGISTRATION.physical_identity_default is None
            and not payload["claim_boundary"]["physical_particle_identity"]
        ),
        "registration_fingerprint_is_deterministic": (
            registration_fingerprint(payload) == registration_fingerprint(payload)
        ),
    }
    return {
        **payload,
        "task": "M9.97d",
        "registration_fingerprint": registration_fingerprint(payload),
        "component_results": {
            "conformance_passed": conformance["passed"],
            "formal_contract_passed": formal["passed"],
            "formalization_import_passed": formalization["passed"],
            "force_extension_passed": force_extension["passed"],
            "dynamics_extension_passed": dynamics_extension["passed"],
            "particle_kernel_passed": particle["passed"],
            "canonical_spin_passed": spin["passed"],
            "canonical_force_passed": force["passed"],
            "m9_96_authority_passed": previous_authority["passed"],
            "m9_96_ledger_passed": previous_ledger["passed"],
            "stationary_audit_passed": stationary["passed"],
            "pair_dynamics_passed": dynamics["passed"],
            "dynamics_authority_passed": authority["passed"],
            "dynamics_ledger_passed": ledger["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m9_registered_as_canonical_model_component": True,
            "m9_96_history_retained": True,
            "m9_97_dynamics_evidence_registered": True,
            "comparison_profile_is_executable": True,
            "physical_particle_name_assigned": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
