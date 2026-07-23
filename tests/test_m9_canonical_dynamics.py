import numpy as np, pytest
from openwave.xperiments.m9_cat_ept.canonical_dynamics import Parameters, initial_state, loss_operator, observables, refinement, reductions, run_canonical_dynamics_study

def test_invalid_loss_is_rejected():
    with pytest.raises(ValueError): Parameters(irreversible_rate=-1)
def test_initial_balance_closes(): assert abs(observables(initial_state(),Parameters())["total_balance"]-1)<1e-14
def test_loss_operator_is_positive(): assert np.min(np.linalg.eigvalsh(loss_operator(Parameters())))>=0
def test_refinement_converges(): assert min(refinement()["orders"])>=3.5
def test_zero_loss_reduction():
    r=reductions(); assert r["zero_loss_norm_drift"]<=2e-8 and abs(r["zero_loss_entropy"])<=2e-10 and abs(r["zero_loss_reservoir"])<=2e-10
def test_backreaction_changes_geometry():
    r=reductions(); assert abs(r["full_geometry_change"]-r["zero_backreaction_geometry_change"])>1e-3
def test_canonical_ledgers_close():
    r=run_canonical_dynamics_study(); assert r["acceptance"]["balance_closes"] and r["acceptance"]["constraint_closes"] and r["acceptance"]["entropy_monotone"]
def test_full_study_passes():
    r=run_canonical_dynamics_study(); assert r["passed"] and all(r["acceptance"].values())
