import numpy as np
from openwave.xperiments.m9_cat_ept.fokker_planck_bridge import (
 FPConfig,velocity_generator,velocity_propagator,detailed_balance_error,
 ou_semigroup_error,simulate,run_fokker_planck_study,refinement)

def test_generator_mass_conservation():
    assert np.max(np.abs(np.sum(velocity_generator(FPConfig()),axis=0)))<=2e-13
def test_semigroup(): assert ou_semigroup_error(FPConfig())<=3e-14
def test_positive_propagator(): assert np.min(velocity_propagator(.1,FPConfig()))>=-2e-14
def test_detailed_balance(): assert detailed_balance_error(FPConfig())<=3e-14
def test_phase_mass_and_positivity():
    r=simulate(); assert abs(r["records"][-1]["mass"]-1)<=3e-13 and r["records"][-1]["minimum"]>=-2e-15
def test_relative_entropy_decreases():
    e=[x["relative_entropy"] for x in simulate()["records"]]
    assert np.all(np.diff(e)<=2e-11)
def test_refinement():
    d=refinement()["successive_differences"]; assert d[-1]<d[0]
def test_full_study():
    r=run_fokker_planck_study(); assert r["passed"] and all(r["acceptance"].values())
