"""M9.5 exact scaling and observable ledger for the 1D bright soliton.

The selected equation is

    i psi_t = -1/2 psi_xx - g |psi|^2 psi,  g > 0.

For conserved scalar norm ``N > 0`` the exact family is

    eta = g N / 2,
    phi(x) = eta / sqrt(g) sech(eta x),
    psi(x,t) = phi(x) exp(i eta^2 t / 2).

All observables below are correlated identities of this selected dimensionless
model. They are not independent particle predictions or an absolute unit map.
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
    coupling: float = 2.0
    norm: float = 1.0

    def __post_init__(self) -> None:
        if self.coupling <= 0.0:
            raise ValueError("coupling must be positive")
        if self.norm <= 0.0:
            raise ValueError("norm must be positive")

    @property
    def eta(self) -> float:
        return self.coupling * self.norm / 2.0

    @property
    def amplitude(self) -> float:
        return self.eta / math.sqrt(self.coupling)

    @property
    def chemical_potential(self) -> float:
        return -(self.eta**2) / 2.0

    @property
    def phase_frequency(self) -> float:
        return -self.chemical_potential

    @property
    def energy(self) -> float:
        return -(self.eta**3) / (3.0 * self.coupling)

    @property
    def rms_radius(self) -> float:
        return math.pi / (2.0 * math.sqrt(3.0) * self.eta)

    @property
    def density_fwhm(self) -> float:
        return 2.0 * math.acosh(math.sqrt(2.0)) / self.eta

    def radius_for_probability(self, probability: float) -> float:
        if not 0.0 < probability < 1.0:
            raise ValueError("probability must lie strictly between zero and one")
        return math.atanh(probability) / self.eta


@dataclass(frozen=True)
class NumericalLedger:
    coupling: float
    requested_norm: float
    eta: float
    amplitude: float
    numerical_norm: float
    numerical_energy: float
    numerical_rms_radius: float
    stationary_residual_relative_l2: float
    enclosed_probability_90: float
    enclosed_probability_99: float
    analytic_energy: float
    analytic_rms_radius: float
    phase_frequency: float
    chemical_potential: float
    norm_relative_error: float
    energy_relative_error: float
    radius_relative_error: float
    enclosed_probability_90_error: float
    enclosed_probability_99_error: float
    frequency_radius_invariant_error: float
    energy_mu_norm_relation_error: float


def sech(values: RealArray) -> RealArray:
    return np.asarray(1.0 / np.cosh(values), dtype=np.float64)


def profile(x: RealArray, parameters: SolitonParameters) -> ComplexArray:
    return np.asarray(
        parameters.amplitude * sech(parameters.eta * x),
        dtype=np.complex128,
    )


def state(x: RealArray, time: float, parameters: SolitonParameters) -> ComplexArray:
    return np.asarray(
        profile(x, parameters) * np.exp(1j * parameters.phase_frequency * time),
        dtype=np.complex128,
    )


def first_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    scaled = parameters.eta * x
    return np.asarray(
        -parameters.amplitude
        * parameters.eta
        * sech(scaled)
        * np.tanh(scaled),
        dtype=np.float64,
    )


def second_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    scaled = parameters.eta * x
    base = sech(scaled)
    return np.asarray(
        parameters.amplitude
        * parameters.eta**2
        * base
        * (1.0 - 2.0 * base**2),
        dtype=np.float64,
    )


def stationary_residual(x: RealArray, parameters: SolitonParameters) -> RealArray:
    phi = np.real(profile(x, parameters))
    return np.asarray(
        -0.5 * second_derivative(x, parameters)
        - parameters.coupling * phi**3
        - parameters.chemical_potential * phi,
        dtype=np.float64,
    )


def _relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / abs(expected)


def numerical_ledger(
    parameters: SolitonParameters,
    *,
    scaled_half_width: float = 16.0,
    points: int = 8193,
) -> NumericalLedger:
    if scaled_half_width <= 0.0:
        raise ValueError("scaled_half_width must be positive")
    if points < 1001 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 1001")

    half_width = scaled_half_width / parameters.eta
    x = np.linspace(-half_width, half_width, points, dtype=np.float64)
    phi = np.real(profile(x, parameters))
    derivative = first_derivative(x, parameters)
    density = phi**2
    numerical_norm = float(np.trapezoid(density, x))
    numerical_energy = float(
        np.trapezoid(
            0.5 * derivative**2
            - 0.5 * parameters.coupling * phi**4,
            x,
        )
    )
    variance = float(np.trapezoid(x**2 * density, x) / numerical_norm)
    numerical_radius = math.sqrt(variance)

    residual = stationary_residual(x, parameters)
    residual_l2 = math.sqrt(float(np.trapezoid(residual**2, x)))
    residual_scale = abs(parameters.chemical_potential) * math.sqrt(parameters.norm)

    enclosed: dict[float, float] = {}
    for probability in (0.90, 0.99):
        radius = parameters.radius_for_probability(probability)
        mask = np.abs(x) <= radius
        enclosed[probability] = float(np.trapezoid(density[mask], x[mask]))

    invariant = parameters.phase_frequency * parameters.rms_radius**2
    invariant_target = math.pi**2 / 24.0
    energy_relation = parameters.energy / (
        parameters.chemical_potential * parameters.norm
    )

    return NumericalLedger(
        coupling=parameters.coupling,
        requested_norm=parameters.norm,
        eta=parameters.eta,
        amplitude=parameters.amplitude,
        numerical_norm=numerical_norm,
        numerical_energy=numerical_energy,
        numerical_rms_radius=numerical_radius,
        stationary_residual_relative_l2=residual_l2 / residual_scale,
        enclosed_probability_90=enclosed[0.90],
        enclosed_probability_99=enclosed[0.99],
        analytic_energy=parameters.energy,
        analytic_rms_radius=parameters.rms_radius,
        phase_frequency=parameters.phase_frequency,
        chemical_potential=parameters.chemical_potential,
        norm_relative_error=_relative_error(numerical_norm, parameters.norm),
        energy_relative_error=_relative_error(numerical_energy, parameters.energy),
        radius_relative_error=_relative_error(numerical_radius, parameters.rms_radius),
        enclosed_probability_90_error=abs(enclosed[0.90] - 0.90),
        enclosed_probability_99_error=abs(enclosed[0.99] - 0.99),
        frequency_radius_invariant_error=abs(invariant - invariant_target),
        energy_mu_norm_relation_error=abs(energy_relation - 1.0 / 3.0),
    )


def _scaling_exponent(first: float, second: float, norm_ratio: float) -> float:
    return math.log(second / first) / math.log(norm_ratio)


def run_observable_study(
    couplings: Sequence[float] = (1.0, 2.0, 4.0),
    norms: Sequence[float] = (0.5, 1.0, 2.0),
) -> dict[str, Any]:
    ledgers = [
        numerical_ledger(SolitonParameters(coupling=coupling, norm=norm))
        for coupling in couplings
        for norm in norms
    ]

    exponents: dict[str, list[float]] = {
        "eta": [],
        "phase_frequency": [],
        "absolute_energy": [],
        "rms_radius": [],
    }
    for coupling in couplings:
        low = SolitonParameters(coupling=coupling, norm=norms[0])
        high = SolitonParameters(coupling=coupling, norm=norms[-1])
        norm_ratio = high.norm / low.norm
        exponents["eta"].append(
            _scaling_exponent(low.eta, high.eta, norm_ratio)
        )
        exponents["phase_frequency"].append(
            _scaling_exponent(
                low.phase_frequency,
                high.phase_frequency,
                norm_ratio,
            )
        )
        exponents["absolute_energy"].append(
            _scaling_exponent(abs(low.energy), abs(high.energy), norm_ratio)
        )
        exponents["rms_radius"].append(
            _scaling_exponent(low.rms_radius, high.rms_radius, norm_ratio)
        )

    exponent_targets = {
        "eta": 1.0,
        "phase_frequency": 2.0,
        "absolute_energy": 3.0,
        "rms_radius": -1.0,
    }
    acceptance = {
        "norm_quadrature": max(item.norm_relative_error for item in ledgers)
        <= 1.0e-10,
        "energy_quadrature": max(item.energy_relative_error for item in ledgers)
        <= 1.0e-10,
        "radius_quadrature": max(item.radius_relative_error for item in ledgers)
        <= 1.0e-10,
        "stationary_residual": max(
            item.stationary_residual_relative_l2 for item in ledgers
        )
        <= 1.0e-12,
        "enclosed_probability": max(
            max(
                item.enclosed_probability_90_error,
                item.enclosed_probability_99_error,
            )
            for item in ledgers
        )
        <= 2.0e-3,
        "frequency_radius_invariant": max(
            item.frequency_radius_invariant_error for item in ledgers
        )
        <= 1.0e-12,
        "energy_mu_norm_relation": max(
            item.energy_mu_norm_relation_error for item in ledgers
        )
        <= 1.0e-12,
        "scaling_exponents": max(
            abs(value - exponent_targets[name])
            for name, values in exponents.items()
            for value in values
        )
        <= 1.0e-12,
    }

    return {
        "schema": "openwave.m9.soliton-observable-ledger.v2",
        "model": "M9-CAT-EPT",
        "equation": "i psi_t = -1/2 psi_xx - g |psi|^2 psi",
        "family": {
            "eta": "g N / 2",
            "profile": "eta/sqrt(g) sech(eta x)",
            "mu": "-eta^2/2",
            "phase_frequency": "eta^2/2",
            "energy": "-eta^3/(3g) = -g^2 N^3/24",
            "rms_radius": "pi/(2 sqrt(3) eta)",
            "density_fwhm": "2 acosh(sqrt(2))/eta",
            "enclosed_probability": "tanh(eta R)",
        },
        "quadrature": {
            "scaled_half_width": 16.0,
            "points": 8193,
        },
        "cases": [asdict(ledger) for ledger in ledgers],
        "scaling_exponents": exponents,
        "scaling_targets": exponent_targets,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "clock_bridge": {
            "dimensionless_identity": "Omega R_rms^2 = pi^2/24",
            "optional_physical_identifications": [
                "Omega_phys = omega_C = m c^2 / hbar",
                "Omega_phys = omega_Z = 2 m c^2 / hbar",
            ],
            "status": "conditional_unit_map_only",
        },
        "classification": {
            "establishes": [
                "the exact dimensionless scaling family",
                "quadrature agreement for nine frozen cases",
                "linked radius-energy-frequency identities",
            ],
            "does_not_establish": [
                "a physical mass, length, or time calibration",
                "an electron identity",
                "independent predictions of radius, energy, and frequency",
                "unique CAT/EPT selection of the focusing cubic term",
            ],
        },
    }
