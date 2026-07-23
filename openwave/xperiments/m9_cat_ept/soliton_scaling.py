"""Exact scaling family and observable ledger for the M9 bright soliton.

The dimensionless focusing equation is

    i d_t psi = -1/2 d_xx psi - g |psi|^2 psi,  g > 0.

For norm ``N > 0`` it admits a stationary bright-soliton family. This module
records exact identities and verifies them by finite-domain quadrature. The
phase frequency remains dimensionless until a separate physical unit map is
chosen.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class SolitonParameters:
    """Positive coupling magnitude and conserved scalar norm."""

    coupling: float = 2.0
    norm: float = 1.0

    def __post_init__(self) -> None:
        if self.coupling <= 0.0:
            raise ValueError("coupling must be positive")
        if self.norm <= 0.0:
            raise ValueError("norm must be positive")

    @property
    def inverse_width(self) -> float:
        return self.coupling * self.norm / 2.0

    @property
    def amplitude(self) -> float:
        return self.inverse_width / math.sqrt(self.coupling)

    @property
    def chemical_potential(self) -> float:
        return -(self.inverse_width**2) / 2.0

    @property
    def phase_frequency(self) -> float:
        return -self.chemical_potential

    @property
    def energy(self) -> float:
        return -(self.inverse_width**3) / (3.0 * self.coupling)

    @property
    def rms_radius(self) -> float:
        return math.pi / (2.0 * math.sqrt(3.0) * self.inverse_width)

    @property
    def density_fwhm(self) -> float:
        return 2.0 * math.acosh(math.sqrt(2.0)) / self.inverse_width

    def enclosed_radius(self, probability: float) -> float:
        """Radius containing the requested centered probability mass."""
        if not 0.0 < probability < 1.0:
            raise ValueError("probability must lie strictly between 0 and 1")
        return math.atanh(probability) / self.inverse_width


def soliton_profile(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return ``eta/sqrt(g) * sech(eta x)``."""
    eta = parameters.inverse_width
    return np.asarray(parameters.amplitude / np.cosh(eta * x), dtype=np.float64)


def soliton_state(
    x: RealArray,
    time: float,
    parameters: SolitonParameters,
) -> ComplexArray:
    """Return the stationary family member at dimensionless time ``time``."""
    phase = np.exp(1j * parameters.phase_frequency * time)
    return np.asarray(soliton_profile(x, parameters) * phase, dtype=np.complex128)


def profile_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return the exact spatial derivative of the real profile."""
    eta = parameters.inverse_width
    profile = soliton_profile(x, parameters)
    return np.asarray(-eta * profile * np.tanh(eta * x), dtype=np.float64)


def profile_second_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return the exact second derivative of the real profile."""
    eta = parameters.inverse_width
    profile = soliton_profile(x, parameters)
    cubic_coefficient = 2.0 * eta**2 / parameters.amplitude**2
    return np.asarray(eta**2 * profile - cubic_coefficient * profile**3)


def stationary_residual(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Evaluate ``-1/2 phi'' - g phi^3 - mu phi``."""
    profile = soliton_profile(x, parameters)
    return np.asarray(
        -0.5 * profile_second_derivative(x, parameters)
        - parameters.coupling * profile**3
        - parameters.chemical_potential * profile,
        dtype=np.float64,
    )


def numerical_characterization(
    parameters: SolitonParameters,
    *,
    scaled_half_width: float = 16.0,
    points: int = 8193,
) -> dict[str, float]:
    """Verify one family member on a box fixed in the scaled coordinate ``eta x``."""
    if scaled_half_width <= 0.0:
        raise ValueError("scaled_half_width must be positive")
    if points < 257 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 257")

    eta = parameters.inverse_width
    x = np.linspace(
        -scaled_half_width / eta,
        scaled_half_width / eta,
        points,
        dtype=np.float64,
    )
    profile = soliton_profile(x, parameters)
    derivative = profile_derivative(x, parameters)
    density = profile**2
    numerical_norm = float(np.trapezoid(density, x))
    kinetic = 0.5 * float(np.trapezoid(derivative**2, x))
    interaction = -0.5 * parameters.coupling * float(np.trapezoid(profile**4, x))
    numerical_energy = kinetic + interaction
    numerical_variance = float(np.trapezoid(x**2 * density, x) / numerical_norm)
    residual = stationary_residual(x, parameters)
    residual_scale = abs(parameters.chemical_potential) * math.sqrt(numerical_norm)
    residual_l2 = math.sqrt(float(np.trapezoid(residual**2, x)))

    radius_90 = parameters.enclosed_radius(0.90)
    radius_99 = parameters.enclosed_radius(0.99)
    inside_90 = np.abs(x) <= radius_90
    inside_99 = np.abs(x) <= radius_99
    probability_90 = float(np.trapezoid(density[inside_90], x[inside_90]) / numerical_norm)
    probability_99 = float(np.trapezoid(density[inside_99], x[inside_99]) / numerical_norm)

    return {
        "coupling": parameters.coupling,
        "norm": parameters.norm,
        "inverse_width": eta,
        "amplitude": parameters.amplitude,
        "chemical_potential": parameters.chemical_potential,
        "phase_frequency": parameters.phase_frequency,
        "energy": parameters.energy,
        "rms_radius": parameters.rms_radius,
        "density_fwhm": parameters.density_fwhm,
        "radius_90": radius_90,
        "radius_99": radius_99,
        "numerical_norm": numerical_norm,
        "norm_relative_error": abs(numerical_norm - parameters.norm) / parameters.norm,
        "numerical_energy": numerical_energy,
        "energy_relative_error": (
            abs(numerical_energy - parameters.energy) / abs(parameters.energy)
        ),
        "numerical_rms_radius": math.sqrt(numerical_variance),
        "rms_relative_error": abs(math.sqrt(numerical_variance) - parameters.rms_radius)
        / parameters.rms_radius,
        "stationary_residual_relative_l2": residual_l2 / residual_scale,
        "probability_90_error": abs(probability_90 - 0.90),
        "probability_99_error": abs(probability_99 - 0.99),
        "phase_radius_invariant": parameters.phase_frequency * parameters.rms_radius**2,
        "energy_mu_norm_ratio": parameters.energy
        / (parameters.chemical_potential * parameters.norm),
    }


def _log_slope(x: Sequence[float], y: Sequence[float]) -> float:
    coefficients = np.polyfit(np.log(np.asarray(x)), np.log(np.asarray(y)), 1)
    return float(coefficients[0])


def conditional_clock_bridge(parameters: SolitonParameters) -> dict[str, float | str]:
    """Return conditional Compton/ZBW radius ratios without assigning a mass.

    The kinetic unit map gives ``T0 = m L0^2 / hbar``. If the dimensionless
    phase frequency is additionally identified with a Compton or rest-frame ZBW
    frequency, the resulting radius ratios are fixed. Neither hypothesis fixes
    the mass or the absolute unit scale.
    """
    omega = parameters.phase_frequency
    radius = parameters.rms_radius
    return {
        "status": "conditional_identification_not_prediction",
        "dimensionless_phase_frequency": omega,
        "compton_hypothesis_L0_over_lambdaC": math.sqrt(omega),
        "compton_hypothesis_Rrms_over_lambdaC": radius * math.sqrt(omega),
        "zitter_hypothesis_L0_over_lambdaC": math.sqrt(omega / 2.0),
        "zitter_hypothesis_Rrms_over_lambdaC": radius * math.sqrt(omega / 2.0),
        "exact_compton_radius_ratio": math.pi / math.sqrt(24.0),
        "exact_zitter_radius_ratio": math.pi / math.sqrt(48.0),
    }


def run_scaling_study(
    couplings: Sequence[float] = (1.0, 2.0, 4.0),
    norms: Sequence[float] = (0.5, 1.0, 2.0),
) -> dict[str, Any]:
    """Run the deterministic M9.5 family ledger and frozen acceptance checks."""
    rows = [
        numerical_characterization(SolitonParameters(coupling=g, norm=norm))
        for g in couplings
        for norm in norms
    ]
    fixed_coupling = float(couplings[len(couplings) // 2])
    norm_rows = [row for row in rows if row["coupling"] == fixed_coupling]
    norm_axis = [float(row["norm"]) for row in norm_rows]

    slopes = {
        "inverse_width_vs_norm": _log_slope(
            norm_axis, [float(row["inverse_width"]) for row in norm_rows]
        ),
        "phase_frequency_vs_norm": _log_slope(
            norm_axis, [float(row["phase_frequency"]) for row in norm_rows]
        ),
        "absolute_energy_vs_norm": _log_slope(
            norm_axis, [abs(float(row["energy"])) for row in norm_rows]
        ),
        "rms_radius_vs_norm": _log_slope(
            norm_axis, [float(row["rms_radius"]) for row in norm_rows]
        ),
    }
    max_errors = {
        "norm_relative": max(float(row["norm_relative_error"]) for row in rows),
        "energy_relative": max(float(row["energy_relative_error"]) for row in rows),
        "rms_relative": max(float(row["rms_relative_error"]) for row in rows),
        "stationary_residual_relative_l2": max(
            float(row["stationary_residual_relative_l2"]) for row in rows
        ),
        "probability_90": max(float(row["probability_90_error"]) for row in rows),
        "probability_99": max(float(row["probability_99_error"]) for row in rows),
        "phase_radius_invariant": max(
            abs(float(row["phase_radius_invariant"]) - math.pi**2 / 24.0)
            for row in rows
        ),
        "energy_mu_norm_ratio": max(
            abs(float(row["energy_mu_norm_ratio"]) - 1.0 / 3.0) for row in rows
        ),
    }
    slope_targets = {
        "inverse_width_vs_norm": 1.0,
        "phase_frequency_vs_norm": 2.0,
        "absolute_energy_vs_norm": 3.0,
        "rms_radius_vs_norm": -1.0,
    }
    slope_errors = {
        name: abs(slopes[name] - target) for name, target in slope_targets.items()
    }
    acceptance = {
        "norm_quadrature": max_errors["norm_relative"] <= 1.0e-10,
        "energy_quadrature": max_errors["energy_relative"] <= 1.0e-10,
        "rms_quadrature": max_errors["rms_relative"] <= 1.0e-10,
        "stationary_equation": max_errors["stationary_residual_relative_l2"] <= 1.0e-12,
        "enclosed_probability_90": max_errors["probability_90"] <= 2.0e-3,
        "enclosed_probability_99": max_errors["probability_99"] <= 2.0e-3,
        "phase_radius_invariant": max_errors["phase_radius_invariant"] <= 1.0e-12,
        "energy_mu_relation": max_errors["energy_mu_norm_ratio"] <= 1.0e-12,
        "norm_scaling_slopes": max(slope_errors.values()) <= 1.0e-12,
    }
    reference = SolitonParameters()
    return {
        "schema": "openwave.m9.soliton-scaling.v1",
        "model": "M9-CAT-EPT",
        "equation": "i psi_t = -1/2 psi_xx - g |psi|^2 psi",
        "exact_family": {
            "profile": "eta/sqrt(g) sech(eta x)",
            "eta": "g N / 2",
            "mu": "-eta^2 / 2",
            "phase_frequency": "eta^2 / 2",
            "energy": "-eta^3/(3g) = -g^2 N^3/24",
            "rms_radius": "pi/(2 sqrt(3) eta)",
        },
        "rows": rows,
        "observed_norm_scaling_slopes": slopes,
        "slope_errors": slope_errors,
        "max_errors": max_errors,
        "conditional_clock_bridge": conditional_clock_bridge(reference),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "scope": {
            "classification": "exact dimensionless 1+1D scalar soliton family",
            "does_not_establish": [
                "a physical mass or absolute length scale",
                "a Compton or Zitterbewegung identification",
                "electric charge or spin",
                "three-dimensional stability",
                "derivation of the focusing cubic interaction from CAT/EPT",
            ],
        },
    }
