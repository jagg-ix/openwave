from openwave.xperiments.m9_cat_ept.gauge_coupled_cat_ept_m133 import run_gauge_coupled_cat_ept
from openwave.xperiments.m9_cat_ept.gauge_exchange_refinement_m133 import run_gauge_exchange_refinement
from openwave.xperiments.m9_cat_ept.m133_gauge_coupled_authority import run_m133_gauge_coupled_authority


def test_gauge_coupled_model_targets():
    result = run_gauge_coupled_cat_ept()
    assert result["passed"]
    assert result["acceptance"]["gauge_field_is_dynamical"]
    assert result["acceptance"]["charged_current_is_nonzero"]
    assert result["acceptance"]["entropic_time_is_monotone"]


def test_exchange_and_refinement_targets():
    result = run_gauge_exchange_refinement()
    assert result["passed"]
    assert result["exchange"]["passed"]
    assert result["refinement"]["passed"]


def test_m133_authority_preserves_boundaries():
    result = run_m133_gauge_coupled_authority()
    assert result["passed"]
    assert result["decision"]["dynamical_U1_sector_added"]
    assert not result["decision"]["complete_Maxwell_Einstein_CAT_EPT"]
    assert not result["decision"]["external_validation_complete"]
