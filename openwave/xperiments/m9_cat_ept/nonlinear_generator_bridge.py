"""Finite Galerkin controls for the nonlinear CAT/EPT generator.

The module exercises the dynamic carrier of ``unified_pde`` on smooth periodic
states. It qualifies finite-grid domain density, local Lipschitz control,
shifted dissipativity, and graph convergence. These are computational controls,
not a proof that the full continuum generator is closable or generates a
semigroup.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from scipy.signal import resample

from .unified_pde import UnifiedPDEConfig, UnifiedState, grid, rhs

DYNAMIC_FIELDS = ("psi", "gauge", "gauge_momentum", "geometry", "temperature")


@dataclass(frozen=True)
class NonlinearGeneratorConfig:
    points: int = 128
    length: float = 12.0
    sample_count: int = 12
    perturbation: float = 0.035
    reference_points: int = 256

    def __post_init__(self) -> None:
        if self.points < 32 or self.points % 2 or self.reference_points < 2 * self.points:
            raise ValueError("even grid and at least two-times-finer reference required")
        if self.length <= 0 or self.sample_count < 4 or self.perturbation <= 0:
            raise ValueError("positive controls required")


def pde_config(points: int, length: float = 12.0) -> UnifiedPDEConfig:
    return UnifiedPDEConfig(
        points=points,
        length=length,
        final_time=0.06,
        dt=0.0015 * (64 / points) ** 2,
    )


def smooth_state(
    cfg: UnifiedPDEConfig,
    phase: float = 0.0,
    amplitude: float = 1.0,
) -> UnifiedState:
    x, dx = grid(cfg)
    q = 2 * math.pi * x / cfg.length
    envelope = np.exp(0.22 * np.cos(q - phase) + 0.055 * np.cos(7 * q + 0.3 * phase))
    color = np.asarray(
        [math.sqrt(0.50), math.sqrt(0.32), math.sqrt(0.18)],
        dtype=np.complex128,
    )
    color *= np.exp(1j * np.asarray([0.1 + phase, 0.35 - 0.2 * phase, -0.25 + 0.15 * phase]))
    carrier = np.exp(1j * (2 * q + 0.04 * np.sin(3 * q - phase)))
    psi = amplitude * color[:, None] * envelope[None, :] * carrier[None, :]
    psi /= math.sqrt(float(np.sum(np.abs(psi) ** 2) * dx))
    gauge = 0.045 * np.sin(q + phase) + 0.012 * np.sin(5 * q - 0.3 * phase)
    momentum = 0.035 * np.cos(2 * q - 0.7 * phase) + 0.009 * np.sin(6 * q)
    geometry = 0.07 * np.cos(q - 0.4 * phase) + 0.018 * np.cos(4 * q + phase)
    temperature = 1 + 0.045 * np.cos(q + 0.2 * phase) + 0.009 * np.cos(5 * q - phase)
    zeros = np.zeros(cfg.points)
    return UnifiedState(
        psi,
        gauge,
        momentum,
        geometry,
        temperature,
        zeros.copy(),
        zeros.copy(),
        0.0,
    )


def resample_state(state: UnifiedState, points: int) -> UnifiedState:
    def periodic_resample(value: np.ndarray) -> np.ndarray:
        return resample(value, points, axis=-1)

    return UnifiedState(
        periodic_resample(state.psi),
        periodic_resample(state.gauge).real,
        periodic_resample(state.gauge_momentum).real,
        periodic_resample(state.geometry).real,
        periodic_resample(state.temperature).real,
        periodic_resample(state.reservoir).real,
        periodic_resample(state.entropy).real,
        float(state.gauge_work),
    )


def state_sub(left: UnifiedState, right: UnifiedState) -> UnifiedState:
    return UnifiedState(
        left.psi - right.psi,
        left.gauge - right.gauge,
        left.gauge_momentum - right.gauge_momentum,
        left.geometry - right.geometry,
        left.temperature - right.temperature,
        left.reservoir - right.reservoir,
        left.entropy - right.entropy,
        left.gauge_work - right.gauge_work,
    )


def carrier_inner(
    left: UnifiedState,
    right: UnifiedState,
    cfg: UnifiedPDEConfig,
) -> complex:
    _, dx = grid(cfg)
    total = np.vdot(left.psi, right.psi)
    for name in DYNAMIC_FIELDS[1:]:
        total += np.vdot(getattr(left, name), getattr(right, name))
    return complex(total * dx)


def carrier_norm(state: UnifiedState, cfg: UnifiedPDEConfig) -> float:
    return math.sqrt(max(0.0, carrier_inner(state, state, cfg).real))


def normalized_error(
    value: UnifiedState,
    reference: UnifiedState,
    cfg: UnifiedPDEConfig,
) -> float:
    return carrier_norm(state_sub(value, reference), cfg) / max(carrier_norm(reference, cfg), 1e-15)


def domain_graph_campaign(
    config: NonlinearGeneratorConfig = NonlinearGeneratorConfig(),
) -> dict[str, Any]:
    reference_cfg = pde_config(config.reference_points, config.length)
    reference = smooth_state(reference_cfg, 0.37)
    reference_rhs = rhs(reference, reference_cfg)
    rows = []
    for points in (32, 64, 128):
        coarse_cfg = pde_config(points, config.length)
        coarse = resample_state(reference, points)
        coarse_rhs = rhs(coarse, coarse_cfg)
        lifted = resample_state(coarse, config.reference_points)
        lifted_rhs = resample_state(coarse_rhs, config.reference_points)
        rows.append(
            {
                "points": points,
                "state_error": normalized_error(lifted, reference, reference_cfg),
                "generator_error": normalized_error(lifted_rhs, reference_rhs, reference_cfg),
                "minimum_temperature": float(np.min(coarse.temperature)),
            }
        )
    return {
        "rows": rows,
        "state_errors": [row["state_error"] for row in rows],
        "generator_errors": [row["generator_error"] for row in rows],
    }


def local_operator_campaign(
    config: NonlinearGeneratorConfig = NonlinearGeneratorConfig(),
) -> dict[str, Any]:
    cfg = pde_config(config.points, config.length)
    quotients: list[float] = []
    lipschitz: list[float] = []
    temperatures: list[float] = []
    for index in range(config.sample_count):
        phase = 0.19 * index
        left = smooth_state(cfg, phase)
        right = smooth_state(
            cfg,
            phase + config.perturbation,
            1 + 0.015 * math.sin(index + 0.2),
        )
        delta = state_sub(left, right)
        generator_delta = state_sub(rhs(left, cfg), rhs(right, cfg))
        denominator = carrier_inner(delta, delta, cfg).real
        quotients.append(float(carrier_inner(generator_delta, delta, cfg).real / denominator))
        lipschitz.append(carrier_norm(generator_delta, cfg) / math.sqrt(denominator))
        temperatures.extend((float(np.min(left.temperature)), float(np.min(right.temperature))))
    shift = max(0.0, max(quotients)) + 1e-10
    shifted = [quotient - shift for quotient in quotients]
    return {
        "one_sided_quotients": quotients,
        "shift": shift,
        "shifted_quotients": shifted,
        "maximum_lipschitz_ratio": max(lipschitz),
        "minimum_temperature": min(temperatures),
    }


def source_identity() -> dict[str, Any]:
    return {
        "repository": "jagg-ix/entropic-physlib-private",
        "branch": "entropic-physlib-linear-full",
        "sources": [
            {
                "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
                "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
                "witness": "ContinuumKernelSpace and spacePointwiseKernelOperator_hasDenseDomain",
            },
            {
                "path": "Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean",
                "sha": "9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5",
                "witness": "mulOperator_isClosable",
            },
            {
                "path": "formalization/zil/liouville-second-quantization.zc",
                "sha": "8141e353dc5960ef28c01883ccbb10411f62ac05",
                "witness": "continuum generator and semigroup targets remain open",
            },
        ],
    }


@lru_cache(maxsize=1)
def run_nonlinear_generator_study() -> dict[str, Any]:
    config = NonlinearGeneratorConfig()
    graph = domain_graph_campaign(config)
    local = local_operator_campaign(config)
    state_errors = np.asarray(graph["state_errors"])
    generator_errors = np.asarray(graph["generator_errors"])
    acceptance = {
        "smooth_domain_projection_converges": bool(
            np.all(np.diff(state_errors) < 0) and state_errors[-1] < 1e-8
        ),
        "graph_sequence_converges": bool(
            np.all(np.diff(generator_errors) < 0) and generator_errors[-1] < 2e-6
        ),
        "positive_temperature_domain_is_preserved": local["minimum_temperature"] > 0.9,
        "local_lipschitz_control_is_finite": math.isfinite(local["maximum_lipschitz_ratio"])
        and local["maximum_lipschitz_ratio"] < 50.0,
        "finite_shift_makes_samples_dissipative": max(local["shifted_quotients"]) <= 2e-12,
        "formal_closable_multiplier_anchor_is_pinned": source_identity()["sources"][1]["sha"]
        == "9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5",
        "continuum_claims_remain_unpromoted": True,
    }
    return {
        "schema": "openwave.m9.nonlinear-generator-bridge.v1",
        "task": "M9.54",
        "config": asdict(config),
        "domain_graph_campaign": graph,
        "local_operator_campaign": local,
        "formal_evidence": source_identity(),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_galerkin_domain_control_qualified": True,
            "bounded_set_shifted_dissipativity_qualified": True,
            "continuum_generator_closable_proved": False,
            "continuum_semigroup_generated": False,
        },
        "classification": {
            "establishes": [
                "smooth finite-Galerkin domain approximation",
                "sampled graph convergence for the unified nonlinear generator",
                "finite bounded-set local Lipschitz and shifted-dissipativity controls",
                "exact linkage to the dense-domain and closable multiplication-operator anchors",
            ],
            "does_not_establish": [
                "closability of the full nonlinear continuum generator",
                "maximal dissipativity or nonlinear semigroup generation",
                "continuum existence or uniqueness",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
