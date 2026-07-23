import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.equivalence_principle import (
    GravityConfig, acceleration, clock_redshift, eotvos_parameter,
    run_equivalence_principle_study, timestep_refinement,
    uniform_field_equivalence, velocity_verlet,
)

def test_invalid_mass_rejected():
    with pytest.raises(ValueError): acceleration(0,0,1)

def test_universal_free_fall():
    cfg=GravityConfig(); a=velocity_verlet(1,0,1,1,cfg); b=velocity_verlet(1,0,7.5,7.5,cfg)
    assert np.max(np.abs(a["positions"]-b["positions"]))<=2e-13

def test_eotvos_violation_control():
    assert eotvos_parameter(1,1,7.5,7.65)>=1e-2

def test_energy_conservation():
    run=velocity_verlet(1,0,1,1)
    assert np.max(np.abs(run["energies"]-run["energies"][0]))<=3e-8

def test_clock_redshift_weak_limit():
    assert clock_redshift(0,.25,10)["weak_error"]<=3e-4

def test_uniform_accelerated_frame_equivalence():
    assert uniform_field_equivalence(.4,-.03)["maximum_position_error"]<=2e-12

def test_verlet_second_order():
    assert min(timestep_refinement()["orders"])>=1.9

def test_full_study_passes():
    result=run_equivalence_principle_study()
    assert result["passed"] and all(result["acceptance"].values())
