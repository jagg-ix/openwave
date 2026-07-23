"""M9.6 executable capability audit for the current complex-scalar carrier.

The audit distinguishes global U(1) norm, local gauge charge, phase current,
intrinsic spin, and topological sectors. It also records a staged replacement
carrier that preserves the density consumed by the entropic-clock interface.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import cmath
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class CarrierCapability:
    name: str
    present: bool
    evidence: str
    limitation: str


@dataclass(frozen=True)
class ReplacementRoute:
    carrier: str
    supplies: tuple[str, ...]
    preserves: tuple[str, ...]
    still_requires: tuple[str, ...]


def global_phase_transform(state: ComplexArray, angle: float) -> ComplexArray:
    return np.asarray(state * np.exp(1j * angle), dtype=np.complex128)


def local_phase_transform(
    x: RealArray, state: ComplexArray, wave_number: float
) -> ComplexArray:
    if x.shape != state.shape:
        raise ValueError("x and state must have the same shape")
    return np.asarray(state * np.exp(1j * wave_number * x), dtype=np.complex128)


def conjugate_state(state: ComplexArray) -> ComplexArray:
    return np.asarray(np.conj(state), dtype=np.complex128)


def contraction_state(state: ComplexArray, parameter: float) -> ComplexArray:
    """Continuous amplitude path from the zero vacuum to the supplied state."""
    if not 0.0 <= parameter <= 1.0:
        raise ValueError("parameter must lie in [0, 1]")
    return np.asarray(parameter * state, dtype=np.complex128)


def scalar_rotation_factor(angle: float) -> complex:
    _ = angle
    return 1.0 + 0.0j


def spinor_rotation_factor(angle: float) -> complex:
    return cmath.exp(-0.5j * angle)


def discrete_norm(state: ComplexArray, dx: float) -> float:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    return float(dx * np.sum(np.abs(state) ** 2))


def spectral_derivative(state: ComplexArray, dx: float) -> ComplexArray:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(state.size, d=dx)
    return np.asarray(
        np.fft.ifft(1j * wave_numbers * np.fft.fft(state)),
        dtype=np.complex128,
    )


def probability_current(state: ComplexArray, dx: float) -> RealArray:
    derivative = spectral_derivative(state, dx)
    return np.asarray(np.imag(np.conj(state) * derivative), dtype=np.float64)


def scalar_energy(state: ComplexArray, dx: float, coupling: float = -2.0) -> float:
    derivative = spectral_derivative(state, dx)
    density = 0.5 * np.abs(derivative) ** 2
    density += 0.5 * coupling * np.abs(state) ** 4
    return float(dx * np.sum(density))


def spinor_density_embedding(state: ComplexArray) -> NDArray[np.complex128]:
    """Embed ``psi`` as ``(psi, 0)`` so Psi-dagger Psi equals |psi|^2."""
    zeros = np.zeros_like(state)
    return np.stack((state, zeros), axis=-1)


def spinor_density(spinor: NDArray[np.complex128]) -> RealArray:
    if spinor.ndim != 2 or spinor.shape[1] != 2:
        raise ValueError("spinor must have shape (n, 2)")
    return np.asarray(np.sum(np.abs(spinor) ** 2, axis=1), dtype=np.float64)


def _sample_state() -> tuple[RealArray, ComplexArray, float]:
    points = 2048
    half_width = 20.0
    dx = 2.0 * half_width / points
    x = -half_width + dx * np.arange(points, dtype=np.float64)
    base = 1.0 / (math.sqrt(2.0) * np.cosh(x))
    state = np.asarray(base * np.exp(0.7j * x), dtype=np.complex128)
    return x, state, dx


def audit_scalar_carrier() -> dict[str, Any]:
    x, state, dx = _sample_state()
    global_phase = global_phase_transform(state, 0.73)
    local_phase = local_phase_transform(x, state, 1.25)
    conjugate = conjugate_state(state)

    norm = discrete_norm(state, dx)
    energy = scalar_energy(state, dx)
    current = probability_current(state, dx)
    conjugate_current = probability_current(conjugate, dx)

    contraction_parameters = np.linspace(0.0, 1.0, 11)
    contraction = [
        {
            "parameter": float(parameter),
            "norm": discrete_norm(contraction_state(state, float(parameter)), dx),
            "energy": scalar_energy(contraction_state(state, float(parameter)), dx),
            "distance_from_vacuum": math.sqrt(
                discrete_norm(contraction_state(state, float(parameter)), dx)
            ),
        }
        for parameter in contraction_parameters
    ]

    capabilities = [
        CarrierCapability(
            "global_u1_phase_symmetry",
            True,
            "constant phase preserves density, norm, current, and scalar energy",
            "the conserved number has no electric unit or gauge field",
        ),
        CarrierCapability(
            "local_u1_gauge_symmetry",
            False,
            "position-dependent phase changes ordinary-gradient energy",
            "covariant derivative and gauge potential are absent",
        ),
        CarrierCapability(
            "electric_charge_derivation",
            False,
            "no Gauss-law flux, Maxwell source, charge unit, or opposite-charge label",
            "conjugation reverses phase current but not an electric charge sector",
        ),
        CarrierCapability(
            "intrinsic_spin_half_representation",
            False,
            "scalar intrinsic rotations return +1 at 2pi",
            "a spinor double-cover representation is absent",
        ),
        CarrierCapability(
            "topological_charge_certificate",
            False,
            "the localized profile contracts continuously to the zero vacuum",
            "a different target manifold and boundary class could alter this result",
        ),
    ]

    replacement_routes = [
        ReplacementRoute(
            "locally gauge-coupled complex scalar",
            ("local U(1) covariance", "gauge current", "charged spin-0 matter"),
            ("density |psi|^2", "normalized-density entropic clock"),
            ("gauge dynamics", "charge-unit calibration", "spin-1/2 mechanism"),
        ),
        ReplacementRoute(
            "Dirac or Weyl spinor with local U(1)",
            ("spin-1/2 double cover", "fermionic current", "gauge charge carrier"),
            ("density Psi-dagger Psi", "normalized-density entropic clock"),
            ("localized solution", "statistics layer", "CAT/EPT action coupling"),
        ),
        ReplacementRoute(
            "multi-component topological order parameter",
            ("possible winding", "defect sectors", "internal geometry"),
            ("positive density functional", "coarse-graining interface"),
            ("target manifold", "boundary class", "physical invariant mapping"),
        ),
    ]

    spinor = spinor_density_embedding(state)
    two_pi = 2.0 * math.pi
    four_pi = 4.0 * math.pi
    checks = {
        "global_phase_norm": abs(discrete_norm(global_phase, dx) - norm),
        "global_phase_energy": abs(scalar_energy(global_phase, dx) - energy),
        "conjugation_norm": abs(discrete_norm(conjugate, dx) - norm),
        "conjugation_energy": abs(scalar_energy(conjugate, dx) - energy),
        "conjugation_current_reversal": float(
            np.max(np.abs(conjugate_current + current))
        ),
        "local_phase_energy_change": abs(scalar_energy(local_phase, dx) - energy),
        "contraction_zero_norm": contraction[0]["norm"],
        "contraction_endpoint_distance": abs(
            contraction[-1]["distance_from_vacuum"] - math.sqrt(norm)
        ),
        "scalar_2pi_distance_from_plus_one": abs(
            scalar_rotation_factor(two_pi) - 1.0
        ),
        "spinor_2pi_distance_from_minus_one": abs(
            spinor_rotation_factor(two_pi) + 1.0
        ),
        "spinor_4pi_distance_from_plus_one": abs(
            spinor_rotation_factor(four_pi) - 1.0
        ),
        "spinor_density_embedding": float(
            np.max(np.abs(spinor_density(spinor) - np.abs(state) ** 2))
        ),
    }

    acceptance = {
        "global_phase_invariance": max(
            checks["global_phase_norm"], checks["global_phase_energy"]
        )
        <= 1.0e-12,
        "conjugation_invariance_and_current_reversal": max(
            checks["conjugation_norm"],
            checks["conjugation_energy"],
            checks["conjugation_current_reversal"],
        )
        <= 1.0e-12,
        "local_gauge_gap_detected": checks["local_phase_energy_change"] >= 1.0e-3,
        "continuous_vacuum_contraction": (
            checks["contraction_zero_norm"] <= 1.0e-15
            and checks["contraction_endpoint_distance"] <= 1.0e-12
            and all(
                left["norm"] <= right["norm"] + 1.0e-15
                for left, right in zip(contraction[:-1], contraction[1:], strict=True)
            )
        ),
        "scalar_spin_zero": checks["scalar_2pi_distance_from_plus_one"] <= 1.0e-15,
        "spinor_reference_double_cover": max(
            checks["spinor_2pi_distance_from_minus_one"],
            checks["spinor_4pi_distance_from_plus_one"],
        )
        <= 1.0e-15,
        "replacement_preserves_density_interface": (
            checks["spinor_density_embedding"] <= 1.0e-15
        ),
        "electric_charge_not_overclaimed": not capabilities[2].present,
        "topological_charge_not_overclaimed": not capabilities[4].present,
    }

    return {
        "schema": "openwave.m9.scalar-carrier-audit.v2",
        "model": "M9-CAT-EPT",
        "carrier": "single complex scalar field in 1+1 dimensions",
        "capabilities": [asdict(item) for item in capabilities],
        "checks": checks,
        "contraction_path": contraction,
        "representation_checks": {
            "scalar_2pi": [1.0, 0.0],
            "scalar_4pi": [1.0, 0.0],
            "spinor_reference_2pi": [
                spinor_rotation_factor(two_pi).real,
                spinor_rotation_factor(two_pi).imag,
            ],
            "spinor_reference_4pi": [
                spinor_rotation_factor(four_pi).real,
                spinor_rotation_factor(four_pi).imag,
            ],
        },
        "replacement_routes": [asdict(route) for route in replacement_routes],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "positive_result": "global U(1) norm symmetry is present",
            "negative_results": [
                "conjugation is not an opposite electric-charge sector",
                "electric charge is not derived",
                "spin-1/2 is not represented",
                "the current profile has no protected topological sector",
            ],
            "scope": "current-carrier audit, not a theorem about every scalar extension",
        },
    }
