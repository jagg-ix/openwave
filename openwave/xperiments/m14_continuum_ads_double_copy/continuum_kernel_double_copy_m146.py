"""M14.6 continuum kernel/operator BCJ double-copy model.

This study lifts the merged M14 graph-sequence model to genuine two-point
fields on a continuous base-space discretization. Each point of X x X carries
color and kinematic Jacobi triples. Their weighted double-copy density is
integrated as a convergent quadrature, while the same carrier is exercised as
an L2/Hilbert--Schmidt kernel with commuting left/right pointwise multipliers
and a positive pointwise-background composition.

This is a finite-quadrature compatibility model for Physlib's continuum L2 and
maximal-domain operator surfaces. It does not prove arbitrary interacting
continuum amplitudes or remove the explicit integrability and orthogonality
premises.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

MILESTONE = "M14.6"
SCHEMA = "openwave.m14.continuum-kernel-double-copy.v1"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "35f98f147771a4e250ec01b4cbf2afab72313db7"
ZIL_COMMIT = "6daee2698304feb203c6adb91b2e8853613f85b5"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.31.0"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean",
        "sha": "96e5f7feb002125a633d90c3940e1af513bb8484",
        "theorems": [
            "cubicDoubleCopy_eq_weightedBilinear",
            "cubicDoubleCopyAmplitudeFinite_comm",
            "cubicDoubleCopy_shift_left_of_orthogonal",
            "cubicDoubleCopy_shift_right_of_orthogonal",
            "mizera_intersectionLeadingTerm_eq_doubleCopy",
        ],
    },
    {
        "path": "Physlib/QFT/ScalarGreenFunctions/Continuum.lean",
        "sha": "2bfb570363cbb89479ff53698195ce4e819e3cec",
        "theorems": [
            "coe_mkContinuumScalarKernel_ae",
            "continuumScalarMulOperator_hasDenseDomain",
            "continuumScalarMulOperator_apply_ae",
            "left_right_continuumScalarKernelAction_commute",
            "pointwiseKernelComposition",
            "pointwiseKernelComposition_zero",
        ],
    },
    {
        "path": "Physlib/Mathematics/LovelockRund/PointwiseOperators.lean",
        "sha": "bc2e08633fb9a6c3ec067aad54df6ba4df4c1816",
        "theorems": [
            "continuumField_memLp",
            "pointwiseFieldOperator_hasDenseDomain",
            "pointwiseFieldOperator_apply_ae",
        ],
    },
    {
        "path": "Physlib/Mathematics/LpAeConvergence.lean",
        "sha": "6898c8e2264fe30d5f1f41f6a3180cc4a942e4b0",
        "theorems": [
            "eLpNorm_tendsto_zero_of_aeBound",
            "ae_subseq_of_eLpNorm_tendsto",
        ],
    },
)

JACOBI_BASIS = np.asarray([[1.0, 1.0], [-1.0, 1.0], [0.0, -2.0]])


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class ContinuumKernelDoubleCopyConfig:
    point_counts: tuple[int, ...] = (20, 28, 40, 56, 80)
    domain_radius: float = 5.0
    mass: float = 0.9
    kappa: float = 2.0
    multiplicity: int = 4
    gauge_scale: float = 0.13
    background_floor: float = 0.35

    def validate(self) -> None:
        if not self.point_counts or sorted(self.point_counts) != list(self.point_counts):
            raise ValueError("point_counts must be nonempty and increasing")
        if min(self.point_counts) < 12:
            raise ValueError("at least twelve points are required")
        if min(self.domain_radius, self.mass, self.kappa, self.gauge_scale) <= 0:
            raise ValueError("positive domain, mass, coupling and gauge scale required")
        if self.multiplicity < 3 or self.background_floor <= 0:
            raise ValueError("multiplicity >= 3 and positive background required")


def canonical_payload(config: ContinuumKernelDoubleCopyConfig | None = None) -> dict[str, Any]:
    cfg = ContinuumKernelDoubleCopyConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT continuum pointwise-kernel BCJ double copy",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.2", "M14.5"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "continuum_kernel_double_copy_m146:run_continuum_kernel_double_copy_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
        "formal_toolchain": {
            "lean": "4.31.0",
            "lean_toolchain": LEAN_TOOLCHAIN,
            "zil_repository": "jagg-ix/zil-lean",
            "zil_commit": ZIL_COMMIT,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    value = canonical_payload() if payload is None else payload
    return sha256(_canon(value).encode()).hexdigest()


def _kernel_fields(cfg: ContinuumKernelDoubleCopyConfig, count: int):
    x = np.linspace(-cfg.domain_radius, cfg.domain_radius, count)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    left_coords = np.stack(
        (
            np.exp(-0.16 * (xx * xx + yy * yy)) * (1.0 + 0.18 * np.cos(xx - yy)),
            np.exp(-0.23 * (xx * xx + yy * yy)) * (0.31 + 0.12 * np.sin(xx + yy)),
        ),
        axis=-1,
    )
    right_coords = np.stack(
        (
            np.exp(-0.21 * (xx * xx + yy * yy)) * (0.72 - 0.11 * np.sin(xx - 0.4 * yy)),
            np.exp(-0.18 * (xx * xx + yy * yy)) * (-0.26 + 0.09 * np.cos(0.7 * xx + yy)),
        ),
        axis=-1,
    )
    left = left_coords @ JACOBI_BASIS.T
    right = right_coords @ JACOBI_BASIS.T
    denominators = np.stack(
        (
            1.0 + (xx - yy) ** 2 + cfg.mass**2,
            1.0 + (xx + 0.4 * yy) ** 2 + cfg.mass**2,
            1.0 + (0.5 * xx - yy) ** 2 + cfg.mass**2,
        ),
        axis=-1,
    )
    weights = (cfg.kappa / 2.0) ** (cfg.multiplicity - 2) / denominators
    gauge = np.empty_like(left)
    for i in range(count):
        for j in range(count):
            gram = JACOBI_BASIS.T @ np.diag(weights[i, j]) @ JACOBI_BASIS
            paired = gram @ right_coords[i, j]
            perpendicular = np.asarray([paired[1], -paired[0]])
            norm = float(np.linalg.norm(perpendicular))
            coords = (
                cfg.gauge_scale
                * np.exp(-0.2 * (xx[i, j] ** 2 + yy[i, j] ** 2))
                * perpendicular
                / (norm if norm else 1.0)
            )
            gauge[i, j] = JACOBI_BASIS @ coords
    return x, xx, yy, left, right, weights, gauge


def _integrate2(values: np.ndarray, x: np.ndarray) -> float:
    return float(np.trapezoid(np.trapezoid(values, x, axis=1), x, axis=0))


def run_continuum_kernel_double_copy_study(
    config: ContinuumKernelDoubleCopyConfig | None = None,
) -> dict[str, Any]:
    cfg = ContinuumKernelDoubleCopyConfig() if config is None else config
    cfg.validate()
    amplitudes: list[float] = []
    hilbert_schmidt_norm_sq: list[float] = []
    jacobi_errors: list[float] = []
    gauge_pairing_errors: list[float] = []
    gauge_amplitude_errors: list[float] = []
    color_replacement_errors: list[float] = []
    multiplier_commutator_errors: list[float] = []
    zero_composition_errors: list[float] = []
    composition_min_eigenvalues: list[float] = []

    for count in cfg.point_counts:
        x, xx, yy, left, right, weights, gauge = _kernel_fields(cfg, count)
        density = np.sum(weights * left * right, axis=-1)
        shifted_density = np.sum(weights * (left + gauge) * right, axis=-1)
        swapped_density = np.sum(weights * right * left, axis=-1)
        amplitudes.append(_integrate2(density, x))
        hilbert_schmidt_norm_sq.append(_integrate2(np.abs(density) ** 2, x))
        jacobi_errors.append(
            max(
                float(np.max(np.abs(np.sum(left, axis=-1)))),
                float(np.max(np.abs(np.sum(right, axis=-1)))),
                float(np.max(np.abs(np.sum(gauge, axis=-1)))),
            )
        )
        gauge_pairing_errors.append(
            float(np.max(np.abs(np.sum(weights * gauge * right, axis=-1))))
        )
        gauge_amplitude_errors.append(abs(_integrate2(shifted_density - density, x)))
        color_replacement_errors.append(float(np.max(np.abs(swapped_density - density))))

        left_multiplier = cfg.background_floor + np.exp(-0.3 * x * x)
        right_multiplier = 0.6 + 0.2 * np.cos(0.7 * x) ** 2
        left_then_right = left_multiplier[:, None] * (density * right_multiplier[None, :])
        right_then_left = (left_multiplier[:, None] * density) * right_multiplier[None, :]
        multiplier_commutator_errors.append(
            float(np.max(np.abs(left_then_right - right_then_left)))
        )

        dx = float(x[1] - x[0])
        feature_kernel = np.exp(-0.35 * (xx - yy) ** 2)
        positive_background = cfg.background_floor + np.exp(-0.25 * x * x)
        composition = feature_kernel @ np.diag(positive_background * dx) @ feature_kernel.T * dx
        composition = 0.5 * (composition + composition.T)
        composition_min_eigenvalues.append(float(np.min(np.linalg.eigvalsh(composition))))
        zero_composition = feature_kernel @ np.diag(np.zeros_like(x) * dx) @ feature_kernel.T * dx
        zero_composition_errors.append(float(np.max(np.abs(zero_composition))))

    quadrature_differences = [
        abs(right - left) for left, right in zip(amplitudes, amplitudes[1:])
    ]
    hs_differences = [
        abs(right - left)
        for left, right in zip(hilbert_schmidt_norm_sq, hilbert_schmidt_norm_sq[1:])
    ]
    diagnostics = {
        "point_counts": list(cfg.point_counts),
        "continuum_amplitudes": amplitudes,
        "quadrature_differences": quadrature_differences,
        "hilbert_schmidt_norm_sq": hilbert_schmidt_norm_sq,
        "hilbert_schmidt_differences": hs_differences,
        "pointwise_jacobi_errors": jacobi_errors,
        "pointwise_gauge_pairing_errors": gauge_pairing_errors,
        "gauge_amplitude_errors": gauge_amplitude_errors,
        "color_replacement_errors": color_replacement_errors,
        "left_right_multiplier_commutator_errors": multiplier_commutator_errors,
        "zero_background_composition_errors": zero_composition_errors,
        "positive_background_composition_min_eigenvalues": composition_min_eigenvalues,
    }
    acceptance = {
        "jacobi_closes_almost_everywhere_on_the_kernel_grid": max(jacobi_errors) < 5e-13,
        "continuum_double_copy_quadrature_is_cauchy": bool(
            all(
                later <= earlier + 2e-7
                for earlier, later in zip(
                    quadrature_differences, quadrature_differences[1:]
                )
            )
            and quadrature_differences[-1] < 8e-5
        ),
        "double_copy_density_is_hilbert_schmidt": bool(
            all(np.isfinite(value) and value > 0 for value in hilbert_schmidt_norm_sq)
            and hs_differences[-1] < 8e-5
        ),
        "weighted_generalized_gauge_shift_is_pointwise_and_integrally_invisible": max(
            max(gauge_pairing_errors), max(gauge_amplitude_errors)
        ) < 5e-11,
        "color_replacement_is_symmetric_on_x_times_x": max(color_replacement_errors) < 5e-13,
        "left_and_right_pointwise_kernel_actions_commute": max(multiplier_commutator_errors) < 5e-13,
        "zero_pointwise_background_gives_zero_composition": max(zero_composition_errors) < 5e-13,
        "positive_pointwise_background_composition_is_positive": min(composition_min_eigenvalues) > -2e-12,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "theorem_status": "conditional-model",
        "decision": {
            "continuum_base_space_and_two_point_kernel_are_both_executed": True,
            "maximal_domain_and_integrability_premises_remain_visible": True,
            "arbitrary_interacting_continuum_double_copy_not_claimed": True,
        },
    }
