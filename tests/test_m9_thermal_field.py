
import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.thermal_field import (
    ThermalConfig, dissipation_identity, evolve_temperature,
    initial_temperature, mode_decay_control, run_thermal_field_study,
    semigroup_control, thermal_evolution, zero_diffusivity_control
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): ThermalConfig(points=63)

def test_total_heat_conserved():
    run=thermal_evolution()
    h=np.asarray([x["total_heat"] for x in run["records"]])
    assert np.max(np.abs(h-h[0]))<=2e-13

def test_entropy_increases():
    run=thermal_evolution()
    s=np.asarray([x["entropy"] for x in run["records"]])
    assert np.all(np.diff(s)>=-2e-14)

def test_variance_decreases():
    run=thermal_evolution()
    v=np.asarray([x["variance"] for x in run["records"]])
    assert np.all(np.diff(v)<=2e-14)

def test_mode_decay_closes():
    assert mode_decay_control()["absolute_error"]<=2e-14

def test_semigroup_closes():
    assert semigroup_control()["maximum_semigroup_error"]<=3e-14

def test_dissipation_identity():
    assert dissipation_identity()["absolute_error"]<=2e-9

def test_full_study_passes():
    r=run_thermal_field_study()
    assert r["passed"] and all(r["acceptance"].values())
