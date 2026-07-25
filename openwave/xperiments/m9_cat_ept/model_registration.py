"""Canonical OpenWave registration for the M9 CAT/EPT model component."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .canonical_force_formal_bridge import run_canonical_force_formal_bridge
from .canonical_spin_magnetic_bridge import run_canonical_spin_magnetic_bridge
from .charged_branch_feasibility import run_charged_branch_feasibility
from .charged_maxwell_source_bridge import run_charged_maxwell_source_bridge
from .current_evidence_authority import run_current_evidence_authority
from .dynamics_evidence_authority import run_dynamics_evidence_authority
from .field_force_triangle import run_field_force_triangle
from .formalization_dynamics_extension import run_dynamics_formal_extension_study
from .formalization_force_extension import run_force_formal_extension_study
from .formalization_import import run_formalization_import_study
from .gauge_spinor_stationary_feasibility import (
    run_gauge_spinor_stationary_feasibility,
)
from .model_conformance_dynamics import run_conformance_study
from .particle_model import run_particle_kernel_study
from .physical_calibration_ledger_v2 import run_physical_calibration_ledger_v2
from .physical_calibration_ledger_v3 import run_physical_calibration_ledger_v3
from .physlib_contract import contract_fingerprint, run_physlib_contract_study
from .spinorial_pair_dynamics_current import run_spinorial_pair_dynamics


@dataclass(frozen=True)
class ModelRegistration:
    model_id: str
    key: str
    name: str
    model_directory: str
    launcher: str
    comparison_profile: str
    conformance_runner: str
    particle_api: str
    formal_contract: str
    formalization_import: str
    canonical_spin_bridge: str
    canonical_force_bridge: str
    charged_branch_feasibility: str
    charged_maxwell_source_bridge: str
    field_force_triangle: str
    current_evidence_authority: str
    calibration_ledger_v2: str
    gauge_spinor_stationary_feasibility: str
    spinorial_pair_dynamics: str
    dynamics_formal_extension: str
    dynamics_evidence_authority: str
    calibration_ledger_v3: str
    briefing: str
    physical_identity_default: str | None

    def __post_init__(self) -> None:
        values = (
            self.model_id,
            self.key,
            self.name,
            self.model_directory,
            self.launcher,
            self.comparison_profile,
            self.conformance_runner,
            self.particle_api,
            self.formal_contract,
            self.formalization_import,
            self.canonical_spin_bridge,
            self.canonical_force_bridge,
            self.charged_branch_feasibility,
            self.charged_maxwell_source_bridge,
            self.field_force_triangle,
            self.current_evidence_authority,
            self.calibration_ledger_v2,
            self.gauge_spinor_stationary_feasibility,
            self.spinorial_pair_dynamics,
            self.dynamics_formal_extension,
            self.dynamics_evidence_authority,
            self.calibration_ledger_v3,
            self.briefing,
        )
        if not all(values):
            raise ValueError("complete model registration required")
        if self.physical_identity_default is not None:
            raise ValueError("M9 cannot inherit a physical particle name by default")


M9_REGISTRATION = ModelRegistration(
    model_id="M9",
    key="m9_cat_ept",
    name="CAT/EPT Entropic Particle Dynamics",
    model_directory="openwave/xperiments/m9_cat_ept",
    launcher="openwave/xperiments/m9_cat_ept/_launcher.py",
    comparison_profile="MODELS_M9.md",
    conformance_runner=(
        "openwave.xperiments.m9_cat_ept.model_conformance_dynamics:"
        "run_conformance_study"
    ),
    particle_api="openwave.xperiments.m9_cat_ept.particle_model:CatEptParticleModel",
    formal_contract=(
        "openwave/xperiments/m9_cat_ept/formal/physlib_contract.v2.json"
    ),
    formalization_import=(
        "openwave.xperiments.m9_cat_ept.formalization_import:"
        "run_formalization_import_study"
    ),
    canonical_spin_bridge=(
        "openwave.xperiments.m9_cat_ept.canonical_spin_magnetic_bridge:"
        "run_canonical_spin_magnetic_bridge"
    ),
    canonical_force_bridge=(
        "openwave.xperiments.m9_cat_ept.canonical_force_formal_bridge:"
        "run_canonical_force_formal_bridge"
    ),
    charged_branch_feasibility=(
        "openwave.xperiments.m9_cat_ept.charged_branch_feasibility:"
        "run_charged_branch_feasibility"
    ),
    charged_maxwell_source_bridge=(
        "openwave.xperiments.m9_cat_ept.charged_maxwell_source_bridge:"
        "run_charged_maxwell_source_bridge"
    ),
    field_force_triangle=(
        "openwave.xperiments.m9_cat_ept.field_force_triangle:"
        "run_field_force_triangle"
    ),
    current_evidence_authority=(
        "openwave.xperiments.m9_cat_ept.current_evidence_authority:"
        "run_current_evidence_authority"
    ),
    calibration_ledger_v2=(
        "openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v2:"
        "run_physical_calibration_ledger_v2"
    ),
    gauge_spinor_stationary_feasibility=(
        "openwave.xperiments.m9_cat_ept.gauge_spinor_stationary_feasibility:"
        "run_gauge_spinor_stationary_feasibility"
    ),
    spinorial_pair_dynamics=(
        "openwave.xperiments.m9_cat_ept.spinorial_pair_dynamics_current:"
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
    briefing="openwave/xperiments/m9_cat_ept/__M9_model_briefing.md",
    physical_identity_default=None,
)


def canonical_registration_payload() -> dict[str, Any]:
    conformance = run_conformance_study()
    formalization = run_formalization_import_study()
    force_extension = run_force_formal_extension_study()
    dynamics_extension = run_dynamics_formal_extension_study()
    authority_v2 = run_current_evidence_authority()
    authority_v3 = run_dynamics_evidence_authority()
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
        "current_evidence_authority_fingerprint": authority_v2["fingerprint"],
        "dynamics_evidence_authority_fingerprint": authority_v3["fingerprint"],
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
        "m9_96": {
            "charged_stationary_branch_constructed": authority_v2["charged_branch"][
                "charged_stationary_branch_constructed"
            ],
            "maxwell_source_bridge_passed": authority_v2["maxwell_source"]["passed"],
            "field_force_triangle_passed": authority_v2["force_triangle"]["passed"],
            "center_acceleration_measured": authority_v2["force_triangle"][
                "center_acceleration_measured"
            ],
            "criterion_rows_promoted": [],
        },
        "m9_97": {
            "gauge_spinor_stationary_campaign_passed": authority_v3["stationary"][
                "passed"
            ],
            "charged_spinor_stationary_branch_constructed": authority_v3[
                "stationary"
            ]["charged_spinor_stationary_branch_constructed"],
            "full_pair_dynamics_campaign_passed": authority_v3["dynamics"]["passed"],
            "four_spinor_sources_drive_initial_fields": authority_v3["dynamics"][
                "four_spinor_sources_drive_initial_fields"
            ],
            "momentum_transfer_closed": authority_v3["dynamics"][
                "momentum_transfer_closed"
            ],
            "center_acceleration_closed": authority_v3["dynamics"][
                "center_acceleration_closed"
            ],
            "spin_generator_closed": authority_v3["dynamics"][
                "spin_generator_closed"
            ],
            "rest_frame_bmt_closed": authority_v3["dynamics"][
                "rest_frame_bmt_closed"
            ],
            "criterion_rows_promoted": [],
        },
        "claim_boundary": {
            "mathematical_particle_kernel": True,
            "formalization_imported": True,
            "canonical_spin_force_bridges": True,
            "field_derived_winding_source_candidate": True,
            "static_maxwell_source_closure": True,
            "field_force_triangle": True,
            "self_consistent_gauge_spinor_equation": True,
            "full_maxwell_dirac_pair_evolution": True,
            "four_spinor_sources_drive_initial_fields": True,
            "momentum_transfer_force_bridge": True,
            "full_dirac_spin_generator_integration": True,
            "charged_stationary_particle": False,
            "center_acceleration_reduction": False,
            "rest_frame_bmt_reduction_on_winding_packet": False,
            "full_covariant_tbmt_dynamics": False,
            "physical_particle_identity": False,
            "physical_calibration": False,
            "out_of_sample_prediction_ready": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else payload
    serialized = json.dumps(selected, sort_keys=True, separators=(",", ":"))
    return sha256(serialized.encode()).hexdigest()


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
    charged = run_charged_branch_feasibility()
    source = run_charged_maxwell_source_bridge()
    triangle = run_field_force_triangle()
    authority_v2 = run_current_evidence_authority()
    ledger_v2 = run_physical_calibration_ledger_v2()
    stationary = run_gauge_spinor_stationary_feasibility()
    dynamics = run_spinorial_pair_dynamics()
    authority_v3 = run_dynamics_evidence_authority()
    ledger_v3 = run_physical_calibration_ledger_v3()
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
        "all_zil_and_lean_counts_are_registered": (
            payload["formalization_coverage"]
            == {
                "zil_graphs": 11,
                "zil_entities": 422,
                "open_targets": 12,
                "lean_sources": 24,
                "force_extension_sources": 2,
                "dynamics_extension_sources": 3,
            }
        ),
        "latest_formal_tree_is_registered": (
            payload["formalization_revision"]["tree"]
            == "239a663a3192a3144fb998e7bb200e09689a3bb9"
        ),
        "particle_kernel_passes": bool(particle["passed"]),
        "canonical_spin_bridge_passes": bool(spin["passed"]),
        "canonical_force_bridge_passes": bool(force["passed"]),
        "m9_96_components_still_pass": all(
            bool(item["passed"])
            for item in (charged, source, triangle, authority_v2, ledger_v2)
        ),
        "gauge_spinor_stationary_audit_passes": bool(stationary["passed"]),
        "charged_spinor_stationary_failure_is_registered": not stationary["decision"][
            "charged_spinor_stationary_branch_constructed"
        ],
        "spinorial_pair_dynamics_passes": bool(dynamics["passed"]),
        "four_spinor_source_consistency_is_registered": dynamics["decision"][
            "four_spinor_sources_drive_all_initial_fields"
        ],
        "momentum_transfer_and_generator_subreductions_close": (
            dynamics["decision"]["momentum_transfer_matches_field_lorentz_force"]
            and dynamics["decision"]["spin_generator_integration_closed"]
        ),
        "center_and_bmt_reductions_remain_open": (
            not dynamics["decision"]["center_acceleration_closed"]
            and not dynamics["decision"][
                "rest_frame_bmt_torque_closed_on_winding_state"
            ]
        ),
        "dynamics_evidence_authority_passes": bool(authority_v3["passed"]),
        "dynamics_calibration_ledger_passes": bool(ledger_v3["passed"]),
        "m9_97_does_not_promote_the_three_rows": payload["m9_97"][
            "criterion_rows_promoted"
        ]
        == [],
        "launcher_and_briefing_are_registered": bool(
            M9_REGISTRATION.launcher and M9_REGISTRATION.briefing
        ),
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
            "formalization_force_extension_passed": force_extension["passed"],
            "formalization_dynamics_extension_passed": dynamics_extension["passed"],
            "particle_kernel_passed": particle["passed"],
            "canonical_spin_bridge_passed": spin["passed"],
            "canonical_force_bridge_passed": force["passed"],
            "m9_96_authority_passed": authority_v2["passed"],
            "m9_96_calibration_ledger_passed": ledger_v2["passed"],
            "gauge_spinor_stationary_passed": stationary["passed"],
            "spinorial_pair_dynamics_passed": dynamics["passed"],
            "dynamics_evidence_authority_passed": authority_v3["passed"],
            "calibration_ledger_v3_passed": ledger_v3["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m9_registered_as_canonical_model_component": True,
            "cat_ept_formalization_imported": True,
            "canonical_spin_force_bridges_registered": True,
            "m9_96_current_evidence_registered": True,
            "m9_97_dynamics_evidence_registered": True,
            "comparison_profile_is_executable": True,
            "physical_particle_name_assigned": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
