import numpy as np
from openwave.xperiments.m9_cat_ept.orbital_quantization import (
    OrbitalConfig, analytic_energy, density_stationarity, domain_study,
    node_count, resolution_study, run_orbital_quantization_study, solve_modes
)

def test_bound_energy_ladder():
    s=solve_modes(); target=np.asarray([analytic_energy(n) for n in range(1,5)])
    assert np.max(np.abs((s["energies"][:3]-target[:3])/target[:3]))<=5e-3

def test_node_ladder():
    s=solve_modes(); assert [node_count(s["modes"][:,i]) for i in range(4)]==[0,1,2,3]

def test_modes_are_orthonormal():
    s=solve_modes(); assert np.max(np.abs(s["overlap"]-np.eye(4)))<=2e-12

def test_density_is_stationary():
    s=solve_modes(); assert density_stationarity(s["modes"][:,0],float(s["energies"][0]))<=2e-15

def test_resolution_converges(): assert min(resolution_study()["orders"])>=1.7

def test_domain_is_stable(): assert domain_study()["maximum_spread"]<=5e-5

def test_invalid_angular_momentum_rejected():
    import pytest
    with pytest.raises(ValueError): OrbitalConfig(angular_momentum=-1)

def test_full_study_passes():
    r=run_orbital_quantization_study(); assert r["passed"] and all(r["acceptance"].values())
