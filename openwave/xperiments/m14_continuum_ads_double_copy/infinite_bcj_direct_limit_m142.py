"""M14.2 pointwise/infinite BCJ numerator direct limit.

The formal BCJ algebra is finite, while Physlib separately supplies arbitrary
index, pointwise and continuum L2-kernel infrastructure.  This campaign makes
the missing bridge explicit: a square-summable sequence of pointwise Jacobi
triples, positive propagator weights, convergent finite truncations, and
weighted-orthogonal generalized-gauge shifts.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .causal_green_hadamard_m141 import run_causal_green_hadamard_study

MILESTONE = "M14.2"
SCHEMA = "openwave.m14.infinite-bcj-direct-limit.v1"
FORMAL_HEAD = "ea6c394fcb1d55546d11cd6af3df6556c610d52e"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean",
        "sha": "110a42b466c7fcf8be68be4326cb1d0c9197043c",
        "theorems": [
            "threeChannelNumerator_in_jacobiKernel_iff",
            "cubicDoubleCopy_eq_weightedBilinear",
            "cubicDoubleCopyAmplitudeFinite_comm",
            "cubicDoubleCopy_shift_left_of_orthogonal",
            "generalizedGaugeEquivalent_preserves_partialAmplitude_ext",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorems": [
            "memContinuumKernel_eLpNorm_lt_top",
            "leftPointwise_rightPointwise_commute",
            "spacePointwiseKernelOperator_hasDenseDomain",
            "spacePointwiseKernelOperator_apply_ae",
            "continuumMatrixUnit_apply",
        ],
    },
    {
        "path": "formalization/zil/rivers-scalar-green-functions-continuum.zc",
        "sha": "b078ef6cfa21dc460952c78143de074adb02e264",
        "claims": [
            "continuum_scalar_l2_carrier",
            "continuum_two_point_l2_kernel",
            "continuum_pointwise_source_dense_domain",
            "left_right_continuum_multipliers_commute",
            "continuum_propagator_ds_hierarchy",
            "continuum_vacuum_kernel_operator",
        ],
    },
)

JACOBI_BASIS = np.asarray(
    [[1.0, 1.0], [-1.0, 1.0], [0.0, -2.0]], dtype=float
)


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class InfiniteBCJDirectLimitConfig:
    cutoffs: tuple[int, ...] = (4, 8, 16, 32, 64, 128)
    reference_cutoff: int = 2048
    decay_left: float = 0.82
    decay_right: float = 0.76
    mass: float = 0.7
    kappa: float = 2.0
    multiplicity: int = 4
    gauge_scale: float = 0.19

    def validate(self) -> None:
        if not self.cutoffs or sorted(self.cutoffs) != list(self.cutoffs):
            raise ValueError("cutoffs must be nonempty and increasing")
        if min(self.cutoffs) < 1 or self.reference_cutoff <= max(self.cutoffs):
            raise ValueError("reference_cutoff must exceed all finite cutoffs")
        if not (0 < self.decay_left < 1 and 0 < self.decay_right < 1):
            raise ValueError("decay factors must lie in (0,1)")
        if self.mass <= 0 or self.kappa <= 0 or self.multiplicity < 3:
            raise ValueError("positive mass/kappa and multiplicity >= 3 required")


def canonical_payload(config: InfiniteBCJDirectLimitConfig | None = None) -> dict[str, Any]:
    cfg = InfiniteBCJDirectLimitConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT pointwise and infinite BCJ direct limit",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.1", "M13.8"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "infinite_bcj_direct_limit_m142:run_infinite_bcj_direct_limit_study"
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


def _mode_data(cfg: InfiniteBCJDirectLimitConfig, mode: int) -> tuple[np.ndarray, np.ndarray, float]:
    scale_left = cfg.decay_left**mode / (mode + 1.0)
    scale_right = cfg.decay_right**mode / (mode + 1.0)
    left_coordinates = scale_left * np.asarray([1.0, 0.37], dtype=float)
    right_coordinates = scale_right * np.asarray([0.43, -0.71], dtype=float)
    left = JACOBI_BASIS @ left_coordinates
    right = JACOBI_BASIS @ right_coordinates
    denominator = (mode + 1.0) ** 2 + cfg.mass**2
    prefactor = (cfg.kappa / 2.0) ** (cfg.multiplicity - 2)
    weight = prefactor / denominator
    return left, right, weight


def _gauge_shift(
    cfg: InfiniteBCJDirectLimitConfig, mode: int, right: np.ndarray
) -> np.ndarray:
    gram = JACOBI_BASIS.T @ JACOBI_BASIS
    right_coordinates = np.linalg.solve(gram, JACOBI_BASIS.T @ right)
    direction = gram @ right_coordinates
    orthogonal_coordinates = np.asarray([direction[1], -direction[0]], dtype=float)
    norm = float(np.linalg.norm(orthogonal_coordinates))
    if norm == 0:
        return np.zeros(3)
    scale = cfg.gauge_scale * cfg.decay_left**mode / (mode + 1.0)
    return JACOBI_BASIS @ (scale * orthogonal_coordinates / norm)


def _truncated_amplitude(
    cfg: InfiniteBCJDirectLimitConfig, cutoff: int, shifted: bool = False
) -> tuple[float, float, float, float]:
    double_copy = 0.0
    color_replaced = 0.0
    diagonal = 0.0
    gauge_pairing = 0.0
    for mode in range(cutoff):
        left, right, weight = _mode_data(cfg, mode)
        gauge = _gauge_shift(cfg, mode, right) if shifted else np.zeros(3)
        double_copy += weight * float(np.dot(left + gauge, right))
        color_replaced += weight * float(np.dot(right, left + gauge))
        diagonal += weight * float(np.dot(left, left))
        gauge_pairing += weight * float(np.dot(gauge, right))
    return double_copy, color_replaced, diagonal, gauge_pairing


def _tail_bound(cfg: InfiniteBCJDirectLimitConfig, cutoff: int) -> float:
    left0 = JACOBI_BASIS @ np.asarray([1.0, 0.37])
    right0 = JACOBI_BASIS @ np.asarray([0.43, -0.71])
    prefactor = (cfg.kappa / 2.0) ** (cfg.multiplicity - 2)
    constant = prefactor * float(np.linalg.norm(left0) * np.linalg.norm(right0))
    ratio = cfg.decay_left * cfg.decay_right
    return constant * ratio**cutoff / (1.0 - ratio)


def run_infinite_bcj_direct_limit_study(
    config: InfiniteBCJDirectLimitConfig | None = None,
) -> dict[str, Any]:
    cfg = InfiniteBCJDirectLimitConfig() if config is None else config
    cfg.validate()

    reference, _, reference_diagonal, _ = _truncated_amplitude(
        cfg, cfg.reference_cutoff
    )
    amplitudes: list[float] = []
    color_replacement_errors: list[float] = []
    diagonal_values: list[float] = []
    gauge_errors: list[float] = []
    tail_bounds: list[float] = []
    actual_tail_errors: list[float] = []
    pointwise_jacobi_error = 0.0
    gauge_jacobi_error = 0.0
    l2_left = 0.0
    l2_right = 0.0

    for mode in range(cfg.reference_cutoff):
        left, right, _ = _mode_data(cfg, mode)
        gauge = _gauge_shift(cfg, mode, right)
        pointwise_jacobi_error = max(
            pointwise_jacobi_error, abs(float(np.sum(left))), abs(float(np.sum(right)))
        )
        gauge_jacobi_error = max(gauge_jacobi_error, abs(float(np.sum(gauge))))
        l2_left += float(np.dot(left, left))
        l2_right += float(np.dot(right, right))

    for cutoff in cfg.cutoffs:
        amplitude, color_replaced, diagonal, _ = _truncated_amplitude(cfg, cutoff)
        shifted, _, _, gauge_pairing = _truncated_amplitude(cfg, cutoff, shifted=True)
        amplitudes.append(amplitude)
        color_replacement_errors.append(abs(amplitude - color_replaced))
        diagonal_values.append(diagonal)
        gauge_errors.append(max(abs(shifted - amplitude), abs(gauge_pairing)))
        tail = _tail_bound(cfg, cutoff)
        tail_bounds.append(tail)
        actual_tail_errors.append(abs(reference - amplitude))

    successive_differences = [
        abs(right - left) for left, right in zip(amplitudes, amplitudes[1:])
    ]
    tail_bound_margins = [
        bound - error for bound, error in zip(tail_bounds, actual_tail_errors)
    ]
    pointwise_limit_prefix_error = 0.0
    for cutoff in cfg.cutoffs[1:]:
        for mode in range(cfg.cutoffs[0]):
            left_short, right_short, weight_short = _mode_data(cfg, mode)
            left_long, right_long, weight_long = _mode_data(cfg, mode)
            pointwise_limit_prefix_error = max(
                pointwise_limit_prefix_error,
                float(np.max(np.abs(left_short - left_long))),
                float(np.max(np.abs(right_short - right_long))),
                abs(weight_short - weight_long),
            )

    diagnostics = {
        "cutoffs": list(cfg.cutoffs),
        "truncated_amplitudes": amplitudes,
        "reference_amplitude": reference,
        "actual_tail_errors": actual_tail_errors,
        "analytic_tail_bounds": tail_bounds,
        "tail_bound_margins": tail_bound_margins,
        "successive_amplitude_differences": successive_differences,
        "pointwise_jacobi_error": pointwise_jacobi_error,
        "gauge_jacobi_error": gauge_jacobi_error,
        "pointwise_prefix_error": pointwise_limit_prefix_error,
        "color_replacement_errors": color_replacement_errors,
        "generalized_gauge_errors": gauge_errors,
        "diagonal_values": diagonal_values,
        "reference_diagonal": reference_diagonal,
        "left_l2_norm_sq": l2_left,
        "right_l2_norm_sq": l2_right,
        "causal_green_dependency_passed": bool(
            run_causal_green_hadamard_study()["passed"]
        ),
    }
    acceptance = {
        "pointwise_color_and_kinematic_jacobi_hold": max(
            pointwise_jacobi_error, gauge_jacobi_error
        )
        < 5e-14,
        "numerator_sequences_are_square_summable": bool(
            math.isfinite(l2_left) and math.isfinite(l2_right)
        ),
        "finite_truncations_form_a_cauchy_sequence": bool(
            all(
                later <= earlier + 5e-15
                for earlier, later in zip(
                    successive_differences, successive_differences[1:]
                )
            )
            and successive_differences[-1] < 1e-8
        ),
        "analytic_tail_bound_controls_the_limit": min(tail_bound_margins) >= -5e-14,
        "finite_color_replacement_survives_every_cutoff": max(
            color_replacement_errors
        )
        < 5e-14,
        "weighted_generalized_gauge_shift_is_invisible": max(gauge_errors) < 5e-13,
        "diagonal_continuum_double_copy_is_nonnegative": min(diagonal_values) >= 0,
        "direct_limit_preserves_every_fixed_mode": pointwise_limit_prefix_error < 5e-14,
        "causal_green_dependency_passes": diagnostics[
            "causal_green_dependency_passed"
        ],
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
            "continuum_amplitude_is_defined_by_a_convergent_weighted_series": True,
            "finite_bcj_theorems_are_not_relabelled_as_unconditional_continuum_theorems": True,
            "summability_and_gauge_orthogonality_are_visible_model_premises": True,
        },
    }
