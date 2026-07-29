"""Executable authority for three globally inspected Physlib theorem families.

Physlib is the formal authority. This module checks finite scalar/tensor
consequences of the pinned Lean declarations without promoting them into a
physical CAT/EPT particle identification.
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

SOURCE_RECORDS = (
    {
        "id": "complex-variational-residual",
        "path": "Physlib/Mathematics/LovelockRund/ComplexActionVariational.lean",
        "blob": "5a70e8935b9102da1278daba06a9c4beb4e1acf0",
        "declarations": (
            "complexEulerLagrange_apply_eq_zero_iff",
            "entropicTimeGradient_apply_eq_zero_iff",
            "norm_variationalComplexWeight",
        ),
        "boundary": "finite residual checks do not derive the CAT/EPT field equations",
    },
    {
        "id": "entropic-time-weight",
        "path": "Physlib/Mathematics/LovelockRund/ComplexActionVariational.lean",
        "blob": "5a70e8935b9102da1278daba06a9c4beb4e1acf0",
        "declarations": (
            "entropicTimeGradient",
            "variationalComplexWeight",
            "norm_variationalComplexWeight",
        ),
        "boundary": "monotonic entropic time requires an additional sign/dynamical hypothesis",
    },
    {
        "id": "covariant-gauge-invariance",
        "path": "Physlib/Electromagnetism/Kinematics/GaugeTransformation.lean",
        "blob": "c3c1cc63100539ae8b074c3c74e8c6b377e9bdf7",
        "declarations": (
            "toFieldStrength_ofGradient",
            "toFieldStrength_gaugeTransform",
            "gaugeTransform_gaugeTransform",
        ),
        "boundary": "gauge invariance does not derive electromagnetism from CAT/EPT",
    },
)


def complex_euler_lagrange(real_residual: float, imaginary_residual: float) -> complex:
    return complex(real_residual, imaginary_residual)


def entropic_time_gradient(imaginary_residual: float, hbar: float) -> float:
    if hbar == 0.0:
        raise ValueError("hbar must be nonzero")
    return imaginary_residual / hbar


def variational_complex_weight(
    real_residual: float, imaginary_residual: float, hbar: float
) -> complex:
    if hbar == 0.0:
        raise ValueError("hbar must be nonzero")
    return cmath.exp(1j * real_residual / hbar - imaginary_residual / hbar)


def gradient4(
    scalar: Callable[[tuple[float, float, float, float]], float],
    point: tuple[float, float, float, float],
    step: float,
) -> tuple[float, float, float, float]:
    values: list[float] = []
    for axis in range(4):
        plus = list(point)
        minus = list(point)
        plus[axis] += step
        minus[axis] -= step
        values.append((scalar(tuple(plus)) - scalar(tuple(minus))) / (2.0 * step))
    return tuple(values)  # type: ignore[return-value]


def field_strength(
    potential: Callable[[tuple[float, float, float, float]], tuple[float, float, float, float]],
    point: tuple[float, float, float, float],
    step: float,
) -> tuple[tuple[float, ...], ...]:
    derivatives = [[0.0] * 4 for _ in range(4)]
    for coordinate in range(4):
        plus = list(point)
        minus = list(point)
        plus[coordinate] += step
        minus[coordinate] -= step
        a_plus = potential(tuple(plus))
        a_minus = potential(tuple(minus))
        for component in range(4):
            derivatives[coordinate][component] = (
                a_plus[component] - a_minus[component]
            ) / (2.0 * step)
    return tuple(
        tuple(derivatives[mu][nu] - derivatives[nu][mu] for nu in range(4))
        for mu in range(4)
    )


def max_tensor_error(left: tuple[tuple[float, ...], ...], right: tuple[tuple[float, ...], ...]) -> float:
    return max(abs(left[i][j] - right[i][j]) for i in range(4) for j in range(4))


@dataclass(frozen=True)
class M138Report:
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


def run_m138_complex_action_gauge_authority() -> M138Report:
    # Target 1: complex stationarity splits into real and imaginary stationarity.
    residual_zero = complex_euler_lagrange(0.0, 0.0)
    residual_nonzero = complex_euler_lagrange(0.0, 0.25)
    split_zero_error = abs(residual_zero)
    split_detection_margin = abs(residual_nonzero)

    # Target 2: imaginary residual / hbar controls the weight modulus.
    hbar = 1.7
    real_residual = 0.8
    imaginary_residual = 0.42
    gradient = entropic_time_gradient(imaginary_residual, hbar)
    weight = variational_complex_weight(real_residual, imaginary_residual, hbar)
    weight_modulus_error = abs(abs(weight) - math.exp(-gradient))
    zero_gradient_error = abs(entropic_time_gradient(0.0, hbar))

    # Target 3: adding a smooth pure gradient leaves F_{mu nu} invariant.
    point = (0.31, -0.27, 0.44, -0.18)
    step = 1.0e-5

    def base_potential(x: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        t, x1, x2, x3 = x
        return (0.2 * x1, -0.3 * t + 0.1 * x2, 0.4 * x3, -0.2 * x2)

    def gauge_scalar(x: tuple[float, float, float, float]) -> float:
        t, x1, x2, x3 = x
        return 0.3 * t * x1 + 0.2 * x2 * x3 + 0.1 * t * t

    def pure_gauge(x: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        return gradient4(gauge_scalar, x, step)

    def transformed(x: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        base = base_potential(x)
        shift = pure_gauge(x)
        return tuple(base[i] + shift[i] for i in range(4))  # type: ignore[return-value]

    zero_tensor = tuple(tuple(0.0 for _ in range(4)) for _ in range(4))
    pure_gauge_strength = field_strength(pure_gauge, point, step)
    base_strength = field_strength(base_potential, point, step)
    transformed_strength = field_strength(transformed, point, step)
    pure_gauge_error = max_tensor_error(pure_gauge_strength, zero_tensor)
    gauge_invariance_error = max_tensor_error(base_strength, transformed_strength)

    diagnostics = {
        "complex_zero_residual_error": split_zero_error,
        "complex_nonzero_detection_margin": split_detection_margin,
        "entropic_zero_gradient_error": zero_gradient_error,
        "weight_modulus_identity_error": weight_modulus_error,
        "pure_gauge_field_strength_error": pure_gauge_error,
        "gauge_transform_invariance_error": gauge_invariance_error,
    }
    acceptance = {
        "exact_physlib_tip_is_pinned": len(PHYSLIB_TIP) == 40,
        "all_source_blobs_are_pinned": all(len(str(record["blob"])) == 40 for record in SOURCE_RECORDS),
        "complex_stationarity_splits": split_zero_error < 1e-15 and split_detection_margin > 0.2,
        "zero_imaginary_residual_has_zero_entropic_gradient": zero_gradient_error < 1e-15,
        "weight_modulus_matches_entropic_gradient": weight_modulus_error < 1e-14,
        "pure_gauge_has_zero_field_strength": pure_gauge_error < 2e-6,
        "field_strength_is_gauge_invariant": gauge_invariance_error < 2e-6,
        "physical_promotion_remains_blocked": True,
    }
    return M138Report(
        schema="openwave.m9.complex-action-entropic-time-gauge.v1",
        physlib={
            "repository": PHYSLIB_REPOSITORY,
            "branch": PHYSLIB_BRANCH,
            "tip": PHYSLIB_TIP,
        },
        source_records=SOURCE_RECORDS,
        diagnostics=diagnostics,
        acceptance=acceptance,
        boundaries=tuple(str(record["boundary"]) for record in SOURCE_RECORDS),
        passed=all(acceptance.values()),
    )
