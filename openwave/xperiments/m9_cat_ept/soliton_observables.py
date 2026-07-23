"""M9.5 exact observable ledger for the selected 1D bright-soliton family.

For ``i psi_t = -psi_xx/2 - g |psi|^2 psi`` with ``g,N > 0``:

``eta = gN/2``, ``phi = eta/sqrt(g) sech(eta x)``, and
``psi = phi exp(i eta^2 t/2)``. The resulting radius, energy, and frequency
are correlated identities of this dimensionless model, not independent physical
predictions.
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
        parameters.amplitude * sech(parameters.eta * x), dtype=np.complex128
    )


def state(x: RealArray, time: float, parameters: SolitonParameters) -> ComplexArray:
    return np.asarray(
        profile(x, parameters) * np.exp(1j * parameters.phase_frequency * time),
        dtype=np.complex128,
    )


def first_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    z = parameters.eta * x
    return np.asarray(
        -parameters.amplitude * parameters.eta * sech(z) * np.tanh(z),
        dtype=np.float64,
    )


def second_derivative(x: RealArray, parameters: SolitonParameters) -> RealArray:
    z = parameters.eta * x
    base = sech(z)
    return np.asarray(
        parameters.amplitude * parameters.eta**2 * base * (1.0 - 2.0 * base**2),
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

    limit = scaled_half_width / parameters.eta
    x = np.linspace(-limit, limit, points, dtype=np.float64)
    phi = np.real(profile(x, parameters))
    derivative = first_derivative(x, parameters)
    density = phi**2
    norm = float(np.trapezoid(density, x))
    energy = float(
        np.trapezoid(
            0.5 * derivative**2 - 0.5 * parameters.coupling * phi**4, x
        )
    )
    radius = math.sqrt(float(np.trapezoid(x**2 * density, x) / norm))
    residual = stationary_residual(x, parameters)
    residual_l2 = math.sqrt(float(np.trapezoid(residual**2, x)))
    residual_scale = abs(parameters.chemical_potential) * math.sqrt(parameters.norm)

    enclosed: dict[float, float] = {}
    for probability in (0.90, 0.99):
        mask = np.abs(x) <= parameters.radius_for_probability(probability)
        enclosed[probability] = float(np.trapezoid(density[mask], x[mask]) / norm)

    invariant = parameters.phase_frequency * parameters.rms_radius**2
    energy_relation = parameters.energy / (
        parameters.chemical_potential * parameters.norm
    )
    return NumericalLedger(
        coupling=parameters.coupling,
        requested_norm=parameters.norm,
        eta=parameters.eta,
        amplitude=parameters.amplitude,
        numerical_norm=norm,
        numerical_energy=energy,
        numerical_rms_radius=radius,
        stationary_residual_relative_l2=residual_l2 / residual_scale,
        enclosed_probability_90=enclosed[0.90],
        enclosed_probability_99=enclosed[0.99],
        analytic_energy=parameters.energy,
        analytic_rms_radius=parameters.rms_radius,
        phase_frequency=parameters.phase_frequency,
        chemical_potential=parameters.chemical_potential,
        norm_relative_error=_relative_error(norm, parameters.norm),
        energy_relative_error=_relative_error(energy, parameters.energy),
        radius_relative_error=_relative_error(radius, parameters.rms_radius),
        enclosed_probability_90_error=abs(enclosed[0.90] - 0.90),
        enclosed_probability_99_error=abs(enclosed[0.99] - 0.99),
        frequency_radius_invariant_error=abs(invariant - math.pi**2 / 24.0),
        energy_mu_norm_relation_error=abs(energy_relation - 1.0 / 3.0),
    )


def _exponent(first: float, second: float, ratio: float) -> float:
    return math.log(second / first) / math.log(ratio)


def run_observable_study(
    couplings: Sequence[float] = (1.0, 2.0, 4.0),
    norms: Sequence[float] = (0.5, 1.0, 2.0),
) -> dict[str, Any]:
    ledgers = [
        numerical_ledger(SolitonParameters(coupling=g, norm=norm))
        for g in couplings
        for norm in norms
    ]
    exponents = {name: [] for name in (
        "eta", "phase_frequency", "absolute_energy", "rms_radius"
    )}
    for g in couplings:
        low = SolitonParameters(g, norms[0])
        high = SolitonParameters(g, norms[-1])
        ratio = high.norm / low.norm
        exponents["eta"].append(_exponent(low.eta, high.eta, ratio))
        exponents["phase_frequency"].append(
            _exponent(low.phase_frequency, high.phase_frequency, ratio)
        )
        exponents["absolute_energy"].append(
            _exponent(abs(low.energy), abs(high.energy), ratio)
        )
        exponents["rms_radius"].append(
            _exponent(low.rms_radius, high.rms_radius, ratio)
        )
    targets = {
        "eta": 1.0,
        "phase_frequency": 2.0,
        "absolute_energy": 3.0,
        "rms_radius": -1.0,
    }
    acceptance = {
        "norm_quadrature": max(x.norm_relative_error for x in ledgers) <= 1e-10,
        "energy_quadrature": max(x.energy_relative_error for x in ledgers) <= 1e-10,
        "radius_quadrature": max(x.radius_relative_error for x in ledgers) <= 1e-10,
        "stationary_residual": max(
            x.stationary_residual_relative_l2 for x in ledgers
        ) <= 1e-12,
        "enclosed_probability": max(
            max(x.enclosed_probability_90_error, x.enclosed_probability_99_error)
            for x in ledgers
        ) <= 2e-3,
        "frequency_radius_invariant": max(
            x.frequency_radius_invariant_error for x in ledgers
        ) <= 1e-12,
        "energy_mu_norm_relation": max(
            x.energy_mu_norm_relation_error for x in ledgers
        ) <= 1e-12,
        "scaling_exponents": max(
            abs(value - targets[name])
            for name, values in exponents.items()
            for value in values
        ) <= 1e-12,
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
        "quadrature": {"scaled_half_width": 16.0, "points": 8193},
        "cases": [asdict(item) for item in ledgers],
        "scaling_exponents": exponents,
        "scaling_targets": targets,
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
