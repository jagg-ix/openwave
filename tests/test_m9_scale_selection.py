
import math
import pytest
from openwave.xperiments.m9_cat_ept.scale_selection import (
    ScaleParameters,
    analytic_derivative,
    derrick_controls,
    relax_scale,
    resolution_study,
    run_scale_selection_study,
    scale_scan,
    selected_scale,
)

def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        ScaleParameters(scale_min=2,scale_max=1)

def test_selected_scale_is_interior():
    p=ScaleParameters()
    s=selected_scale(p)
    assert s is not None
    assert p.scale_min<s<p.scale_max

def test_scan_matches_analytic_scale():
    p=ScaleParameters(); r=scale_scan(p)
    assert abs(r["numerical_minimum_scale"]-selected_scale(p))<=0.02

def test_radial_quadrature_converges():
    assert min(resolution_study(ScaleParameters())["observed_orders"])>=1.7

def test_derivative_closes_at_selected_scale():
    p=ScaleParameters(); s=selected_scale(p)
    assert s is not None
    assert abs(analytic_derivative(s,p))<=2e-12

def test_relaxation_converges_from_both_sides():
    p=ScaleParameters(); s=selected_scale(p)
    assert s is not None
    for initial in (0.6,1.7):
        r=relax_scale(initial,p)
        assert r["energy_nonincreasing"]
        assert abs(r["final_scale"]-s)<=2e-4

def test_derrick_controls_remove_interior_scale():
    r=derrick_controls(ScaleParameters())
    assert r["no_skyrme_minimum_at_lower_boundary"]
    assert r["no_potential_minimum_at_upper_boundary"]
    assert r["no_skyrme_selected_scale"] is None
    assert r["no_potential_selected_scale"] is None

def test_full_scale_study_passes_without_mass_promotion():
    r=run_scale_selection_study()
    assert r["passed"]
    assert r["selected_dimensionless_scale"]
    assert 
["physical_rest_mass_established"] is False
    assert r["accepted_three_dimensional_particle"] is False
