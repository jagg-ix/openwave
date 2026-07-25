import numpy as np

from openwave.xperiments.m9_cat_ept.spinorial_pair_dynamics_authoritative import (
    run_spinorial_pair_dynamics,
)


def test_full_maxwell_dirac_pair_closes_momentum_transfer_against_lorentz_force():
    result = run_spinorial_pair_dynamics()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.spinorial-pair-dynamics.v3"
    assert result["decision"]["four_spinor_sources_drive_all_initial_fields"]
    assert result["decision"]["full_maxwell_dirac_pair_evolved"]
    assert result["decision"]["momentum_transfer_matches_field_lorentz_force"]
    assert result["relative_errors"]["momentum_vs_lorentz"] <= 0.1
    assert result["predicted_momentum_rate"] > 0.0
    assert result["response"]["interaction_momentum_rate"] > 0.0
    assert abs(result["source"]["positive_integrated_charge"] - 1.0) <= 2e-12
    assert abs(result["source"]["negative_integrated_charge"] + 1.0) <= 2e-12
    assert result["source"]["pair_charge_error"] <= 2e-12
    assert result["max_plus_norm_drift"] <= 2e-4


def test_center_response_has_wrong_sign_and_does_not_close_reduction():
    result = run_spinorial_pair_dynamics()
    response = result["response"]
    assert result["predicted_momentum_rate"] > 0.0
    assert response["interaction_center_acceleration"] < 0.0
    assert result["relative_errors"]["center_acceleration_vs_lorentz"] > 0.5
    assert not result["decision"]["center_response_has_lorentz_sign"]
    assert not result["decision"]["center_acceleration_closed"]


def test_finite_spin_rate_closes_generator_but_not_rest_frame_bmt_shadow():
    result = run_spinorial_pair_dynamics()
    measured = np.asarray(result["response"]["interaction_spin_rate"])
    generator = np.asarray(result["response"]["interaction_generator_spin_rate"])
    bmt = np.asarray(result["rest_frame_bmt_spin_rate"])
    assert np.linalg.norm(measured) > 0.0
    assert np.linalg.norm(generator) > 0.0
    assert np.linalg.norm(bmt) > 0.0
    assert result["relative_errors"]["finite_spin_vs_generator"] <= 0.03
    assert result["relative_errors"]["finite_spin_vs_rest_frame_bmt"] > 0.5
    assert result["decision"]["spin_generator_integration_closed"]
    assert not result["decision"]["rest_frame_bmt_torque_closed_on_winding_state"]


def test_pair_dynamics_preserves_physical_and_stationary_boundaries():
    result = run_spinorial_pair_dynamics()
    assert not result["decision"]["stable_charged_stationary_pair_constructed"]
    assert result["decision"]["criterion_rows_promoted"] == []
    assert not result["decision"]["physical_force_or_moment_calibration_complete"]
