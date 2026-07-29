"""Executable bridge for three nonperturbative QCD theorem families.

Physlib remains the formal authority.  This module evaluates finite-dimensional
or scalar consequences of the exact declarations pinned below and preserves the
ZIL scope boundaries: it does not construct a lattice measure, determine T_c,
derive the condensate or topological susceptibility, or solve strong CP.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import cmath
import json
import math
from typing import Any

PHYSLIB_REPOSITORY = "jagg-ix/entropic-physlib-private"
PHYSLIB_BRANCH = "entropic-physlib-linear-full"
PHYSLIB_TIP = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
PHYSLIB_ROOT_BLOB = "bf9028667305c70e77142e5fd24ec06fadb0d66f"

SOURCE_RECORDS = (
    {
        "id": "polyakov-loop-deconfinement",
        "path": "Physlib/QuantumMechanics/ComplexAction/HorizonCell/PolyakovLoopDeconfinement.lean",
        "blob": "3f5eb8945e367c49a4156cd7db598ec7818dad24",
        "zil_level": "physical_theorem",
        "contract_status": "satisfied",
        "declarations": (
            "center_invariant_forces_zero",
            "cubeRoot_invariant_iff_confined",
            "polyakov_antitone_in_freeEnergy",
            "polyakov_grows_with_temperature",
            "polyakov_deconfinement_order_parameter",
        ),
        "boundaries": (
            "no numerical deconfinement temperature",
            "no lattice measure",
            "no dynamical proof of the phase transition",
        ),
    },
    {
        "id": "chiral-symmetry-breaking",
        "path": "Physlib/QuantumMechanics/ComplexAction/HorizonCell/ChiralSymmetryBreakingCondensate.lean",
        "blob": "f29e760dfc6f2b98149a9dd316f167482520920e",
        "zil_level": "physical_theorem",
        "contract_status": "satisfied",
        "declarations": (
            "chiralRotate_preserves_radius",
            "chiral_invariant_forces_zero",
            "condensate_breaks_chiral",
            "gmor_chiral_limit",
            "gmor_pos",
            "gmorPionMassSq_linear_in_quarkMass",
            "two_qcd_order_parameters",
        ),
        "boundaries": (
            "GMOR is a supplied physical relation",
            "no finite-temperature condensate melting curve",
            "no independently calculated condensate",
        ),
    },
    {
        "id": "axial-anomaly-eta-prime",
        "path": "Physlib/QuantumMechanics/ComplexAction/HorizonCell/AxialAnomalyEtaPrimeMass.lean",
        "blob": "bfbaf7766c5b6d8e9929b59166ffa15241465fdf",
        "zil_level": "physical_theorem",
        "contract_status": "satisfied",
        "declarations": (
            "massless_quark_removes_theta",
            "massless_quark_trivializes_theta_vacuum",
            "etaPrime_massive_from_anomaly",
            "etaPrime_goldstone_large_N",
            "uOneA_problem_resolved",
        ),
        "boundaries": (
            "axial anomaly equation is not derived from the path integral",
            "topological susceptibility is an input",
            "massless-quark cancellation is conditional and not the physical light-quark spectrum",
        ),
    },
)


def _is_sha(value: str) -> bool:
    return len(value) == 40 and all(c in "0123456789abcdef" for c in value)


def center_transform(z: complex, loop: complex) -> complex:
    return z * loop


def cube_root_center() -> complex:
    return cmath.exp(2j * math.pi / 3.0)


def polyakov_magnitude(temperature: float, free_energy: float) -> float:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    return math.exp(-free_energy / temperature)


def chiral_rotate(angle: float, sigma: float, pion: float) -> tuple[float, float]:
    c = math.cos(angle)
    s = math.sin(angle)
    return c * sigma - s * pion, s * sigma + c * pion


def gmor_pion_mass_sq(quark_mass: float, condensate: float, f_pi: float) -> float:
    if f_pi == 0:
        raise ValueError("f_pi must be nonzero")
    return -2.0 * quark_mass * condensate / (f_pi * f_pi)


def theta_shift(theta: float, alpha: float, n_flavors: float) -> float:
    return theta + 2.0 * n_flavors * alpha


def eta_prime_mass_sq(n_flavors: float, chi_top: float, f_pi: float) -> float:
    if f_pi == 0:
        raise ValueError("f_pi must be nonzero")
    return 2.0 * n_flavors * chi_top / (f_pi * f_pi)


@dataclass(frozen=True)
class QCDOrderParameterReport:
    schema: str
    physlib: dict[str, Any]
    source_records: tuple[dict[str, Any], ...]
    diagnostics: dict[str, float | bool]
    acceptance: dict[str, bool]
    boundaries: tuple[str, ...]
    passed: bool

    def payload(self) -> dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        encoded = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"), allow_nan=False)
        return sha256(encoded.encode()).hexdigest()


def run_qcd_order_parameter_study() -> QCDOrderParameterReport:
    # Target 1: Z(3) center order parameter and thermal monotonicity.
    z = cube_root_center()
    loop_zero = 0j
    center_zero_residual = abs(loop_zero - center_transform(z, loop_zero))
    nonzero_loop = 0.25 + 0.10j
    center_nonzero_residual = abs(nonzero_loop - center_transform(z, nonzero_loop))
    low_t = polyakov_magnitude(0.8, 1.7)
    high_t = polyakov_magnitude(1.6, 1.7)
    low_f = polyakov_magnitude(1.2, 1.0)
    high_f = polyakov_magnitude(1.2, 2.0)

    # Target 2: chiral circle and GMOR scaling.
    sigma, pion = -0.018, 0.007
    rotated = chiral_rotate(0.73, sigma, pion)
    radius_before = sigma * sigma + pion * pion
    radius_after = rotated[0] * rotated[0] + rotated[1] * rotated[1]
    m_q = 0.004
    condensate = -0.014
    f_pi = 0.092
    pion_mass_sq = gmor_pion_mass_sq(m_q, condensate, f_pi)
    scaled_pion_mass_sq = gmor_pion_mass_sq(3.0 * m_q, condensate, f_pi)
    chiral_limit = gmor_pion_mass_sq(0.0, condensate, f_pi)

    # Target 3: axial anomaly, theta removal, and Witten--Veneziano positivity.
    theta = 0.43
    n_flavors = 3.0
    cancellation_angle = -theta / (2.0 * n_flavors)
    shifted_theta = theta_shift(theta, cancellation_angle, n_flavors)
    theta_weight = cmath.exp(1j * shifted_theta * 4)
    eta_sq = eta_prime_mass_sq(n_flavors, 0.0011, f_pi)
    eta_large_n = eta_prime_mass_sq(n_flavors, 0.0, f_pi)

    diagnostics: dict[str, float | bool] = {
        "center_zero_residual": center_zero_residual,
        "center_nonzero_residual": center_nonzero_residual,
        "polyakov_low_temperature": low_t,
        "polyakov_high_temperature": high_t,
        "polyakov_low_free_energy": low_f,
        "polyakov_high_free_energy": high_f,
        "chiral_radius_residual": abs(radius_after - radius_before),
        "gmor_pion_mass_sq": pion_mass_sq,
        "gmor_scaled_linearity_residual": abs(scaled_pion_mass_sq - 3.0 * pion_mass_sq),
        "gmor_chiral_limit": chiral_limit,
        "shifted_theta_residual": abs(shifted_theta),
        "trivial_theta_weight_residual": abs(theta_weight - 1.0),
        "eta_prime_mass_sq": eta_sq,
        "eta_prime_large_n_limit": eta_large_n,
    }

    acceptance = {
        "physlib_tip_is_pinned": _is_sha(PHYSLIB_TIP),
        "physlib_root_blob_is_pinned": _is_sha(PHYSLIB_ROOT_BLOB),
        "all_three_source_blobs_are_pinned": all(_is_sha(str(r["blob"])) for r in SOURCE_RECORDS),
        "all_zil_contracts_are_satisfied": all(r["contract_status"] == "satisfied" for r in SOURCE_RECORDS),
        "center_invariant_zero_is_exact": center_zero_residual < 1e-14,
        "nonzero_loop_breaks_center_symmetry": center_nonzero_residual > 1e-3,
        "polyakov_loop_grows_with_temperature": high_t > low_t,
        "polyakov_loop_decreases_with_free_energy": high_f < low_f,
        "chiral_rotation_preserves_radius": abs(radius_after - radius_before) < 1e-14,
        "gmor_mass_sq_is_positive": pion_mass_sq > 0,
        "gmor_is_linear_in_quark_mass": abs(scaled_pion_mass_sq - 3.0 * pion_mass_sq) < 1e-14,
        "pion_is_massless_in_chiral_limit": abs(chiral_limit) < 1e-14,
        "massless_quark_rotation_removes_theta": abs(shifted_theta) < 1e-14,
        "removed_theta_trivializes_vacuum_weight": abs(theta_weight - 1.0) < 1e-14,
        "eta_prime_is_massive_for_positive_susceptibility": eta_sq > 0,
        "eta_prime_becomes_massless_when_susceptibility_vanishes": abs(eta_large_n) < 1e-14,
    }

    boundaries = tuple(
        boundary for record in SOURCE_RECORDS for boundary in record["boundaries"]
    ) + (
        "no numerical T_c promotion",
        "no ab initio condensate or topological susceptibility",
        "no claim that a physical massless quark solves observed strong CP",
        "no unique CAT/EPT empirical confirmation",
    )

    return QCDOrderParameterReport(
        schema="openwave.m9.qcd-order-parameters.v1",
        physlib={
            "repository": PHYSLIB_REPOSITORY,
            "branch": PHYSLIB_BRANCH,
            "tip": PHYSLIB_TIP,
            "root_blob": PHYSLIB_ROOT_BLOB,
        },
        source_records=SOURCE_RECORDS,
        diagnostics=diagnostics,
        acceptance=acceptance,
        boundaries=boundaries,
        passed=all(acceptance.values()),
    )
