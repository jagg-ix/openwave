from openwave.xperiments.m9_cat_ept.formalization_m125_extension import run_formalization_m125_extension
from openwave.xperiments.m9_cat_ept.m125_three_clock_common_carrier_authority import run_m125_three_clock_common_carrier_authority
from openwave.xperiments.m9_cat_ept.model_registration_m125 import run_model_registration_study


def test_formal_continuity_and_authority_pass():
    formal = run_formalization_m125_extension()
    authority = run_m125_three_clock_common_carrier_authority()
    assert formal["passed"]
    assert authority["passed"]
    assert len(formal["sources"]) == 4
    assert all(
        not item["used_as_merged_master_authority"]
        for item in formal["candidate_relaxation_heads"]
    )


def test_m125_versioned_registration_preserves_scope():
    registration = run_model_registration_study()
    assert registration["schema"] == "openwave.model-registration.v28"
    assert registration["passed"]
    assert registration["m9_125"]["physical_claims_promoted"] == []
    assert not registration["m9_125"]["single_universal_physical_clock_established"]
    assert not registration["m9_125"]["external_validation_complete"]
