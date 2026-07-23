"""Tests for the M9.4 nonlinear localization decision gate."""

from __future__ import annotations

import pytest

from openwave.xperiments.m9_cat_ept.localized_particle import (
    NLSConfig,
    candidate_metrics,
    evolve_nls,
    run_localization_study,
    state_norm,
    stationary_residual,
)


def test_exact_seed_is_normalized() -> None:
    run = evolve_nls(NLSConfig(points=512, final_time=0.0))
    assert state_norm(run.initial_state, run.dx) == pytest.approx(
        1.0,
        abs=1.0e-13,
    )


def test_stationary_residual_is_within_periodic_truncation_budget() -> None:
    run = evolve_nls(NLSConfig(points=512, final_time=0.0))
    assert stationary_residual(run.initial_state, run.dx) <= 5.0e-8


def test_focusing_soliton_conserves_and_returns() -> None:
    metrics = candidate_metrics(
        evolve_nls(
            NLSConfig(
                points=512,
                kappa=-2.0,
                final_time=2.0,
            )
        )
    )
    assert metrics["norm_drift"] < 1.0e-11
    assert metrics["energy_drift"] < 2.0e-8
    assert metrics["fidelity"] > 0.99999
    assert metrics["edge_probability"] < 2.0e-12


def test_free_and_defocusing_controls_disperse() -> None:
    for kappa in (0.0, 2.0):
        metrics = candidate_metrics(
            evolve_nls(
                NLSConfig(
                    points=512,
                    kappa=kappa,
                    final_time=2.0,
                )
            )
        )
        assert metrics["variance_ratio"] > 1.5
        assert metrics["peak_ratio"] < 0.8


def test_full_localization_gate_passes() -> None:
    result = run_localization_study()
    assert result["passed"] is True
    assert all(result["acceptance"].values())


def test_invalid_grid_is_rejected() -> None:
    with pytest.raises(ValueError, match="even integer"):
        NLSConfig(points=63)
