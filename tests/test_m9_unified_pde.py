import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.unified_pde import (
    UnifiedPDEConfig, grid, initial_state, matter_density,
    run_unified_pde_study, simulate, timestep_refinement,
    zero_coupling_control
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): UnifiedPDEConfig(points=63)

def test_initial_matter_is_normalized():
    cfg=UnifiedPDEConfig(); state=initial_state(cfg); _,dx=grid(cfg)
    assert abs(np.sum(matter_density(state.psi))*dx-1)<=2e-14

def test_matter_reservoir_closes():
    records=simulate()["records"]; initial=records[0]["matter_reservoir_balance"]
    assert max(abs(r["matter_reservoir_balance"]-initial) for r in records)<=2e-8

def test_thermal_loss_closes():
    records=simulate()["records"]; initial=records[0]["thermal_loss_balance"]
    assert max(abs(r["thermal_loss_balance"]-initial) for r in records)<=2e-8

def test_entropy_is_monotone():
    values=[r["entropy"] for r in simulate()["records"]]
    assert np.all(np.diff(values)>=-2e-12)

def test_zero_coupling_reduction():
    r=zero_coupling_control(); assert r["reservoir_max"]<=2e-14 and r["gauge_max"]<=2e-14

def test_refinement_improves():
    r=timestep_refinement(); assert r["successive_differences"][1]<r["successive_differences"][0]

def test_full_study_passes():
    r=run_unified_pde_study(); assert r["passed"] and all(r["acceptance"].values())
