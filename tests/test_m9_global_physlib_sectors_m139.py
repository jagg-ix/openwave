from openwave.xperiments.m9_cat_ept.global_physlib_sectors_m139 import (
    FORMAL_HEAD,
    SOURCES,
    axial_anomaly_sector,
    anomalous_moment_sector,
    fingerprint,
    retarded_sector,
    run_global_physlib_sectors,
)


def test_global_authority_passes():
    result = run_global_physlib_sectors()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert FORMAL_HEAD == "deb1eb3ecb4aabbba1555b24253d9dd8f6fba1f2"
    assert len(SOURCES) == 3


def test_retarded_sector_is_null_and_future_directed():
    result = retarded_sector(t=9.0, r=5.0, c=2.5)
    assert result["lightlike"]
    assert result["future_directed"]
    assert abs(result["lightcone_form"]) <= 1.0e-12


def test_anomalous_moment_sector_preserves_gauge_and_split():
    result = anomalous_moment_sector(a=0.0023, chi=-1.7)
    assert result["faraday_gauge_error"] <= 1.0e-12
    assert result["interaction_scaling_error"] <= 1.0e-12
    assert result["g_factor"] == 2.0 * (1.0 + 0.0023)


def test_axial_rotation_and_eta_prime_limits():
    result = axial_anomaly_sector(theta=1.2, n_flavors=3.0, chi_top=0.2, f_pi=0.093)
    assert abs(result["shifted_theta"]) <= 1.0e-12
    assert result["theta_vacuum_error"] <= 1.0e-12
    assert result["eta_prime_massive"]
    assert result["large_n_zero_susceptibility_mass_sq"] == 0.0
    assert not result["anomaly_equation_derived_from_path_integral"]
    assert not result["topological_susceptibility_computed"]


def test_fingerprint_is_stable():
    assert len(fingerprint()) == 64
    assert fingerprint() == fingerprint()
