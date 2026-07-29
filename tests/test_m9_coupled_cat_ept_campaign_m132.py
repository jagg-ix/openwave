from openwave.xperiments.m9_cat_ept.coupled_cat_ept_campaign_m132 import (
    run_coupled_cat_ept_campaign,
)
from openwave.xperiments.m9_cat_ept.m132_coupled_cat_ept_authority import (
    run_m132_coupled_cat_ept_authority,
)


def test_coupled_campaign_distinguishes_model_sectors():
    result = run_coupled_cat_ept_campaign()
    assert result["passed"]
    assert result["feedback"]["acceptance"]["entropy_production_is_positive"]
    assert result["baselines"]["acceptance"]["gravity_changes_matter_observables"]
    assert result["baselines"]["acceptance"]["dissipation_changes_matter_observables"]
    assert result["baselines"]["acceptance"]["one_parameter_set_is_shared"]


def test_m132_authority_marks_model_improvement_without_physical_overclaim():
    result = run_m132_coupled_cat_ept_authority()
    assert result["passed"]
    assert result["internal_ready"]
    assert not result["physical_ready"]
    assert result["decision"]["CAT_EPT_model_core_materially_extended"]
    assert not result["decision"]["complete_physical_theory_validated"]
