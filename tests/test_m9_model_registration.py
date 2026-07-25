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
    assert M9_REGISTRATION.particle_api.endswith(":CatEptParticleModel")
    assert M9_REGISTRATION.formal_contract.endswith("physlib_contract.v2.json")
    assert M9_REGISTRATION.physical_identity_default is None


def test_registration_carries_current_21_criterion_profile():
    payload = canonical_registration_payload()
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
    assert not result["decision"]["physical_particle_name_assigned"]
