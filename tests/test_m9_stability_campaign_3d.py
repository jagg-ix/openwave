import pytest
from openwave.xperiments.m9_cat_ept.stability_campaign_3d import (
    StabilityConfig, ground_state, perturbation_continuity,
    run_long_horizon_stability_study, timestep_refinement,
    trapped_campaign, untrapped_control
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): StabilityConfig(points=15)

def test_ground_state_shape():
    cfg=StabilityConfig(points=16,final_time=1); assert ground_state(cfg).shape==(16,16,16)

def test_trapped_campaign_bounded():
    assert trapped_campaign(StabilityConfig(final_time=6,dt=.01,sample_stride=30))["all_bounded"]

def test_untrapped_spreads():
    r=untrapped_control(StabilityConfig(final_time=12,dt=.01,sample_stride=40)); assert r["final_rms_radius"]>2 and r["final_boundary_fraction"]>2e-2

def test_refinement_improves():
    r=timestep_refinement(); assert r["successive_differences"][1]<r["successive_differences"][0]

def test_perturbation_continuity(): assert perturbation_continuity()["ordered"]

def test_campaign_norm_errors_small():
    rows=trapped_campaign(StabilityConfig(final_time=6,dt=.01,sample_stride=30))["scenarios"]; assert max(x["maximum_norm_error"] for x in rows)<=2e-12

def test_full_study_passes():
    r=run_long_horizon_stability_study(); assert r["passed"] and all(r["acceptance"].values())
