import json
import math

import pytest

from openwave.xperiments.m9_cat_ept.transverse_maxwell_spinor import (
    TransverseGrid,
    TransverseParameters,
    run_transverse_study,
)


def study():
    return run_transverse_study()


def test_parameter_validation() -> None:
    with pytest.raises(ValueError):
        TransverseParameters(mass=0.0)
    with pytest.raises(ValueError):
        TransverseGrid(points=127)


def test_vacuum_refinement_is_second_order() -> None:
    result = study()["vacuum_refinement"]
    assert min(result["observed_orders"]["a"]) >= 1.9
    assert min(result["observed_orders"]["e"]) >= 1.9
    assert max(record["energy_relative_drift"] for record in result["records"]) < 5e-5


def test_coupled_refinement_converges() -> None:
    result = study()["coupled_refinement"]
    assert result["observed_orders"]["a"] >= 1.9
    assert result["observed_orders"]["e"] >= 1.9


def test_dynamic_gauss_and_pair_norm_close_without_projection() -> None:
    finest = study()["coupled_refinement"]["summaries"][-1]
    assert finest["max_charge_density"] <= 1e-14
    assert finest["max_pair_norm_error"] <= 1e-14


def test_energy_and_radiation_ledgers_close() -> None:
    finest = study()["coupled_refinement"]["summaries"][-1]
    assert finest["corrected_energy_relative_drift"] <= 1e-6
    assert finest["emitted_energy"] >= 1e-5
    assert finest["final"]["field_energy_central_fraction"] <= 0.2


def test_long_run_absorbs_radiation_and_balances_energy() -> None:
    result = study()["long_run"]
    assert result["absorbed_energy"] >= 4e-4
    assert result["emitted_energy"] >= 5e-4
    assert result["corrected_energy_relative_drift"] <= 3e-6
    assert result["final"]["field_energy_central_fraction"] <= 0.75


def test_absorber_study_is_window_stable() -> None:
    result = study()["absorber_study"]
    assert result["emitted_relative_spread"] <= 0.01
    assert max(
        record["corrected_energy_relative_drift"] for record in result["records"]
    ) <= 3e-6


def test_full_acceptance_and_json_round_trip() -> None:
    result = study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert json.loads(json.dumps(result))["task"] == "M9.7c"
    assert math.isfinite(result["long_run"]["emitted_energy"])
