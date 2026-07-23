from __future__ import annotations

import json

from openwave.xperiments.m9_cat_ept.spatial_3d_maxwell_dirac import (
    run_spatial_3d_transport_study,
)


def test_coupled_refinement_converges() -> None:
    result = run_spatial_3d_transport_study()
    assert result["refinement"]["observed_order"] >= 1.2


def test_long_run_norm_and_energy_close() -> None:
    summary = run_spatial_3d_transport_study()["long_run"]
    assert summary["max_norm_drift"] <= 3.0e-6
    assert summary["max_corrected_energy_relative_drift"] <= 3.0e-5


def test_long_run_gauss_and_charge_close() -> None:
    summary = run_spatial_3d_transport_study()["long_run"]
    assert summary["final"]["gauss_residual_absolute"] <= 5.0e-4
    assert summary["final"]["gauss_residual_relative"] <= 2.5e-1
    assert summary["max_net_total_charge"] <= 2.0e-8


def test_packets_transport_in_three_axes() -> None:
    result = run_spatial_3d_transport_study()
    summary = result["long_run"]
    assert summary["final_separation"] <= 0.90 * summary["initial_separation"]
    assert result["direction_change"] >= 1.0e-3


def test_magnetic_field_and_radiation_are_nonzero() -> None:
    summary = run_spatial_3d_transport_study()["long_run"]
    assert summary["final"]["max_magnetic_field"] >= 1.0e-4
    assert summary["emitted_energy"] > 0.0


def test_domain_shape_study_is_stable() -> None:
    result = run_spatial_3d_transport_study()["domain_shape_study"]
    assert result["relative_spreads"]["final_separation"] <= 1.0e-3
    assert max(record["max_energy_drift"] for record in result["records"]) <= 1.0e-6
    assert max(record["max_gauss_relative"] for record in result["records"]) <= 2.0e-1


def test_transport_acceptance_passes() -> None:
    result = run_spatial_3d_transport_study()
    assert result["passed"]
    assert all(result["acceptance"].values())


def test_transport_result_is_json_serializable() -> None:
    decoded = json.loads(json.dumps(run_spatial_3d_transport_study()))
    assert decoded["task"] == "M9.13"
