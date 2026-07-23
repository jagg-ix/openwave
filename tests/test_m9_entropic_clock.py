"""Tests for the M9.3 field-to-probability and coarse-graining contract."""

from __future__ import annotations

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.entropic_clock import (
    PeriodicCoarseGraining,
    apply_periodic_channel,
    channel_total_correlation,
    run_entropic_clock_study,
    snapshot_clock_trajectory,
    state_probability,
    uniform_reference,
)
from openwave.xperiments.m9_cat_ept.free_solver import (
    GaussianPacket,
    SolverConfig,
    evolve_free_packet,
)


def test_state_probability_is_normalized() -> None:
    run = evolve_free_packet(GaussianPacket(), SolverConfig(points=128))
    probability = state_probability(run.final_state, run.dx)
    assert float(np.sum(probability)) == pytest.approx(1.0, abs=1.0e-14)
    assert np.all(probability >= 0.0)


def test_channel_preserves_uniform_distribution() -> None:
    channel = PeriodicCoarseGraining()
    uniform = uniform_reference(64)
    after = apply_periodic_channel(uniform, channel)
    assert float(np.max(np.abs(after - uniform))) <= 1.0e-15


def test_remaining_disequilibrium_contracts_and_gain_accumulates() -> None:
    probability = np.zeros(64, dtype=np.float64)
    probability[0] = 1.0
    trajectory = snapshot_clock_trajectory(
        probability,
        PeriodicCoarseGraining(steps=20),
    )
    assert trajectory["remaining_nonincreasing"] is True
    assert trajectory["gain_nondecreasing"] is True
    assert trajectory["max_ledger_closure_error"] <= 1.0e-12


def test_channel_total_correlation_is_nonnegative() -> None:
    probability = np.zeros(64, dtype=np.float64)
    probability[0] = 0.5
    probability[1] = 0.5
    correlation = channel_total_correlation(
        probability,
        PeriodicCoarseGraining(),
    )
    assert correlation >= -1.0e-12


def test_frozen_m9_3_study_passes() -> None:
    result = run_entropic_clock_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())


def test_invalid_channel_is_rejected() -> None:
    with pytest.raises(ValueError, match="sum to 1"):
        PeriodicCoarseGraining(left=0.2, center=0.2, right=0.2)
