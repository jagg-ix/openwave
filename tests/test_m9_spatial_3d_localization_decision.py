from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spatial_3d_localization_decision import (
    run_spatial_3d_localization_decision,
)


def test_bounded_family_is_complete() -> None:
    result = run_spatial_3d_localization_decision()
    assert result["survey"]["couplings"] == [0.0, 2.0, 4.0, 8.0]


def test_strongest_member_is_lambda_eight() -> None:
    result = run_spatial_3d_localization_decision()
    assert result["selected_coupling"] == 8.0
    assert result["spreading_improvement"] >= 2.0e-3


def test_finite_time_candidate_and_perturbation_survive() -> None:
    result = run_spatial_3d_localization_decision()
    assert result["finite_time_candidate"]
    assert result["acceptance"]["fixed_perturbation_survives"]


def test_long_time_particle_claim_is_rejected() -> None:
    result = run_spatial_3d_localization_decision()
    assert not result["accepted_particle_candidate"]
    assert "no stable three-dimensional particle candidate" in result["decision"]


def test_global_norm_and_energy_ledgers_close() -> None:
    ledgers = run_spatial_3d_localization_decision()["global_ledgers"]
    assert ledgers["max_norm_drift"] <= 2.0e-5
    assert ledgers["max_corrected_energy_relative_drift"] <= 2.0e-4


def test_global_final_gauss_ledgers_close() -> None:
    ledgers = run_spatial_3d_localization_decision()["global_ledgers"]
    assert ledgers["max_final_gauss_absolute"] <= 1.0e-3
    assert ledgers["max_final_gauss_relative"] <= 5.5e-1


def test_decision_acceptance_passes() -> None:
    result = run_spatial_3d_localization_decision()
    assert result["passed"]
    assert all(result["acceptance"].values())


def test_decision_result_is_json_serializable() -> None:
    decoded = json.loads(json.dumps(run_spatial_3d_localization_decision()))
    assert decoded["task"] == "M9.14"
