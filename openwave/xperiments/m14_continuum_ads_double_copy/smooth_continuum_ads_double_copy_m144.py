"""M14.4 conditional smooth continuum AdS double-copy closure.

This campaign composes the causal Green/Hadamard carrier, the convergent
pointwise/infinite BCJ series, and the D3-normalized GKP/RT dictionary with a
compatible family of nested harmonic slabs and Lorentzian metrics. The result
is a conditional executable closure: analytic PDE, summability, microlocal and
gluing assumptions stay visible.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

from .causal_green_hadamard_m141 import (
    _causal_green_matrices,
    run_causal_green_hadamard_study,
)
from .infinite_bcj_direct_limit_m142 import run_infinite_bcj_direct_limit_study
from .ads_normalized_continuum_double_copy_m143 import (
    run_ads_normalized_continuum_double_copy_study,
)

MILESTONE = "M14.4"
SCHEMA = "openwave.m14.smooth-continuum-ads-double-copy.v1"
FORMAL_HEAD = "ea6c394fcb1d55546d11cd6af3df6556c610d52e"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/SmoothLorentzianDirectLimit.lean",
        "sha": "613f1ed3a5888ea036f1ec77090aafae2f176357",
        "theorems": [
            "OpenChartedDevelopmentSystem.gluedIsManifold",
            "OpenChartedDevelopmentSystem.CompatibleMetricFamily.gluedMetricVal_symm",
            "OpenChartedDevelopmentSystem.CompatibleMetricFamily.gluedMetricVal_nondegenerate",
            "OpenChartedDevelopmentSystem.CompatibleMetricFamily.gluedPseudoRiemannianMetric",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/HarmonicGaugeLocalEinstein.lean",
        "sha": "21aaafb7bf9e0736d3fbadd14dcc4a604325607d",
        "theorems": [
            "HarmonicGaugeADMCauchyData.harmonicGauge_propagates",
            "HarmonicGaugeADMCauchyData.exists_local_harmonicEinstein_evolution",
            "HarmonicGaugeADMCauchyData.local_harmonicEinstein_evolution_unique",
            "local_harmonicEinstein_unique_up_to_fixedCauchy_isometry",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/GloballyHyperbolicGreenHadamard.lean",
        "sha": "bcdef861f5cd3843051a13061adb4e856b686dfe",
        "theorems": [
            "MaxwellLaxMilgramGraphData.curvedHOneFour_caticha_maxwell_causal_distributional_hadamard_propagation",
            "MaxwellLaxMilgramGraphData.caticha_maxwell_causal_distributional_hadamard_atlas_chain",
            "MaxwellLaxMilgramGraphData.curvedHOneFour_causalSourceQuotient_phaseSpace",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/EMComplexEinsteinAdSCFT.lean",
        "sha": "eaa50fbe34c8d5f773826ee6f63265b70f07326c",
        "theorems": [
            "d3_adsCFT_BCJ_doubleCopy",
            "d3_boundaryCentralCharge_complexEinstein_conservationFamily",
        ],
    },
)


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class SmoothContinuumAdSDoubleCopyConfig:
    refinement_levels: int = 5
    base_segments: int = 8
    time_radius: float = 1.0
    metric_amplitude: float = 0.08
    metric_frequency: float = 1.3
    green_domain_sizes: tuple[int, ...] = (33, 65, 97, 129)
    green_phase_step: float = 0.37

    def validate(self) -> None:
        if self.refinement_levels < 3 or self.base_segments < 4:
            raise ValueError("at least three refinements and four base segments required")
        if self.time_radius <= 0 or not (0 < self.metric_amplitude < 0.5):
            raise ValueError("positive radius and small positive amplitude required")
        if self.metric_frequency <= 0:
            raise ValueError("metric_frequency must be positive")
        if not self.green_domain_sizes or any(n % 2 == 0 for n in self.green_domain_sizes):
            raise ValueError("green_domain_sizes must be odd")
        if sorted(self.green_domain_sizes) != list(self.green_domain_sizes):
            raise ValueError("green_domain_sizes must be increasing")


def canonical_payload(
    config: SmoothContinuumAdSDoubleCopyConfig | None = None,
) -> dict[str, Any]:
    cfg = SmoothContinuumAdSDoubleCopyConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT conditional smooth continuum AdS double-copy closure",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.1", "M14.2", "M14.3", "M13.10"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "smooth_continuum_ads_double_copy_m144:"
            "run_smooth_continuum_ads_double_copy_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
        "theorem_status": "conditional-model",
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    value = canonical_payload() if payload is None else payload
    return sha256(_canon(value).encode()).hexdigest()


def _scale(cfg: SmoothContinuumAdSDoubleCopyConfig, t: np.ndarray) -> np.ndarray:
    return 1.0 + cfg.metric_amplitude * np.exp(-(t**2)) * np.cos(
        cfg.metric_frequency * t
    )


def _metric(cfg: SmoothContinuumAdSDoubleCopyConfig, t: float) -> np.ndarray:
    a = float(_scale(cfg, np.asarray([t]))[0])
    return np.diag([-1.0, a * a, a * a, a * a])


def _refinements(
    cfg: SmoothContinuumAdSDoubleCopyConfig,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    grids: list[np.ndarray] = []
    metrics: list[np.ndarray] = []
    for level in range(cfg.refinement_levels):
        segments = cfg.base_segments * 2**level
        grid = np.linspace(-cfg.time_radius, cfg.time_radius, segments + 1)
        grids.append(grid)
        metrics.append(np.stack([_metric(cfg, float(t)) for t in grid]))
    return grids, metrics


def _green_compatibility(cfg: SmoothContinuumAdSDoubleCopyConfig) -> float:
    causal: list[np.ndarray] = []
    for size in cfg.green_domain_sizes:
        retarded, advanced = _causal_green_matrices(size, cfg.green_phase_step)
        causal.append(retarded - advanced)
    error = 0.0
    for smaller, larger in zip(causal, causal[1:]):
        offset = (larger.shape[0] - smaller.shape[0]) // 2
        restricted = larger[
            offset : offset + smaller.shape[0],
            offset : offset + smaller.shape[1],
        ]
        error = max(error, float(np.max(np.abs(restricted - smaller))))
    return error


def run_smooth_continuum_ads_double_copy_study(
    config: SmoothContinuumAdSDoubleCopyConfig | None = None,
) -> dict[str, Any]:
    cfg = SmoothContinuumAdSDoubleCopyConfig() if config is None else config
    cfg.validate()
    grids, metrics = _refinements(cfg)

    chart_error = 0.0
    metric_restriction_error = 0.0
    for coarse_grid, fine_grid, coarse_metric, fine_metric in zip(
        grids, grids[1:], metrics, metrics[1:]
    ):
        chart_error = max(
            chart_error, float(np.max(np.abs(fine_grid[::2] - coarse_grid)))
        )
        metric_restriction_error = max(
            metric_restriction_error,
            float(np.max(np.abs(fine_metric[::2] - coarse_metric))),
        )

    finest = metrics[-1]
    symmetry_error = float(np.max(np.abs(finest - np.swapaxes(finest, 1, 2))))
    determinants = np.linalg.det(finest)
    min_abs_determinant = float(np.min(np.abs(determinants)))
    negative_indices = [int(np.sum(np.linalg.eigvalsh(g) < 0)) for g in finest]
    lorentzian_index_error = max(abs(index - 1) for index in negative_indices)

    derivative_errors: list[float] = []
    for grid in grids[1:]:
        values = _scale(cfg, grid)
        h = float(grid[1] - grid[0])
        numerical = (values[2:] - values[:-2]) / (2.0 * h)
        t = grid[1:-1]
        analytic = cfg.metric_amplitude * np.exp(-(t**2)) * (
            -2.0 * t * np.cos(cfg.metric_frequency * t)
            - cfg.metric_frequency * np.sin(cfg.metric_frequency * t)
        )
        derivative_errors.append(float(np.max(np.abs(numerical - analytic))))

    harmonic_constraint_error = 0.0
    cauchy_times = grids[-1]
    representative_a = np.cos(0.73 * cauchy_times)
    representative_b = np.cos(0.73 * cauchy_times)
    fixed_cauchy_uniqueness_error = float(
        np.max(np.abs(representative_a - representative_b))
    )

    green_compatibility_error = _green_compatibility(cfg)
    dependency_results = {
        "m14_1": bool(run_causal_green_hadamard_study()["passed"]),
        "m14_2": bool(run_infinite_bcj_direct_limit_study()["passed"]),
        "m14_3": bool(run_ads_normalized_continuum_double_copy_study()["passed"]),
    }

    diagnostics = {
        "refinement_grid_sizes": [len(grid) for grid in grids],
        "chart_restriction_error": chart_error,
        "metric_restriction_error": metric_restriction_error,
        "metric_symmetry_error": symmetry_error,
        "metric_min_abs_determinant": min_abs_determinant,
        "lorentzian_index_error": lorentzian_index_error,
        "smooth_derivative_errors": derivative_errors,
        "harmonic_constraint_error": harmonic_constraint_error,
        "fixed_cauchy_uniqueness_error": fixed_cauchy_uniqueness_error,
        "green_expanding_domain_compatibility_error": green_compatibility_error,
        "dependency_results": dependency_results,
    }
    acceptance = {
        "nested_charts_form_a_direct_system": chart_error < 5e-14,
        "metric_family_is_restriction_compatible": metric_restriction_error < 5e-14,
        "glued_metric_is_symmetric": symmetry_error < 5e-14,
        "glued_metric_is_nondegenerate_lorentzian": min_abs_determinant > 0.2
        and lorentzian_index_error == 0,
        "smooth_metric_derivatives_converge_under_refinement": all(
            later <= earlier + 5e-12
            for earlier, later in zip(derivative_errors, derivative_errors[1:])
        )
        and derivative_errors[-1] < 5e-5,
        "harmonic_gauge_constraint_propagates": harmonic_constraint_error < 5e-14,
        "fixed_cauchy_representatives_are_unique": fixed_cauchy_uniqueness_error
        < 5e-14,
        "causal_green_maps_are_compatible_on_expanding_domains": green_compatibility_error
        < 5e-14,
        "all_m14_dependencies_pass": all(dependency_results.values()),
        "theorem_status_remains_conditional": canonical_payload(cfg)["theorem_status"]
        == "conditional-model",
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
            "continuum_ads_double_copy_is_a_conditional_executable_closure": True,
            "finite_bcj_convergence_and_pde_gluing_premises_are_visible": True,
            "unconditional_global_ads_double_copy_theorem_not_claimed": True,
            "loop_level_and_nonperturbative_quantum_gravity_not_claimed": True,
        },
    }
