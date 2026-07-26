import openwave.xperiments.m9_cat_ept.model_registration_reconciliation as registration


def _previous_payload():
    return {
        "schema": "openwave.model-registration.v5",
        "claim_boundary": {
            "physical_particle_identity": False,
            "zil_runtime_current": True,
        },
        "conformance": {
            "status_counts": {
                "validated": 7,
                "partial": 13,
                "negative": 1,
                "not_yet": 0,
            }
        },
    }


def _authority():
    return {
        "passed": True,
        "fingerprint": "a" * 64,
        "formal_branch": "entropic-physlib-linear-full",
        "closed_infrastructure": {
            "current_formal_equations_machine_mapped": True,
            "schrodinger_mass_map_consistent": True,
            "one_discrete_differential_complex": True,
            "shared_maxwell_constraints": True,
            "exact_dirac_center_observable_measured": True,
            "momentum_lorentz_retained": True,
        },
        "open_boundaries": {
            "formal_hartree_coupling_selected": False,
            "single_action_derivation_completed": False,
            "charged_stationary_branch_constructed": False,
            "foldy_wouthuysen_position_projection_constructed": False,
            "covariant_packet_tbmt_reduction_constructed": False,
            "physical_calibration_complete": False,
        },
        "component_results": {
            "equation_contract_passed": True,
            "reconciled_stationary_passed": True,
            "dirac_observables_passed": True,
        },
        "decision": {
            "full_current_formal_target_numerically_closed": False,
        },
    }


def test_schema_v6_payload_preserves_statuses(monkeypatch):
    monkeypatch.setattr(registration, "m9_98_registration_payload", _previous_payload)
    monkeypatch.setattr(
        registration,
        "run_formal_numerical_reconciliation_authority",
        _authority,
    )
    payload = registration.canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v6"
    assert payload["formal_numerical_branch"] == "entropic-physlib-linear-full"
    assert payload["m9_99"]["criterion_rows_promoted"] == []
    assert not payload["m9_99"]["legacy_disagreements_are_lean_contradictions"]
    assert not payload["m9_99"]["full_current_formal_target_numerically_closed"]
    assert payload["conformance"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }


def test_schema_v6_claim_boundaries_remain_open(monkeypatch):
    monkeypatch.setattr(registration, "m9_98_registration_payload", _previous_payload)
    monkeypatch.setattr(
        registration,
        "run_formal_numerical_reconciliation_authority",
        _authority,
    )
    payload = registration.canonical_registration_payload()
    assert payload["claim_boundary"]["current_formal_equations_machine_mapped"]
    assert payload["claim_boundary"]["one_discrete_differential_complex"]
    assert payload["claim_boundary"]["schrodinger_pauli_mass_map_consistent"]
    assert payload["claim_boundary"]["dirac_center_observable_corrected"]
    assert not payload["claim_boundary"]["formal_hartree_coupling_selected"]
    assert not payload["claim_boundary"]["single_action_derivation_complete"]
    assert not payload["claim_boundary"][
        "formal_numerical_reconciliation_promotes_physical_criteria"
    ]


def test_registration_fingerprint_accepts_explicit_payload():
    payload = {"schema": "test", "value": 1}
    digest = registration.registration_fingerprint(payload)
    assert len(digest) == 64
    assert digest == registration.registration_fingerprint(payload)
