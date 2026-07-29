from openwave.xperiments.m9_cat_ept.qcd_particle_authority_m135 import (
    FORMAL_SOURCES,
    beta_function,
    beta_zero,
    complex_action_weight,
    hadron_mass_sq,
    ratio_r_uds,
    run_qcd_particle_authority,
    running_coupling,
    running_coupling_derivative,
    theta_weight,
    trace_anomaly,
    wilson_area_law,
)


def test_verified_physlib_sources_and_zil_root_are_registered():
    assert len(FORMAL_SOURCES) == 5
    assert all(len(source.blob) == 40 for source in FORMAL_SOURCES)
    assert FORMAL_SOURCES[0].declarations == ("Physlib.Meta.Zil", "Physlib.Meta.ZilGraph")
    assert any("numerical hadron mass" in boundary for source in FORMAL_SOURCES for boundary in source.boundary)


def test_one_loop_qcd_running_solves_beta_function():
    b0 = beta_zero(6.0)
    alpha0 = 0.22
    t = 4.0
    alpha = running_coupling(b0, alpha0, t)
    assert b0 > 0
    assert beta_function(b0, alpha0) < 0
    assert abs(running_coupling_derivative(b0, alpha0, t) - beta_function(b0, alpha)) < 1e-12
    assert running_coupling(b0, alpha0, 20.0) < alpha < alpha0


def test_theta_phase_and_confinement_factorize_master_weight():
    theta = 0.37
    winding = 3
    sigma = 0.81
    area = 1.7
    phase = theta_weight(theta, winding)
    assert abs(abs(phase) - 1.0) < 1e-12
    assert abs(theta_weight(theta + 2.0 * 3.141592653589793, winding) - phase) < 1e-12
    assert abs(theta_weight(theta, -winding) - phase.conjugate()) < 1e-12
    assert abs(
        complex_action_weight(theta * winding, sigma * area)
        - phase * wilson_area_law(sigma, area)
    ) < 1e-12


def test_color_counting_and_trace_anomaly_boundaries():
    assert ratio_r_uds() == 2.0
    assert 3**2 - 1 == 8
    anomaly = trace_anomaly(beta_zero(6.0), 1.3, 2.1)
    assert anomaly < 0
    assert hadron_mass_sq(anomaly) > 0


def test_complete_qcd_particle_authority_passes_without_promotion():
    result = run_qcd_particle_authority()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.qcd-particle-authority.v1"
    assert result["formal_repository"] == {
        "name": "jagg-ix/entropic-physlib-private",
        "branch": "entropic-physlib-linear-full",
    }
    assert len(result["source_fingerprint"]) == 64
    assert result["decision"]["qcd_formal_program_is_substantial"]
    assert not result["decision"]["numerical_hadron_spectrum_derived"]
    assert not result["decision"]["continuum_yang_mills_mass_gap_proved"]
    assert not result["decision"]["first_principles_confinement_proved"]
    assert result["decision"]["physical_claims_promoted"] == []
