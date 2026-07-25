from openwave.xperiments.m9_cat_ept.model_registration_zil import (
    M9_REGISTRATION,
    canonical_registration_payload,
    registration_fingerprint,
    run_model_registration_study,
)


def test_zil_registration_overlay_preserves_m9_component_and_statuses():
    payload = canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v5"
    assert M9_REGISTRATION.model_id == "M9"
    assert payload["zil_runtime_revision"] == {
        "name": "jagg-ix/zil-lean",
        "branch": "main",
        "head": "3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc",
    }
    assert payload["m9_98"] == {
        "zil_runtime_upgrade_passed": True,
        "physlib_root": "Zil",
        "openwave_graph_root": "Zil.Native",
        "formal_or_physical_status_changed": False,
    }
    assert payload["conformance"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }


def test_zil_registration_records_exact_runtime_coverage():
    payload = canonical_registration_payload()
    assert payload["zil_runtime_coverage"] == {
        "runtime_sources": 6,
        "openwave_native_graphs": 4,
        "historical_pins": 2,
    }
    assert payload["claim_boundary"]["zil_runtime_current"]
    assert payload["claim_boundary"]["zil_dual_root_contract_explicit"]
    assert not payload["claim_boundary"]["zil_runtime_is_lean_proof_authority"]
    assert not payload["claim_boundary"]["zil_upgrade_promotes_physical_criteria"]


def test_zil_registration_fingerprint_is_deterministic():
    payload = canonical_registration_payload()
    assert len(registration_fingerprint(payload)) == 64
    assert registration_fingerprint(payload) == registration_fingerprint(payload)


def test_full_zil_registration_study_passes_without_promotion():
    result = run_model_registration_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["zil_runtime_upgraded"]
    assert result["decision"]["dual_root_contract_registered"]
    assert not result["decision"]["historical_zil_pins_are_current_authority"]
    assert result["decision"]["criterion_rows_promoted"] == []
