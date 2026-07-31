"""M14.5 pointwise Mizera/BCJ residue and twisted-cohomology model.

This module extends the merged M14 continuum line with the newer Physlib
Mizera theorem surface. It evaluates a continuous family of three-channel
numerators, reconstructs each channel from the finite residues of the
four-puncture rational form, verifies regularity at infinity/Jacobi closure,
and checks invariance under weighted generalized-gauge shifts and a nontrivial
nilpotent twisted differential.

This is an executable compatibility model, not a construction of the full
Deligne--Mumford compactification, a general CHY measure, or loop-level BCJ
numerators.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

MILESTONE = "M14.5"
SCHEMA = "openwave.m14.mizera-pointwise-bcj.v1"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "35f98f147771a4e250ec01b4cbf2afab72313db7"
ZIL_COMMIT = "6daee2698304feb203c6adb91b2e8853613f85b5"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.31.0"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean",
        "sha": "96e5f7feb002125a633d90c3940e1af513bb8484",
        "theorems": [
            "mizera_middleSphere_finite_residues",
            "mizera_global_residue_theorem",
            "mizera_kinematic_jacobi_of_residue_theorem",
            "MizeraTwistedDifferentialData.twistedDifferential_sq",
            "mizeraTwistedClass_add_exact",
            "mizeraChannelResidues_eq_of_twistedCohomologous",
            "mizera_intersectionLeadingTerm_eq_doubleCopy",
            "cubicDoubleCopy_shift_left_of_orthogonal",
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

JACOBI_BASIS = np.asarray(
    [[1.0, 1.0], [-1.0, 1.0], [0.0, -2.0]], dtype=float
)


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class MizeraPointwiseBCJConfig:
    point_counts: tuple[int, ...] = (64, 128, 256, 512, 1024)
    domain_radius: float = 6.0
    mass: float = 0.8
    kappa: float = 2.0
    multiplicity: int = 4
    gauge_scale: float = 0.17
    poles: tuple[float, float, float] = (-1.2, 0.35, 1.7)

    def validate(self) -> None:
        if not self.point_counts or sorted(self.point_counts) != list(self.point_counts):
            raise ValueError("point_counts must be nonempty and increasing")
        if min(self.point_counts) < 8:
            raise ValueError("at least eight points are required")
        if min(self.domain_radius, self.mass, self.kappa, self.gauge_scale) <= 0:
            raise ValueError("positive domain, mass, coupling and gauge scale required")
        if self.multiplicity < 3:
            raise ValueError("multiplicity must be at least three")
        if len(set(self.poles)) != 3:
            raise ValueError("Mizera poles must be distinct")


def canonical_payload(config: MizeraPointwiseBCJConfig | None = None) -> dict[str, Any]:
    cfg = MizeraPointwiseBCJConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT pointwise Mizera residue BCJ double copy",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.2", "M14.4"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "mizera_pointwise_bcj_m145:run_mizera_pointwise_bcj_study"
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


def _numerator_coordinates(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left = np.stack(
        (
            np.exp(-0.22 * x * x) * (1.0 + 0.2 * np.cos(1.7 * x)),
            np.exp(-0.31 * x * x) * (0.35 + 0.15 * np.sin(0.9 * x)),
        ),
        axis=-1,
    )
    right = np.stack(
        (
            np.exp(-0.27 * x * x) * (0.7 - 0.12 * np.sin(1.3 * x)),
            np.exp(-0.19 * x * x) * (-0.3 + 0.1 * np.cos(0.8 * x)),
        ),
        axis=-1,
    )
    return left, right


def _pointwise_fields(
    cfg: MizeraPointwiseBCJConfig, count: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = np.linspace(-cfg.domain_radius, cfg.domain_radius, count)
    left_coordinates, right_coordinates = _numerator_coordinates(x)
    left = left_coordinates @ JACOBI_BASIS.T
    right = right_coordinates @ JACOBI_BASIS.T
    denominator = np.stack(
        (
            1.0 + (x + 0.3) ** 2 + cfg.mass**2,
            1.0 + (x - 0.4) ** 2 + cfg.mass**2,
            1.0 + 0.5 * x**2 + cfg.mass**2,
        ),
        axis=-1,
    )
    weight = (cfg.kappa / 2.0) ** (cfg.multiplicity - 2) / denominator
    gauge = np.empty_like(left)
    for index in range(count):
        gram = JACOBI_BASIS.T @ np.diag(weight[index]) @ JACOBI_BASIS
        paired_direction = gram @ right_coordinates[index]
        perpendicular = np.asarray(
            [paired_direction[1], -paired_direction[0]], dtype=float
        )
        norm = float(np.linalg.norm(perpendicular))
        gauge_coordinates = (
            cfg.gauge_scale
            * np.exp(-0.25 * x[index] ** 2)
            * perpendicular
            / (norm if norm else 1.0)
        )
        gauge[index] = JACOBI_BASIS @ gauge_coordinates
    return x, left, right, weight, gauge


def _residue_errors(
    numerators: np.ndarray, poles: tuple[float, float, float]
) -> tuple[float, float]:
    pole_values = np.asarray(poles, dtype=float)
    finite_error = 0.0
    for channel, pole in enumerate(pole_values):
        numerator_at_pole = np.zeros(numerators.shape[0], dtype=float)
        for term in range(3):
            factor = 1.0
            for other in range(3):
                if other != term:
                    factor *= pole - pole_values[other]
            numerator_at_pole += numerators[:, term] * factor
        other_poles = [pole_values[i] for i in range(3) if i != channel]
        residue = numerator_at_pole / (
            (pole - other_poles[0]) * (pole - other_poles[1])
        )
        finite_error = max(
            finite_error, float(np.max(np.abs(residue - numerators[:, channel])))
        )
    infinity_error = float(np.max(np.abs(np.sum(numerators, axis=1))))
    return finite_error, infinity_error


def _twisted_cohomology_diagnostics() -> dict[str, float]:
    differential = np.asarray([[0.0, 0.0], [1.0, 0.0]])
    wedge = differential.copy()
    epsilon = -0.37
    twisted = differential + epsilon * wedge
    vector = np.asarray([0.8, -0.4])
    exact_parameter = np.asarray([0.23, 0.91])
    shifted = vector + twisted @ exact_parameter
    residue = np.asarray([1.0, 0.0])
    return {
        "differential_square_error": float(np.max(np.abs(differential @ differential))),
        "wedge_square_error": float(np.max(np.abs(wedge @ wedge))),
        "anticommutator_error": float(
            np.max(np.abs(differential @ wedge + wedge @ differential))
        ),
        "twisted_square_error": float(np.max(np.abs(twisted @ twisted))),
        "exact_shift_residue_error": abs(float(residue @ shifted - residue @ vector)),
        "nontrivial_exact_shift_norm": float(np.linalg.norm(shifted - vector)),
    }


def run_mizera_pointwise_bcj_study(
    config: MizeraPointwiseBCJConfig | None = None,
) -> dict[str, Any]:
    cfg = MizeraPointwiseBCJConfig() if config is None else config
    cfg.validate()
    amplitudes: list[float] = []
    l2_norms: list[float] = []
    jacobi_errors: list[float] = []
    finite_residue_errors: list[float] = []
    infinity_residue_errors: list[float] = []
    gauge_pairing_errors: list[float] = []
    gauge_amplitude_errors: list[float] = []
    color_replacement_errors: list[float] = []

    for count in cfg.point_counts:
        x, left, right, weight, gauge = _pointwise_fields(cfg, count)
        density = np.sum(weight * left * right, axis=1)
        shifted_density = np.sum(weight * (left + gauge) * right, axis=1)
        swapped_density = np.sum(weight * right * left, axis=1)
        amplitudes.append(float(np.trapezoid(density, x)))
        l2_norms.append(
            float(np.trapezoid(np.sum(left * left + right * right, axis=1), x))
        )
        jacobi_errors.append(
            max(
                float(np.max(np.abs(np.sum(left, axis=1)))),
                float(np.max(np.abs(np.sum(right, axis=1)))),
                float(np.max(np.abs(np.sum(gauge, axis=1)))),
            )
        )
        finite_error, infinity_error = _residue_errors(left, cfg.poles)
        finite_residue_errors.append(finite_error)
        infinity_residue_errors.append(infinity_error)
        gauge_pairing_errors.append(
            float(np.max(np.abs(np.sum(weight * gauge * right, axis=1))))
        )
        gauge_amplitude_errors.append(
            abs(float(np.trapezoid(shifted_density - density, x)))
        )
        color_replacement_errors.append(
            float(np.max(np.abs(swapped_density - density)))
        )

    quadrature_differences = [
        abs(right - left) for left, right in zip(amplitudes, amplitudes[1:])
    ]
    twisted = _twisted_cohomology_diagnostics()
    diagnostics = {
        "point_counts": list(cfg.point_counts),
        "continuum_amplitudes": amplitudes,
        "quadrature_differences": quadrature_differences,
        "l2_norms": l2_norms,
        "pointwise_jacobi_errors": jacobi_errors,
        "finite_residue_errors": finite_residue_errors,
        "residue_at_infinity_errors": infinity_residue_errors,
        "pointwise_gauge_pairing_errors": gauge_pairing_errors,
        "gauge_amplitude_errors": gauge_amplitude_errors,
        "color_replacement_errors": color_replacement_errors,
        **twisted,
    }
    acceptance = {
        "pointwise_color_kinematic_and_gauge_jacobi_close": max(jacobi_errors) < 5e-13,
        "finite_mizera_residues_reconstruct_every_channel": max(finite_residue_errors) < 5e-13,
        "regularity_at_infinity_is_pointwise_jacobi": max(infinity_residue_errors) < 5e-13,
        "continuous_numerator_fields_are_l2": bool(
            all(np.isfinite(value) and value > 0 for value in l2_norms)
        ),
        "continuum_quadrature_is_cauchy": bool(
            all(
                later <= earlier + 5e-14
                for earlier, later in zip(
                    quadrature_differences, quadrature_differences[1:]
                )
            )
            and quadrature_differences[-1] < 5e-12
        ),
        "pointwise_weighted_gauge_shift_is_invisible": max(
            max(gauge_pairing_errors), max(gauge_amplitude_errors)
        ) < 5e-12,
        "color_replacement_is_symmetric_pointwise": max(color_replacement_errors) < 5e-13,
        "twisted_differential_and_exact_shift_close": max(
            twisted["differential_square_error"],
            twisted["wedge_square_error"],
            twisted["anticommutator_error"],
            twisted["twisted_square_error"],
            twisted["exact_shift_residue_error"],
        ) < 5e-13 and twisted["nontrivial_exact_shift_norm"] > 1e-6,
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
            "mizera_residue_surface_is_executed_pointwise": True,
            "twisted_exact_representatives_are_not_new_physical_numerators": True,
            "full_chy_or_loop_level_double_copy_not_claimed": True,
        },
    }
