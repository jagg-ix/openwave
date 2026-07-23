"""M9.4 nonlinear localization decision gate for a neutral 1D field.

The frozen family uses the same normalized ``sech`` seed in three equations:
free, defocusing cubic, and focusing cubic nonlinear Schrödinger dynamics. The
focusing member has an exact bright-soliton solution. Passing this gate creates
a localized mathematical candidate only; it does not identify an electron or a
three-dimensional particle.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class NLSConfig:
    """Periodic split-step Fourier configuration."""

    half_width: float = 20.0
    points: int = 512
    final_time: float = 2.0
    dt_over_dx: float = 0.01
    kappa: float = -2.0

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 64 or self.points % 2 != 0:
            raise ValueError("points must be an even integer at least 64")
        if self.final_time < 0.0:
            raise ValueError("final_time must be nonnegative")
        if self.dt_over_dx <= 0.0:
            raise ValueError("dt_over_dx must be positive")


@dataclass(frozen=True)
class NLSRun:
    """One nonlinear evolution and the state used to start it."""

    x: RealArray
    initial_state: ComplexArray
    final_state: ComplexArray
    dx: float
    dt: float
    steps: int
    config: NLSConfig


def grid(config: NLSConfig) -> tuple[RealArray, float]:
    """Return the periodic half-open grid ``[-L, L)``."""
    dx = 2.0 * config.half_width / config.points
    x = -config.half_width + dx * np.arange(config.points, dtype=np.float64)
    return x, dx


def sech(values: RealArray) -> RealArray:
    """Return the hyperbolic secant."""
    return np.asarray(1.0 / np.cosh(values), dtype=np.float64)


def normalized_sech_seed(
    x: RealArray,
    dx: float,
    *,
    width: float = 1.0,
    modulation: float = 0.0,
) -> ComplexArray:
    """Return the common normalized seed used for every family member."""
    if width <= 0.0:
        raise ValueError("width must be positive")
    state = sech(x / width).astype(np.complex128)
    if modulation != 0.0:
        state *= 1.0 + modulation * np.cos(0.5 * x)
    state_norm = math.sqrt(dx * np.sum(np.abs(state) ** 2))
    return np.asarray(state / state_norm, dtype=np.complex128)


def exact_focusing_soliton(x: RealArray, time: float) -> ComplexArray:
    """Return ``sech(x)/sqrt(2) * exp(i t/2)`` for ``kappa = -2``."""
    return np.asarray(
        sech(x) / math.sqrt(2.0) * np.exp(0.5j * time),
        dtype=np.complex128,
    )


def spectral_derivative(state: ComplexArray, dx: float) -> ComplexArray:
    """Return the periodic spectral first derivative."""
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(state.size, d=dx)
    return np.asarray(
        np.fft.ifft(1j * wave_numbers * np.fft.fft(state)),
        dtype=np.complex128,
    )


def state_norm(state: ComplexArray, dx: float) -> float:
    """Return ``integral |psi|^2 dx``."""
    return float(dx * np.sum(np.abs(state) ** 2))


def energy(state: ComplexArray, dx: float, kappa: float) -> float:
    """Return ``integral [|psi_x|^2/2 + kappa |psi|^4/2] dx``."""
    derivative = spectral_derivative(state, dx)
    density = 0.5 * np.abs(derivative) ** 2
    density += 0.5 * kappa * np.abs(state) ** 4
    return float(dx * np.sum(density))


def moments(x: RealArray, state: ComplexArray, dx: float) -> tuple[float, float]:
    """Return mean position and variance."""
    probability_density = np.abs(state) ** 2
    normalization = state_norm(state, dx)
    mean = float(dx * np.sum(x * probability_density) / normalization)
    variance = float(
        dx * np.sum((x - mean) ** 2 * probability_density) / normalization
    )
    return mean, variance


def evolve_nls(
    config: NLSConfig,
    initial_state: ComplexArray | None = None,
) -> NLSRun:
    """Evolve with second-order Strang split-step Fourier integration."""
    x, dx = grid(config)
    if initial_state is None:
        initial = normalized_sech_seed(x, dx)
    else:
        initial = np.asarray(initial_state, dtype=np.complex128).copy()
    if initial.shape != (config.points,):
        raise ValueError("initial_state shape does not match grid")

    if config.final_time == 0.0:
        return NLSRun(
            x=x,
            initial_state=initial,
            final_state=initial.copy(),
            dx=dx,
            dt=0.0,
            steps=0,
            config=config,
        )

    requested_dt = config.dt_over_dx * dx
    steps = max(1, math.ceil(config.final_time / requested_dt))
    dt = config.final_time / steps
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(config.points, d=dx)
    linear_half_step = np.exp(-0.25j * wave_numbers**2 * dt)

    state = initial.copy()
    for _ in range(steps):
        state = np.fft.ifft(linear_half_step * np.fft.fft(state))
        state *= np.exp(-1j * config.kappa * np.abs(state) ** 2 * dt)
        state = np.fft.ifft(linear_half_step * np.fft.fft(state))

    return NLSRun(
        x=x,
        initial_state=initial,
        final_state=np.asarray(state, dtype=np.complex128),
        dx=dx,
        dt=dt,
        steps=steps,
        config=config,
    )


def phase_aligned_error(
    reference: ComplexArray,
    state: ComplexArray,
    dx: float,
) -> tuple[float, float, float]:
    """Return phase-aligned L2 error, fidelity, and overlap phase."""
    overlap = dx * np.vdot(reference, state)
    aligned = state * np.exp(-1j * np.angle(overlap))
    error = float(math.sqrt(dx * np.sum(np.abs(aligned - reference) ** 2)))
    fidelity = float(
        abs(overlap) ** 2
        / (state_norm(reference, dx) * state_norm(state, dx))
    )
    return error, fidelity, float(np.angle(overlap))


def edge_probability(
    state: ComplexArray,
    dx: float,
    *,
    fraction: float = 0.15,
) -> float:
    """Return probability in the outer fraction of each periodic boundary."""
    count = max(1, int(state.size * fraction))
    density = np.abs(state) ** 2
    return float(dx * (np.sum(density[:count]) + np.sum(density[-count:])))


def core_probability(
    x: RealArray,
    state: ComplexArray,
    dx: float,
    *,
    radius: float = 5.0,
) -> float:
    """Return probability inside ``|x| <= radius``."""
    mask = np.abs(x) <= radius
    return float(dx * np.sum(np.abs(state[mask]) ** 2))


def stationary_residual(
    state: ComplexArray,
    dx: float,
    *,
    kappa: float = -2.0,
    chemical_potential: float = -0.5,
) -> float:
    """Return the L2 stationary-equation residual of the seed."""
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(state.size, d=dx)
    second_derivative = np.fft.ifft(
        -(wave_numbers**2) * np.fft.fft(state)
    )
    residual = (
        -0.5 * second_derivative
        + kappa * np.abs(state) ** 2 * state
        - chemical_potential * state
    )
    return float(math.sqrt(dx * np.sum(np.abs(residual) ** 2)))


def candidate_metrics(run: NLSRun) -> dict[str, Any]:
    """Measure conservation, localization, shape, and exact-return diagnostics."""
    initial = run.initial_state
    final = run.final_state
    initial_norm = state_norm(initial, run.dx)
    final_norm = state_norm(final, run.dx)
    initial_energy = energy(initial, run.dx, run.config.kappa)
    final_energy = energy(final, run.dx, run.config.kappa)
    _, initial_variance = moments(run.x, initial, run.dx)
    _, final_variance = moments(run.x, final, run.dx)

    if run.config.kappa == -2.0:
        reference = exact_focusing_soliton(
            run.x,
            run.config.final_time,
        )
        residual: float | None = stationary_residual(
            initial,
            run.dx,
            kappa=run.config.kappa,
        )
    else:
        reference = initial
        residual = None

    error, fidelity, phase = phase_aligned_error(reference, final, run.dx)
    density_error = float(
        run.dx
        * np.sum(
            np.abs(np.abs(final) ** 2 - np.abs(reference) ** 2)
        )
    )
    initial_peak = float(np.max(np.abs(initial) ** 2))
    final_peak = float(np.max(np.abs(final) ** 2))

    return {
        "points": run.config.points,
        "half_width": run.config.half_width,
        "dx": run.dx,
        "dt": run.dt,
        "steps": run.steps,
        "kappa": run.config.kappa,
        "initial_norm": initial_norm,
        "final_norm": final_norm,
        "norm_drift": abs(final_norm - initial_norm),
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "energy_drift": abs(final_energy - initial_energy),
        "phase_aligned_l2_error": error,
        "fidelity": fidelity,
        "phase_error": phase,
        "density_l1_error": density_error,
        "initial_variance": initial_variance,
        "final_variance": final_variance,
        "variance_ratio": final_variance / initial_variance,
        "initial_peak": initial_peak,
        "final_peak": final_peak,
        "peak_ratio": final_peak / initial_peak,
        "edge_probability": edge_probability(final, run.dx),
        "core_probability_r5": core_probability(run.x, final, run.dx),
        "stationary_residual": residual,
    }


def _observed_orders(
    levels: Sequence[dict[str, Any]],
    field: str,
) -> list[float]:
    return [
        math.log(float(coarse[field]) / float(fine[field]), 2.0)
        for coarse, fine in zip(levels[:-1], levels[1:], strict=True)
    ]


def run_localization_study() -> dict[str, Any]:
    """Run the frozen three-family M9.4 localization decision gate."""
    levels = [
        candidate_metrics(
            evolve_nls(
                NLSConfig(
                    points=points,
                    kappa=-2.0,
                    dt_over_dx=0.01,
                )
            )
        )
        for points in (256, 512, 1024)
    ]

    controls = {
        name: candidate_metrics(
            evolve_nls(
                NLSConfig(
                    points=512,
                    kappa=kappa,
                    dt_over_dx=0.01,
                )
            )
        )
        for name, kappa in (
            ("free", 0.0),
            ("defocusing", 2.0),
        )
    }

    windows = [
        candidate_metrics(
            evolve_nls(
                NLSConfig(
                    half_width=half_width,
                    points=points,
                    kappa=-2.0,
                    dt_over_dx=0.01,
                )
            )
        )
        for half_width, points in (
            (16.0, 512),
            (20.0, 640),
            (24.0, 768),
        )
    ]

    perturbation_config = NLSConfig(
        points=512,
        kappa=-2.0,
        final_time=5.0,
        dt_over_dx=0.01,
    )
    perturbation_x, perturbation_dx = grid(perturbation_config)
    perturbation_seed = normalized_sech_seed(
        perturbation_x,
        perturbation_dx,
        modulation=0.05,
    )
    perturbation_metrics = candidate_metrics(
        evolve_nls(
            perturbation_config,
            perturbation_seed,
        )
    )

    phase_orders = _observed_orders(levels, "phase_aligned_l2_error")
    density_orders = _observed_orders(levels, "density_l1_error")
    finest = levels[-1]
    window_variances = [float(metrics["final_variance"]) for metrics in windows]
    window_peaks = [float(metrics["final_peak"]) for metrics in windows]

    acceptance = {
        "candidate_norm_conserved": (
            max(float(metrics["norm_drift"]) for metrics in levels)
            <= 1.0e-11
        ),
        "candidate_energy_conserved": (
            max(float(metrics["energy_drift"]) for metrics in levels)
            <= 2.0e-8
        ),
        "candidate_stationary_residual": (
            float(finest["stationary_residual"]) <= 5.0e-8
        ),
        "candidate_converges_second_order": (
            min(phase_orders + density_orders) >= 1.8
        ),
        "candidate_fidelity": float(finest["fidelity"]) >= 0.999999,
        "candidate_localized": (
            float(finest["edge_probability"]) <= 2.0e-12
            and float(finest["core_probability_r5"]) >= 0.999
        ),
        "candidate_shape_stable": (
            abs(float(finest["variance_ratio"]) - 1.0) <= 1.0e-4
            and abs(float(finest["peak_ratio"]) - 1.0) <= 1.0e-4
        ),
        "window_independent": (
            max(window_variances) - min(window_variances) <= 1.0e-8
            and max(window_peaks) - min(window_peaks) <= 1.0e-8
        ),
        "perturbation_survives": (
            float(perturbation_metrics["edge_probability"]) <= 1.0e-7
            and float(perturbation_metrics["core_probability_r5"]) >= 0.99
            and float(perturbation_metrics["variance_ratio"]) <= 1.5
        ),
        "free_control_disperses": (
            float(controls["free"]["variance_ratio"]) >= 1.5
            and float(controls["free"]["peak_ratio"]) <= 0.8
        ),
        "defocusing_control_disperses": (
            float(controls["defocusing"]["variance_ratio"]) >= 1.5
            and float(controls["defocusing"]["peak_ratio"]) <= 0.8
        ),
    }
    passed = all(acceptance.values())

    return {
        "schema": "openwave.m9.localization-result.v1",
        "model": "M9-CAT-EPT",
        "equation": "i psi_t = -1/2 psi_xx + kappa |psi|^2 psi",
        "frozen_family": {
            "free": 0.0,
            "defocusing": 2.0,
            "focusing": -2.0,
        },
        "seed": "normalized sech(x), identical across family",
        "candidate": (
            "kappa=-2 bright soliton "
            "psi=sech(x)/sqrt(2) exp(i t/2)"
        ),
        "levels": levels,
        "observed_orders": {
            "phase_aligned_l2": phase_orders,
            "density_l1": density_orders,
        },
        "controls": controls,
        "windows": windows,
        "perturbation": perturbation_metrics,
        "acceptance": acceptance,
        "passed": passed,
        "classification": {
            "result": (
                "localized mathematical candidate" if passed else "gate failed"
            ),
            "dimension": "1+1",
            "charge": "none",
            "spin": "none",
            "physical_identity": "unassigned",
        },
        "scope": {
            "does_not_establish": [
                "electron identity",
                "three-dimensional stability",
                "charge",
                "spin",
                "mass prediction",
                "CAT/EPT uniqueness of the cubic term",
            ]
        },
    }
