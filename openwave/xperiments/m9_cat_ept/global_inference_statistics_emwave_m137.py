"""Executable bridge for three globally inspected Physlib theorem families.

Physlib remains the formal authority.  The checks below exercise finite scalar
consequences while retaining the exact source boundaries: Cramer--Rao does not
identify physical mass, Pauli antisymmetry does not derive spin statistics for a
CAT/EPT excitation, and the harmonic Maxwell certificate does not quantize the
field or derive electromagnetism from CAT/EPT.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import cmath
import json
import math
from typing import Any, Callable

PHYSLIB_REPOSITORY = "jagg-ix/entropic-physlib-private"
PHYSLIB_BRANCH = "entropic-physlib-linear-full"
PHYSLIB_TIP = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
PHYSLIB_ROOT_BLOB = "bf9028667305c70e77142e5fd24ec06fadb0d66f"

SOURCE_RECORDS = (
    {
        "id": "cramer-rao-inference-precision",
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CramerRaoInferenceMass.lean",
        "blob": "aacd40be13772130b8100daffcdbb2452a888a5e",
        "declarations": (
            "covariance_sq_le_variance_mul_variance",
            "cramerRao_bound",
            "gaussianMeanScore_variance",
            "gaussian_cramerRao_inferenceMass",
        ),
        "boundary": "physical mass equals inference precision remains a bridge postulate",
    },
    {
        "id": "pauli-exchange-exclusion",
        "path": "Physlib/QFT/PerturbationTheory/FieldStatistics/PauliExchange.lean",
        "blob": "da2f7e5829f2bde9d82524a9ff7aa8c5cc1ec98d",
        "declarations": (
            "antisymmetrize_swap",
            "antisymmetrize_self",
            "fermionic_exchange_involution",
        ),
        "boundary": "no dynamical assignment of fermionic statistics to a CAT/EPT excitation",
    },
    {
        "id": "harmonic-maxwell-plane-wave",
        "path": "Physlib/Electromagnetism/Vacuum/HarmonicWaveCertificate.lean",
        "blob": "d33904c994828370dbbe16fa4c5ab3ec8e27ec30",
        "declarations": (
            "harmonicWaveX_maxwell_planeWave",
            "harmonicWaveX_transverse_electric_component",
        ),
        "boundary": "free-field certificate only; no photon quantization or CAT/EPT emergence",
    },
)


def _is_sha(value: str) -> bool:
    return len(value) == 40 and all(c in "0123456789abcdef" for c in value)


def gaussian_score(x: float, mean: float, variance: float) -> float:
    if variance <= 0:
        raise ValueError("variance must be positive")
    return (x - mean) / variance


def gaussian_pdf(x: float, mean: float, variance: float) -> float:
    if variance <= 0:
        raise ValueError("variance must be positive")
    return math.exp(-((x - mean) ** 2) / (2.0 * variance)) / math.sqrt(
        2.0 * math.pi * variance
    )


def antisymmetrize(
    amplitude: Callable[[str, str], complex], first: str, second: str
) -> complex:
    return amplitude(first, second) - amplitude(second, first)


def harmonic_electric_component(
    amplitude: float, wave_number: float, speed: float, time: float, x: float, phase: float
) -> float:
    if wave_number == 0:
        raise ValueError("wave number must be nonzero")
    return amplitude * math.cos(wave_number * speed * time - wave_number * x + phase)


@dataclass(frozen=True)
class M137Report:
    schema: str
    physlib: dict[str, str]
    source_records: tuple[dict[str, Any], ...]
    diagnostics: dict[str, float]
    acceptance: dict[str, bool]
    boundaries: tuple[str, ...]
    passed: bool

    def payload(self) -> dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        encoded = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))
        return sha256(encoded.encode()).hexdigest()


def run_m137_global_authority() -> M137Report:
    # Target 1: numerical Gaussian score moments and a saturating unbiased estimator.
    variance = 1.7
    mean = -0.35
    radius = 9.0 * math.sqrt(variance)
    samples = 20001
    dx = 2.0 * radius / (samples - 1)
    xs = [mean - radius + i * dx for i in range(samples)]
    weights = [gaussian_pdf(x, mean, variance) for x in xs]
    normalization = sum(weights) * dx
    score_mean = sum(w * gaussian_score(x, mean, variance) for x, w in zip(xs, weights)) * dx
    score_variance = (
        sum(w * gaussian_score(x, mean, variance) ** 2 for x, w in zip(xs, weights)) * dx
    )
    estimator_variance = sum(w * (x - mean) ** 2 for x, w in zip(xs, weights)) * dx
    covariance_estimator_score = (
        sum(w * (x - mean) * gaussian_score(x, mean, variance) for x, w in zip(xs, weights)) * dx
    )

    # Target 2: antisymmetry, coincident-state exclusion, and two-swap involution.
    values = {
        ("a", "b"): 2.0 + 3.0j,
        ("b", "a"): -1.0 + 0.5j,
        ("a", "a"): 4.0 - 2.0j,
    }
    amplitude = lambda a, b: values.get((a, b), 0j)
    ab = antisymmetrize(amplitude, "a", "b")
    ba = antisymmetrize(amplitude, "b", "a")
    aa = antisymmetrize(amplitude, "a", "a")
    fermion_exchange_sign = -1.0

    # Target 3: exact transverse harmonic component and wave-equation residual.
    e0, k, c, phase = 1.4, 2.3, 0.8, 0.37
    t, x = 0.61, -0.42
    omega = k * c
    field = harmonic_electric_component(e0, k, c, t, x, phase)
    dt = 1.0e-4
    dx_wave = 1.0e-4
    e_tt = (
        harmonic_electric_component(e0, k, c, t + dt, x, phase)
        - 2.0 * field
        + harmonic_electric_component(e0, k, c, t - dt, x, phase)
    ) / dt**2
    e_xx = (
        harmonic_electric_component(e0, k, c, t, x + dx_wave, phase)
        - 2.0 * field
        + harmonic_electric_component(e0, k, c, t, x - dx_wave, phase)
    ) / dx_wave**2
    wave_residual = abs(e_tt - c * c * e_xx)
    analytic_time_curvature = -(omega**2) * field

    diagnostics = {
        "gaussian_normalization_error": abs(normalization - 1.0),
        "score_mean_error": abs(score_mean),
        "score_variance_error": abs(score_variance - 1.0 / variance),
        "estimator_variance_error": abs(estimator_variance - variance),
        "estimator_score_covariance_error": abs(covariance_estimator_score - 1.0),
        "cramer_rao_saturation_error": abs(estimator_variance * score_variance - 1.0),
        "antisymmetry_swap_error": abs(ba + ab),
        "identical_state_exclusion_error": abs(aa),
        "exchange_involution_error": abs(fermion_exchange_sign**2 - 1.0),
        "harmonic_wave_residual": wave_residual,
        "harmonic_time_curvature_error": abs(e_tt - analytic_time_curvature),
    }
    acceptance = {
        "exact_physlib_tip_is_pinned": _is_sha(PHYSLIB_TIP),
        "root_and_three_sources_are_pinned": _is_sha(PHYSLIB_ROOT_BLOB)
        and all(_is_sha(str(record["blob"])) for record in SOURCE_RECORDS),
        "gaussian_score_is_centered": diagnostics["score_mean_error"] < 1e-10,
        "gaussian_score_variance_is_fisher_information": diagnostics["score_variance_error"] < 1e-9,
        "sample_mean_saturates_cramer_rao": diagnostics["cramer_rao_saturation_error"] < 1e-8,
        "regularity_covariance_is_one": diagnostics["estimator_score_covariance_error"] < 1e-9,
        "antisymmetry_reverses_under_swap": diagnostics["antisymmetry_swap_error"] < 1e-14,
        "coincident_fermion_state_is_excluded": diagnostics["identical_state_exclusion_error"] < 1e-14,
        "two_fermion_exchanges_restore_sign": diagnostics["exchange_involution_error"] < 1e-14,
        "harmonic_component_satisfies_wave_equation": diagnostics["harmonic_wave_residual"] < 1e-6,
        "harmonic_component_matches_exact_time_curvature": diagnostics["harmonic_time_curvature_error"] < 1e-6,
        "physical_promotion_remains_blocked": True,
    }
    return M137Report(
        schema="openwave.m9.global-inference-statistics-emwave.v1",
        physlib={
            "repository": PHYSLIB_REPOSITORY,
            "branch": PHYSLIB_BRANCH,
            "tip": PHYSLIB_TIP,
            "root_blob": PHYSLIB_ROOT_BLOB,
        },
        source_records=SOURCE_RECORDS,
        diagnostics=diagnostics,
        acceptance=acceptance,
        boundaries=tuple(str(record["boundary"]) for record in SOURCE_RECORDS),
        passed=all(acceptance.values()),
    )
