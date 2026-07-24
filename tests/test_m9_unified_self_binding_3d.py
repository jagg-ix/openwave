import pytest
from openwave.xperiments.m9_cat_ept.unified_self_binding_3d import (
    Unified3DConfig, coupling_scan, initial_state, observables,
    run_unified_self_binding_campaign, simulate, timestep_refinement,
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): Unified3DConfig(points=11)

def test_initial_balance_closes():
    cfg=Unified3DConfig(); assert abs(observables(initial_state(cfg),cfg)["balance"]-1)<1e-12

def test_scan_has_five_couplings(): assert len(coupling_scan()["rows"])==5

def test_no_candidate_in_reference_scan(): assert all(not r["retained_localization"] for r in coupling_scan()["rows"])

def test_balance_is_controlled(): assert max(r["maximum_balance_error"] for r in coupling_scan()["rows"])<=3e-4

def test_color_sector_is_active(): assert simulate(Unified3DConfig(final_time=.2))["records"][-1]["color_source_l2"]>1e-5

def test_refinement_improves():
    r=timestep_refinement(); assert r["successive_differences"][1]<r["successive_differences"][0]

def test_full_campaign_passes():
    r=run_unified_self_binding_campaign(); assert r["passed"] and all(r["acceptance"].values())
