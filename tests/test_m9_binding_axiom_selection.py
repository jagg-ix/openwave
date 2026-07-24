import numpy as np
from openwave.xperiments.m9_cat_ept.binding_axiom_selection import (
    SelectionConfig, action_density, gauge_covariance_control,
    run_binding_axiom_selection, structural_selection, coefficient_nonuniqueness)

def test_invalid_controls():
    import pytest
    with pytest.raises(ValueError): SelectionConfig(alpha=0)

def test_bounded_saturation_and_unbounded_cubic():
    r=structural_selection()
    assert r["cubic_only_unbounded_direction"] and r["saturated_high_density_growth"]
    assert r["minimum_error"]<1e-12

def test_u1_covariance(): assert gauge_covariance_control()["u1_covariant"]
def test_coefficients_not_unique(): assert not coefficient_nonuniqueness()["coefficients_unique"]

def test_full_study():
    r=run_binding_axiom_selection()
    assert r["passed"] and not r["decision"]["selected_coefficients_unique_or_derived"]
