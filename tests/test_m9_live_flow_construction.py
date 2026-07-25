from openwave.xperiments.m9_cat_ept.live_flow_construction import (
    run_live_flow_construction,
)


def test_live_flow_construction_passes():
    result = run_live_flow_construction()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["free_h1_unitary_group_available"]
    assert result["decision"]["exact_nonlinear_continuum_semiflow_available"]
    assert result["decision"]["flow_infrastructure_unavailable"] is False


def test_exact_subflows_close_at_roundoff():
    result = run_live_flow_construction()
    assert result["free_subflow"]["group_error"] < 2e-15
    assert result["local_subflow"]["group_error"] < 2e-15
    assert result["constructed_split_flow"]["composition_error"] < 2e-15
