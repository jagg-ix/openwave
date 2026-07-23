import pytest
from openwave.xperiments.m9_cat_ept.weak_chiral_sector import (
    WeakConfig, basis_state, chiral_selectivity_control, evolve, generator,
    run_weak_chiral_study, timestep_refinement, zero_decay_unitary_control,
)

def test_invalid_basis_rejected():
    with pytest.raises(ValueError): basis_state(4)

def test_generator_shape():
    assert generator(WeakConfig()).shape==(4,4)

def test_flavor_transition_occurs():
    run=evolve(basis_state(0))
    assert max(row["mu_left"] for row in run["records"])>=.15

def test_balance_closes():
    run=evolve(basis_state(0))
    assert max(abs(row["balance"]-1) for row in run["records"])<=2e-13

def test_chiral_selectivity():
    result=chiral_selectivity_control()
    assert result["left_final_matter"]<.05
    assert abs(result["right_final_matter"]-1)<=2e-13

def test_zero_decay_unitary():
    result=zero_decay_unitary_control()
    assert result["balance_error"]<=2e-13 and result["maximum_mu_left"]>=.5

def test_refinement_stabilizes():
    assert max(timestep_refinement()["successive_differences"])<=5e-13

def test_full_study_passes():
    result=run_weak_chiral_study()
    assert result["passed"] and all(result["acceptance"].values())
