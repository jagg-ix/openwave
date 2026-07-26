from openwave.xperiments.m9_cat_ept.model_conformance_maturity_current import (
    canonical_payload as conformance_payload,
    run_conformance_study,
)
from openwave.xperiments.m9_cat_ept.model_registration_maturity_current import (
    canonical_registration_payload,
)


def test_current_conformance_uses_maturity_summary():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.models-conformance.v17"
    assert result["summary"] == {
        "validated_in_scope": 7,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 1,
        "total": 21,
    }
    assert not result["legacy_compatibility"]["statuses_are_primary"]


def test_registration_v8_removes_fixed_status_gate():
    payload = canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v8"
    assert payload["m9_100"]["multi_axis_maturity_registered"]
    assert not payload["m9_100"]["legacy_scalar_status_is_primary"]
    assert not payload["claim_boundary"]["legacy_7_13_1_is_acceptance_gate"]
    assert payload["m9_100"]["physical_claims_promoted"] == []
    assert not payload["claim_boundary"]["maturity_reclassification_implies_physical_identity"]
    assert not payload["claim_boundary"]["maturity_reclassification_implies_calibration"]


def test_legacy_profile_is_retained_only_for_compatibility():
    payload = conformance_payload()
    assert payload["legacy_compatibility"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    assert payload["summary"]["conditional_validated"] == 5
    assert payload["summary"]["reduced_model_validated"] == 3
