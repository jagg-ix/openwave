"""M9.7a bounded nonlinear Dirac/Soler spinor-carrier qualification gate.

This module validates a two-component 1+1D spinor replacement carrier before any
three-dimensional, Maxwell, or renderer work. The selected Soler equation is

    i d_t Psi = -i alpha d_x Psi + beta (m - lambda * bar(Psi) Psi) Psi

with alpha = -sigma_2, beta = sigma_3, m = 1, lambda = 1. The exact solitary
wave is used as a reference. A background local-U(1) connection is implemented
for gauge-covariance checks, but no dynamical Maxwell field is claimed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

from openwave.xperiments.m9_cat_ept.entropic_clock import (
    PeriodicCoarseGraining,
    snapshot_clock_trajectory,
)

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

ALPHA = np.asarray([[0.0, 1.0j], [-1.0j, 0.0]], dtype=np.complex128)
BETA = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)


@dataclass(frozen=True)
class SolerParameters:
    mass: float = 1.0
    frequency: float = 0.8
    coupling: float = 1.0
    gauge_charge: float = 1.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if not 0.0 < self.frequency < self.mass:
            raise ValueError("frequency must lie strictly between zero and mass")
        if self.coupling <= 0.0:
            raise ValueError("coupling must be positive")
        if self.gauge_charge == 0.0:
            raise ValueError("gauge_charge must be nonzero")

    @property
    def decay_rate(self) -> float:
        return math.sqrt(self.mass**2 - self.frequency**2)


@dataclass(frozen=True)
class SpinorConfig:
    half_width: float = 30.0
    points: int = 1024
    final_time: float = 2.0
    dt_over_dx: float = 0.05
    nonlinear_coupling: float = 1.0

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 128 or self.points % 2 != 0:
            raise ValueError("points must be an even integer at least 128")
        if self.final_time < 0.0:
            raise ValueError("final_time must be nonnegative")
        if self.dt_over_dx <= 0.0:
            raise ValueError("dt_over_dx must be positive")
        if self.nonlinear_coupling < 0.0:
            raise ValueError("nonlinear_coupling must be nonnegative")


@dataclass(frozen=True)
class SpinorRun:
    x: RealArray
    initial_state: ComplexArray
    final_state: ComplexArray
    dx: float
    dt: float
    steps: int
    parameters: SolerParameters
    config: SpinorConfig


def periodic_grid(config: SpinorConfig) -> tuple[RealArray, float]:
    dx = 2.0 * config.half_width / config.points
    x = -config.half_width + dx * np.arange(config.points, dtype=np.float64)
    return x, dx


def soler_profile(
    x: RealArray,
    parameters: SolerParameters = SolerParameters(),
) -> ComplexArray:
    m = parameters.mass
    omega = parameters.frequency
    lam = parameters.coupling
    kappa = parameters.decay_rate
    denominator = m + omega * np.cosh(2.0 * kappa * x)
    upper = (
        math.sqrt(2.0 * (m - omega) / lam)
        * (m + omega)
        * np.cosh(kappa * x)
        / denominator
    )
    lower = (
        math.sqrt(2.0 * (m + omega) / lam)
        * (m - omega)
        * np.sinh(kappa * x)
        / denominator
    )
    return np.asarray([upper, lower], dtype=np.complex128)


def soler_profile_derivative(
    x: RealArray,
    parameters: SolerParameters = SolerParameters(),
) -> ComplexArray:
    m = parameters.mass
    omega = parameters.frequency
    lam = parameters.coupling
    kappa = parameters.decay_rate
    denominator = m + omega * np.cosh(2.0 * kappa * x)
    denominator_prime = 2.0 * omega * kappa * np.sinh(2.0 * kappa * x)

    upper_prefactor = math.sqrt(2.0 * (m - omega) / lam) * (m + omega)
    lower_prefactor = math.sqrt(2.0 * (m + omega) / lam) * (m - omega)
    upper = upper_prefactor * (
        kappa * np.sinh(kappa * x) * denominator
        - np.cosh(kappa * x) * denominator_prime
    ) / denominator**2
    lower = lower_prefactor * (
        kappa * np.cosh(kappa * x) * denominator
        - np.sinh(kappa * x) * denominator_prime
    ) / denominator**2
    return np.asarray([upper, lower], dtype=np.complex128)


def soler_state(
    x: RealArray,
    time: float,
    parameters: SolerParameters = SolerParameters(),
) -> ComplexArray:
    return np.asarray(
        soler_profile(x, parameters) * np.exp(-1j * parameters.frequency * time),
        dtype=np.complex128,
    )


def spinor_density(state: ComplexArray) -> RealArray:
    if state.ndim != 2 or state.shape[0] != 2:
        raise ValueError("state must have shape (2, points)")
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def lorentz_scalar(state: ComplexArray) -> RealArray:
    if state.ndim != 2 or state.shape[0] != 2:
        raise ValueError("state must have shape (2, points)")
    return np.asarray(
        np.abs(state[0]) ** 2 - np.abs(state[1]) ** 2,
        dtype=np.float64,
    )


def spinor_norm(state: ComplexArray, dx: float) -> float:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    return float(dx * np.sum(spinor_density(state)))


def spectral_derivative(state: ComplexArray, dx: float) -> ComplexArray:
    if dx <= 0.0:
        raise ValueError("dx must be positive")
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(state.shape[1], d=dx)
    return np.asarray(
        np.fft.ifft(
            1j * wave_numbers[None, :] * np.fft.fft(state, axis=1),
            axis=1,
        ),
        dtype=np.complex128,
    )


def dirac_current(state: ComplexArray) -> RealArray:
    alpha_state = ALPHA @ state
    return np.asarray(
        np.real(np.sum(np.conj(state) * alpha_state, axis=0)),
        dtype=np.float64,
    )


def covariant_energy(
    state: ComplexArray,
    dx: float,
    parameters: SolerParameters = SolerParameters(),
    *,
    vector_potential: RealArray | None = None,
    scalar_potential: RealArray | None = None,
    nonlinear_coupling: float | None = None,
) -> float:
    points = state.shape[1]
    ax = (
        np.zeros(points, dtype=np.float64)
        if vector_potential is None
        else np.asarray(vector_potential, dtype=np.float64)
    )
    a0 = (
        np.zeros(points, dtype=np.float64)
        if scalar_potential is None
        else np.asarray(scalar_potential, dtype=np.float64)
    )
    if ax.shape != (points,) or a0.shape != (points,):
        raise ValueError("gauge potentials must match the spatial grid")

    derivative = spectral_derivative(state, dx)
    covariant_momentum = -1j * derivative - parameters.gauge_charge * ax[None, :] * state
    kinetic = np.real(
        np.sum(np.conj(state) * (ALPHA @ covariant_momentum), axis=0)
    )
    scalar = lorentz_scalar(state)
    selected_coupling = (
        parameters.coupling if nonlinear_coupling is None else nonlinear_coupling
    )
    interaction = parameters.mass * scalar - 0.5 * selected_coupling * scalar**2
    electric = parameters.gauge_charge * a0 * spinor_density(state)
    return float(dx * np.sum(kinetic + interaction + electric))


def gauge_transform(
    state: ComplexArray,
    phase: RealArray,
    parameters: SolerParameters = SolerParameters(),
) -> ComplexArray:
    phase_array = np.asarray(phase, dtype=np.float64)
    if phase_array.shape != (state.shape[1],):
        raise ValueError("phase must match the spatial grid")
    return np.asarray(
        state * np.exp(1j * parameters.gauge_charge * phase_array)[None, :],
        dtype=np.complex128,
    )


def analytic_stationary_residual(
    x: RealArray,
    parameters: SolerParameters = SolerParameters(),
) -> float:
    profile = soler_profile(x, parameters)
    derivative = soler_profile_derivative(x, parameters)
    scalar = lorentz_scalar(profile)
    h_profile = -1j * (ALPHA @ derivative) + BETA @ (
        (parameters.mass - parameters.coupling * scalar)[None, :] * profile
    )
    residual = h_profile - parameters.frequency * profile
    scale = math.sqrt(
        np.trapezoid(np.sum(np.abs(parameters.frequency * profile) ** 2, axis=0), x)
    )
    value = math.sqrt(np.trapezoid(np.sum(np.abs(residual) ** 2, axis=0), x))
    return value / scale


def evolve_soler(
    parameters: SolerParameters,
    config: SpinorConfig,
    initial_state: ComplexArray | None = None,
) -> SpinorRun:
    x, dx = periodic_grid(config)
    initial = (
        soler_profile(x, parameters)
        if initial_state is None
        else np.asarray(initial_state, dtype=np.complex128).copy()
    )
    if initial.shape != (2, config.points):
        raise ValueError("initial_state must match the spinor grid")

    if config.final_time == 0.0:
        return SpinorRun(
            x=x,
            initial_state=initial,
            final_state=initial.copy(),
            dx=dx,
            dt=0.0,
            steps=0,
            parameters=parameters,
            config=config,
        )

    steps = max(1, math.ceil(config.final_time / (config.dt_over_dx * dx)))
    dt = config.final_time / steps
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(config.points, d=dx)
    cosine = np.cos(wave_numbers * dt)
    sine = np.sin(wave_numbers * dt)

    state = initial.copy()
    for _ in range(steps):
        scalar = lorentz_scalar(state)
        local_mass = parameters.mass - config.nonlinear_coupling * scalar
        state[0] *= np.exp(-0.5j * local_mass * dt)
        state[1] *= np.exp(+0.5j * local_mass * dt)

        upper_fourier = np.fft.fft(state[0])
        lower_fourier = np.fft.fft(state[1])
        state[0] = np.fft.ifft(cosine * upper_fourier + sine * lower_fourier)
        state[1] = np.fft.ifft(cosine * lower_fourier - sine * upper_fourier)

        scalar = lorentz_scalar(state)
        local_mass = parameters.mass - config.nonlinear_coupling * scalar
        state[0] *= np.exp(-0.5j * local_mass * dt)
        state[1] *= np.exp(+0.5j * local_mass * dt)

    return SpinorRun(
        x=x,
        initial_state=initial,
        final_state=np.asarray(state, dtype=np.complex128),
        dx=dx,
        dt=dt,
        steps=steps,
        parameters=parameters,
        config=config,
    )


def _moments(x: RealArray, state: ComplexArray, dx: float) -> tuple[float, float]:
    density = spinor_density(state)
    norm = spinor_norm(state, dx)
    mean = float(dx * np.sum(x * density) / norm)
    variance = float(dx * np.sum((x - mean) ** 2 * density) / norm)
    return mean, variance


def _edge_fraction(state: ComplexArray, dx: float, fraction: float = 0.15) -> float:
    count = max(1, int(state.shape[1] * fraction))
    density = spinor_density(state)
    enclosed = dx * (np.sum(density[:count]) + np.sum(density[-count:]))
    return float(enclosed / spinor_norm(state, dx))


def _core_fraction(
    x: RealArray,
    state: ComplexArray,
    dx: float,
    radius: float = 8.0,
) -> float:
    density = spinor_density(state)
    enclosed = dx * np.sum(density[np.abs(x) <= radius])
    return float(enclosed / spinor_norm(state, dx))


def _phase_aligned_metrics(
    reference: ComplexArray,
    state: ComplexArray,
    dx: float,
) -> tuple[float, float, float]:
    overlap = dx * np.sum(np.conj(reference) * state)
    aligned = state * np.exp(-1j * np.angle(overlap))
    error = math.sqrt(dx * np.sum(np.abs(aligned - reference) ** 2))
    fidelity = abs(overlap) ** 2 / (
        spinor_norm(reference, dx) * spinor_norm(state, dx)
    )
    return float(error), float(fidelity), float(np.angle(overlap))


def run_metrics(run: SpinorRun) -> dict[str, Any]:
    reference = soler_state(run.x, run.config.final_time, run.parameters)
    error, fidelity, phase = _phase_aligned_metrics(
        reference,
        run.final_state,
        run.dx,
    )
    density_error = (
        run.dx
        * np.sum(
            np.abs(
                spinor_density(run.final_state)
                - spinor_density(reference)
            )
        )
        / spinor_norm(reference, run.dx)
    )
    initial_energy = covariant_energy(
        run.initial_state,
        run.dx,
        run.parameters,
        nonlinear_coupling=run.config.nonlinear_coupling,
    )
    final_energy = covariant_energy(
        run.final_state,
        run.dx,
        run.parameters,
        nonlinear_coupling=run.config.nonlinear_coupling,
    )
    _, initial_variance = _moments(run.x, run.initial_state, run.dx)
    _, final_variance = _moments(run.x, run.final_state, run.dx)
    initial_peak = float(np.max(spinor_density(run.initial_state)))
    final_peak = float(np.max(spinor_density(run.final_state)))
    initial_norm = spinor_norm(run.initial_state, run.dx)
    final_norm = spinor_norm(run.final_state, run.dx)

    return {
        "points": run.config.points,
        "half_width": run.config.half_width,
        "dx": run.dx,
        "dt": run.dt,
        "steps": run.steps,
        "nonlinear_coupling": run.config.nonlinear_coupling,
        "initial_norm": initial_norm,
        "final_norm": final_norm,
        "norm_drift": abs(final_norm - initial_norm),
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "energy_drift": abs(final_energy - initial_energy),
        "phase_aligned_l2_error": error,
        "density_relative_l1_error": float(density_error),
        "fidelity": fidelity,
        "phase_error": phase,
        "variance_ratio": final_variance / initial_variance,
        "peak_ratio": final_peak / initial_peak,
        "core_fraction_r8": _core_fraction(run.x, run.final_state, run.dx),
        "edge_fraction": _edge_fraction(run.final_state, run.dx),
    }


def spinor_probability(state: ComplexArray, dx: float) -> RealArray:
    cell_mass = dx * spinor_density(state)
    total = float(np.sum(cell_mass))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("state must have finite positive norm")
    return np.asarray(cell_mass / total, dtype=np.float64)


def _orders(levels: Sequence[dict[str, Any]], field: str) -> list[float]:
    return [
        math.log(float(coarse[field]) / float(fine[field]), 2.0)
        for coarse, fine in zip(levels[:-1], levels[1:], strict=True)
    ]


@lru_cache(maxsize=1)
def run_spinor_carrier_study() -> dict[str, Any]:
    parameters = SolerParameters()

    levels = [
        run_metrics(evolve_soler(parameters, SpinorConfig(points=points)))
        for points in (512, 1024, 2048)
    ]
    phase_orders = _orders(levels, "phase_aligned_l2_error")
    density_orders = _orders(levels, "density_relative_l1_error")
    finest = levels[-1]

    windows = [
        run_metrics(
            evolve_soler(
                parameters,
                SpinorConfig(half_width=half_width, points=points),
            )
        )
        for half_width, points in (
            (20.625, 704),
            (25.3125, 864),
            (30.0, 1024),
        )
    ]

    perturbation_config = SpinorConfig(points=1024, final_time=10.0)
    x, dx = periodic_grid(perturbation_config)
    base = soler_profile(x, parameters)
    mode = 3.0 * math.pi / perturbation_config.half_width
    modulation = 0.02 * np.cos(mode * x)
    perturbation = base.copy()
    perturbation[0] *= 1.0 + modulation
    perturbation[1] *= 1.0 - modulation
    perturbation *= math.sqrt(
        spinor_norm(base, dx) / spinor_norm(perturbation, dx)
    )
    perturbed_metrics = run_metrics(
        evolve_soler(parameters, perturbation_config, perturbation)
    )

    control_metrics = run_metrics(
        evolve_soler(
            parameters,
            SpinorConfig(
                points=1024,
                final_time=10.0,
                nonlinear_coupling=0.0,
            ),
        )
    )

    gauge_config = SpinorConfig(points=1024, final_time=0.0)
    gauge_x, gauge_dx = periodic_grid(gauge_config)
    gauge_state = soler_profile(gauge_x, parameters)
    gauge_mode = 2.0 * math.pi / (2.0 * gauge_config.half_width) * 2.0
    gauge_phase = 0.3 * np.sin(gauge_mode * gauge_x)
    gauge_gradient = 0.3 * gauge_mode * np.cos(gauge_mode * gauge_x)
    transformed = gauge_transform(gauge_state, gauge_phase, parameters)
    gauge_norm_error = abs(
        spinor_norm(transformed, gauge_dx) - spinor_norm(gauge_state, gauge_dx)
    )
    gauge_density_error = float(
        np.max(np.abs(spinor_density(transformed) - spinor_density(gauge_state)))
    )
    gauge_energy_error = abs(
        covariant_energy(
            transformed,
            gauge_dx,
            parameters,
            vector_potential=gauge_gradient,
        )
        - covariant_energy(gauge_state, gauge_dx, parameters)
    )

    baseline_run = evolve_soler(parameters, SpinorConfig(points=1024))
    baseline_probability = spinor_probability(
        baseline_run.initial_state,
        baseline_run.dx,
    )
    final_probability = spinor_probability(
        baseline_run.final_state,
        baseline_run.dx,
    )
    gauge_probability = spinor_probability(transformed, gauge_dx)
    channel = PeriodicCoarseGraining(steps=64)
    initial_clock = snapshot_clock_trajectory(baseline_probability, channel)
    final_clock = snapshot_clock_trajectory(final_probability, channel)

    window_variances = [float(item["variance_ratio"]) for item in windows]
    window_peaks = [float(item["peak_ratio"]) for item in windows]

    acceptance = {
        "analytic_stationary_profile": (
            analytic_stationary_residual(
                np.linspace(-30.0, 30.0, 20001),
                parameters,
            )
            <= 1.0e-12
        ),
        "second_order_spinor_return": (
            min(phase_orders + density_orders) >= 1.8
        ),
        "finest_return_accuracy": (
            float(finest["phase_aligned_l2_error"]) <= 2.0e-7
            and float(finest["density_relative_l1_error"]) <= 1.0e-7
            and float(finest["fidelity"]) >= 0.999999999999
        ),
        "norm_and_energy_conserved": (
            max(float(item["norm_drift"]) for item in levels) <= 2.0e-12
            and max(float(item["energy_drift"]) for item in levels) <= 2.0e-10
        ),
        "localized_and_window_independent": (
            float(finest["core_fraction_r8"]) >= 0.999
            and float(finest["edge_fraction"]) <= 1.0e-9
            and max(window_variances) - min(window_variances) <= 1.0e-6
            and max(window_peaks) - min(window_peaks) <= 1.0e-6
        ),
        "fixed_perturbation_remains_localized": (
            float(perturbed_metrics["core_fraction_r8"]) >= 0.999
            and float(perturbed_metrics["edge_fraction"]) <= 1.0e-7
            and 0.9 <= float(perturbed_metrics["variance_ratio"]) <= 1.2
            and float(perturbed_metrics["fidelity"]) >= 0.999
        ),
        "free_dirac_control_disperses": (
            float(control_metrics["variance_ratio"]) >= 2.0
            and float(control_metrics["peak_ratio"]) <= 0.6
        ),
        "local_u1_covariant_interface": (
            gauge_norm_error <= 1.0e-13
            and gauge_density_error <= 1.0e-13
            and gauge_energy_error <= 1.0e-11
        ),
        "entropic_clock_interface_preserved": (
            np.max(np.abs(gauge_probability - baseline_probability)) <= 1.0e-13
            and bool(initial_clock["remaining_nonincreasing"])
            and bool(initial_clock["gain_nondecreasing"])
            and bool(final_clock["remaining_nonincreasing"])
            and bool(final_clock["gain_nondecreasing"])
            and float(initial_clock["max_ledger_closure_error"]) <= 1.0e-12
            and float(final_clock["max_ledger_closure_error"]) <= 1.0e-12
        ),
    }

    return {
        "schema": "openwave.m9.spinor-carrier-gate.v1",
        "model": "M9-CAT-EPT",
        "task": "M9.7a",
        "equation": (
            "i d_t Psi = -i alpha d_x Psi "
            "+ beta (m - lambda bar(Psi)Psi) Psi"
        ),
        "parameters": asdict(parameters),
        "exact_profile": {
            "frequency": parameters.frequency,
            "decay_rate": parameters.decay_rate,
            "classification": "two-component 1+1D Soler solitary wave",
        },
        "refinement": {
            "levels": levels,
            "phase_orders": phase_orders,
            "density_orders": density_orders,
        },
        "window_study": windows,
        "perturbation": perturbed_metrics,
        "free_dirac_control": control_metrics,
        "gauge_covariance": {
            "norm_error": gauge_norm_error,
            "density_max_error": gauge_density_error,
            "covariant_energy_error": gauge_energy_error,
            "status": (
                "background pure-gauge connection only; "
                "no dynamical Maxwell field"
            ),
        },
        "entropic_clock": {
            "initial": {
                key: value
                for key, value in initial_clock.items()
                if key != "trajectory"
            },
            "final": {
                key: value
                for key, value in final_clock.items()
                if key != "trajectory"
            },
            "gauge_probability_max_error": float(
                np.max(np.abs(gauge_probability - baseline_probability))
            ),
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a localized two-component 1+1D spinor carrier",
                "second-order numerical return to the exact Soler profile",
                "short-time perturbation stability under the frozen test",
                "a local-U(1) covariant background-connection interface",
                "preservation of the M9 normalized-density clock interface",
            ],
            "does_not_establish": [
                "three-dimensional localization",
                "a dynamical Maxwell field",
                "an electric charge unit or electron identity",
                "quantized fermionic statistics",
                "unique CAT/EPT derivation of the Soler interaction",
            ],
        },
    }
