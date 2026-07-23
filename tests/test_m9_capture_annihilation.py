import numpy as np
from openwave.xperiments.m9_cat_ept.capture_annihilation import (
    CaptureConfig, potential, radial_force, run_capture_annihilation_study,
    simulate, timestep_refinement
)

def test_force_is_energy_gradient():
    cfg=CaptureConfig(); r=2.3; eps=1e-6
    numerical=-(potential(r+eps,-1,cfg)-potential(r-eps,-1,cfg))/(2*eps)
    assert abs(numerical-radial_force(r,-1,cfg))<1e-8

def test_opposite_sector_captures():
    assert simulate(-1)["first_capture_time"] is not None

def test_opposite_sector_annihilates():
    assert simulate(-1)["final_sector_mass"]<=1e-3

def test_energy_ledger_closes():
    assert simulate(-1)["maximum_energy_error"]<=5e-8

def test_radiation_is_monotone():
    assert simulate(-1)["radiation_monotone"]

def test_same_sector_control():
    run=simulate(+1,CaptureConfig(initial_velocity=0))
    assert run["first_capture_time"] is None
    assert abs(run["final_sector_mass"]-1)<1e-12

def test_timestep_refinement_improves():
    r=timestep_refinement()
    assert r["mass_successive_differences"][1]<=r["mass_successive_differences"][0]+1e-10

def test_full_study_passes():
    r=run_capture_annihilation_study()
    assert r["passed"] and all(r["acceptance"].values())
