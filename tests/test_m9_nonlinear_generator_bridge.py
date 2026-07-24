import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.nonlinear_generator_bridge import (
    NonlinearGeneratorConfig,
    domain_graph_campaign,
    local_operator_campaign,
    run_nonlinear_generator_study,
    source_identity,
)


def test_invalid_reference_grid_rejected():
    with pytest.raises(ValueError):
        NonlinearGeneratorConfig(points=128, reference_points=128)


def test_domain_projection_and_graph_converge():
    result = domain_graph_campaign()
    assert np.all(np.diff(result["state_errors"]) < 0)
    assert np.all(np.diff(result["generator_errors"]) < 0)


def test_shifted_dissipativity_control():
    result = local_operator_campaign()
    assert max(result["shifted_quotients"]) <= 2e-12


def test_local_lipschitz_control_is_finite():
    result = local_operator_campaign()
    assert np.isfinite(result["maximum_lipschitz_ratio"])


def test_temperature_domain_is_positive():
    assert local_operator_campaign()["minimum_temperature"] > 0.9


def test_closable_anchor_is_pinned():
    assert source_identity()["sources"][1]["sha"] == "9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5"


def test_full_study_passes_without_continuum_overclaim():
    result = run_nonlinear_generator_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert not result["decision"]["continuum_generator_closable_proved"]
