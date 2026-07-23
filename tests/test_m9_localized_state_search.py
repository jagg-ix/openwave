import math
import pytest
from openwave.xperiments.m9_cat_ept.localized_state_search import (
    LocalizationParameters,
    candidate_family,
    residual_refinement,
    run_localized_state_search,
    target_norm,
)

def test_invalid_parameters_rejected():
    with pytest.raises(ValueError):
        LocalizationParameters(points=255)

def test_target_norm_is_positive():
    p=LocalizationParameters()
    assert math.isclose(target_norm(p),1.6)

def test_static_residual_is_second_order():
    assert min(residual_refinement()["orders"])>=1.8

def test_candidate_family_is_continuous_and_localized():
    family=candidate_family()
    assert len(family)==3
    assert all(item["tail_fraction"]<1e-6 for item in family)

def test_perturbed_candidate_remains_localized():
    r=run_localized_state_search()["finite_perturbation"]
    assert r["rms_ratio_to_reference"]<=1.12
    assert r["peak_ratio_to_reference"]>=0.90
    assert r["final"]["core_fraction"]>=0.995

def test_long_horizon_candidate_remains_localized():
    r=run_localized_state_search()["long_horizon"]
    assert r["rms_ratio_to_reference"]<=1.12
    assert r["peak_ratio_to_reference"]>=0.95

def test_domain_study_closes():
    r=run_localized_state_search()["domain_study"]
    assert r["rms_relative_spread"]<=2e-3
    assert r["peak_relative_spread"]<=2e-3

def test_full_search_passes_without_particle_promotion():
    r=run_localized_state_search()
    assert r["passed"]
    assert r["accepted_one_dimensional_localized_family"]
    assert r["accepted_three_dimensional_particle"] is False
    assert r["scale_selected_dynamically"] is False
