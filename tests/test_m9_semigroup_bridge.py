import pytest
from scipy.linalg import norm
from openwave.xperiments.m9_cat_ept.semigroup_bridge import (
    SemigroupConfig,contraction_campaign,evidence_fingerprint,generator_parts,
    heat_symbol_consistency,resolvent_campaign,run_semigroup_bridge_study,
    semigroup_composition,splitting_refinement)

def test_invalid_loss_profile_rejected():
    with pytest.raises(ValueError): SemigroupConfig(base_loss=.01,loss_modulation=.03)

def test_skew_part_is_skew_adjoint():
    s,_d,_a=generator_parts(); assert norm(s+s.conj().T,2)<=2e-13

def test_contraction_campaign():
    r=contraction_campaign(); assert r["maximum_norm"]<=1+2e-12 and r["nonincreasing"]

def test_semigroup_composition(): assert semigroup_composition()["composition_error"]<=2e-12

def test_resolvent_bound(): assert resolvent_campaign()["all_bounded"]

def test_splitting_orders():
    r=splitting_refinement(); assert min(r["lie_orders"][-2:])>=.9 and min(r["strang_orders"][-2:])>=1.8

def test_grid_symbol_second_order(): assert min(heat_symbol_consistency()["orders"][-2:])>=1.9

def test_full_bridge_passes():
    r=run_semigroup_bridge_study(); assert r["passed"] and all(r["acceptance"].values())
    assert not r["decision"]["continuum_wellposedness_proved"] and len(evidence_fingerprint())==64
