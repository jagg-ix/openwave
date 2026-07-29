from openwave.xperiments.m9_cat_ept.qcd_order_parameters_m136 import (
    PHYSLIB_TIP,
    SOURCE_RECORDS,
    chiral_rotate,
    eta_prime_mass_sq,
    gmor_pion_mass_sq,
    polyakov_magnitude,
    run_qcd_order_parameter_study,
    theta_shift,
)


def test_physlib_tip_and_source_records_are_pinned() -> None:
    assert PHYSLIB_TIP == "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
    assert len(SOURCE_RECORDS) == 3
    assert all(len(record["blob"]) == 40 for record in SOURCE_RECORDS)
    assert all(record["contract_status"] == "satisfied" for record in SOURCE_RECORDS)


def test_polyakov_weight_has_expected_monotonicities() -> None:
    assert polyakov_magnitude(2.0, 1.0) > polyakov_magnitude(1.0, 1.0)
    assert polyakov_magnitude(1.0, 2.0) < polyakov_magnitude(1.0, 1.0)


def test_chiral_rotation_preserves_radius() -> None:
    before = (0.2, -0.4)
    after = chiral_rotate(0.9, *before)
    assert abs(after[0] ** 2 + after[1] ** 2 - (before[0] ** 2 + before[1] ** 2)) < 1e-14


def test_gmor_and_anomaly_limits() -> None:
    assert gmor_pion_mass_sq(0.004, -0.014, 0.092) > 0
    assert gmor_pion_mass_sq(0.0, -0.014, 0.092) == 0
    theta = 0.7
    n_f = 3.0
    assert abs(theta_shift(theta, -theta / (2 * n_f), n_f)) < 1e-14
    assert eta_prime_mass_sq(n_f, 0.001, 0.092) > 0
    assert eta_prime_mass_sq(n_f, 0.0, 0.092) == 0


def test_qcd_order_parameter_study_passes_without_promoting_boundaries() -> None:
    result = run_qcd_order_parameter_study()
    assert result.passed
    assert all(result.acceptance.values())
    assert "no numerical T_c promotion" in result.boundaries
    assert "no ab initio condensate or topological susceptibility" in result.boundaries
    assert result.fingerprint() == result.fingerprint()
