"""Executable no-go checks for the current M9 scalar carrier.

The accepted M9.4 state is a one-component nonrelativistic complex scalar field.
This module records what that carrier can express and what it cannot express
without additional structure. The conclusions apply to the present M9 NLS
carrier, not to every possible scalar quantum field theory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class CarrierCapabilities:
    """Machine-readable capability summary for a candidate field carrier."""

    name: str
    complex_components: int
    local_u1_connection: bool
    gauss_law_flux: bool
    opposite_charge_sector: bool
    spin_representation: str
    two_pi_character_real: float
    intrinsic_spin_half: bool
    target_contains_zero_and_is_contractible: bool
    cat_ept_positive_density: bool


CURRENT_SCALAR = CarrierCapabilities(
    name="one-component nonrelativistic complex scalar NLS",
    complex_components=1,
    local_u1_connection=False,
    gauss_law_flux=False,
    opposite_charge_sector=False,
    spin_representation="trivial scalar representation",
    two_pi_character_real=1.0,
    intrinsic_spin_half=False,
    target_contains_zero_and_is_contractible=True,
    cat_ept_positive_density=True,
)

DIRAC_U1_TARGET = CarrierCapabilities(
    name="four-component Dirac spinor with local U(1) connection",
    complex_components=4,
    local_u1_connection=True,
    gauss_law_flux=True,
    opposite_charge_sector=True,
    spin_representation="Spin(1,3) Dirac representation",
    two_pi_character_real=-1.0,
    intrinsic_spin_half=True,
    target_contains_zero_and_is_contractible=True,
    cat_ept_positive_density=True,
)


def scalar_density(state: ComplexArray) -> RealArray:
    return np.asarray(np.abs(state) ** 2, dtype=np.float64)


def scalar_norm(state: ComplexArray, dx: float) -> float:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    return float(dx * np.sum(scalar_density(state)))


def global_phase_transform(state: ComplexArray, angle: float) -> ComplexArray:
    return np.asarray(state * np.exp(1j * angle), dtype=np.complex128)


def scalar_contraction(state: ComplexArray, homotopy_parameter: float) -> ComplexArray:
    """Witness contraction of the scalar configuration to the zero vacuum."""
    if not 0.0 <= homotopy_parameter <= 1.0:
        raise ValueError("homotopy_parameter must lie in [0, 1]")
    return np.asarray((1.0 - homotopy_parameter) * state, dtype=np.complex128)


def centered_current(state: ComplexArray, dx: float) -> RealArray:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    derivative = (np.roll(state, -1) - np.roll(state, 1)) / (2.0 * dx)
    return np.asarray(np.imag(np.conj(state) * derivative), dtype=np.float64)


def scalar_energy(state: ComplexArray, dx: float, coupling: float = 2.0) -> float:
    """Return the focusing-NLS energy used by the accepted M9.4 candidate."""
    if coupling <= 0.0:
        raise ValueError("coupling must be positive")
    derivative = (np.roll(state, -1) - np.roll(state, 1)) / (2.0 * dx)
    kinetic = 0.5 * dx * float(np.sum(np.abs(derivative) ** 2))
    interaction = -0.5 * coupling * dx * float(np.sum(np.abs(state) ** 4))
    return kinetic + interaction


def scalar_rotation_character(angle: float) -> complex:
    """Intrinsic scalar representation: every spatial rotation acts by +1."""
    del angle
    return 1.0 + 0.0j


def spin_half_rotation_character(angle: float) -> complex:
    """Reference spin-1/2 character for a rotation about one fixed axis."""
    return complex(np.exp(-0.5j * angle))


def replacement_carrier_contract() -> dict[str, Any]:
    """Requirements for extending M9 from a neutral scalar to charged spin-1/2 matter."""
    return {
        "schema": "openwave.m9.replacement-carrier-contract.v1",
        "current_carrier": asdict(CURRENT_SCALAR),
        "target_carrier": asdict(DIRAC_U1_TARGET),
        "requirements": {
            "signed_electric_charge": [
                "local U(1) connection A_mu",
                "covariant derivative D_mu = partial_mu - i q A_mu",
                "Gauss-law flux observable tied to the source current",
                "opposite-charge or antiparticle sector",
            ],
            "intrinsic_spin_half": [
                "nontrivial Spin(1,3) or Spin(3) representation",
                "at least two complex spinor components",
                "2pi action = -identity and 4pi action = +identity",
                "spin current distinct from orbital angular momentum",
            ],
            "three_dimensional_localization": [
                "declared 3D energy functional",
                "Derrick or virial balance",
                "grid, window, perturbation and radiation ledgers",
            ],
            "cat_ept_compatibility": [
                "positive density psi-dagger psi",
                "complex phase/action carrier",
                "conserved or explicitly sourced current",
                "fixed field-to-probability map for the entropic clock",
            ],
        },
        "staged_path": [
            {
                "stage": "M9.6A",
                "carrier": "Pauli spinor plus local U(1)",
                "settles": "nonrelativistic spin and gauge coupling",
                "does_not_settle": "relativistic antiparticles or Dirac branch structure",
            },
            {
                "stage": "M9.6B",
                "carrier": "Dirac spinor plus local U(1)",
                "settles": "spinorial 2pi sign and opposite-charge relativistic sectors",
                "does_not_settle": "3D nonlinear localization",
            },
            {
                "stage": "M9.6C",
                "carrier": "localized Dirac-gauge nonlinear model",
                "settles": "candidate charged spin-1/2 particle only after numerical gates",
                "does_not_settle": "Standard Model identity without calibration and observables",
            },
        ],
    }


def run_scalar_carrier_audit(
    *,
    half_width: float = 16.0,
    points: int = 4096,
    wave_number: float = 0.7,
) -> dict[str, Any]:
    """Run deterministic invariance and representation checks for M9.6."""
    if half_width <= 0.0:
        raise ValueError("half_width must be positive")
    if points < 64:
        raise ValueError("points must be at least 64")
    dx = 2.0 * half_width / points
    x = -half_width + dx * np.arange(points, dtype=np.float64)
    envelope = 1.0 / (math.sqrt(2.0) * np.cosh(x))
    state = np.asarray(envelope * np.exp(1j * wave_number * x), dtype=np.complex128)
    phase_state = global_phase_transform(state, 1.234)
    conjugate_state = np.conj(state)

    density = scalar_density(state)
    norm = scalar_norm(state, dx)
    energy = scalar_energy(state, dx)
    current = centered_current(state, dx)
    conjugate_current = centered_current(conjugate_state, dx)

    phase_density_error = float(np.max(np.abs(scalar_density(phase_state) - density)))
    phase_norm_error = abs(scalar_norm(phase_state, dx) - norm)
    phase_energy_error = abs(scalar_energy(phase_state, dx) - energy)
    conjugate_density_error = float(np.max(np.abs(scalar_density(conjugate_state) - density)))
    conjugate_norm_error = abs(scalar_norm(conjugate_state, dx) - norm)
    conjugate_energy_error = abs(scalar_energy(conjugate_state, dx) - energy)
    current_reversal_error = float(np.max(np.abs(conjugate_current + current)))

    contraction_start_error = float(np.max(np.abs(scalar_contraction(state, 0.0) - state)))
    contraction_end_norm = scalar_norm(scalar_contraction(state, 1.0), dx)
    contraction_mid_norm_ratio = scalar_norm(scalar_contraction(state, 0.5), dx) / norm

    scalar_two_pi = scalar_rotation_character(2.0 * math.pi)
    scalar_four_pi = scalar_rotation_character(4.0 * math.pi)
    spinor_two_pi = spin_half_rotation_character(2.0 * math.pi)
    spinor_four_pi = spin_half_rotation_character(4.0 * math.pi)

    checks = {
        "global_phase_density_invariant": phase_density_error <= 1.0e-15,
        "global_phase_norm_invariant": phase_norm_error <= 1.0e-14,
        "global_phase_energy_invariant": phase_energy_error <= 1.0e-13,
        "conjugation_density_invariant": conjugate_density_error <= 1.0e-15,
        "conjugation_norm_invariant": conjugate_norm_error <= 1.0e-14,
        "conjugation_energy_invariant": conjugate_energy_error <= 1.0e-13,
        "conjugation_reverses_current": current_reversal_error <= 1.0e-14,
        "scalar_configuration_contracts_to_zero": (
            contraction_start_error <= 1.0e-15 and contraction_end_norm <= 1.0e-30
        ),
        "contraction_norm_scales_quadratically": abs(contraction_mid_norm_ratio - 0.25)
        <= 1.0e-14,
        "scalar_two_pi_returns_identity": abs(scalar_two_pi - 1.0) <= 1.0e-15,
        "spinor_reference_two_pi_changes_sign": abs(spinor_two_pi + 1.0) <= 1.0e-15,
        "spinor_reference_four_pi_returns_identity": abs(spinor_four_pi - 1.0)
        <= 1.0e-15,
        "current_carrier_lacks_signed_gauss_charge": (
            not CURRENT_SCALAR.local_u1_connection
            and not CURRENT_SCALAR.gauss_law_flux
            and not CURRENT_SCALAR.opposite_charge_sector
        ),
        "current_carrier_lacks_intrinsic_spin_half": (
            CURRENT_SCALAR.two_pi_character_real == 1.0
            and not CURRENT_SCALAR.intrinsic_spin_half
        ),
        "replacement_target_meets_charge_spin_requirements": (
            DIRAC_U1_TARGET.local_u1_connection
            and DIRAC_U1_TARGET.gauss_law_flux
            and DIRAC_U1_TARGET.opposite_charge_sector
            and DIRAC_U1_TARGET.intrinsic_spin_half
            and DIRAC_U1_TARGET.two_pi_character_real == -1.0
        ),
    }

    return {
        "schema": "openwave.m9.scalar-carrier-audit.v1",
        "model": "M9-CAT-EPT",
        "carrier": asdict(CURRENT_SCALAR),
        "sample": {
            "half_width": half_width,
            "points": points,
            "wave_number": wave_number,
            "norm": norm,
            "energy": energy,
        },
        "invariance_errors": {
            "phase_density": phase_density_error,
            "phase_norm": phase_norm_error,
            "phase_energy": phase_energy_error,
            "conjugate_density": conjugate_density_error,
            "conjugate_norm": conjugate_norm_error,
            "conjugate_energy": conjugate_energy_error,
            "current_reversal": current_reversal_error,
        },
        "contraction_witness": {
            "start_error": contraction_start_error,
            "end_norm": contraction_end_norm,
            "mid_norm_ratio": contraction_mid_norm_ratio,
        },
        "rotation_characters": {
            "scalar_2pi": [scalar_two_pi.real, scalar_two_pi.imag],
            "scalar_4pi": [scalar_four_pi.real, scalar_four_pi.imag],
            "spinor_reference_2pi": [spinor_two_pi.real, spinor_two_pi.imag],
            "spinor_reference_4pi": [spinor_four_pi.real, spinor_four_pi.imag],
        },
        "checks": checks,
        "passed": all(checks.values()),
        "replacement_contract": replacement_carrier_contract(),
        "conclusions": {
            "norm_is_not_signed_electric_charge": (
                "The scalar norm is nonnegative and unchanged by conjugation; no Gauss flux or "
                "opposite-charge sector is present."
            ),
            "scalar_has_no_intrinsic_spin_half": (
                "The intrinsic scalar rotation character is +1 at 2pi. Orbital angular "
                "momentum in a future higher-dimensional scalar field would not change this."
            ),
            "localized_profile_has_no_protected_winding": (
                "Because the carrier includes the zero vacuum, H_s=(1-s)psi contracts the "
                "localized profile continuously to zero."
            ),
        },
        "scope": {
            "applies_to": "the current one-component nonrelativistic M9 NLS carrier",
            "does_not_claim": [
                "that every complex scalar field theory lacks a signed Noether charge",
                "that scalar fields cannot carry orbital angular momentum",
                "that the proposed Dirac-U(1) carrier automatically localizes",
                "that a replacement carrier is already implemented",
            ],
        },
    }
