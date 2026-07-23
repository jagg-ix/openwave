import pytest
from openwave.xperiments.m9_cat_ept.confinement_sector import (
    ConfinementConfig, asymptotic_fit, color_singlet_residual,
    deconfinement_control, potential, radial_force,
    run_confinement_study, string_breaking_ledger, string_breaking_radius,
)

def test_invalid_separation_rejected():
    with pytest.raises(ValueError): potential(-1)

def test_force_is_energy_gradient():
    cfg=ConfinementConfig(); r=2.7; eps=1e-6
    numeric=-(potential(r+eps,cfg)-potential(r-eps,cfg))/(2*eps)
    assert abs(numeric-radial_force(r,cfg))<=2e-8

def test_asymptotic_string_tension():
    fit=asymptotic_fit()
    assert fit["slope_error"]<=2e-3 and fit["force_plateau_error"]<=2e-3

def test_color_singlet_closes():
    assert color_singlet_residual(("red","green","blue"))<=1e-14

def test_string_breaking_threshold():
    cfg=ConfinementConfig(); radius=string_breaking_radius(cfg)
    assert not string_breaking_ledger(.9*radius,cfg)["string_broken"]
    assert string_breaking_ledger(1.1*radius,cfg)["string_broken"]

def test_breaking_energy_closes():
    cfg=ConfinementConfig(); result=string_breaking_ledger(1.1*string_breaking_radius(cfg),cfg)
    assert abs(result["energy_closure"])<=1e-14

def test_zero_tension_loses_confinement():
    assert abs(deconfinement_control()["force_power"]+2)<=2e-2

def test_full_study_passes():
    result=run_confinement_study()
    assert result["passed"] and all(result["acceptance"].values())
