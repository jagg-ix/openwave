import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.unified_convergence import (
    ConvergenceConfig,
    convergence_campaign,
    run_unified_convergence_study,
)


def test_invalid_grid_sequence_rejected():
    with pytest.raises(ValueError):
        ConvergenceConfig(points=(64, 32, 128, 256))


def test_nested_grid_error_decreases():
    result = convergence_campaign()
    assert np.all(np.diff(result["aggregate_errors"]) < 0)


def test_observed_orders_are_positive():
    assert min(convergence_campaign()["observed_orders"]) > 0.5


def test_ledgers_close_on_every_grid():
    result = convergence_campaign()
    rows = [row["ledger_errors"] for row in result["rows"]] + [result["reference"]["ledger_errors"]]
    assert max(row["matter_reservoir"] for row in rows) < 3e-8
    assert max(row["thermal_loss"] for row in rows) < 3e-8
    assert max(row["gauge_work"] for row in rows) < 3e-7


def test_temperature_and_entropy_controls_hold():
    result = convergence_campaign()
    rows = [row["ledger_errors"] for row in result["rows"]] + [result["reference"]["ledger_errors"]]
    assert min(row["minimum_temperature"] for row in rows) > 0.9
    assert all(row["entropy_monotone"] for row in rows)


def test_full_study_passes_without_continuum_claim():
    result = run_unified_convergence_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert not result["decision"]["continuum_convergence_proved"]
