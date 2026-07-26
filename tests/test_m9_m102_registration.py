import openwave.xperiments.m9_cat_ept.model_registration_m102 as registration


def fake_previous():
    return {
        "schema": "openwave.model-registration.v9",
        "claim_boundary": {
            "historical_boundary": False,
        },
    }


def fake_conformance():
    return {
        "schema": "openwave.m9.models-conformance.v19",
        "summary": {
            "validated_in_scope": 7,
            "conditional_validated": 5,
            "reduced_model_validated": 3,
            "calibration_pending": 1,
            "candidate": 4,
            "negative": 1,
        },
        "maturity": {
            "policy": {
                "carrier_implementation_is_not_state_existence": True,
            }
        },
        "m9_101_reproducibility": {
            "policy": {
                "fresh_snapshot_generation_and_verification_available": True,
                "committed_post_merge_reference_snapshots_present": False,
            }
        },
    }


def test_schema_v10_registers_live_and_historical_formal_heads(monkeypatch):
    monkeypatch.setattr(registration, "m9_101_payload", fake_previous)
    monkeypatch.setattr(registration, "conformance_payload", fake_conformance)
    payload = registration.canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v10"
    assert payload["m9_102"]["historical_formal_head"] == (
        "acdbe8ce6456e66837bd18604cf3107d3181c4de"
    )
    assert payload["m9_102"]["current_formal_head"] == (
        "eba0124fcfbc1216d973bb6f504c5a6d324de60c"
    )
    assert len(payload["m9_102"]["governance_sources"]) == 3


def test_registration_does_not_hide_missing_committed_snapshots(monkeypatch):
    monkeypatch.setattr(registration, "m9_101_payload", fake_previous)
    monkeypatch.setattr(registration, "conformance_payload", fake_conformance)
    payload = registration.canonical_registration_payload()
    assert payload["m9_102"]["snapshot_generation_available"]
    assert not payload["m9_102"]["committed_post_merge_reference_snapshots_present"]
    assert payload["m9_102"]["physical_claims_promoted"] == []
    assert not payload["claim_boundary"]["carrier_implementation_is_state_existence"]
    assert not payload["claim_boundary"]["snapshot_contract_is_external_validation"]
