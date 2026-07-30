"""M14.3 D3-normalized continuum BCJ/GKP/RT composition.

The same D3/boundary-central-charge coupling is used for the convergent M14.2
BCJ series, a positive-frequency continuum boundary kernel, the finite GKP
quadratic source response, and the RT normalization.  The module composes
normalizations; it does not identify an amplitude with an entropy or construct
an interacting Witten functional.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .causal_green_hadamard_m141 import run_causal_green_hadamard_study
from .infinite_bcj_direct_limit_m142 import (
    InfiniteBCJDirectLimitConfig,
    run_infinite_bcj_direct_limit_study,
)

MILESTONE = "M14.3"
SCHEMA = "openwave.m14.ads-normalized-continuum-double-copy.v1"
FORMAL_HEAD = "ea6c394fcb1d55546d11cd6af3df6556c610d52e"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/EMComplexEinsteinAdSCFT.lean",
        "sha": "eaa50fbe34c8d5f773826ee6f63265b70f07326c",
        "theorems": [
            "d3_adsCFT_BCJ_doubleCopy",
            "d3_gkpWittenHessian_complexEinsteinCoupling",
            "d3_gkpWittenHessian_boundaryCentralCharge",
            "d3_rtEntropy_complexEinsteinCoupling",
            "d3_rtEntropy_boundaryCentralCharge",
            "d3_boundaryCentralCharge_complexEinstein_conservationFamily",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean",
        "sha": "d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3",
        "theorems": [
            "massDimension_relation",
            "cftTwoPoint_scaling",
            "gkpWitten_regularized_source_response",
            "gkpWitten_affine_source_hessian",
        ],
    },
    {
        "path": "Physlib/QFT/ScalarGreenFunctions.lean",
        "sha": "b985c5442a61615f81ebbaaaea45d165338f344a",
        "modules": [
            "Continuum",
            "ContinuumDysonSchwinger",
            "ContinuumVacuum",
            "PropagatorHierarchy",
            "TraceLog",
        ],
    },
)


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class AdSNormalizedContinuumConfig:
    ads_radius: float = 2.3
    color_rank: float = 6.0
    compactification_volume: float = 1.7
    c: float = 1.0
    boundary_dimension: float = 4.0
    bulk_mass: float = 0.42
    rt_area: float = 1.6
    boundary_points: int = 14
    momentum_max: float = 18.0
    quadrature_counts: tuple[int, ...] = (128, 256, 512, 1024)
    uv_cutoff: float = 0.09
    derivative_step: float = 2e-5

    def validate(self) -> None:
        positive = (
            self.ads_radius,
            self.color_rank,
            self.compactification_volume,
            self.c,
            self.boundary_dimension,
            self.bulk_mass,
            self.rt_area,
            self.momentum_max,
            self.uv_cutoff,
            self.derivative_step,
        )
        if min(positive) <= 0:
            raise ValueError("all geometric and spectral controls must be positive")
        if self.boundary_points < 4:
            raise ValueError("at least four boundary points required")
        if not self.quadrature_counts or sorted(self.quadrature_counts) != list(
            self.quadrature_counts
        ):
            raise ValueError("quadrature_counts must be increasing")


def canonical_payload(config: AdSNormalizedContinuumConfig | None = None) -> dict[str, Any]:
    cfg = AdSNormalizedContinuumConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT D3-normalized continuum AdS double-copy kernel",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.2", "M13.8"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "ads_normalized_continuum_double_copy_m143:"
            "run_ads_normalized_continuum_double_copy_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    value = canonical_payload() if payload is None else payload
    return sha256(_canon(value).encode()).hexdigest()


def _boundary_kernel(
    cfg: AdSNormalizedContinuumConfig, count: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    points = np.linspace(0.35, 2.35, cfg.boundary_points)
    dq = cfg.momentum_max / count
    momenta = (np.arange(count, dtype=float) + 0.5) * dq
    propagator_weights = (
        dq
        * np.exp(-2.0 * cfg.uv_cutoff * momenta)
        / (momenta**2 + cfg.bulk_mass**2)
    )
    root = np.sqrt(propagator_weights)
    cosine = np.cos(np.outer(points, momenta)) * root
    sine = np.sin(np.outer(points, momenta)) * root
    features = np.concatenate((cosine, sine), axis=1)
    kernel = features @ features.T
    return points, momenta, kernel


def _conformal_dimension(boundary_dimension: float, mass_radius_sq: float) -> float:
    radicand = (boundary_dimension / 2.0) ** 2 + mass_radius_sq
    if radicand < 0:
        raise ValueError("BF bound violated")
    return boundary_dimension / 2.0 + math.sqrt(radicand)


def run_ads_normalized_continuum_double_copy_study(
    config: AdSNormalizedContinuumConfig | None = None,
) -> dict[str, Any]:
    cfg = AdSNormalizedContinuumConfig() if config is None else config
    cfg.validate()

    central_charge = cfg.color_rank**2 / 4.0
    kappa_ads = (
        4.0
        * math.pi**2
        * cfg.ads_radius**3
        / (cfg.color_rank**2 * cfg.compactification_volume * cfg.c**4)
    )
    kappa_boundary = (
        math.pi**2
        * cfg.ads_radius**3
        / (cfg.compactification_volume * cfg.c**4 * central_charge)
    )
    newton_g4 = kappa_ads * cfg.c**4 / (8.0 * math.pi)

    bcj_cfg = replace(InfiniteBCJDirectLimitConfig(), kappa=kappa_ads)
    bcj = run_infinite_bcj_direct_limit_study(bcj_cfg)

    kernels: list[np.ndarray] = []
    for count in cfg.quadrature_counts:
        _, _, kernel = _boundary_kernel(cfg, count)
        kernels.append(kernel)
    kernel_differences = [
        float(np.linalg.norm(right - left, ord="fro"))
        for left, right in zip(kernels, kernels[1:])
    ]
    points, momenta, kernel = _boundary_kernel(cfg, cfg.quadrature_counts[-1])
    kernel_symmetry_error = float(np.max(np.abs(kernel - kernel.T)))
    kernel_eigenvalues = np.linalg.eigvalsh(kernel)
    kernel_min_eigenvalue = float(np.min(kernel_eigenvalues))

    hessian = kernel / newton_g4
    source = np.exp(-points**2)
    variation = np.cos(points) * np.exp(-0.2 * points)

    def response(t: float) -> float:
        current = source + t * variation
        return 0.5 * float(current @ hessian @ current)

    step = cfg.derivative_step
    first = (response(step) - response(-step)) / (2.0 * step)
    second = (response(step) - 2.0 * response(0.0) + response(-step)) / step**2
    expected_first = float(source @ hessian @ variation)
    expected_second = float(variation @ hessian @ variation)

    mass_radius_sq = (cfg.bulk_mass * cfg.ads_radius) ** 2
    conformal_dimension = _conformal_dimension(
        cfg.boundary_dimension, mass_radius_sq
    )
    separation = 1.4
    dilation = 1.9
    two_point = separation ** (-2.0 * conformal_dimension)
    moved_two_point = (dilation * separation) ** (-2.0 * conformal_dimension)

    rt_entropy = cfg.rt_area / (4.0 * newton_g4)
    rt_boundary = (
        2.0
        * cfg.compactification_volume
        * central_charge
        * cfg.rt_area
        / (math.pi * cfg.ads_radius**3)
    )

    diagnostics = {
        "central_charge": central_charge,
        "kappa_ads": kappa_ads,
        "kappa_boundary": kappa_boundary,
        "coupling_dictionary_error": abs(kappa_ads - kappa_boundary),
        "newton_g4": newton_g4,
        "continuum_bcj_amplitude": bcj["diagnostics"]["reference_amplitude"],
        "continuum_bcj_dependency_passed": bool(bcj["passed"]),
        "kernel_quadrature_differences": kernel_differences,
        "kernel_symmetry_error": kernel_symmetry_error,
        "kernel_min_eigenvalue": kernel_min_eigenvalue,
        "kernel_eigenvalues": kernel_eigenvalues.tolist(),
        "positive_momentum_min": float(np.min(momenta)),
        "gkp_first_response_error": abs(first - expected_first),
        "gkp_hessian_error": abs(second - expected_second),
        "conformal_dimension": conformal_dimension,
        "mass_dimension_error": abs(
            conformal_dimension
            * (conformal_dimension - cfg.boundary_dimension)
            - mass_radius_sq
        ),
        "two_point_scaling_error": abs(
            moved_two_point - dilation ** (-2.0 * conformal_dimension) * two_point
        ),
        "rt_entropy": rt_entropy,
        "rt_boundary_entropy": rt_boundary,
        "rt_boundary_dictionary_error": abs(rt_entropy - rt_boundary),
        "kappa_rt_normalization_error": abs(
            kappa_ads * rt_entropy - 2.0 * math.pi * cfg.rt_area / cfg.c**4
        ),
        "hadamard_dependency_passed": bool(
            run_causal_green_hadamard_study()["passed"]
        ),
        "amplitude_entropy_difference": abs(
            bcj["diagnostics"]["reference_amplitude"] - rt_entropy
        ),
    }
    acceptance = {
        "d3_and_boundary_couplings_agree": diagnostics["coupling_dictionary_error"]
        < 5e-13,
        "infinite_bcj_limit_uses_the_ads_coupling": diagnostics[
            "continuum_bcj_dependency_passed"
        ],
        "positive_frequency_boundary_kernel_converges": bool(
            all(
                later <= earlier + 5e-10
                for earlier, later in zip(
                    kernel_differences, kernel_differences[1:]
                )
            )
            and kernel_differences[-1] < 3e-3
            and diagnostics["positive_momentum_min"] > 0
        ),
        "boundary_kernel_is_symmetric_positive": kernel_symmetry_error < 5e-11
        and kernel_min_eigenvalue > -5e-9,
        "gkp_source_response_and_hessian_close": max(
            diagnostics["gkp_first_response_error"],
            diagnostics["gkp_hessian_error"],
        )
        < 2e-4,
        "gkp_mass_dimension_and_two_point_scaling_close": max(
            diagnostics["mass_dimension_error"],
            diagnostics["two_point_scaling_error"],
        )
        < 5e-12,
        "rt_and_complex_einstein_normalizations_agree": max(
            diagnostics["rt_boundary_dictionary_error"],
            diagnostics["kappa_rt_normalization_error"],
        )
        < 5e-12,
        "causal_hadamard_dependency_passes": diagnostics[
            "hadamard_dependency_passed"
        ],
        "amplitude_is_not_identified_with_entropy": diagnostics[
            "amplitude_entropy_difference"
        ]
        > 1e-6,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "same_d3_coupling_normalizes_bcj_gkp_rt_and_einstein_faces": True,
            "continuum_kernel_is_a_positive_frequency_quadrature_limit": True,
            "amplitude_entropy_equality_not_claimed": True,
            "interacting_witten_functional_not_constructed": True,
        },
    }
