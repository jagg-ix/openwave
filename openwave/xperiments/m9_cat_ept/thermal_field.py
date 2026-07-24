
"""Heat/thermal-field simulation criterion.

The reference sector solves the periodic heat equation

    d_t T = kappa d_x^2 T

with exact spectral evolution.  It records conserved total heat, decay of
temperature variance, Shannon entropy increase of the normalized positive
temperature profile, Fourier-mode decay, and the diffusion dissipation identity.

This is a dimensionless thermal-field control, not a microscopic derivation of
thermodynamics from CAT/EPT.
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
class ThermalConfig:
    length: float = 2.0 * math.pi
    points: int = 256
    diffusivity: float = 0.35
    final_time: float = 4.0
    samples: int = 101

    def __post_init__(self) -> None:
        if self.length <= 0 or self.points < 32 or self.points % 2:
            raise ValueError("positive length and even grid >=32 required")
        if self.diffusivity < 0:
            raise ValueError("nonnegative diffusivity required")
        if self.final_time <= 0 or self.samples < 2:
            raise ValueError("positive evolution interval required")


def grid(cfg: ThermalConfig) -> tuple[RealArray, float]:
    dx = cfg.length / cfg.points
    x = np.arange(cfg.points, dtype=np.float64) * dx
    return x, dx


def wave_numbers(cfg: ThermalConfig) -> RealArray:
    _x, dx = grid(cfg)
    return 2.0 * math.pi * np.fft.fftfreq(cfg.points, d=dx)


def initial_temperature(cfg: ThermalConfig = ThermalConfig()) -> RealArray:
    x, _dx = grid(cfg)
    temperature = (
        1.0
        + 0.35 * np.cos(x)
        + 0.15 * np.cos(2.0 * x + 0.3)
    )
    if float(np.min(temperature)) <= 0.0:
        raise RuntimeError("reference temperature must be positive")
    return temperature


def evolve_temperature(
    temperature0: RealArray,
    time: float,
    cfg: ThermalConfig = ThermalConfig(),
) -> RealArray:
    if time < 0:
        raise ValueError("nonnegative time required")
    temperature0 = np.asarray(temperature0, dtype=np.float64)
    if temperature0.shape != (cfg.points,):
        raise ValueError("temperature shape mismatch")
    k = wave_numbers(cfg)
    multiplier = np.exp(-cfg.diffusivity * k * k * time)
    return np.fft.ifft(np.fft.fft(temperature0) * multiplier).real


def total_heat(temperature: RealArray, cfg: ThermalConfig) -> float:
    _x, dx = grid(cfg)
    return float(np.sum(temperature) * dx)


def normalized_entropy(temperature: RealArray, cfg: ThermalConfig) -> float:
    _x, dx = grid(cfg)
    heat = total_heat(temperature, cfg)
    probability_density = temperature / heat
    if float(np.min(probability_density)) <= 0.0:
        raise ValueError("positive profile required for entropy")
    return -float(
        np.sum(probability_density * np.log(probability_density)) * dx
    )


def variance_functional(temperature: RealArray, cfg: ThermalConfig) -> float:
    _x, dx = grid(cfg)
    centered = temperature - float(np.mean(temperature))
    return 0.5 * float(np.sum(centered * centered) * dx)


def gradient_dissipation(temperature: RealArray, cfg: ThermalConfig) -> float:
    _x, dx = grid(cfg)
    k = wave_numbers(cfg)
    gradient = np.fft.ifft(
        1j * k * np.fft.fft(temperature)
    ).real
    return cfg.diffusivity * float(np.sum(gradient * gradient) * dx)


def mode_amplitude(
    temperature: RealArray,
    mode: int,
    cfg: ThermalConfig,
) -> float:
    transformed = np.fft.fft(temperature) / cfg.points
    return float(abs(transformed[mode]))


def thermal_evolution(
    cfg: ThermalConfig = ThermalConfig(),
) -> dict[str, Any]:
    initial = initial_temperature(cfg)
    times = np.linspace(0.0, cfg.final_time, cfg.samples)
    records = []
    fields = []

    for time in times:
        temperature = evolve_temperature(initial, float(time), cfg)
        records.append(
            {
                "time": float(time),
                "total_heat": total_heat(temperature, cfg),
                "entropy": normalized_entropy(temperature, cfg),
                "variance": variance_functional(temperature, cfg),
                "mode1_amplitude": mode_amplitude(temperature, 1, cfg),
                "minimum_temperature": float(np.min(temperature)),
            }
        )
        fields.append(temperature)

    return {
        "times": times,
        "fields": fields,
        "records": records,
    }


def semigroup_control(cfg: ThermalConfig = ThermalConfig()) -> dict[str, float]:
    initial = initial_temperature(cfg)
    first = evolve_temperature(initial, 1.1, cfg)
    composed = evolve_temperature(first, 0.9, cfg)
    direct = evolve_temperature(initial, 2.0, cfg)
    return {
        "maximum_semigroup_error": float(np.max(np.abs(composed - direct))),
    }


def mode_decay_control(cfg: ThermalConfig = ThermalConfig()) -> dict[str, float]:
    initial = initial_temperature(cfg)
    time = 1.7
    evolved = evolve_temperature(initial, time, cfg)
    initial_amplitude = mode_amplitude(initial, 1, cfg)
    final_amplitude = mode_amplitude(evolved, 1, cfg)
    expected_ratio = math.exp(-cfg.diffusivity * time)
    observed_ratio = final_amplitude / initial_amplitude
    return {
        "observed_ratio": observed_ratio,
        "expected_ratio": expected_ratio,
        "absolute_error": abs(observed_ratio - expected_ratio),
    }


def dissipation_identity(cfg: ThermalConfig = ThermalConfig()) -> dict[str, float]:
    initial = initial_temperature(cfg)
    time = 0.8
    epsilon = 1e-5
    before = evolve_temperature(initial, time - epsilon, cfg)
    current = evolve_temperature(initial, time, cfg)
    after = evolve_temperature(initial, time + epsilon, cfg)
    derivative = (
        variance_functional(after, cfg)
        - variance_functional(before, cfg)
    ) / (2.0 * epsilon)
    expected = -gradient_dissipation(current, cfg)
    return {
        "observed_derivative": derivative,
        "expected_derivative": expected,
        "absolute_error": abs(derivative - expected),
    }


def zero_diffusivity_control() -> dict[str, float]:
    cfg = ThermalConfig(diffusivity=0.0)
    initial = initial_temperature(cfg)
    final = evolve_temperature(initial, cfg.final_time, cfg)
    return {
        "maximum_field_change": float(np.max(np.abs(final - initial))),
    }


def resolution_study() -> dict[str, Any]:
    points = (64, 128, 256, 512)
    entropy = []
    heat_errors = []
    for count in points:
        cfg = ThermalConfig(points=count)
        run = thermal_evolution(cfg)
        entropy.append(run["records"][-1]["entropy"])
        initial_heat = run["records"][0]["total_heat"]
        heat_errors.append(
            max(
                abs(row["total_heat"] - initial_heat)
                for row in run["records"]
            )
        )
    differences = [
        abs(entropy[i] - entropy[i + 1])
        for i in range(len(entropy) - 1)
    ]
    return {
        "points": points,
        "final_entropy": entropy,
        "successive_entropy_differences": differences,
        "maximum_heat_error": max(heat_errors),
    }


@lru_cache(maxsize=1)
def run_thermal_field_study() -> dict[str, Any]:
    cfg = ThermalConfig()
    run = thermal_evolution(cfg)
    records = run["records"]
    heat = np.asarray([row["total_heat"] for row in records])
    entropy = np.asarray([row["entropy"] for row in records])
    variance = np.asarray([row["variance"] for row in records])
    mode = np.asarray([row["mode1_amplitude"] for row in records])

    semigroup = semigroup_control(cfg)
    decay = mode_decay_control(cfg)
    dissipation = dissipation_identity(cfg)
    frozen = zero_diffusivity_control()
    refinement = resolution_study()

    acceptance = {
        "total_heat_is_conserved": float(
            np.max(np.abs(heat - heat[0]))
        ) <= 2e-13,
        "thermal_entropy_is_monotone": bool(
            np.all(np.diff(entropy) >= -2e-14)
        ),
        "temperature_variance_decays": bool(
            np.all(np.diff(variance) <= 2e-14)
        ),
        "fourier_mode_decay_closes": decay["absolute_error"] <= 2e-14,
        "diffusion_dissipation_identity_closes": (
            dissipation["absolute_error"] <= 2e-9
        ),
        "semigroup_property_closes": (
            semigroup["maximum_semigroup_error"] <= 3e-14
        ),
        "zero_diffusivity_freezes_field": (
            frozen["maximum_field_change"] <= 2e-14
        ),
        "resolution_is_stable": (
            refinement["successive_entropy_differences"][-1] <= 2e-14
            and refinement["maximum_heat_error"] <= 3e-13
        ),
    }

    return {
        "schema": "openwave.m9.thermal-field-result.v1",
        "task": "M9.44",
        "config": asdict(cfg),
        "initial": records[0],
        "final": records[-1],
        "entropy_increase": float(entropy[-1] - entropy[0]),
        "variance_decrease": float(variance[0] - variance[-1]),
        "mode_decay": decay,
        "dissipation_identity": dissipation,
        "semigroup": semigroup,
        "zero_diffusivity": frozen,
        "resolution": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "explicit heat/thermal-field criterion",
                "conserved total heat",
                "monotone thermal entropy",
                "variance and Fourier-mode dissipation",
                "semigroup, zero-diffusivity, and resolution controls",
            ],
            "does_not_establish": [
                "microscopic thermodynamics from CAT/EPT",
                "physical temperature calibration or material transport",
                "quantum thermalization",
                "relativistic heat conduction",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
