from openwave.xperiments.m9_cat_ept.orbital_compactness_bridge import (
    OrbitalConfig, compactness_campaign, perturbation_campaign,
    run_orbital_compactness_study, stationary_scales)

def test_stationary_minimum_and_barrier():
    rows=stationary_scales()
    assert [r["kind"] for r in rows]==["minimum","maximum"]
    assert rows[0]["second_derivative"]>0 and rows[1]["second_derivative"]<0

def test_perturbation_well():
    r=perturbation_campaign()
    assert r["all_small_perturbations_raise_energy"] and r["all_small_perturbations_remain_in_well"]

def test_compactness_proxy():
    r=compactness_campaign()
    assert r["successive_errors_decrease"] and r["tightness_proxy"]

def test_full_study_boundary():
    r=run_orbital_compactness_study()
    assert r["passed"] and not r["decision"]["full_continuum_orbital_stability_proved"]
