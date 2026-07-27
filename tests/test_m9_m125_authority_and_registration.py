from openwave.xperiments.m9_cat_ept.formalization_m125_extension import run_formalization_m125_extension
from openwave.xperiments.m9_cat_ept.m125_three_clock_common_carrier_authority import run_m125_three_clock_common_carrier_authority
from openwave.xperiments.m9_cat_ept.model_registration_current import CURRENT_MILESTONE, CURRENT_SCHEMA, run_model_registration_study
from openwave.xperiments.m9_cat_ept.model_conformance_current import run_conformance_study
from openwave.xperiments.m9_cat_ept.platform_integration_contract import run_platform_integration_contract

def test_formal_continuity_and_authority_pass():
    formal = run_formalization_m125_extension()
    authority = run_m125_three_clock_common_carrier_authority()
    assert formal['passed']
    assert authority['passed']
    assert len(formal['sources']) == 4
    assert all(not item['used_as_merged_master_authority'] for item in formal['candidate_relaxation_heads'])

def test_stable_alias_registration_conformance_and_platform_pass():
    registration = run_model_registration_study()
    conformance = run_conformance_study()
    platform = run_platform_integration_contract()
    assert CURRENT_MILESTONE == 'M9.125'
    assert CURRENT_SCHEMA == 'openwave.model-registration.v28'
    assert registration['passed']
    assert conformance['passed']
    assert platform['passed']
    assert platform['schema'] == 'openwave.m9.platform-integration-contract.v8'
    assert registration['m9_125']['physical_claims_promoted'] == []
