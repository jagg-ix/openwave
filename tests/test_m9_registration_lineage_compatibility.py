from openwave.xperiments.m9_cat_ept.model_conformance_m96 import run_conformance_study as run_m96
from openwave.xperiments.m9_cat_ept.model_conformance_current import run_conformance_study as run_current_conformance
from openwave.xperiments.m9_cat_ept.model_registration import run_model_registration_study as run_m97_registration
from openwave.xperiments.m9_cat_ept.model_registration_current import run_model_registration_study as run_current_registration
from openwave.xperiments.m9_cat_ept.model_registration_zil import run_model_registration_study as run_m98_registration


def test_versioned_and_current_lineages_execute_without_recursion():
    m96 = run_m96()
    m97 = run_m97_registration()
    m98 = run_m98_registration()
    current_registration = run_current_registration()
    current_conformance = run_current_conformance()

    assert m96["passed"]
    assert m97["passed"]
    assert m98["passed"]
    assert current_registration["passed"]
    assert current_conformance["passed"]

    assert m96["schema"] == "openwave.m9.models-conformance.v14"
    assert m97["schema"] == "openwave.model-registration.v4"
    assert m98["schema"] == "openwave.model-registration.v5"
    assert current_registration["schema"] == "openwave.model-registration.v29"
    assert current_conformance["schema"] == "openwave.m9.models-conformance.v22"
