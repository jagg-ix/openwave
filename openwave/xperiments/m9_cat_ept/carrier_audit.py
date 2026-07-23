"""M9.6 capability audit for the current complex-scalar carrier.

The audit separates four notions that are often conflated:

- global U(1) phase symmetry and its conserved norm;
- local U(1) gauge symmetry and electric charge;
- intrinsic rotation representation and spin;
- model-specific topological charge.

The current 1+1D complex scalar has the first item only. A conserved global norm
is not automatically electric charge, and the trivial scalar representation
cannot realize the 2pi sign change of spin-1/2.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import cmath
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

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
    still_requires: tuple[str, ...]


def global_phase_transform(state: ComplexArray, angle: float) -> ComplexArray:
    """Apply the current carrier's global U(1) action."""
    return np.asarray(state * np.exp(1j * angle), dtype=np.complex128)


def local_phase_transform(
    x: NDArray[np.float64], state: ComplexArray, wave_number: float
) -> ComplexArray:
    """Apply a position-dependent phase without introducing a gauge field."""
    if x.shape != state.shape:
        raise ValueError("x and state must have the same shape")
    return np.asarray(state * np.exp(1j * wave_number * x), dtype=np.complex128)


def scalar_rotation_factor(angle: float) -> complex:
    """Return the intrinsic rotation factor of a spin-0 scalar."""
    _ = angle
    return 1.0 + 0.0j


def spinor_rotation_factor(angle: float) -> complex:
    """Reference spin-1/2 factor used only to expose the missing structure."""
    return cmath.exp(-0.5j * angle)


def discrete_norm(state: ComplexArray, dx: float) -> float:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    return float(dx * np.sum(np.abs(state) ** 2))


def spectral_kinetic_energy(state: ComplexArray, dx: float) -> float:
    """Return integral |d_x psi|^2/2 on a periodic grid."""
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(state.size, d=dx)
    derivative = np.fft.ifft(1j * wave_numbers * np.fft.fft(state))
    return float(0.5 * dx * np.sum(np.abs(derivative) ** 2))


def audit_scalar_carrier() -> dict[str, Any]:
    """Return the frozen M9.6 capability and replacement-carrier ledger."""
    capabilities = [
        CarrierCapability(
            name="global_u1_phase_symmetry",
            present=True,
            evidence="psi -> exp(i alpha) psi leaves |psi|^2 and the scalar norm unchanged",
            limitation="the associated conserved number has no electric unit or gauge field",
        ),
        CarrierCapability(
            name="local_u1_gauge_symmetry",
            present=False,
            evidence="a position-dependent phase changes the ordinary-gradient kinetic energy",
            limitation="a covariant derivative and dynamical gauge potential are absent",
        ),
        CarrierCapability(
            name="electric_charge_derivation",
            present=False,
            evidence="no Maxwell source equation or charge normalization is implemented",
            limitation="global norm may be identified with particle number, not automatically electric charge",
        ),
        CarrierCapability(
            name="intrinsic_spin_half_representation",
            present=False,
            evidence="the scalar rotation factor is 1 at every angle, including 2pi",
            limitation="the carrier has the trivial spin-0 representation rather than a spinor double cover",
        ),
        CarrierCapability(
            name="topological_charge_certificate",
            present=False,
            evidence="the current sech profile has no declared target-space winding or boundary class",
            limitation="a different multi-component target and explicit boundary conditions could change this",
        ),
    ]

    replacement_routes = [
        ReplacementRoute(
            carrier="locally gauge-coupled complex scalar",
            supplies=("local U(1) covariance", "gauge current", "spin-0 charged matter"),
            still_requires=(
                "Maxwell or other gauge dynamics",
                "electric-unit calibration",
                "a separate mechanism for spin-1/2",
            ),
        ),
        ReplacementRoute(
            carrier="Dirac or Weyl spinor with local U(1)",
            supplies=("spin-1/2 double cover", "fermionic current", "gauge charge carrier"),
            still_requires=(
                "a localized nonlinear solution",
                "statistics/quantization layer",
                "coupling to the CAT/EPT clock and imaginary action",
            ),
        ),
        ReplacementRoute(
            carrier="multi-component topological order parameter",
            supplies=("possible integer winding", "defect sectors", "nontrivial internal geometry"),
            still_requires=(
                "explicit target manifold",
                "boundary conditions",
                "proof that the invariant matches electric charge or spin",
            ),
        ),
    ]

    two_pi = 2.0 * math.pi
    four_pi = 4.0 * math.pi
    representation_checks = {
        "scalar_2pi": [
            scalar_rotation_factor(two_pi).real,
            scalar_rotation_factor(two_pi).imag,
        ],
        "scalar_4pi": [
            scalar_rotation_factor(four_pi).real,
            scalar_rotation_factor(four_pi).imag,
        ],
        "spinor_reference_2pi": [
            spinor_rotation_factor(two_pi).real,
            spinor_rotation_factor(two_pi).imag,
        ],
        "spinor_reference_4pi": [
            spinor_rotation_factor(four_pi).real,
            spinor_rotation_factor(four_pi).imag,
        ],
    }

    acceptance = {
        "global_u1_recorded_without_electric_overclaim": (
            capabilities[0].present and not capabilities[2].present
        ),
        "local_gauge_gap_explicit": not capabilities[1].present,
        "spin_half_gap_explicit": not capabilities[3].present,
        "topology_gap_explicit": not capabilities[4].present,
        "scalar_representation_is_trivial": (
            abs(scalar_rotation_factor(two_pi) - 1.0) <= 1.0e-15
        ),
        "spinor_reference_exhibits_double_cover": (
            abs(spinor_rotation_factor(two_pi) + 1.0) <= 1.0e-15
            and abs(spinor_rotation_factor(four_pi) - 1.0) <= 1.0e-15
        ),
        "replacement_routes_named": len(replacement_routes) == 3,
    }

    return {
        "schema": "openwave.m9.scalar-carrier-audit.v1",
        "model": "M9-CAT-EPT",
        "carrier": "single complex scalar field in 1+1 dimensions",
        "capabilities": [asdict(capability) for capability in capabilities],
        "representation_checks": representation_checks,
        "replacement_routes": [asdict(route) for route in replacement_routes],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "positive_result": "global U(1) norm symmetry is present",
            "negative_results": [
                "electric charge is not derived",
                "spin-1/2 is not represented",
                "no topological charge certificate is implemented",
            ],
            "scope": "carrier capability audit, not a theorem that all scalar extensions are impossible",
        },
    }
