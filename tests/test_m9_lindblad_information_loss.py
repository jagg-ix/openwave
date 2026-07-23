import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.lindblad_information_loss import (
    LindbladParameters,
    exact_density,
    initial_density,
    run_lindblad_information_study,
    zero_loss_study,
)


def test_parameters_reject_negative_rate() -> None:
    with pytest.raises(ValueError):
        LindbladParameters(gamma=-0.1)


def test_initial_density_is_pure_and_normalized() -> None:
    rho = initial_density()
    assert math.isclose(float(np.trace(rho).real), 1.0)
    assert math.isclose(float(np.trace(rho @ rho).real), 1.0)


def test_exact_solution_preserves_trace_and_populations() -> None:
    parameters = LindbladParameters()
    rho0 = initial_density()
    rho = exact_density(parameters.final_time, parameters)
    assert math.isclose(float(np.trace(rho).real), 1.0, abs_tol=1e-14)
    assert np.allclose(np.diag(rho), np.diag(rho0))


def test_refinement_is_fourth_order() -> None:
    result = run_lindblad_information_study()
    assert min(result["refinement"]["observed_orders"]) >= 3.8


def test_trace_hermiticity_and_positivity_close() -> None:
    finest = run_lindblad_information_study()["finest"]
    assert finest["max_trace_error"] <= 2e-12
    assert finest["max_hermiticity_error"] <= 2e-12
    assert finest["minimum_eigenvalue"] >= -2e-12


def test_information_metrics_are_monotone() -> None:
    finest = run_lindblad_information_study()["finest"]
    assert finest["purity_monotone"]
    assert finest["relative_coherence_monotone"]
    assert finest["final_purity"] < 0.999


def test_zero_loss_reduces_to_unitary() -> None:
    result = zero_loss_study()
    assert result["max_trace_error"] <= 2e-12
    assert result["purity_drift"] <= 2e-8
    assert result["coherence_drift"] <= 2e-8


def test_full_study_passes_with_claim_boundaries() -> None:
    result = run_lindblad_information_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]


def test_public_facade_serializes_acceptance_as_boolean() -> None:
    from openwave.xperiments.m9_cat_ept.lindblad_information_loss_api import (
        result_to_json,
        run_lindblad_information_study as public_study,
    )
    result = public_study()
    assert isinstance(result["acceptance"]["zero_loss_reduces_to_unitary"], bool)
    assert '"zero_loss_reduces_to_unitary": true' in result_to_json(result)
