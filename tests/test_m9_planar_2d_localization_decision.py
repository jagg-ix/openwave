from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.planar_2d_localization_decision import (
    result_to_json,
    run_localization_decision,
)


def test_bounded_family_is_complete() -> None:
    result = run_localization_decision()
    assert result["survey"]["couplings"] == [0.0, 2.0, 4.0, 8.0]
    assert len(result["survey"]["records"]) == 4


def test_strongest_member_reduces_spreading() -> None:
    result = run_localization_decision()
    assert result["spreading_improvement"] >= 0.10
    strongest = result["survey"]["records"][-1]
    assert strongest["maximum_rms_ratio"] <= 1.42
    assert strongest["minimum_peak_ratio"] >= 0.80


def test_fixed_perturbation_survives_finite_gate() -> None:
    perturbed = run_localization_decision()["fixed_perturbation"]
    assert perturbed["maximum_rms_ratio"] <= 1.45
    assert perturbed["minimum_peak_ratio"] >= 0.80
    assert perturbed["minimum_core_fraction"] >= 0.95


def test_long_time_gate_rejects_particle_claim() -> None:
    result = run_localization_decision()
    long_time = result["long_time_candidate"]
    assert long_time["maximum_rms_ratio"] >= 1.60
    assert result["accepted_particle_candidate"] is False
    assert "no stable" in result["decision"]


def test_all_conservation_ledgers_close() -> None:
    result = run_localization_decision()
    assert result["acceptance"]["norm_ledgers_close"]
    assert result["acceptance"]["energy_ledgers_close"]
    assert result["acceptance"]["gauss_ledgers_close"]


def test_radiation_is_recorded_for_every_member() -> None:
    result = run_localization_decision()
    assert result["acceptance"]["radiation_recorded"]
    for record in result["survey"]["records"]:
        assert "emitted_energy" in record["run"]


def test_decision_gate_passes_without_accepting_particle() -> None:
    result = run_localization_decision()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["finite_time_reduced_spreading_candidate"] == 8.0
    assert not result["accepted_particle_candidate"]


def test_result_schema_and_claims() -> None:
    result = run_localization_decision()
    assert result["classification"]["establishes"]
    assert result["classification"]["does_not_establish"]
    assert json.loads(result_to_json(result))["passed"] is True
