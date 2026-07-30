from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.su3_link_backreaction_m105 import (
    SU3LinkBackreactionConfig,
    construct_link_state,
    gell_mann_diagnostics,
    run_su3_link_backreaction_study,
)


def test_gell_mann_basis_and_casimir_close() -> None:
    result = gell_mann_diagnostics()
    assert max(result.values()) <= 2.0e-12


def test_constructed_link_state_has_nontrivial_backreaction() -> None:
    state = construct_link_state(SU3LinkBackreactionConfig(), sample=0)
    assert len(state.links) == 4
    assert len(state.currents) == 4
    assert state.wilson_action_before >= 0.0
    assert abs(state.wilson_action_after - state.wilson_action_before) >= 1.0e-7
    assert all(abs(np.trace(current)) <= 2.0e-12 for current in state.currents)


def test_complete_m10_5_study_passes() -> None:
    result = run_su3_link_backreaction_study()
    assert result["passed"]
    assert result["sample_count"] == 24
    assert result["maximum_unitarity_error"] <= 2.0e-12
    assert result["maximum_determinant_error"] <= 2.0e-12
    assert result["maximum_plaquette_covariance_error"] <= 2.0e-12
    assert result["maximum_wilson_gauge_error"] <= 2.0e-12
    assert result["maximum_current_covariance_error"] <= 2.0e-12
    assert result["maximum_current_reconstruction_error"] <= 2.0e-12
    assert result["maximum_backreaction_covariance_error"] <= 2.0e-12
    assert result["minimum_nonabelian_commutator"] >= 1.0e-3
    assert result["minimum_backreaction_action_shift"] >= 1.0e-7
    assert result["source_first_derivative_error"] <= 1.0e-8
    assert result["source_second_derivative_error"] <= 1.0e-7
    assert result["relative_partition_shift"] >= 1.0e-5
    assert result["decision"]["matrix_valued_su3_links_are_constructed"]
    assert result["decision"]["local_gauge_covariance_is_executed"]
    assert result["decision"]["color_fermion_backreaction_is_executed"]
    assert result["decision"]["center_only_qcd_has_been_strictly_extended"]
