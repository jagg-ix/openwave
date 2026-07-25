from openwave.xperiments.m9_cat_ept.hminus_one_mild_flow_audit import (
    HMinusOneAuditConfig,
    laplacian_mapping_table,
    normalized_gaussian_energy,
    run_hminus_one_mild_flow_audit,
    weak_unit_sphere_counterexample,
)


def test_laplacian_mapping_selects_hminus_one():
    rows = laplacian_mapping_table(HMinusOneAuditConfig(fourier_modes=(1, 2, 4)))
    assert rows[-1]["laplacian_h1_to_h1_ratio"] == 16.0
    assert all(0 <= row["laplacian_h1_to_hminus1_ratio"] < 1 for row in rows)


def test_unit_sphere_is_not_weakly_closed():
    result = weak_unit_sphere_counterexample(HMinusOneAuditConfig())
    assert not result["unit_sphere_is_weakly_closed"]
    assert result["sequence_l2_mass"] == 1.0


def test_negative_translation_energy():
    assert normalized_gaussian_energy(1.0) < 0


def test_m9_75_passes():
    assert run_hminus_one_mild_flow_audit()["passed"]