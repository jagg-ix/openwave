from openwave.xperiments.m9_cat_ept.adm_general_shift_m134 import (
    FORMAL_SOURCE,
    run_adm_general_shift_study,
)
from openwave.xperiments.m9_cat_ept.m134_adm_general_shift_authority import (
    run_m134_adm_general_shift_authority,
)


def test_formal_source_records_six_declarations_without_fake_full_pin():
    assert len(FORMAL_SOURCE["declarations"]) == 6
    assert FORMAL_SOURCE["short_commit"] == "31461dc67"
    assert FORMAL_SOURCE["full_commit_verified"] is False
    assert FORMAL_SOURCE["source_blob_verified"] is False


def test_general_shift_adm_identities_close():
    result = run_adm_general_shift_study()
    diagnostics = result["diagnostics"]
    assert result["passed"]
    assert diagnostics["general_shift_effect_relative"] >= 1.0e-3
    assert diagnostics["metric_rate_symmetry_error"] <= 2.0e-12
    assert diagnostics["zero_shift_reduction_error"] <= 2.0e-12
    assert diagnostics["extrinsic_curvature_recovery_error"] <= 2.0e-12
    assert diagnostics["momentum_flux_decomposition_error"] <= 2.0e-12
    assert diagnostics["traceless_trace_max"] <= 2.0e-12


def test_scope_is_corrected_but_not_overpromoted():
    result = run_adm_general_shift_study()
    decision = result["decision"]
    assert decision["general_shift_adm_evolution_constructed"]
    assert decision["shift_free_model_is_zero_shift_special_case"]
    assert decision["momentum_flux_carries_tracefree_curvature"]
    assert not decision["curved_covariant_derivative_operator_constructed"]
    assert not decision["sourced_tt_wave_propagation_constructed"]


def test_composed_authority_preserves_existing_gravity_carriers():
    result = run_m134_adm_general_shift_authority()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["gravity_beyond_weak_field_general_shift_gap_closed"]
    assert result["decision"]["general_extrinsic_curvature_gap_closed"]
    assert result["decision"]["tt_mode_carrier_gap_closed"]
    assert result["decision"]["sourced_tt_wave_equation_open"]
    assert result["decision"]["curved_covariant_derivative_operator_open"]
    assert result["decision"]["physical_claims_promoted"] == []
