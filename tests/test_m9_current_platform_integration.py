from pathlib import Path
from openwave.xperiments.m9_cat_ept.model_conformance_current import CURRENT_CONFORMANCE_SCHEMA,CURRENT_MILESTONE,run_conformance_study
from openwave.xperiments.m9_cat_ept.model_registration_current import CURRENT_SCHEMA,run_model_registration_study
from openwave.xperiments.m9_cat_ept.platform_integration_contract import run_platform_integration_contract

def test_current_aliases_and_platform_reach_m126():
    r=run_model_registration_study(); c=run_conformance_study(); p=run_platform_integration_contract()
    assert r["passed"] and c["passed"] and p["passed"]
    assert CURRENT_MILESTONE=="M9.126"
    assert CURRENT_SCHEMA=="openwave.model-registration.v29"
    assert CURRENT_CONFORMANCE_SCHEMA=="openwave.m9.models-conformance.v22"
    assert p["schema"]=="openwave.m9.platform-integration-contract.v9"

def test_public_docs_exist():
    root=Path(__file__).resolve().parents[1]
    assert "M9.126" in (root/"MODELS.md").read_text()
    assert "Planckian" in (root/"MODELS_M9.md").read_text()
