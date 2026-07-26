from copy import deepcopy

from openwave.xperiments.m9_cat_ept.m101_reproducibility_contract import (
    canonical_manifest,
    validate_component,
)


def fake_payloads():
    return {
        "coupled_action": {
            "schema": "openwave.m9.coupled-gauge-spinor-hartree-action.v1",
            "passed": True,
            "initial": {"action": {"total": 3.0}},
            "final": {
                "action": {"total": 2.0},
                "symmetry_reduced": {
                    "relative_projected_residual": 0.4,
                    "spin_sector_leakage": 0.01,
                },
                "winding": {"integer_winding": 3},
            },
            "action_nonincrease": True,
            "symmetry_reduced_stationary_branch_constructed": False,
            "decision": {
                "unrestricted_stable_charged_branch_constructed": False,
            },
        },
        "packet_tbmt": {
            "schema": "openwave.m9.covariant-packet-tbmt.v1",
            "passed": True,
            "interaction_packet_tbmt_rate": [0.0, 1.0, 0.0],
            "interaction_dirac_generator_rate": [0.0, 2.0, 0.0],
            "legacy_rest_frame_rate": [0.0, -1.0, 0.0],
            "relative_errors": {
                "local_packet_tbmt_vs_generator": 0.5,
                "legacy_rest_frame_vs_generator": 1.5,
                "finite_time_vs_generator": 0.02,
            },
            "local_packet_improves_on_rest_frame": True,
            "local_packet_tbmt_closes_on_current_packet": False,
            "pair_velocity_audit": {"maximum_used_beta": 0.8},
        },
        "clock": {
            "schema": "openwave.m9.clock-action-rate-calibration.v1",
            "passed": True,
            "measured_internal_frequency": 1.4,
            "action_rate": 1.4,
            "compton_clock_mass": 1.4,
            "isolated_yukawa": 2.0,
            "observed_mean_entropy_rate": 0.1,
            "entropy_action_unit": 8.0,
            "entropy_rate_modulation_fraction": 0.2,
            "held_out": [{"points": 24, "omega": 1.35}],
            "decision": {
                "external_clock_or_mass_calibration_complete": False,
            },
        },
        "gravity": {
            "schema": "openwave.m9.electrogravitic-weak-field-evolution.v1",
            "passed": True,
            "records": [
                {
                    "einstein00_relative_residual": 1e-13,
                    "gauss_relative_residual": 2e-13,
                    "ampere_relative_residual": 3e-13,
                    "magnetic_divergence_max": 4e-13,
                    "minimum_g00": 0.9,
                    "maximum_metric_perturbation": 0.1,
                    "norm": 1.0,
                }
            ],
            "maximum_pre_normalization_norm_drift": 1e-8,
            "equivalence_probe_error": 0.0,
            "decision": {
                "end_to_end_weak_field_electrogravitic_evolution_constructed": True,
                "full_nonlinear_four_dimensional_einstein_evolution_constructed": False,
            },
        },
    }


def test_manifest_hashes_full_components_and_exposes_subgates():
    payloads = fake_payloads()
    manifest = canonical_manifest(payloads)
    assert all(not component["validation_errors"] for component in manifest["components"].values())
    assert all(len(component["sha256"]) == 64 for component in manifest["components"].values())
    action = manifest["quantitative_summary"]["coupled_action"]
    assert action["campaign_passed"]
    assert not action["symmetry_reduced_state_gate"]
    packet = manifest["quantitative_summary"]["packet_tbmt"]
    assert packet["campaign_passed"]
    assert not packet["reduction_gate"]


def test_missing_quantitative_field_fails_validation():
    payload = deepcopy(fake_payloads()["coupled_action"])
    del payload["final"]["symmetry_reduced"]["relative_projected_residual"]
    errors = validate_component("coupled_action", payload)
    assert "coupled_action: missing final.symmetry_reduced.relative_projected_residual" in errors


def test_component_hash_changes_when_a_measurement_changes():
    first = canonical_manifest(fake_payloads())
    changed = fake_payloads()
    changed["clock"]["measured_internal_frequency"] = 1.41
    second = canonical_manifest(changed)
    assert first["components"]["clock"]["sha256"] != second["components"]["clock"]["sha256"]
    assert first["components"]["gravity"]["sha256"] == second["components"]["gravity"]["sha256"]
