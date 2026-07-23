import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.minimizer_3d import (
    MinimizerConfig, continuation, minimize, noninteracting_reference,
    resolution_study, run_minimizer_continuation_study, untrapped_control
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): MinimizerConfig(points=15)

def test_noninteracting_reference():
    r=noninteracting_reference()
    assert r["absolute_error"]<=5e-4 and r["rms_error"]<=5e-4

def test_minimization_lowers_energy():
    run=minimize(MinimizerConfig(coupling=1.0))
    values=[row["energy"] for row in run["history"]]
    assert np.all(np.diff(values)<=1e-12)

def test_continuation_normalizes():
    r=continuation()
    assert max(abs(row["norm"]-1) for row in r["branches"])<=2e-12

def test_continuation_residuals_close():
    r=continuation()
    assert max(row["projected_residual_l2"] for row in r["branches"])<=5e-6

def test_repulsive_branch_expands():
    r=continuation()
    radii=[row["rms_radius"] for row in r["branches"]]
    assert all(b>=a-1e-8 for a,b in zip(radii,radii[1:]))

def test_resolution_stabilizes():
    r=resolution_study()
    assert r["energy_successive_differences"][1]<r["energy_successive_differences"][0]

def test_full_study_passes():
    r=run_minimizer_continuation_study()
    assert r["passed"] and all(r["acceptance"].values())
