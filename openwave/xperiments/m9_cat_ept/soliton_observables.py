"""M9.5 analytic and numerical ledger for the 1D focusing-cubic soliton family.

The family belongs to

    i psi_t = -1/2 psi_xx - g |psi|^2 psi,  g > 0.

For prescribed norm ``N > 0``, the exact stationary profile is

    psi(x,t) = A sech(B x) exp(i Omega t),
    B = g N / 2,
    A = N sqrt(g) / 2,
    Omega = B^2 / 2.

These equations correlate norm, radius, energy, and frequency. They are
mathematical identities of the selected model, not independent particle
predictions and not a physical unit calibration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class SolitonParameters:
    """Positive focusing strength and conserved norm."""

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
        return self.norm * math.sqrt(self.coupling) / 2.0

    @property
    def chemical_potential(self) -> float:
        return -(self.inverse_width**2) / 2.0

    @property
    def phase_frequency(self) -> float:
        return -self.chemical_potential

    @property
    def energy(self) -> float:
        return -(self.coupling**2) * self.norm**3 / 24.0

    @property
    def rms_radius(self) -> float:
        return math.pi / (math.sqrt(12.0) * self.inverse_width)

    @property
    def density_half_width(self) -> float:
        return math.acosh(math.sqrt(2.0)) / self.inverse_width


@dataclass(frozen=True)
class NumericalLedger:
    """Quadrature checks for one member of the analytic family."""

    coupling: float
    requested_norm: float
    inverse_width: float
    amplitude: float
    numerical_norm: float
    numerical_energy: float
    numerical_rms_radius: float
    numerical_stationary_residual: float
    analytic_energy: float
    analytic_rms_radius: float
    phase_frequency: float
    chemical_potential: float
    norm_error: float
    energy_error: float
    radius_error: float


def sech(values: RealArray) -> RealArray:
    return np.asarray(1.0 / np.cosh(values), dtype=np.float64)


def profile(x: RealArray, parameters: SolitonParameters) -> ComplexArray:
    """Return the real stationary profile at time zero."""
    return np.asarray(
        parameters.amplitude * sech(parameters.inverse_width * x),
        dtype=np.complex128,
    )


def state(x: RealArray, time: float, parameters: SolitonParameters) -> ComplexArray:
    """Return the exact time-dependent family member."""
    return np.asarray(
        profile(x, parameters) * np.exp(1j * parameters.phase_frequency * time),
        dtype=np.complex128,
    )


def first_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return the exact spatial derivative of the real profile."""
    scaled = parameters.inverse_width * x
    return np.asarray(
        -parameters.amplitude
        * parameters.inverse_width
        * sech(scaled)
        * np.tanh(scaled),
        dtype=np.float64,
    )


def second_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return the exact second spatial derivative of the real profile."""
    scaled = parameters.inverse_width * x
    base = sech(scaled)
    return np.asarray(
        parameters.amplitude
        * parameters.inverse_width**2
        * base
        * (1.0 - 2.0 * base**2),
        dtype=np.float64,
    )


def stationary_residual(x: RealArray, parameters: SolitonParameters) -> RealArray:
    """Return ``-phi_xx/2 - g phi^3 - mu phi`` pointwise."""
    phi = np.real(profile(x, parameters))
    return np.asarray(
        -0.5 * second_derivative(x, parameters)
        - parameters.coupling * phi**3
        - parameters.chemical_potential * phi,
        dtype=np.float64,
    )


def numerical_ledger(
    parameters: SolitonParameters,
    *,
    scaled_half_width: float = 24.0,
    points: int = 200_001,
) -> NumericalLedger:
    """Numerically verify the closed-form observables on a wide scaled domain."""
    if scaled_half_width <= 0.0:
        raise ValueError("scaled_half_width must be positive")
    if points < 1001 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 1001")

    half_width = scaled_half_width / parameters.inverse_width
    x = np.linspace(-half_width, half_width, points, dtype=np.float64)
    phi = np.real(profile(x, parameters))
    derivative = first_derivative(x, parameters)
    density = phi**2
    norm = float(np.trapezoid(density, x))
    kinetic = 0.5 * derivative**2
    nonlinear = -0.5 * parameters.coupling * phi**4
    energy_value = float(np.trapezoid(kinetic + nonlinear, x))
    variance = float(np.trapezoid(x**2 * density, x) / norm)
    residual = stationary_residual(x, parameters)
    residual_l2 = float(math.sqrt(np.trapezoid(residual**2, x)))
    numerical_radius = math.sqrt(variance)

    return NumericalLedger(
        coupling=parameters.coupling,
        requested_norm=parameters.norm,
        inverse_width=parameters.inverse_width,
        amplitude=parameters.amplitude,
        numerical_norm=norm,
        numerical_energy=energy_value,
        numerical_rms_radius=numerical_radius,
        numerical_stationary_residual=residual_l2,
        analytic_energy=parameters.energy,
        analytic_rms_radius=parameters.rms_radius,
        phase_frequency=parameters.phase_frequency,
        chemical_potential=parameters.chemical_potential,
        norm_error=abs(norm - parameters.norm),
        energy_error=abs(energy_value - parameters.energy),
        radius_error=abs(numerical_radius - parameters.rms_radius),
    )


def run_observable_study(
    cases: Sequence[tuple[float, float]] = (
        (1.0, 0.5),
        (1.0, 1.0),
        (2.0, 1.0),
        (3.0, 0.5),
        (2.0, 2.0),
    ),
) -> dict[str, Any]:
    """Run the deterministic M9.5 identity and quadrature ledger."""
    ledgers = [
        numerical_ledger(SolitonParameters(coupling=coupling, norm=norm))
        for coupling, norm in cases
    ]
    serialized = [asdict(ledger) for ledger in ledgers]

    scaling_checks = []
    for coupling, norm in cases:
        parameters = SolitonParameters(coupling=coupling, norm=norm)
        scaling_checks.append(
            {
                "coupling": coupling,
                "norm": norm,
                "inverse_width_eq_gN_over_2": math.isclose(
                    parameters.inverse_width,
                    coupling * norm / 2.0,
                    rel_tol=0.0,
                    abs_tol=1.0e-15,
                ),
                "energy_eq_minus_g2N3_over_24": math.isclose(
                    parameters.energy,
                    -(coupling**2) * norm**3 / 24.0,
                    rel_tol=0.0,
                    abs_tol=1.0e-15,
                ),
                "frequency_eq_inverse_width_sq_over_2": math.isclose(
                    parameters.phase_frequency,
                    parameters.inverse_width**2 / 2.0,
                    rel_tol=0.0,
                    abs_tol=1.0e-15,
                ),
                "radius_width_product": parameters.rms_radius
                * parameters.inverse_width,
            }
        )

    acceptance = {
        "all_norms_match": max(item.norm_error for item in ledgers) <= 1.0e-10,
        "all_energies_match": max(item.energy_error for item in ledgers) <= 1.0e-10,
        "all_radii_match": max(item.radius_error for item in ledgers) <= 1.0e-10,
        "all_stationary_residuals_small": max(
            item.numerical_stationary_residual for item in ledgers
        )
        <= 1.0e-10,
        "all_scaling_identities_hold": all(
            check["inverse_width_eq_gN_over_2"]
            and check["energy_eq_minus_g2N3_over_24"]
            and check["frequency_eq_inverse_width_sq_over_2"]
            for check in scaling_checks
        ),
        "radius_width_constant": max(
            abs(check["radius_width_product"] - math.pi / math.sqrt(12.0))
            for check in scaling_checks
        )
        <= 1.0e-15,
    }

    return {
        "schema": "openwave.m9.soliton-observable-ledger.v1",
        "model": "M9-CAT-EPT",
        "equation": "i psi_t = -1/2 psi_xx - g |psi|^2 psi",
        "family": {
            "profile": "A sech(B x) exp(i Omega t)",
            "B": "g N / 2",
            "A": "N sqrt(g) / 2",
            "mu": "-B^2 / 2",
            "Omega": "B^2 / 2",
            "energy": "-g^2 N^3 / 24",
            "rms_radius": "pi / (sqrt(12) B)",
        },
        "cases": serialized,
        "scaling_checks": scaling_checks,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "closed-form scaling identities of the selected 1D model",
                "numerical quadrature agreement for the frozen family cases",
            ],
            "does_not_establish": [
                "a physical mass or length calibration",
                "an electron identity",
                "independent predictions of radius, energy, and frequency",
                "unique selection of the focusing cubic equation by CAT/EPT",
            ],
        },
    }
