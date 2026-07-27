from openwave.xperiments.m9_cat_ept.m126_existing_experimental_evidence_authority import run_m126_existing_experimental_evidence_authority
from openwave.xperiments.m9_cat_ept.model_registration_current import CURRENT_MILESTONE,CURRENT_SCHEMA,run_model_registration_study

def test_m126_authority_and_registration():
    a=run_m126_existing_experimental_evidence_authority()
    r=run_model_registration_study()
    assert a["passed"] and r["passed"]
    assert CURRENT_MILESTONE=="M9.126"
    assert CURRENT_SCHEMA=="openwave.model-registration.v29"
    assert r["m9_126"]["planckian_record_count"]==8
    assert not r["m9_126"]["prospective_external_validation_complete"]
