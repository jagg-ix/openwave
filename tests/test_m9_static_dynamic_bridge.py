import numpy as np, pytest
from openwave.xperiments.m9_cat_ept.static_dynamic_bridge import Parameters, evolve, grid, kink, resolution_study, run_static_dynamic_bridge_study, topological_charge

def test_invalid_grid_is_rejected():
    with pytest.raises(ValueError): Parameters(points=200)
def test_kink_has_unit_topological_charge():
    p=Parameters(); x,_=grid(p); assert abs(topological_charge(kink(x,p),p)-1)<1e-6
def test_static_residual_converges(): assert min(resolution_study()["orders"])>=1.7
def test_dynamic_energy_decreases(): assert np.all(np.diff(evolve()["energies"])<=2e-7)
def test_perturbation_relaxes():
    r=evolve(); assert r["final_l2_to_static"]<r["initial_l2_to_static"]
def test_topological_sector_is_preserved(): assert abs(evolve()["topological_charge"]-1)<1e-10
def test_boundaries_are_shared():
    p=Parameters(); r=evolve(p); assert abs(r["phi"][0]+p.vacuum)<1e-12 and abs(r["phi"][-1]-p.vacuum)<1e-12
def test_full_bridge_study_passes():
    r=run_static_dynamic_bridge_study(); assert r["passed"] and all(r["acceptance"].values())
