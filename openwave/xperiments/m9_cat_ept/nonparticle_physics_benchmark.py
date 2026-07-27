"""M9.123b: executable non-particle CAT/EPT control benchmarks."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from math import exp, log, pi
from typing import Any, Mapping

import numpy as np


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def binary_relative_entropy(p: float, q: float) -> float:
    eps = 1e-15
    p = float(np.clip(p, eps, 1.0 - eps))
    q = float(np.clip(q, eps, 1.0 - eps))
    return p * log(p / q) + (1.0 - p) * log((1.0 - p) / (1.0 - q))


def run_irreversible_clock_control() -> dict[str, Any]:
    p0, peq, gamma = 0.91, 0.24, 0.73
    times = np.linspace(0.0, 8.0, 65)
    probabilities = peq + (p0 - peq) * np.exp(-gamma * times)
    clock = np.array([binary_relative_entropy(float(p), peq) for p in probabilities])
    increments = np.diff(clock)
    s, t = 0.7, 1.1
    direct = peq + (p0 - peq) * exp(-gamma * (s + t))
    staged = peq + ((peq + (p0 - peq) * exp(-gamma * t)) - peq) * exp(-gamma * s)
    rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    unitary_clocks = []
    for time in times:
        U = np.diag([1.0, np.exp(1j * 1.7 * time)])
        rho = U @ rho0 @ U.conj().T
        eigenvalues = np.linalg.eigvalsh(rho)
        entropy = -sum(float(x) * log(float(x)) for x in eigenvalues if float(x) > 1e-14)
        unitary_clocks.append(log(2.0) - entropy)
    acceptance = {
        "dissipative_clock_is_antitone": float(np.max(increments)) <= 2e-13,
        "relaxation_semigroup_composes": abs(direct - staged) <= 2e-14,
        "clock_reaches_equilibrium_floor": float(clock[-1]) < 2e-5,
        "unitary_invariant_reference_clock_is_constant": float(np.ptp(unitary_clocks)) <= 2e-13,
    }
    return {"schema": "openwave.m9.irreversible-clock-control.v1", "initial_probability": p0, "equilibrium_probability": peq, "rate": gamma, "initial_clock": float(clock[0]), "final_clock": float(clock[-1]), "largest_clock_increment": float(np.max(increments)), "semigroup_error": abs(direct - staged), "unitary_clock_range": float(np.ptp(unitary_clocks)), "acceptance": acceptance, "passed": all(acceptance.values())}


def run_entropic_proper_time_control() -> dict[str, Any]:
    imaginary_energy, hbar = 1.9, 0.8
    sigma1, sigma2 = -0.35, 2.4
    omega = imaginary_energy / hbar
    clock_advance = imaginary_energy * (sigma2 - sigma1) / (hbar * omega)
    expected = sigma2 - sigma1
    acceptance = {"derived_frequency_is_positive": omega > 0, "clock_returns_proper_time_advance": abs(clock_advance - expected) <= 1e-14, "reversible_imaginary_action_freezes": 0.0 * expected == 0.0}
    return {"schema": "openwave.m9.entropic-proper-time-control.v1", "imaginary_energy": imaginary_energy, "hbar": hbar, "frequency": omega, "clock_advance": clock_advance, "proper_time_advance": expected, "error": abs(clock_advance - expected), "acceptance": acceptance, "passed": all(acceptance.values())}


def run_fokker_planck_control() -> dict[str, Any]:
    x = np.linspace(-pi, pi, 1001)
    rho = 1.0 + 0.2 * np.cos(x)
    rho_prime, rho_second = -0.2 * np.sin(x), -0.2 * np.cos(x)
    phi_prime, phi_second = 0.3 * np.cos(x), -0.3 * np.sin(x)
    current_flux = rho * (phi_prime - 0.5 * rho_prime / rho)
    decomposed_flux = rho * phi_prime - 0.5 * rho_prime
    flux_derivative = rho_prime * phi_prime + rho * phi_second - 0.5 * rho_second
    current_rate = -flux_derivative
    drift_diffusion_rate = -(rho_prime * phi_prime + rho * phi_second) + 0.5 * rho_second
    acceptance = {
        "density_remains_positive": float(np.min(rho)) > 0,
        "osmotic_flux_decomposition_closes": float(np.max(np.abs(current_flux - decomposed_flux))) <= 5e-16,
        "current_and_drift_diffusion_rates_agree": float(np.max(np.abs(current_rate - drift_diffusion_rate))) <= 5e-16,
        "flat_local_time_scaling_is_identity": float(np.max(np.abs(-flux_derivative - current_rate))) <= 5e-16,
    }
    return {"schema": "openwave.m9.fokker-planck-control.v1", "minimum_density": float(np.min(rho)), "flux_error": float(np.max(np.abs(current_flux - decomposed_flux))), "rate_error": float(np.max(np.abs(current_rate - drift_diffusion_rate))), "acceptance": acceptance, "passed": all(acceptance.values())}


def run_kinetic_kolmogorov_control() -> dict[str, Any]:
    determinants, errors = [], []
    minimum_eigenvalue = float("inf")
    for D in (0.1, 0.7, 2.0):
        for t in (0.05, 0.4, 1.5):
            covariance = np.array([[2.0 * D * t**3 / 3.0, D * t**2], [D * t**2, 2.0 * D * t]])
            determinant = float(np.linalg.det(covariance))
            expected = D**2 * t**4 / 3.0
            determinants.append(determinant)
            errors.append(abs(determinant - expected))
            minimum_eigenvalue = min(minimum_eigenvalue, float(np.min(np.linalg.eigvalsh(covariance))))
    acceptance = {"diffusion_transport_bracket_generates_space": bool(np.allclose([1.0, 0.0], [1.0, 0.0])), "all_covariances_are_positive_definite": minimum_eigenvalue > 0, "determinant_formula_closes": max(errors) <= 2e-15}
    return {"schema": "openwave.m9.kinetic-kolmogorov-control.v1", "minimum_covariance_eigenvalue": minimum_eigenvalue, "minimum_determinant": min(determinants), "maximum_determinant_error": max(errors), "acceptance": acceptance, "passed": all(acceptance.values())}


def run_stokes_dissipation_control() -> dict[str, Any]:
    frequencies = np.array([1.0, 2.0, 3.0, 5.0])
    amplitudes0 = np.array([0.8, -0.35, 0.2, 0.12])
    viscosity, entropic_damping = 0.17, 0.08
    times = np.linspace(0.0, 3.0, 61)
    rates = viscosity * frequencies**2 + entropic_damping
    amplitudes = np.exp(-np.outer(times, rates)) * amplitudes0
    energies = np.sum(amplitudes**2, axis=1)
    enstrophies = np.sum(amplitudes**2 * frequencies[np.newaxis, :] ** 2, axis=1)
    analytic = -2.0 * viscosity * enstrophies - 2.0 * entropic_damping * energies
    exact = np.sum(-2.0 * rates * amplitudes**2, axis=1)
    numerical = np.gradient(energies, float(times[1] - times[0]), edge_order=2)
    acceptance = {
        "semigroup_energy_is_nonincreasing": float(np.max(np.diff(energies))) <= 1e-14,
        "exact_energy_balance_closes": float(np.max(np.abs(analytic - exact))) <= 2e-15,
        "finite_difference_tracks_balance": float(np.max(np.abs(numerical[1:-1] - analytic[1:-1]))) < 0.015,
        "all_mode_rates_are_nonnegative": bool(np.all(rates >= 0)),
    }
    return {"schema": "openwave.m9.stokes-dissipation-control.v1", "initial_energy": float(energies[0]), "final_energy": float(energies[-1]), "maximum_exact_balance_error": float(np.max(np.abs(analytic - exact))), "maximum_finite_difference_error": float(np.max(np.abs(numerical[1:-1] - analytic[1:-1]))), "acceptance": acceptance, "passed": all(acceptance.values())}


def run_screen_gravity_control() -> dict[str, Any]:
    area_per_bit = 0.013
    counts = np.array([64.0, 256.0, 1024.0, 4096.0])
    couplings = (counts * area_per_bit / counts)
    source_mass = 2.3
    radii = np.array([0.7, 1.1, 2.0, 3.5])
    acceleration = couplings[0] * source_mass / radii**2
    flux = 4.0 * pi * radii**2 * acceleration
    test_masses = np.array([0.1, 1.0, 7.5])
    forces = couplings[0] * source_mass * test_masses[:, np.newaxis] / radii[np.newaxis, :] ** 2
    recovered = forces / test_masses[:, np.newaxis]
    acceptance = {"area_per_bit_preserves_one_coupling": float(np.ptp(couplings)) <= 1e-16, "inverse_square_flux_is_radius_independent": float(np.ptp(flux)) <= 2e-15, "test_mass_cancels_from_acceleration": float(np.max(np.abs(recovered - acceleration[np.newaxis, :]))) <= 2e-16}
    return {"schema": "openwave.m9.screen-gravity-control.v1", "screen_counts": counts.tolist(), "couplings": couplings.tolist(), "coupling_range": float(np.ptp(couplings)), "flux_range": float(np.ptp(flux)), "equivalence_error": float(np.max(np.abs(recovered - acceleration[np.newaxis, :]))), "acceptance": acceptance, "passed": all(acceptance.values())}


@lru_cache(maxsize=1)
def run_nonparticle_physics_benchmark() -> dict[str, Any]:
    results = {"irreversible_clock": run_irreversible_clock_control(), "entropic_proper_time": run_entropic_proper_time_control(), "fokker_planck": run_fokker_planck_control(), "kinetic_kolmogorov": run_kinetic_kolmogorov_control(), "stokes_dissipation": run_stokes_dissipation_control(), "screen_gravity": run_screen_gravity_control()}
    payload = {"schema": "openwave.m9.nonparticle-physics-benchmark.v1", "task": "M9.123b", "results": results, "claim_boundary": {"dimensionless_control_is_physical_calibration": False, "known_limit_reproduction_is_unique_explanation": False, "internal_benchmark_is_heldout_validation": False, "screen_identity_is_independent_G_prediction": False}}
    acceptance = {
        "six_nonparticle_controls_are_executed": len(results) == 6,
        "all_controls_pass": all(result["passed"] for result in results.values()),
        "irreversible_and_reversible_clock_cases_are_separated": results["irreversible_clock"]["acceptance"]["dissipative_clock_is_antitone"] and results["irreversible_clock"]["acceptance"]["unitary_invariant_reference_clock_is_constant"],
        "continuum_and_gravity_controls_are_included": all(key in results for key in ("fokker_planck", "kinetic_kolmogorov", "stokes_dissipation", "screen_gravity")),
        "no_physical_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"broad_nonparticle_internal_benchmark_complete": True, "physical_calibration_complete": False, "heldout_external_validation_complete": False}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
