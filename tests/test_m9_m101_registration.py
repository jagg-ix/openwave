import openwave.xperiments.m9_cat_ept.model_registration_m101 as registration


def fake_previous():
    return {
        "schema": "openwave.model-registration.v8",
        "claim_boundary": {
            "criterion_maturity_is_multi_axis": True,
        },
    }


def fake_conformance():
    return {
        "schema": "openwave.m9.models-conformance.v18",
        "formal_head": "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "summary": {
            "validated_in_scope": 7,
            "conditional_validated": 5,
            "reduced_model_validated": 3,
            "calibration_pending": 1,
            "candidate": 4,
            "negative": 1,
        },
        "m9_101": {
            "coupled_action": {"passed": True},
            "packet_tbmt": {"passed": True},
            "clock": {"passed": True},
            "gravity": {"passed": True},
        },
    }


def test_schema_v9_registers_all_four_scoped_campaigns(monkeypatch):
    monkeypatch.setattr(registration, "m9_100_payload", fake_previous)
    monkeypatch.setattr(registration, "conformance_payload", fake_conformance)
    payload = registration.canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v9"
    assert payload["m9_101"]["formal_head"] == "acdbe8ce6456e66837bd18604cf3107d3181c4de"
    assert payload["m9_101"]["coupled_action_registered"]
    assert payload["m9_101"]["packet_tbmt_registered"]
    assert payload["m9_101"]["clock_calibration_registered"]
    assert payload["m9_101"]["weak_field_gravity_registered"]
    assert payload["m9_101"]["physical_claims_promoted"] == []


def test_new_claim_boundaries_are_fail_closed(monkeypatch):
    monkeypatch.setattr(registration, "m9_100_payload", fake_previous)
    monkeypatch.setattr(registration, "conformance_payload", fake_conformance)
    boundary = registration.canonical_registration_payload()["claim_boundary"]
    assert not boundary["finite_coupled_action_is_full_continuum_action"]
    assert not boundary["symmetry_reduced_branch_is_unrestricted_stability"]
    assert not boundary["packet_tbmt_is_qed_derived_covariant_extension"]
    assert not boundary["internal_clock_calibration_is_external_validation"]
    assert not boundary["weak_field_gravity_is_full_einstein_development"]
