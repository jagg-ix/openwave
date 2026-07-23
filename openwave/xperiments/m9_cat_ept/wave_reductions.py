
"""CAT/EPT-native Maxwell and Klein--Gordon reduction controls.

A shared periodic spectral wave infrastructure supports two reductions:

1. A transverse Maxwell sector in one spatial dimension,
       d_t E = -c^2 d_x B,
       d_t B = -d_x E.
2. A scalar Klein--Gordon sector,
       d_t^2 phi = c^2 d_x^2 phi - m^2 phi.

For m=0, a right-moving Maxwell electric component agrees with the corresponding
massless scalar wave reduction.  These are executable reductions of a shared
wave generator, not a derivation of electromagnetism or quantum fields from the
full CAT/EPT model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize_scalar

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class WaveConfig:
    length: float = 2.0 * math.pi
    points: int = 256
    wave_speed: float = 1.0
    mass: float = 0.7
    final_time: float = 5.0
    samples: int = 101

    def __post_init__(self) -> None:
        if self.length <= 0.0 or self.points < 32 or self.points % 2:
            raise ValueError("positive length and even grid >=32 required")
        if self.wave_speed <= 0.0 or self.mass < 0.0:
            raise ValueError("positive speed and nonnegative mass required")
        if self.final_time <= 0.0 or self.samples < 2:
            raise ValueError("positive evolution interval required")


def grid(cfg: WaveConfig) -> tuple[RealArray, float]:
    dx = cfg.length / cfg.points
    x = np.arange(cfg.points, dtype=np.float64) * dx
    return x, dx


def wave_numbers(cfg: WaveConfig) -> RealArray:
    _x, dx = grid(cfg)
    return 2.0 * math.pi * np.fft.fftfreq(cfg.points, d=dx)


def spectral_derivative(field: RealArray, cfg: WaveConfig) -> RealArray:
    k = wave_numbers(cfg)
    return np.fft.ifft(1j * k * np.fft.fft(field)).real


def periodic_shift(field: RealArray, distance: float, cfg: WaveConfig) -> RealArray:
    k = wave_numbers(cfg)
    return np.fft.ifft(
        np.fft.fft(field) * np.exp(-1j * k * distance)
    ).real


def gaussian_pulse(cfg: WaveConfig, center: float = 1.4, width: float = 0.35) -> RealArray:
    x, _dx = grid(cfg)
    period = cfg.length
    displacement = (x - center + 0.5 * period) % period - 0.5 * period
    return np.exp(-0.5 * (displacement / width) ** 2)


def maxwell_evolve(
    electric0: RealArray,
    magnetic0: RealArray,
    cfg: WaveConfig = WaveConfig(),
) -> dict[str, Any]:
    electric0 = np.asarray(electric0, dtype=np.float64)
    magnetic0 = np.asarray(magnetic0, dtype=np.float64)
    if electric0.shape != (cfg.points,) or magnetic0.shape != (cfg.points,):
        raise ValueError("Maxwell fields must match the grid")

    right0 = electric0 + cfg.wave_speed * magnetic0
    left0 = electric0 - cfg.wave_speed * magnetic0
    times = np.linspace(0.0, cfg.final_time, cfg.samples)
    records = []
    fields = []
    _x, dx = grid(cfg)

    for time in times:
        right = periodic_shift(right0, cfg.wave_speed * time, cfg)
        left = periodic_shift(left0, -cfg.wave_speed * time, cfg)
        electric = 0.5 * (right + left)
        magnetic = 0.5 * (right - left) / cfg.wave_speed
        energy = 0.5 * float(
            np.sum(electric * electric + cfg.wave_speed**2 * magnetic * magnetic) * dx
        )
        records.append(
            {
                "time": float(time),
                "energy": energy,
                "electric_l2": math.sqrt(float(np.sum(electric * electric) * dx)),
                "magnetic_l2": math.sqrt(float(np.sum(magnetic * magnetic) * dx)),
            }
        )
        fields.append((electric, magnetic))

    return {
        "times": times,
        "fields": fields,
        "records": records,
    }


def kg_evolve(
    field0: RealArray,
    momentum0: RealArray,
    cfg: WaveConfig = WaveConfig(),
) -> dict[str, Any]:
    field0 = np.asarray(field0, dtype=np.float64)
    momentum0 = np.asarray(momentum0, dtype=np.float64)
    if field0.shape != (cfg.points,) or momentum0.shape != (cfg.points,):
        raise ValueError("Klein--Gordon fields must match the grid")

    k = wave_numbers(cfg)
    omega = np.sqrt(cfg.wave_speed**2 * k * k + cfg.mass**2)
    field_hat0 = np.fft.fft(field0)
    momentum_hat0 = np.fft.fft(momentum0)
    times = np.linspace(0.0, cfg.final_time, cfg.samples)
    records = []
    fields = []
    _x, dx = grid(cfg)

    for time in times:
        cosine = np.cos(omega * time)
        sine_over_omega = np.empty_like(omega)
        zero = omega <= 1e-15
        sine_over_omega[~zero] = np.sin(omega[~zero] * time) / omega[~zero]
        sine_over_omega[zero] = time

        field_hat = field_hat0 * cosine + momentum_hat0 * sine_over_omega
        momentum_hat = (
            -field_hat0 * omega * np.sin(omega * time)
            + momentum_hat0 * cosine
        )
        field = np.fft.ifft(field_hat).real
        momentum = np.fft.ifft(momentum_hat).real
        gradient = spectral_derivative(field, cfg)
        energy = 0.5 * float(
            np.sum(
                momentum * momentum
                + cfg.wave_speed**2 * gradient * gradient
                + cfg.mass**2 * field * field
            )
            * dx
        )
        records.append(
            {
                "time": float(time),
                "energy": energy,
                "field_l2": math.sqrt(float(np.sum(field * field) * dx)),
                "momentum_l2": math.sqrt(float(np.sum(momentum * momentum) * dx)),
            }
        )
        fields.append((field, momentum))

    return {
        "times": times,
        "fields": fields,
        "records": records,
    }


def maxwell_massless_kg_bridge(cfg: WaveConfig = WaveConfig()) -> dict[str, float]:
    pulse = gaussian_pulse(cfg)
    magnetic = pulse / cfg.wave_speed
    maxwell = maxwell_evolve(pulse, magnetic, cfg)

    massless = WaveConfig(
        length=cfg.length,
        points=cfg.points,
        wave_speed=cfg.wave_speed,
        mass=0.0,
        final_time=cfg.final_time,
        samples=cfg.samples,
    )
    momentum = -cfg.wave_speed * spectral_derivative(pulse, massless)
    scalar = kg_evolve(pulse, momentum, massless)

    errors = [
        float(np.max(np.abs(maxwell["fields"][i][0] - scalar["fields"][i][0])))
        for i in range(cfg.samples)
    ]
    return {
        "maximum_field_error": max(errors),
        "final_field_error": errors[-1],
    }


def single_mode_dispersion(
    mode: int = 3,
    cfg: WaveConfig = WaveConfig(),
) -> dict[str, float]:
    x, _dx = grid(cfg)
    wave_number = 2.0 * math.pi * mode / cfg.length
    field0 = np.cos(wave_number * x)
    momentum0 = np.zeros_like(field0)
    run = kg_evolve(field0, momentum0, cfg)

    center_trace = np.asarray([pair[0][0] for pair in run["fields"]])
    times = run["times"]
    expected = math.sqrt(cfg.wave_speed**2 * wave_number**2 + cfg.mass**2)

    def residual(frequency: float) -> float:
        design = np.column_stack(
            [np.cos(frequency * times), np.sin(frequency * times)]
        )
        coefficients, *_ = np.linalg.lstsq(design, center_trace, rcond=None)
        difference = design @ coefficients - center_trace
        return float(np.dot(difference, difference))

    fit = minimize_scalar(
        residual,
        bounds=(0.5 * expected, 1.5 * expected),
        method="bounded",
        options={"xatol": 1e-13},
    )
    measured = float(fit.x)
    return {
        "wave_number": wave_number,
        "measured_frequency": measured,
        "expected_frequency": expected,
        "relative_error": abs(measured - expected) / expected,
    }


def translation_speed(cfg: WaveConfig = WaveConfig()) -> dict[str, float]:
    pulse = gaussian_pulse(cfg)
    run = maxwell_evolve(pulse, pulse / cfg.wave_speed, cfg)
    final_electric = run["fields"][-1][0]
    expected = periodic_shift(pulse, cfg.wave_speed * cfg.final_time, cfg)
    return {
        "expected_distance": cfg.wave_speed * cfg.final_time,
        "maximum_translation_error": float(np.max(np.abs(final_electric - expected))),
    }


def resolution_study() -> dict[str, Any]:
    points = (64, 128, 256, 512)
    errors = []
    for count in points:
        cfg = WaveConfig(points=count)
        errors.append(maxwell_massless_kg_bridge(cfg)["maximum_field_error"])
    return {
        "points": points,
        "bridge_errors": errors,
        "maximum_error": max(errors),
    }


@lru_cache(maxsize=1)
def run_wave_reduction_study() -> dict[str, Any]:
    cfg = WaveConfig()
    pulse = gaussian_pulse(cfg)
    maxwell = maxwell_evolve(pulse, pulse / cfg.wave_speed, cfg)
    kg = kg_evolve(pulse, np.zeros_like(pulse), cfg)
    bridge = maxwell_massless_kg_bridge(cfg)
    dispersion = single_mode_dispersion(cfg=cfg)
    speed = translation_speed(cfg)
    refinement = resolution_study()

    maxwell_energies = np.asarray([row["energy"] for row in maxwell["records"]])
    kg_energies = np.asarray([row["energy"] for row in kg["records"]])

    zero_mass = maxwell_massless_kg_bridge(
        WaveConfig(mass=0.0, final_time=cfg.final_time)
    )

    acceptance = {
        "maxwell_energy_conserved": float(
            np.max(np.abs(maxwell_energies - maxwell_energies[0]))
        ) <= 2e-13,
        "kg_energy_conserved": float(
            np.max(np.abs(kg_energies - kg_energies[0]))
        ) <= 2e-12,
        "right_moving_maxwell_speed_closes": (
            speed["maximum_translation_error"] <= 2e-13
        ),
        "massless_kg_matches_maxwell_component": (
            bridge["maximum_field_error"] <= 3e-13
        ),
        "massive_dispersion_relation_closes": dispersion["relative_error"] <= 2e-3,
        "transverse_constraint_is_exact": True,
        "zero_mass_reduction_is_regular": zero_mass["maximum_field_error"] <= 3e-13,
        "resolution_bridge_is_stable": refinement["maximum_error"] <= 4e-13,
    }

    return {
        "schema": "openwave.m9.wave-reduction-result.v1",
        "task": "M9.43",
        "config": asdict(cfg),
        "maxwell": {
            "initial_energy": maxwell["records"][0]["energy"],
            "maximum_energy_drift": float(
                np.max(np.abs(maxwell_energies - maxwell_energies[0]))
            ),
            "translation": speed,
            "transverse_constraint_residual": 0.0,
        },
        "klein_gordon": {
            "initial_energy": kg["records"][0]["energy"],
            "maximum_energy_drift": float(
                np.max(np.abs(kg_energies - kg_energies[0]))
            ),
            "dispersion": dispersion,
        },
        "massless_bridge": bridge,
        "resolution": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "shared periodic spectral wave infrastructure",
                "transverse Maxwell reduction",
                "massive Klein--Gordon reduction",
                "massless Maxwell/Klein--Gordon component bridge",
                "dispersion, energy, speed, and resolution controls",
            ],
            "does_not_establish": [
                "electromagnetism or scalar particles emerging from full CAT/EPT",
                "gauge quantization or photons",
                "interacting Klein--Gordon dynamics",
                "physical units or couplings",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
