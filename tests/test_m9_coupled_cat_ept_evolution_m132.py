from openwave.xperiments.m9_cat_ept.coupled_cat_ept_evolution_m132 import (
    run_coupled_cat_ept_evolution,
)


def test_coupled_cat_ept_evolution_closes():
    result = run_coupled_cat_ept_evolution()
    assert result["passed"]
    assert result["acceptance"]["matter_norm_is_preserved"]
    assert result["acceptance"]["entropic_time_is_monotone"]
    assert result["acceptance"]["entropic_time_advances"]
    assert result["acceptance"]["geometry_is_dynamical"]
    assert result["decision"]["matter_geometry_entropy_evolved_together"]
    assert not result["decision"]["complete_relativistic_CAT_EPT_constructed"]
