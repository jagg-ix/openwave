import pytest
from openwave.xperiments.m9_cat_ept.continuum_semigroup_bridge import (
    SemigroupConfig, contraction_study, generator_recovery, resolution_bridge,
    run_semigroup_bridge_study, semigroup_law_error,
    strong_continuity_study, zero_generator_control,
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): SemigroupConfig(points=31)

def test_semigroup_law(): assert semigroup_law_error()<=3e-14

def test_strong_continuity(): assert strong_continuity_study()["strictly_decreasing"]

def test_generator_recovery(): assert min(generator_recovery()["orders"][-3:])>.85

def test_contraction():
    r=contraction_study(); assert r["matter_nonincreasing"] and r["thermal_nonincreasing"]

def test_resolution_bridge(): assert max(resolution_bridge()["successive_low_mode_differences"])<=2e-12

def test_zero_generator_identity():
    r=zero_generator_control(); assert max(r["psi_error"],r["temperature_error"],abs(r["reservoir"]))<=3e-14

def test_full_study_passes():
    r=run_semigroup_bridge_study(); assert r["passed"] and all(r["acceptance"].values())
