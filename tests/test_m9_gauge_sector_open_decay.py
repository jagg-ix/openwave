import math

import numpy as np

from openwave.xperiments.m9_cat_ept.gauge_sector_open_decay import (
    amplitude_damping_kraus,
    exact_amplitude_damping,
    lindblad_generator,
    run_gauge_sector_open_decay,
)


def test_amplitude_damping_is_cptp_and_composes() -> None:
    gamma = 0.37
    omega = 1.2
    rho = np.asarray(((0.2, 0.1j), (-0.1j, 0.8)), dtype=np.complex128)
    s, t = 0.4, 0.7
    kraus = amplitude_damping_kraus(gamma, s, omega)
    completeness = sum(operator.conjugate().T @ operator for operator in kraus)
    assert np.allclose(completeness, np.eye(2), atol=2.0e-14)

    direct = exact_amplitude_damping(rho, gamma, s + t, omega)
    composed = exact_amplitude_damping(
        exact_amplitude_damping(rho, gamma, t, omega), gamma, s, omega
    )
    assert np.allclose(direct, composed, atol=2.0e-13)
    assert np.isclose(np.trace(direct), np.trace(rho), atol=2.0e-14)
    assert np.min(np.linalg.eigvalsh(direct)) >= -2.0e-14


def test_exact_channel_has_declared_lindblad_generator() -> None:
    gamma = 0.23
    omega = 0.9
    rho = np.asarray(((0.55, 0.13 + 0.09j), (0.13 - 0.09j, 0.45)), dtype=np.complex128)
    step = 1.0e-7
    derivative = (exact_amplitude_damping(rho, gamma, step, omega) - rho) / step
    expected = lindblad_generator(rho, gamma, omega)
    error = np.linalg.norm(derivative - expected) / np.linalg.norm(expected)
    assert error <= 2.0e-6


def test_excited_population_defines_lifetime_and_half_life() -> None:
    gamma = 0.41
    excited = np.asarray(((0.0, 0.0), (0.0, 1.0)), dtype=np.complex128)
    lifetime = 1.0 / gamma
    half_life = math.log(2.0) / gamma
    assert np.isclose(
        exact_amplitude_damping(excited, gamma, lifetime)[1, 1].real,
        math.exp(-1.0),
        atol=2.0e-14,
    )
    assert np.isclose(
        exact_amplitude_damping(excited, gamma, half_life)[1, 1].real,
        0.5,
        atol=2.0e-14,
    )


def test_m121a_campaign_passes_without_physical_width_promotion() -> None:
    result = run_gauge_sector_open_decay()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["cptp_open_system_decay_constructed"]
    assert result["decision"]["intrinsic_model_unit_lifetime_constructed"]
    assert not result["decision"]["physical_decay_width_calibrated"]
    assert not result["decision"]["observed_transition_identity_promoted"]
    assert not any(result["claim_boundary"].values())
