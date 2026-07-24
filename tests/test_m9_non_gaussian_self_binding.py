import pytest
from openwave.xperiments.m9_cat_ept.non_gaussian_self_binding import (
    ProfileCampaignConfig,domain_control,evolve_profile,profile_campaign,
    run_profile_self_binding_search,topology_control)

def test_invalid_campaign_grid_rejected():
    with pytest.raises(ValueError): ProfileCampaignConfig(points=11)

def test_all_profiles_execute_and_close_balance():
    campaign=ProfileCampaignConfig(final_time=.1,dt=.02)
    for name in ("gaussian","exponential","super_gaussian","shell","vortex_torus"):
        assert evolve_profile(name,.9,campaign)["maximum_balance_error"]<=4e-4

def test_campaign_has_fifteen_runs(): assert len(profile_campaign()["rows"])==15

def test_no_profile_candidate(): assert profile_campaign()["candidate_count"]==0

def test_all_runs_spread_or_reach_boundary():
    assert all(row["radius_ratio"]>=1.35 or row["maximum_boundary_fraction"]>=.02 for row in profile_campaign()["rows"])

def test_vortex_winding_control():
    r=topology_control(); assert r["initial_winding_is_unit"] and r["short_time_winding_is_retained"]

def test_vortex_domain_tracks_box(): assert domain_control()["larger_domain_has_larger_final_radius"]

def test_full_search_passes():
    r=run_profile_self_binding_search(); assert r["passed"] and all(r["acceptance"].values())
    assert r["decision"]["profile_family_no_go"]
