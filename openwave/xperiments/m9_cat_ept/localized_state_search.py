"""M9.25: CAT/EPT-native localized-state search in a bounded 1D sector.

The reference equation is a normalized complex-time focusing field,

    d psi / dt = (i + gamma) [ 1/2 d_xx psi + g |psi|^2 psi ] + normalization,

so the reversible and irreversible sectors act on the same field while the
conserved norm fixes the member of the localized family. The analytic sech
profile is used as a static reference and perturbation target.

This establishes a one-dimensional constrained localized family only. It does
not select a unique scale, establish a three-dimensional particle, or derive
electric charge, spin, or physical mass.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class LocalizationParameters:
    half_width: float = 20.0
    points: int = 256
    nonlinearity: float = 1.0
    kappa: float = 0.8
    irreversible_rate: float = 0.05
    dt: float = 0.01
    final_time: float = 8.0
    long_time: float = 20.0
    core_radius: float = 5.0

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 64 or self.points % 2:
            raise ValueError("points must be an even integer at least 64")
        if self.nonlinearity <= 0.0 or self.kappa <= 0.0:
            raise ValueError("nonlinearity and kappa must be positive")
        if self.irreversible_rate < 0.0:
            raise ValueError("irreversible_rate must be nonnegative")
        if self.dt <= 0.0 or self.final_time <= 0.0 or self.long_time <= 0.0:
            raise ValueError("times must be positive")


def periodic_grid(p: LocalizationParameters) -> tuple[RealArray, float, RealArray]:
    dx = 2.0 * p.half_width / p.points
    x = -p.half_width + dx * np.arange(p.points, dtype=np.float64)
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(p.points, d=dx)
    return x, dx, wave_numbers


def target_norm(p: LocalizationParameters) -> float:
    return 2.0 * p.kappa / p.nonlinearity


def analytic_soliton(x: RealArray, p: LocalizationParameters) -> ComplexArray:
    amplitude = p.kappa / math.sqrt(p.nonlinearity)
    return np.asarray(amplitude / np.cosh(p.kappa * x), dtype=np.complex128)


def norm(state: ComplexArray, dx: float) -> float:
    return float(dx * np.sum(np.abs(state) ** 2))


def normalize(state: ComplexArray, dx: float, desired_norm: float) -> ComplexArray:
    current = norm(state, dx)
    if current <= 0.0:
        raise ValueError("state norm must be positive")
    return np.asarray(state * math.sqrt(desired_norm / current), dtype=np.complex128)


def stationary_residual(
    half_width: float,
    points: int,
    *,
    kappa: float = 0.8,
    nonlinearity: float = 1.0,
) -> dict[str, float]:
    dx = 2.0 * half_width / (points - 1)
    x = np.linspace(-half_width, half_width, points)
    profile = (kappa / math.sqrt(nonlinearity)) / np.cosh(kappa * x)
    laplacian = np.zeros_like(profile)
    laplacian[1:-1] = (profile[2:] - 2.0 * profile[1:-1] + profile[:-2]) / dx**2
    chemical_potential = -0.5 * kappa**2
    residual = -0.5 * laplacian - nonlinearity * profile**3 - chemical_potential * profile
    interior = residual[4:-4]
    return {
        "dx": dx,
        "residual_l2": math.sqrt(dx * float(np.sum(interior**2))),
        "tail_amplitude": float(max(abs(profile[0]), abs(profile[-1]))),
    }


def split_step(
    state: ComplexArray,
    *,
    dt: float,
    irreversible_rate: float,
    nonlinearity: float,
    wave_number_squared: RealArray,
    dx: float,
    desired_norm: float,
) -> ComplexArray:
    coefficient = irreversible_rate + 1j
    kinetic = np.exp(-coefficient * wave_number_squared * dt / 4.0)
    state = np.fft.ifft(np.fft.fft(state) * kinetic)
    state = state * np.exp(coefficient * nonlinearity * np.abs(state) ** 2 * dt)
    state = np.fft.ifft(np.fft.fft(state) * kinetic)
    return normalize(state, dx, desired_norm)


def localization_metrics(
    x: RealArray,
    state: ComplexArray,
    dx: float,
    *,
    core_radius: float,
) -> dict[str, float]:
    density = np.abs(state) ** 2
    total = float(dx * np.sum(density))
    center = float(dx * np.sum(x * density) / total)
    rms = math.sqrt(dx * float(np.sum((x - center) ** 2 * density)) / total)
    peak = float(np.max(density))
    core_fraction = float(dx * np.sum(density[np.abs(x - center) <= core_radius]) / total)
    edge = 0.75 * max(abs(float(x[0])), abs(float(x[-1])))
    tail_fraction = float(dx * np.sum(density[np.abs(x - center) >= edge]) / total)
    return {
        "norm": total,
        "center": center,
        "rms_radius": rms,
        "peak_density": peak,
        "core_fraction": core_fraction,
        "tail_fraction": tail_fraction,
    }


def perturbed_state(x: RealArray, state: ComplexArray, dx: float, desired_norm: float) -> ComplexArray:
    perturbation = (1.0 + 0.08 * np.cos(0.7 * x)) * np.exp(0.03j * x)
    return normalize(state * perturbation, dx, desired_norm)


def evolve(
    p: LocalizationParameters,
    *,
    final_time: float | None = None,
    irreversible_rate: float | None = None,
    perturb: bool = True,
) -> dict[str, Any]:
    x, dx, wave_numbers = periodic_grid(p)
    state = normalize(analytic_soliton(x, p), dx, target_norm(p))
    desired_norm = target_norm(p)
    reference = localization_metrics(x, state, dx, core_radius=p.core_radius)
    if perturb:
        state = perturbed_state(x, state, dx, desired_norm)
    initial = localization_metrics(x, state, dx, core_radius=p.core_radius)
    horizon = p.final_time if final_time is None else final_time
    rate = p.irreversible_rate if irreversible_rate is None else irreversible_rate
    steps = max(1, math.ceil(horizon / p.dt))
    dt = horizon / steps
    for _ in range(steps):
        state = split_step(
            state,
            dt=dt,
            irreversible_rate=rate,
            nonlinearity=p.nonlinearity,
            wave_number_squared=wave_numbers**2,
            dx=dx,
            desired_norm=desired_norm,
        )
    final = localization_metrics(x, state, dx, core_radius=p.core_radius)
    return {
        "dt": dt,
        "steps": steps,
        "reference": reference,
        "initial": initial,
        "final": final,
        "norm_error": abs(final["norm"] - desired_norm),
        "rms_ratio_to_reference": final["rms_radius"] / reference["rms_radius"],
        "peak_ratio_to_reference": final["peak_density"] / reference["peak_density"],
    }


def residual_refinement(points: Sequence[int] = (129, 257, 513)) -> dict[str, Any]:
    records = [stationary_residual(20.0, count) for count in points]
    errors = [record["residual_l2"] for record in records]
    orders = [math.log(errors[i] / errors[i + 1], 2.0) for i in range(len(errors) - 1)]
    return {"points": list(points), "records": records, "orders": orders}


def domain_study() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for half_width, points in ((16.0, 204), (20.0, 256), (24.0, 308)):
        p = LocalizationParameters(half_width=half_width, points=points, final_time=6.0, long_time=12.0)
        records.append({
            "half_width": half_width,
            "points": points,
            **evolve(p, final_time=6.0, irreversible_rate=0.05),
        })
    final_rms = np.asarray([item["final"]["rms_radius"] for item in records])
    final_peak = np.asarray([item["final"]["peak_density"] for item in records])
    return {
        "records": records,
        "rms_relative_spread": float(np.ptp(final_rms) / np.mean(final_rms)),
        "peak_relative_spread": float(np.ptp(final_peak) / np.mean(final_peak)),
    }


def candidate_family(kappas: Sequence[float] = (0.5, 0.8, 1.1)) -> list[dict[str, float]]:
    family: list[dict[str, float]] = []
    for kappa in kappas:
        p = LocalizationParameters(kappa=kappa)
        x, dx, _ = periodic_grid(p)
        state = normalize(analytic_soliton(x, p), dx, target_norm(p))
        metrics = localization_metrics(x, state, dx, core_radius=p.core_radius)
        family.append({
            "kappa": kappa,
            "norm": metrics["norm"],
            "rms_radius": metrics["rms_radius"],
            "peak_density": metrics["peak_density"],
            "tail_fraction": metrics["tail_fraction"],
        })
    return family


@lru_cache(maxsize=1)
def run_localized_state_search() -> dict[str, Any]:
    p = LocalizationParameters()
    refinement = residual_refinement()
    finite = evolve(p, final_time=p.final_time, irreversible_rate=p.irreversible_rate)
    long_run = evolve(p, final_time=p.long_time, irreversible_rate=0.0)
    domains = domain_study()
    family = candidate_family()
    acceptance = {
        "static_residual_second_order": min(refinement["orders"]) >= 1.8,
        "finite_norm_and_decay": finite["reference"]["norm"] > 0.0 and finite["reference"]["tail_fraction"] <= 1.0e-8,
        "perturbed_candidate_remains_localized": (
            finite["rms_ratio_to_reference"] <= 1.12
            and finite["peak_ratio_to_reference"] >= 0.90
            and finite["final"]["core_fraction"] >= 0.995
        ),
        "long_horizon_reversible_localization": (
            long_run["rms_ratio_to_reference"] <= 1.12
            and long_run["peak_ratio_to_reference"] >= 0.95
            and long_run["final"]["core_fraction"] >= 0.995
        ),
        "norm_constraint_closes": max(finite["norm_error"], long_run["norm_error"]) <= 2.0e-12,
        "domain_independent_at_scored_resolution": (
            domains["rms_relative_spread"] <= 2.0e-3
            and domains["peak_relative_spread"] <= 2.0e-3
        ),
        "continuous_family_is_explicit": len(family) == 3 and max(item["tail_fraction"] for item in family) <= 1.0e-6,
        "no_unique_scale_or_particle_promoted": True,
    }
    return {
        "schema": "openwave.m9.localized-state-search-result.v1",
        "task": "M9.25",
        "model": "normalized complex-time focusing field",
        "parameters": asdict(p),
        "candidate_family": family,
        "residual_refinement": refinement,
        "finite_perturbation": finite,
        "long_horizon": long_run,
        "domain_study": domains,
        "accepted_one_dimensional_localized_family": all(acceptance.values()),
        "accepted_three_dimensional_particle": False,
        "scale_selected_dynamically": False,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a finite-norm one-dimensional localized family",
                "second-order convergence of the static residual",
                "bounded perturbation response and long-horizon localization",
                "shared reversible and irreversible evolution on the same field",
            ],
            "does_not_establish": [
                "a unique dynamically selected scale",
                "a stable three-dimensional CAT/EPT particle",
                "emergent charge, spin, or physical mass",
                "that the constrained norm is a microscopic CAT/EPT law",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
