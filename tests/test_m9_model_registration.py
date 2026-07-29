from openwave.xperiments.m9_cat_ept.model_registration import (
    M9_REGISTRATION,
    canonical_registration_payload,
    registration_fingerprint,
    run_model_registration_study,
)


def test_m9_registration_names_all_canonical_surfaces():
    assert M9_REGISTRATION.model_id == "M9"
    assert M9_REGISTRATION.key == "m9_cat_ept"
    assert M9_REGISTRATION.launcher.endswith("/_launcher.py")
    assert M9_REGISTRATION.comparison_profile == "MODELS_M9.md"
    assert M9_REGISTRATION.conformance_runner.endswith(
        "model_conformance_dynamics:run_conformance_study"
    )
    assert M9_REGISTRATION.particle_api.endswith(":CatEptParticleModel")
    assert M9_REGISTRATION.formal_contract.endswith("physlib_contract.v2.json")
    assert M9_REGISTRATION.formalization_import.endswith(
        ":run_formalization_import_study"
    )
    assert M9_REGISTRATION.canonical_spin_bridge.endswith(
        ":run_canonical_spin_magnetic_bridge"
    )
    assert M9_REGISTRATION.canonical_force_bridge.endswith(
        ":run_canonical_force_formal_bridge"
    )
    assert M9_REGISTRATION.charged_branch_feasibility.endswith(
        ":run_charged_branch_feasibility"
    )
    assert M9_REGISTRATION.charged_maxwell_source_bridge.endswith(
        ":run_charged_maxwell_source_bridge"
    )
    assert M9_REGISTRATION.field_force_triangle.endswith(":run_field_force_triangle")
    assert M9_REGISTRATION.current_evidence_authority.endswith(
        ":run_current_evidence_authority"
    )
    assert M9_REGISTRATION.calibration_ledger_v2.endswith(
        ":run_physical_calibration_ledger_v2"
    )
    assert M9_REGISTRATION.gauge_spinor_stationary_feasibility.endswith(
        "gauge_spinor_stationary_current:run_gauge_spinor_stationary_feasibility"
    )
    assert M9_REGISTRATION.spinorial_pair_dynamics.endswith(
        "spinorial_pair_dynamics_authoritative:run_spinorial_pair_dynamics"
    )
    assert M9_REGISTRATION.dynamics_formal_extension.endswith(
        ":run_dynamics_formal_extension_study"
    )
    assert M9_REGISTRATION.dynamics_evidence_authority.endswith(
        ":run_dynamics_evidence_authority"
    )
    assert M9_REGISTRATION.calibration_ledger_v3.endswith(
        ":run_physical_calibration_ledger_v3"
    )
    assert M9_REGISTRATION.physical_identity_default is None


def test_registration_carries_current_21_criterion_profile():
    payload = canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v4"
    assert payload["conformance"]["criterion_count"] == 21
    assert payload["conformance"]["domain_counts"] == {
        "particles": 12,
        "forces": 5,
        "waves": 3,
        "thermal": 1,
    }
    assert payload["conformance"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    assert payload["formalization_coverage"] == {
        "zil_graphs": 11,
        "zil_entities": 422,
        "open_targets": 12,
        "lean_sources": 24,
        "force_extension_sources": 2,
        "dynamics_extension_sources": 3,
    }
    assert payload["formalization_revision"] == {
        "name": "jagg-ix/entropic-physlib-private",
        "branch": "entropic-physlib-linear-full",
        "base_commit": "e10af9a3b47bf90afc0a88167a5d495b6935f4dc",
        "tree": "239a663a3192a3144fb998e7bb200e09689a3bb9",
        "module_index_path": "Physlib.lean",
        "module_index_blob": "182a06e0f50314ec54436da602b4ac86eba4ee08",
    }
    assert payload["m9_97"]["stationary_campaign_passed"]
    assert payload["m9_97"]["pair_dynamics_passed"]
    assert payload["m9_97"]["four_spinor_sources_drive_initial_fields"]
    assert payload["m9_97"]["momentum_transfer_closed"]
    assert payload["m9_97"]["spin_generator_closed"]
    assert not payload["m9_97"]["charged_spinor_stationary_branch_constructed"]
    assert not payload["m9_97"]["center_acceleration_closed"]
    assert not payload["m9_97"]["center_response_has_lorentz_sign"]
    assert not payload["m9_97"]["rest_frame_bmt_closed"]
    assert payload["m9_97"]["criterion_rows_promoted"] == []
    assert payload["claim_boundary"]["formalization_imported"]
    assert payload["claim_boundary"]["self_consistent_gauge_spinor_equation"]
    assert payload["claim_boundary"]["four_spinor_source_maxwell_dirac_evolution"]
    assert payload["claim_boundary"]["momentum_transfer_force_bridge"]
    assert payload["claim_boundary"]["full_dirac_spin_generator_integration"]
    assert not payload["claim_boundary"]["charged_stationary_particle"]
    assert not payload["claim_boundary"]["center_acceleration_reduction"]
    assert not payload["claim_boundary"]["center_response_lorentz_sign"]
    assert not payload["claim_boundary"]["rest_frame_bmt_reduction_on_winding_packet"]
    assert not payload["claim_boundary"]["full_covariant_tbmt_dynamics"]
    assert not payload["claim_boundary"]["physical_particle_identity"]
    assert not payload["claim_boundary"]["physical_calibration"]


def test_registration_fingerprint_is_deterministic():
    payload = canonical_registration_payload()
    assert len(registration_fingerprint(payload)) == 64
    assert registration_fingerprint(payload) == registration_fingerprint(payload)


def test_full_registration_study_passes():
    result = run_model_registration_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["m9_registered_as_canonical_model_component"]
    assert result["decision"]["m9_96_history_retained"]
    assert result["decision"]["m9_97_dynamics_evidence_registered"]
    assert result["decision"]["criterion_rows_promoted"] == []
    assert not result["decision"]["physical_particle_name_assigned"]
