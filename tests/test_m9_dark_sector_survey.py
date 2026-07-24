
import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.dark_sector_survey import (
    DarkSectorConfig, no_attraction_control, no_stabilization_control,
    numerical_hessian_log_variables, optimize_charge,
    run_dark_sector_survey, survey, variational_energy
)

def test_invalid_charge_rejected():
    with pytest.raises(ValueError): optimize_charge(0)

def test_low_charge_is_unbound():
    r=optimize_charge(20)
    assert not r["bound_candidate"] and r["energy_per_charge"]>=.999

def test_high_charge_is_bound():
    r=optimize_charge(100)
    assert r["bound_candidate"] and r["energy_per_charge"]<.95

def test_threshold_is_detected():
    assert survey()["first_bound_charge"]==60

def test_bound_minimum_has_positive_hessian():
    cfg=DarkSectorConfig(); r=optimize_charge(100,cfg)
    eigen=np.linalg.eigvalsh(numerical_hessian_log_variables(100,r,cfg))
    assert np.min(eigen)>1e-2

def test_attraction_is_required():
    assert not no_attraction_control()["any_bound"]

def test_no_stabilization_runs_away():
    assert no_stabilization_control()["runaway_detected"]

def test_full_study_passes():
    r=run_dark_sector_survey()
    assert r["passed"] and all(r["acceptance"].values())
