"""Dimensionless geometry/metric back-reaction plugin.

A periodic matter-density contrast sources a scalar conformal metric potential.
The metric sector is the gradient flow of a screened weak-field functional,

    F[h] = 1/2 ∫ ((∂x h)^2 + m_g^2 h^2) dx - κ ∫ ρ_c h dx,

with exact spectral relaxation.  The plugin exposes matter-to-geometry sourcing,
constraint residuals, lapse/conformal observables, and proper-time probes.

This is a weak-field simulation interface.  It is not Einstein gravity.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class GeometryConfig:
    length: float = 20.0
    points: int = 256
    coupling: float = 0.35
    screening_mass: float = 0.8
    lapse_coupling: float = 0.6
    source_width: float = 1.1
    relaxation_time: float = 16.0
    samples: int = 81

    def __post_init__(self) -> None:
        if self.length <= 0 or self.points < 32 or self.points % 2:
            raise ValueError("positive length and even grid >=32 required")
        if self.coupling < 0 or self.screening_mass <= 0:
            raise ValueError("nonnegative coupling and positive screening mass required")
        if self.source_width <= 0 or self.relaxation_time <= 0 or self.samples < 2:
            raise ValueError("positive source/time parameters required")


def grid(cfg: GeometryConfig) -> tuple[RealArray, float]:
    dx = cfg.length / cfg.points
    x = (np.arange(cfg.points, dtype=np.float64) - cfg.points / 2) * dx
    return x, dx


def periodic_density(cfg: GeometryConfig, shift_cells: int = 0) -> RealArray:
    x, dx = grid(cfg)
    density = np.exp(-0.5 * (x / cfg.source_width) ** 2)
    density /= float(np.sum(density) * dx)
    return np.roll(density, shift_cells)


def density_contrast(density: RealArray) -> RealArray:
    values = np.asarray(density, dtype=np.float64)
    if values.ndim != 1 or values.size < 4:
        raise ValueError("one-dimensional density required")
    return values - float(np.mean(values))


def wave_numbers(cfg: GeometryConfig) -> RealArray:
    _x, dx = grid(cfg)
    return 2.0 * math.pi * np.fft.fftfreq(cfg.points, d=dx)


def source_to_metric(source: RealArray, cfg: GeometryConfig) -> RealArray:
    source = np.asarray(source, dtype=np.float64)
    if source.shape != (cfg.points,):
        raise ValueError("source shape does not match geometry grid")
    k = wave_numbers(cfg)
    denominator = k * k + cfg.screening_mass**2
    metric_hat = cfg.coupling * np.fft.fft(source) / denominator
    return np.fft.ifft(metric_hat).real


def screened_operator(metric: RealArray, cfg: GeometryConfig) -> RealArray:
    metric = np.asarray(metric, dtype=np.float64)
    k = wave_numbers(cfg)
    transformed = np.fft.fft(metric)
    return np.fft.ifft((k * k + cfg.screening_mass**2) * transformed).real


def constraint_residual(metric: RealArray, source: RealArray, cfg: GeometryConfig) -> RealArray:
    return screened_operator(metric, cfg) - cfg.coupling * source


def functional(metric: RealArray, source: RealArray, cfg: GeometryConfig) -> float:
    _x, dx = grid(cfg)
    k = wave_numbers(cfg)
    metric_hat = np.fft.fft(metric)
    gradient = np.fft.ifft(1j * k * metric_hat).real
    density = 0.5 * gradient * gradient + 0.5 * cfg.screening_mass**2 * metric * metric - cfg.coupling * source * metric
    return float(np.sum(density) * dx)


def relax_metric(source: RealArray, cfg: GeometryConfig = GeometryConfig(), initial: RealArray | None = None) -> dict[str, Any]:
    source = np.asarray(source, dtype=np.float64)
    target = source_to_metric(source, cfg)
    metric = np.zeros(cfg.points, dtype=np.float64) if initial is None else np.asarray(initial, dtype=np.float64).copy()
    if metric.shape != (cfg.points,):
        raise ValueError("initial metric shape mismatch")
    k = wave_numbers(cfg)
    rates = k * k + cfg.screening_mass**2
    target_hat = np.fft.fft(target)
    initial_hat = np.fft.fft(metric)
    times = np.linspace(0.0, cfg.relaxation_time, cfg.samples)
    records = []
    for time in times:
        metric_hat = target_hat + (initial_hat - target_hat) * np.exp(-rates * time)
        current = np.fft.ifft(metric_hat).real
        residual = constraint_residual(current, source, cfg)
        records.append({"time": float(time), "functional": functional(current, source, cfg), "constraint_l2": float(np.linalg.norm(residual) / math.sqrt(cfg.points)), "metric_l2_to_target": float(np.linalg.norm(current - target) / math.sqrt(cfg.points))})
    return {"target": target, "metric": current, "times": times, "records": records}


def metric_observables(metric: RealArray, cfg: GeometryConfig) -> dict[str, RealArray]:
    metric = np.asarray(metric, dtype=np.float64)
    return {"metric": metric, "lapse": np.exp(-cfg.lapse_coupling * metric), "conformal_scale": np.exp(metric)}


def proper_time(lapse: RealArray, coordinate_time: float, index: int) -> float:
    if coordinate_time < 0:
        raise ValueError("nonnegative coordinate time required")
    return coordinate_time * float(np.asarray(lapse)[index])


def resolution_study() -> dict[str, Any]:
    points = (64, 128, 256, 512)
    center_values, residuals = [], []
    for count in points:
        cfg = GeometryConfig(points=count)
        source = density_contrast(periodic_density(cfg))
        metric = source_to_metric(source, cfg)
        center_values.append(float(metric[count // 2]))
        residuals.append(float(np.linalg.norm(constraint_residual(metric, source, cfg)) / math.sqrt(count)))
    differences = [abs(center_values[i] - center_values[i + 1]) for i in range(len(center_values) - 1)]
    return {"points": points, "center_metric": center_values, "successive_differences": differences, "constraint_l2": residuals}


@lru_cache(maxsize=1)
def run_geometry_backreaction_study() -> dict[str, Any]:
    cfg = GeometryConfig()
    density = periodic_density(cfg)
    source = density_contrast(density)
    run = relax_metric(source, cfg)
    metric, target, records = run["metric"], run["target"], run["records"]
    observables = metric_observables(metric, cfg)
    functionals = np.asarray([row["functional"] for row in records])
    zero_cfg = GeometryConfig(coupling=0.0)
    zero_metric = source_to_metric(density_contrast(periodic_density(zero_cfg)), zero_cfg)
    half_cfg = GeometryConfig(coupling=0.5 * cfg.coupling)
    half_metric = source_to_metric(density_contrast(periodic_density(half_cfg)), half_cfg)
    shift = 19
    shifted_metric = source_to_metric(np.roll(source, shift), cfg)
    translation_error = float(np.max(np.abs(shifted_metric - np.roll(target, shift))))
    refinement = resolution_study()
    center, far, coordinate_time = cfg.points // 2, 0, 10.0
    center_tau = proper_time(observables["lapse"], coordinate_time, center)
    far_tau = proper_time(observables["lapse"], coordinate_time, far)
    acceptance = {
        "functional_is_nonincreasing": bool(np.all(np.diff(functionals) <= 2e-13)),
        "constraint_closes": records[-1]["constraint_l2"] <= 2e-5,
        "relaxation_reaches_spectral_target": records[-1]["metric_l2_to_target"] <= 2e-5,
        "zero_coupling_is_flat": float(np.max(np.abs(zero_metric))) <= 1e-15,
        "weak_field_is_linear_in_coupling": float(np.max(np.abs(half_metric - 0.5 * target))) <= 2e-14,
        "translation_covariance": translation_error <= 2e-14,
        "proper_time_probe_is_positive_and_nontrivial": center_tau > 0.0 and far_tau > 0.0 and abs(center_tau - far_tau) > 1e-4,
        "resolution_stabilizes": (max(refinement["successive_differences"]) <= 2e-13 or refinement["successive_differences"][-1] < refinement["successive_differences"][0]) and max(refinement["constraint_l2"]) <= 2e-13,
    }
    return {
        "schema": "openwave.m9.geometry-backreaction-result.v1", "task": "M9.34", "config": asdict(cfg),
        "source": {"integral": float(np.sum(density) * grid(cfg)[1]), "contrast_mean": float(np.mean(source))},
        "final": {"metric_min": float(np.min(metric)), "metric_max": float(np.max(metric)), "lapse_min": float(np.min(observables["lapse"])), "lapse_max": float(np.max(observables["lapse"])), "constraint_l2": records[-1]["constraint_l2"], "metric_l2_to_target": records[-1]["metric_l2_to_target"], "center_proper_time": center_tau, "far_proper_time": far_tau, "translation_error": translation_error},
        "resolution": refinement, "acceptance": acceptance, "passed": all(acceptance.values()),
        "classification": {"establishes": ["versioned matter-to-geometry source interface", "screened weak-field metric constraint", "energy-monotone metric relaxation", "lapse, conformal-scale, and proper-time probes", "zero-coupling, linearity, translation, and resolution controls"], "does_not_establish": ["Einstein field equations", "a tensor metric or gauge-complete gravity theory", "physical Newton coupling or units", "equivalence principle or gravitational radiation"]},
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
