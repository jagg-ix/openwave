from __future__ import annotations

import pytest

from openwave.xperiments.m9_cat_ept.pauli_hartree_u1_carrier_m141 import (
    PauliHartreeU1Config,
    construct_state,
    run_pauli_hartree_u1_campaign,
)


def test_m141_three_dimensional_carrier_closes_without_promotion() -> None:
    result = run_pauli_hartree_u1_campaign()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"][
        "three_dimensional_pauli_hartree_u1_carrier_constructed"
    ]
    assert not result["decision"]["stable_charged_stationary_branch_promoted"]
    assert result["decision"]["physical_claims_promoted"] == []


def test_m141_winding_charge_spin_and_constraints_are_field_derived() -> None:
    result = run_pauli_hartree_u1_campaign()
    final = result["final"]
    assert final["measured_winding"] == 3
    assert final["winding_quantization_error"] <= 2.0e-12
    assert result["charge_winding_error"] <= 2.0e-12
    assert abs(final["spin_z"] - 0.5) <= 5.0e-9
    assert final["maxwell_fixed_point_error"] <= 2.0e-11
    assert final["gauss_relative_residual"] <= 1.0e-11
    assert final["ampere_relative_residual"] <= 1.0e-11
    assert final["magnetic_divergence_max"] <= 1.0e-11


def test_m141_discrete_imaginary_functional_drives_entropic_relaxation() -> None:
    result = run_pauli_hartree_u1_campaign()
    assert result["final"]["discrete_imaginary_action"] < result["initial"][
        "discrete_imaginary_action"
    ]
    assert result["final"]["relative_stationary_residual"] < result["initial"][
        "relative_stationary_residual"
    ]
    assert result["final_state_manifest"]["entropic_time"] > 0.0


def test_m141_state_manifest_and_validation() -> None:
    cfg = PauliHartreeU1Config(relaxation_steps=1)
    state = construct_state(cfg)
    manifest = state.manifest(cfg)
    assert manifest["shape"] == [2, cfg.points, cfg.points, cfg.points]
    assert manifest["measured_winding"] == cfg.winding
    assert len(manifest["state_fingerprint"]) == 64
    with pytest.raises(ValueError, match="odd"):
        PauliHartreeU1Config(points=16)
