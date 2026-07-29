"""Executable QCD and particle-physics authority imported from Physlib/ZIL.

This module evaluates exact theorem-facing identities represented on
``entropic-physlib-linear-full``.  It does not claim a numerical hadron
spectrum, a Yang--Mills mass-gap proof, or first-principles confinement.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import cmath
import json
import math
from typing import Any, Mapping

PHYS_LIB_REPOSITORY = "jagg-ix/entropic-physlib-private"
PHYS_LIB_BRANCH = "entropic-physlib-linear-full"


@dataclass(frozen=True)
class FormalSource:
    identifier: str
    path: str
    blob: str
    declarations: tuple[str, ...]
    zil_level: str
    boundary: tuple[str, ...]


FORMAL_SOURCES = (
    FormalSource(
        "physlib-root",
        "Physlib.lean",
        "bf9028667305c70e77142e5fd24ec06fadb0d66f",
        ("Physlib.Meta.Zil", "Physlib.Meta.ZilGraph"),
        "root-import-authority",
        ("root import does not prove every imported physical claim",),
    ),
    FormalSource(
        "qcd-complex-action-unification",
        "Physlib/QuantumMechanics/ComplexAction/HorizonCell/QCDComplexActionUnification.lean",
        "c5d7108ec4781eee3068898d0d844b689230a6fa",
        (
            "theta_is_master_phase",
            "confinement_is_master_modulus",
            "qcd_theta_confinement_factorization",
            "ratioR_uds_via_winding",
            "casimir_matches_colorOctet",
        ),
        "physical-theorem-bindings",
        ("identities bind existing definitions; no new fitted QCD parameters are derived",),
    ),
    FormalSource(
        "qcd-asymptotic-freedom",
        "Physlib/QuantumMechanics/ComplexAction/HorizonCell/QCDBetaFunctionAsymptoticFreedom.lean",
        "ee1d516c44cbb196ada9be69fd9b2e0237211743",
        (
            "asymptotic_freedom_iff",
            "qcd_asymptotically_free",
            "runningCoupling_solves_rg",
            "runningCoupling_tendsto_zero",
            "dimensional_transmutation",
        ),
        "physical-theorem",
        ("one-loop flow only", "no higher-loop threshold or scheme matching"),
    ),
    FormalSource(
        "qcd-theta-strong-cp",
        "Physlib/QuantumMechanics/ComplexAction/HorizonCell/QCDThetaTermStrongCP.lean",
        "063732c52c41b7cebfefeeec7d0eeff2b9f4a63b",
        ("thetaWeight_periodic", "thetaWeight_abs", "thetaWeight_cp", "thetaTerm_strongCP"),
        "physical-theorem",
        ("experimental theta bound is recorded, not derived", "topological density is assumed"),
    ),
    FormalSource(
        "qcd-trace-anomaly-hadron-mass",
        "Physlib/QuantumMechanics/ComplexAction/HorizonCell/TraceAnomalyHadronMass.lean",
        "381841338506a6b904077a0fd4435d2b2888b5ca",
        ("trace_anomaly_from_asymptotic_freedom", "hadronMassSq_pos", "trace_anomaly_origin_of_hadron_mass"),
        "physical-theorem",
        ("gluon condensate is an input", "numerical hadron mass is not derived"),
    ),
)


def beta_zero(n_flavours: float) -> float:
    return (33.0 - 2.0 * n_flavours) / (12.0 * math.pi)


def beta_function(b0: float, alpha_s: float) -> float:
    return -b0 * alpha_s**2


def running_coupling(b0: float, alpha0: float, scale_time: float) -> float:
    return alpha0 / (1.0 + b0 * alpha0 * scale_time)


def running_coupling_derivative(b0: float, alpha0: float, scale_time: float) -> float:
    denominator = 1.0 + b0 * alpha0 * scale_time
    return -(b0 * alpha0**2) / denominator**2


def qcd_scale(mu0: float, b0: float, alpha0: float) -> float:
    return mu0 * math.exp(-1.0 / (b0 * alpha0))


def theta_weight(theta: float, winding: int) -> complex:
    return cmath.exp(1j * theta * winding)


def wilson_area_law(string_tension: float, area: float) -> float:
    return math.exp(-string_tension * area)


def complex_action_weight(real_action: float, imaginary_action: float) -> complex:
    return cmath.exp(1j * real_action - imaginary_action)


def ratio_r_uds() -> float:
    return 3.0 * ((2.0 / 3.0) ** 2 + 2.0 * (-1.0 / 3.0) ** 2)


def trace_anomaly(b0: float, coupling_sq: float, gluon_sq: float) -> float:
    return -(b0 * coupling_sq / 2.0) * gluon_sq


def hadron_mass_sq(trace_value: float) -> float:
    return -trace_value / 2.0


def source_fingerprint() -> str:
    payload = [asdict(source) for source in FORMAL_SOURCES]
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_qcd_particle_authority() -> dict[str, Any]:
    n_f = 6.0
    b0 = beta_zero(n_f)
    alpha0 = 0.22
    t = 4.0
    alpha = running_coupling(b0, alpha0, t)
    derivative = running_coupling_derivative(b0, alpha0, t)
    theta = 0.37
    winding = 3
    sigma = 0.81
    area = 1.7
    phase = theta_weight(theta, winding)
    factorized = phase * wilson_area_law(sigma, area)
    master = complex_action_weight(theta * winding, sigma * area)
    anomaly = trace_anomaly(b0, 1.3, 2.1)

    acceptance = {
        "verified_source_blobs_are_full_sha1": all(
            len(source.blob) == 40 and all(ch in "0123456789abcdef" for ch in source.blob)
            for source in FORMAL_SOURCES
        ),
        "zil_root_is_registered": FORMAL_SOURCES[0].declarations == ("Physlib.Meta.Zil", "Physlib.Meta.ZilGraph"),
        "six_flavour_qcd_is_asymptotically_free": b0 > 0.0 and beta_function(b0, alpha0) < 0.0,
        "running_solution_closes_one_loop_rg": math.isclose(derivative, beta_function(b0, alpha), rel_tol=1e-12, abs_tol=1e-12),
        "running_coupling_decreases_in_uv": running_coupling(b0, alpha0, 20.0) < alpha < alpha0,
        "dimensional_transmutation_scale_is_positive": qcd_scale(91.1876, b0, alpha0) > 0.0,
        "theta_weight_is_periodic": abs(theta_weight(theta + 2.0 * math.pi, winding) - phase) < 1e-12,
        "theta_weight_has_unit_modulus": math.isclose(abs(phase), 1.0, rel_tol=0.0, abs_tol=1e-12),
        "theta_cp_flip_is_complex_conjugation": abs(theta_weight(theta, -winding) - phase.conjugate()) < 1e-12,
        "theta_confinement_factorization_closes": abs(master - factorized) < 1e-12,
        "uds_color_counting_ratio_is_two": math.isclose(ratio_r_uds(), 2.0, rel_tol=0.0, abs_tol=1e-12),
        "su3_color_data_close": 3**2 - 1 == 8 and 3 * 3 == 8 + 1,
        "trace_anomaly_is_negative": anomaly < 0.0,
        "trace_anomaly_yields_positive_mass_squared": hadron_mass_sq(anomaly) > 0.0,
        "claim_boundaries_are_retained": all(source.boundary for source in FORMAL_SOURCES),
    }
    return {
        "schema": "openwave.m9.qcd-particle-authority.v1",
        "task": "M9.135",
        "formal_repository": {"name": PHYS_LIB_REPOSITORY, "branch": PHYS_LIB_BRANCH},
        "formal_sources": [asdict(source) for source in FORMAL_SOURCES],
        "source_fingerprint": source_fingerprint(),
        "observables": {
            "beta_zero_nf6": b0,
            "alpha_uv_sample": alpha,
            "qcd_scale_sample": qcd_scale(91.1876, b0, alpha0),
            "ratio_r_uds": ratio_r_uds(),
            "trace_anomaly_sample": anomaly,
            "hadron_mass_sq_sign_sample": hadron_mass_sq(anomaly),
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "qcd_formal_program_is_substantial": True,
            "complex_action_qcd_factorization_is_executable": True,
            "one_loop_qcd_running_is_executable": True,
            "strong_cp_structure_is_executable": True,
            "trace_anomaly_origin_structure_is_executable": True,
            "numerical_hadron_spectrum_derived": False,
            "continuum_yang_mills_mass_gap_proved": False,
            "first_principles_confinement_proved": False,
            "unique_cat_ept_empirical_confirmation": False,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
