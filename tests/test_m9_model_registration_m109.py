from openwave.xperiments.m9_cat_ept.model_registration_m109 import (
    canonical_registration_payload,
    run_model_registration_study,
)


def test_schema_v13_preserves_G_boundaries():
    payload = canonical_registration_payload()
    current = payload["m9_109"]
    assert payload["schema"] == "openwave.model-registration.v13"
    assert current["G_is_derived_not_primitive"]
    assert not current["particle_clocks_define_universal_G"]
    assert not current["withheld_G_prediction_executed"]
    assert not current["calibrated_gravity_coupling_injected"]
    assert current["physical_claims_promoted"] == []


def test_current_registration_passes_without_overpromotion():
    result = run_model_registration_study()
    assert result["passed"]
    assert result["decision"]["Newton_G_formal_maturity_changed"]
    assert not result["decision"]["Newton_G_physical_prediction_changed"]
