import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.imaginary_action_backreaction import (
    ImaginaryActionParameters,
    exact_uniform_state,
    initial_state,
    nonuniform_loss_study,
    run_imaginary_action_study,
    zero_loss_study,
)


def test_parameters_reject_negative_loss() -> None:
    with pytest.raises(ValueError):
        ImaginaryActionParameters(gamma=-0.1)


def test_initial_state_is_normalized() -> None:
    assert math.isclose(float(np.vdot(initial_state(), initial_state()).real), 1.0)


def test_exact_uniform_norm_matches_imaginary_action() -> None:
    parameters = ImaginaryActionParameters()
    state = exact_uniform_state(parameters.final_time, parameters)
    norm = float(np.vdot(state, state).real)
    assert math.isclose(norm, math.exp(-2 * parameters.gamma * parameters.final_time), rel_tol=1e-13)


def test_refinement_is_fourth_order() -> None:
    result = run_imaginary_action_study()
    assert min(result["refinement"]["observed_orders"]) >= 3.8


def test_entropic_clock_and_weight_close() -> None:
    finest = run_imaginary_action_study()["finest"]
    assert finest["norm_monotone"]
    assert finest["tau_monotone"]
    assert finest["max_tau_error"] <= 2e-8
    assert finest["weight_identity_error"] <= 2e-15


def test_zero_loss_reduces_to_unitary() -> None:
    result = zero_loss_study()
    assert result["norm_drift"] <= 2e-8
    assert result["state_error_l2"] <= 2e-7
    assert abs(result["tau_ent"]) <= 2e-8


def test_nonuniform_positive_loss_is_contracting() -> None:
    result = nonuniform_loss_study()
    assert result["minimum_gamma_eigenvalue"] >= 0.0
    assert result["maximum_norm_derivative"] <= 1e-13
    assert result["norm_monotone"]
    assert abs(result["normalized_sigma_z_change"]) > 1e-3


def test_full_study_passes_with_claim_boundaries() -> None:
    result = run_imaginary_action_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]
