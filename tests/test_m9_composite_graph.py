import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.composite_graph import (
    Bond, CompositeSpec, Constituent, energy_and_forces, neutral_pair_template,
    permuted_spec, relax, run_composite_graph_study, total_charge,
    triplet_template
)

def test_disconnected_graph_rejected():
    with pytest.raises(ValueError):
        CompositeSpec("bad",(Constituent("a",1,1,0),Constituent("b",-1,1,0)),())

def test_fingerprint_is_permutation_invariant():
    spec,_=triplet_template()
    assert spec.fingerprint()==permuted_spec(spec).fingerprint()

def test_neutral_pair_charge_closes():
    spec,_=neutral_pair_template()
    assert abs(total_charge(spec))<1e-12

def test_triplet_charge_closes():
    spec,_=triplet_template()
    assert abs(total_charge(spec)-1)<1e-12

def test_pair_relaxation_lowers_energy():
    spec,pos=neutral_pair_template()
    initial,_=energy_and_forces(spec,pos); final=relax(spec,pos)
    assert final["energy"]<initial and final["binding_energy"]<0

def test_triplet_relaxation_lowers_energy():
    spec,pos=triplet_template()
    initial,_=energy_and_forces(spec,pos); final=relax(spec,pos)
    assert final["energy"]<initial and final["binding_energy"]<0

def test_action_reaction_internal_force_closes():
    spec,pos=triplet_template()
    _,forces=energy_and_forces(spec,pos)
    assert np.linalg.norm(np.sum(forces,axis=0))<1e-12

def test_full_study_passes():
    r=run_composite_graph_study()
    assert r["passed"] and all(r["acceptance"].values())
