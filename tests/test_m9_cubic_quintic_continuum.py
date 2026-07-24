import numpy as np

from openwave.xperiments.m9_cat_ept.cubic_quintic_continuum import (
    coercivity_control,
    initial_gaussian,
    local_nonlinear_flow,
    run_cubic_quintic_continuum_study,
)


def test_coercive_bound_closes():
    result = coercivity_control()
    assert result["minimum_sampled_slack"] >= -2e-12
    assert result["equality_slack"] < 2e-12


def test_local_flow_preserves_density():
    psi, _grid = initial_gaussian(16, 8, 1)
    out = local_nonlinear_flow(psi, 0.1, 74.66304462649356, 415.7483217223993)
    assert np.max(np.abs(abs(out) ** 2 - abs(psi) ** 2)) < 2e-15


def test_full_study_passes_without_overclaim():
    result = run_cubic_quintic_continuum_study()
    assert result["passed"]
    assert not result["decision"]["arbitrary_h1_orbital_stability_formally_proved"]
