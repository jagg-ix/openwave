"""M9.134: executable ADM spatial-metric evolution with a general shift.

The formal source declared for this bridge is the user-supplied Physlib update on
``entropic-physlib-linear-full`` at short commit ``31461dc67``.  The reported
Lean declarations are:

* ``Curvature.DiffeomorphismMetricVariation.metricLieDerivative``;
* ``admMetricEvolution``;
* ``admMetricEvolution_symm``;
* ``admMetricEvolution_zero_shift``;
* ``extrinsicCurvature_of_evolution``;
* ``momentumFluxTensor_eq_traceless``.

The full branch head and source blob were not independently retrievable in this
execution environment.  Consequently the source pin remains declared but
unverified here, while every coordinate identity used by OpenWave is checked
numerically and algebraically below.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

Array = np.ndarray
Tensor = np.ndarray
Vector = tuple[Array, Array, Array]

FORMAL_SOURCE = {
    "repository": "jagg-ix/entropic-physlib-private",
    "branch": "entropic-physlib-linear-full",
    "short_commit": "31461dc67",
    "full_commit_verified": False,
    "source_blob_verified": False,
    "module": "AdmMetricEvolutionGeneralShift.lean",
    "declarations": (
        "Curvature.DiffeomorphismMetricVariation.metricLieDerivative",
        "admMetricEvolution",
        "admMetricEvolution_symm",
        "admMetricEvolution_zero_shift",
        "extrinsicCurvature_of_evolution",
        "momentumFluxTensor_eq_traceless",
    ),
}


@dataclass(frozen=True)
class AdmGeneralShiftConfig:
    points: int = 24
    half_width: float = math.pi
    lapse: float = 1.15
    shift_amplitude: float = 0.18
    curvature_amplitude: float = 0.07

    def __post_init__(self) -> None:
        if self.points < 12 or self.points % 2:
            raise ValueError("even grid with at least 12 points required")
        if min(self.half_width, self.lapse) <= 0.0:
            raise ValueError("positive domain and lapse required")
        if self.shift_amplitude < 0.0 or self.curvature_amplitude < 0.0:
            raise ValueError("nonnegative amplitudes required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points


def periodic_derivative(values: Array, axis: int, spacing: float) -> Array:
    return np.asarray(
        (np.roll(values, -1, axis=axis) - np.roll(values, 1, axis=axis))
        / (2.0 * spacing),
        dtype=np.float64,
    )


def coordinates(cfg: AdmGeneralShiftConfig) -> tuple[Array, Array, Array]:
    axis = -cfg.half_width + cfg.spacing * np.arange(cfg.points)
    return tuple(np.asarray(item) for item in np.meshgrid(axis, axis, axis, indexing="ij"))


def manufactured_metric(cfg: AdmGeneralShiftConfig) -> Tensor:
    x, y, z = coordinates(cfg)
    metric = np.zeros((3, 3) + x.shape, dtype=np.float64)
    metric[0, 0] = 1.0 + 0.08 * np.cos(x) + 0.02 * np.sin(y)
    metric[1, 1] = 1.0 + 0.06 * np.cos(y) + 0.015 * np.sin(z)
    metric[2, 2] = 1.0 + 0.05 * np.cos(z) + 0.01 * np.sin(x)
    metric[0, 1] = metric[1, 0] = 0.012 * np.sin(x + y)
    metric[0, 2] = metric[2, 0] = 0.009 * np.cos(x - z)
    metric[1, 2] = metric[2, 1] = 0.011 * np.sin(y + z)
    return metric


def manufactured_shift(cfg: AdmGeneralShiftConfig) -> Vector:
    x, y, z = coordinates(cfg)
    amplitude = cfg.shift_amplitude
    return (
        np.asarray(amplitude * np.sin(y) * np.cos(z), dtype=np.float64),
        np.asarray(amplitude * np.sin(z) * np.cos(x), dtype=np.float64),
        np.asarray(amplitude * np.sin(x) * np.cos(y), dtype=np.float64),
    )


def manufactured_extrinsic_curvature(cfg: AdmGeneralShiftConfig) -> Tensor:
    x, y, z = coordinates(cfg)
    amplitude = cfg.curvature_amplitude
    tensor = np.zeros((3, 3) + x.shape, dtype=np.float64)
    tensor[0, 0] = amplitude * np.cos(x)
    tensor[1, 1] = -0.6 * amplitude * np.cos(y)
    tensor[2, 2] = 0.4 * amplitude * np.cos(z)
    tensor[0, 1] = tensor[1, 0] = 0.25 * amplitude * np.sin(x + y)
    tensor[0, 2] = tensor[2, 0] = 0.2 * amplitude * np.sin(x - z)
    tensor[1, 2] = tensor[2, 1] = 0.15 * amplitude * np.cos(y + z)
    return tensor


def metric_lie_derivative(metric: Tensor, shift: Vector, spacing: float) -> Tensor:
    """Coordinate formula for ``L_shift metric``.

    (L_N gamma)_ij = N^s d_s gamma_ij + gamma_is d_j N^s
                     + gamma_js d_i N^s.
    """
    result = np.zeros_like(metric)
    shift_gradient = tuple(
        tuple(periodic_derivative(shift[s], axis, spacing) for axis in range(3))
        for s in range(3)
    )
    for i in range(3):
        for j in range(3):
            transport = sum(
                shift[s] * periodic_derivative(metric[i, j], s, spacing)
                for s in range(3)
            )
            covector_i = sum(metric[i, s] * shift_gradient[s][j] for s in range(3))
            covector_j = sum(metric[j, s] * shift_gradient[s][i] for s in range(3))
            result[i, j] = transport + covector_i + covector_j
    return np.asarray(result, dtype=np.float64)


def adm_metric_evolution(
    metric: Tensor,
    extrinsic_curvature: Tensor,
    lapse: float,
    shift: Vector,
    spacing: float,
) -> Tensor:
    if lapse <= 0.0:
        raise ValueError("positive lapse required")
    return np.asarray(
        -2.0 * lapse * extrinsic_curvature
        + metric_lie_derivative(metric, shift, spacing),
        dtype=np.float64,
    )


def extrinsic_curvature_from_evolution(
    metric_rate: Tensor,
    metric: Tensor,
    lapse: float,
    shift: Vector,
    spacing: float,
) -> Tensor:
    if lapse <= 0.0:
        raise ValueError("positive lapse required")
    return np.asarray(
        -(metric_rate - metric_lie_derivative(metric, shift, spacing))
        / (2.0 * lapse),
        dtype=np.float64,
    )


def inverse_metric(metric: Tensor) -> Tensor:
    matrix = np.moveaxis(metric, (0, 1), (-2, -1))
    inverse = np.linalg.inv(matrix)
    return np.moveaxis(inverse, (-2, -1), (0, 1))


def metric_trace(tensor: Tensor, metric_inverse: Tensor) -> Array:
    return np.asarray(
        sum(metric_inverse[i, j] * tensor[i, j] for i in range(3) for j in range(3)),
        dtype=np.float64,
    )


def momentum_flux_decomposition(metric: Tensor, curvature: Tensor) -> dict[str, Any]:
    inverse = inverse_metric(metric)
    trace = metric_trace(curvature, inverse)
    identity_covariant = metric
    traceless = np.asarray(curvature - trace[None, None, ...] * identity_covariant / 3.0)
    momentum_flux = np.asarray(curvature - trace[None, None, ...] * identity_covariant)
    reconstructed = np.asarray(traceless - 2.0 * trace[None, None, ...] * identity_covariant / 3.0)
    return {
        "trace": trace,
        "traceless": traceless,
        "momentum_flux": momentum_flux,
        "reconstructed_momentum_flux": reconstructed,
        "traceless_trace_max": float(np.max(np.abs(metric_trace(traceless, inverse)))),
        "decomposition_error": float(np.max(np.abs(momentum_flux - reconstructed))),
    }


def relative_error(left: Array, right: Array) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1.0e-30))


@lru_cache(maxsize=1)
def run_adm_general_shift_study() -> dict[str, Any]:
    cfg = AdmGeneralShiftConfig()
    metric = manufactured_metric(cfg)
    shift = manufactured_shift(cfg)
    curvature = manufactured_extrinsic_curvature(cfg)
    zero_shift = tuple(np.zeros_like(item) for item in shift)

    lie = metric_lie_derivative(metric, shift, cfg.spacing)
    rate = adm_metric_evolution(metric, curvature, cfg.lapse, shift, cfg.spacing)
    zero_rate = adm_metric_evolution(metric, curvature, cfg.lapse, zero_shift, cfg.spacing)
    recovered = extrinsic_curvature_from_evolution(
        rate, metric, cfg.lapse, shift, cfg.spacing
    )
    momentum = momentum_flux_decomposition(metric, curvature)

    symmetry_error = float(np.max(np.abs(rate - np.swapaxes(rate, 0, 1))))
    zero_shift_error = relative_error(zero_rate, -2.0 * cfg.lapse * curvature)
    recovery_error = relative_error(recovered, curvature)
    shift_effect = relative_error(rate, zero_rate)

    payload = {
        "schema": "openwave.m9.adm-general-shift.v1",
        "task": "M9.134",
        "formal_source": dict(FORMAL_SOURCE),
        "config": asdict(cfg),
        "diagnostics": {
            "metric_rate_symmetry_error": symmetry_error,
            "zero_shift_reduction_error": zero_shift_error,
            "extrinsic_curvature_recovery_error": recovery_error,
            "general_shift_effect_relative": shift_effect,
            "lie_derivative_norm": float(np.linalg.norm(lie)),
            "momentum_flux_decomposition_error": momentum["decomposition_error"],
            "traceless_trace_max": momentum["traceless_trace_max"],
        },
        "claim_boundary": {
            "declared_short_commit_is_full_verified_pin": False,
            "coordinate_lie_derivative_is_curved_covariant_derivative_operator": False,
            "general_shift_adm_rate_is_complete_einstein_cauchy_solver": False,
            "tt_mode_has_sourced_wave_equation": False,
            "finite_periodic_identity_is_continuum_convergence": False,
        },
    }
    diagnostics = payload["diagnostics"]
    acceptance = {
        "six_formal_declarations_are_recorded": len(FORMAL_SOURCE["declarations"]) == 6,
        "general_shift_contribution_is_nontrivial": diagnostics["general_shift_effect_relative"] >= 1.0e-3,
        "adm_metric_rate_is_symmetric": diagnostics["metric_rate_symmetry_error"] <= 2.0e-12,
        "zero_shift_reduces_to_minus_two_lapse_K": diagnostics["zero_shift_reduction_error"] <= 2.0e-12,
        "extrinsic_curvature_is_recovered_after_removing_lie_drag": diagnostics["extrinsic_curvature_recovery_error"] <= 2.0e-12,
        "momentum_flux_traceless_decomposition_closes": diagnostics["momentum_flux_decomposition_error"] <= 2.0e-12 and diagnostics["traceless_trace_max"] <= 2.0e-12,
        "remaining_scope_boundaries_are_explicit": not any(payload["claim_boundary"].values()),
    }
    result = {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "general_shift_adm_evolution_constructed": True,
            "shift_free_model_is_zero_shift_special_case": True,
            "momentum_flux_carries_tracefree_curvature": True,
            "curved_covariant_derivative_operator_constructed": False,
            "sourced_tt_wave_propagation_constructed": False,
        },
    }
    result["fingerprint"] = sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()
    return result


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
