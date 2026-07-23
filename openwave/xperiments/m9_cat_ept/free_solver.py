"""One-dimensional free Schrödinger solver and Gaussian-packet benchmark.

The numerical method is Crank--Nicolson on a periodic second-order finite-
difference Laplacian. It is unitary for the discrete Hamiltonian, so discrete
norm and discrete energy are conserved up to linear-solver roundoff. Agreement
with the continuum Gaussian solution remains a separate convergence question.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csc_matrix, csr_matrix, diags, eye
from scipy.sparse.linalg import splu

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class GaussianPacket:
    """Parameters of a normalized minimum-uncertainty Gaussian packet."""

    sigma: float = 1.0
    center: float = -4.0
    wave_number: float = 1.5
    mass: float = 1.0
    hbar: float = 1.0

    def __post_init__(self) -> None:
        if self.sigma <= 0.0:
            raise ValueError("sigma must be positive")
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.hbar <= 0.0:
            raise ValueError("hbar must be positive")

    @property
    def group_velocity(self) -> float:
        return self.hbar * self.wave_number / self.mass

    @property
    def exact_energy(self) -> float:
        momentum_term = self.wave_number**2
        spread_term = 1.0 / (4.0 * self.sigma**2)
        return self.hbar**2 * (momentum_term + spread_term) / (2.0 * self.mass)


@dataclass(frozen=True)
class SolverConfig:
    """Periodic grid and time-stepping parameters."""

    half_width: float = 20.0
    points: int = 256
    final_time: float = 2.0
    dt_over_dx: float = 0.1

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 8:
            raise ValueError("points must be at least 8")
        if self.final_time < 0.0:
            raise ValueError("final_time must be nonnegative")
        if self.dt_over_dx <= 0.0:
            raise ValueError("dt_over_dx must be positive")


@dataclass(frozen=True)
class SolverRun:
    """Numerical state and the discrete operator used to evolve it."""

    x: RealArray
    initial_state: ComplexArray
    final_state: ComplexArray
    laplacian: csr_matrix
    dx: float
    dt: float
    steps: int
    packet: GaussianPacket
    config: SolverConfig


@dataclass(frozen=True)
class BenchmarkMetrics:
    """Diagnostics for one grid resolution."""

    points: int
    dx: float
    dt: float
    steps: int
    initial_norm: float
    final_norm: float
    norm_drift: float
    initial_discrete_energy: float
    final_discrete_energy: float
    discrete_energy_drift: float
    exact_continuum_energy: float
    continuum_energy_relative_error: float
    phase_aligned_l2_error: float
    direct_l2_error: float
    density_l1_error: float
    current_relative_l2_error: float
    overlap_fidelity: float
    overlap_phase_error: float
    mean_position_error: float
    variance_error: float
    edge_probability: float


@dataclass(frozen=True)
class RefinementResult:
    """Complete M9.2 refinement ledger and its acceptance status."""

    model: str
    equation: str
    method: str
    packet: dict[str, float]
    common_config: dict[str, float]
    levels: list[dict[str, Any]]
    observed_orders: dict[str, list[float]]
    acceptance: dict[str, bool]
    passed: bool
    scope: dict[str, Any]


def periodic_grid(config: SolverConfig) -> tuple[RealArray, float]:
    """Return the half-open periodic grid ``[-L, L)`` and its spacing."""
    dx = 2.0 * config.half_width / config.points
    x = -config.half_width + dx * np.arange(config.points, dtype=np.float64)
    return x, dx


def periodic_laplacian(points: int, dx: float) -> csr_matrix:
    """Return the second-order periodic finite-difference Laplacian."""
    if points < 3:
        raise ValueError("points must be at least 3")
    if dx <= 0.0:
        raise ValueError("dx must be positive")

    matrix = diags(
        (np.ones(points - 1), -2.0 * np.ones(points), np.ones(points - 1)),
        offsets=(-1, 0, 1),
        shape=(points, points),
        format="lil",
        dtype=np.float64,
    )
    matrix[0, points - 1] = 1.0
    matrix[points - 1, 0] = 1.0
    return matrix.tocsr() / dx**2


def analytic_gaussian_state(x: RealArray, time: float, packet: GaussianPacket) -> ComplexArray:
    """Evaluate the exact infinite-line free Gaussian wave packet."""
    beta = packet.hbar * time / (2.0 * packet.mass * packet.sigma**2)
    displacement = x - packet.center - packet.group_velocity * time
    normalization = (1.0 / (2.0 * math.pi * packet.sigma**2)) ** 0.25
    spreading = np.sqrt(1.0 + 1j * beta)
    envelope = np.exp(
        -(displacement**2) / (4.0 * packet.sigma**2 * (1.0 + 1j * beta))
    )
    phase = np.exp(
        1j
        * packet.wave_number
        * (x - packet.center - packet.group_velocity * time / 2.0)
    )
    return np.asarray(normalization * envelope * phase / spreading, dtype=np.complex128)


def analytic_gaussian_current(x: RealArray, time: float, packet: GaussianPacket) -> RealArray:
    """Return the exact probability current of the free Gaussian packet."""
    state = analytic_gaussian_state(x, time, packet)
    beta = packet.hbar * time / (2.0 * packet.mass * packet.sigma**2)
    displacement = x - packet.center - packet.group_velocity * time
    phase_gradient = packet.wave_number + beta * displacement / (
        2.0 * packet.sigma**2 * (1.0 + beta**2)
    )
    return np.asarray(
        np.abs(state) ** 2 * (packet.hbar / packet.mass) * phase_gradient,
        dtype=np.float64,
    )


def discrete_norm(state: ComplexArray, dx: float) -> float:
    return float(dx * np.sum(np.abs(state) ** 2))


def centered_derivative(state: ComplexArray, dx: float) -> ComplexArray:
    return np.asarray((np.roll(state, -1) - np.roll(state, 1)) / (2.0 * dx))


def probability_current(
    state: ComplexArray, dx: float, packet: GaussianPacket
) -> RealArray:
    derivative = centered_derivative(state, dx)
    return np.asarray(
        (packet.hbar / packet.mass) * np.imag(np.conj(state) * derivative),
        dtype=np.float64,
    )


def discrete_energy(
    state: ComplexArray, laplacian: csr_matrix, dx: float, packet: GaussianPacket
) -> float:
    coefficient = packet.hbar**2 / (2.0 * packet.mass)
    return float(np.real(dx * np.vdot(state, -coefficient * (laplacian @ state))))


def evolve_free_packet(packet: GaussianPacket, config: SolverConfig) -> SolverRun:
    """Evolve one packet with the periodic Crank--Nicolson scheme."""
    x, dx = periodic_grid(config)
    laplacian = periodic_laplacian(config.points, dx)
    initial_state = analytic_gaussian_state(x, 0.0, packet)

    if config.final_time == 0.0:
        return SolverRun(
            x=x,
            initial_state=initial_state,
            final_state=initial_state.copy(),
            laplacian=laplacian,
            dx=dx,
            dt=0.0,
            steps=0,
            packet=packet,
            config=config,
        )

    requested_dt = config.dt_over_dx * dx
    steps = max(1, math.ceil(config.final_time / requested_dt))
    dt = config.final_time / steps
    coefficient = packet.hbar * dt / (4.0 * packet.mass)
    identity: csc_matrix = eye(config.points, format="csc", dtype=np.complex128)
    left = (identity - 1j * coefficient * laplacian).tocsc()
    right = (identity + 1j * coefficient * laplacian).tocsr()
    solve_left = splu(left).solve

    state = initial_state.copy()
    for _ in range(steps):
        state = np.asarray(solve_left(right @ state), dtype=np.complex128)

    return SolverRun(
        x=x,
        initial_state=initial_state,
        final_state=state,
        laplacian=laplacian,
        dx=dx,
        dt=dt,
        steps=steps,
        packet=packet,
        config=config,
    )


def _l2_norm(values: NDArray[np.generic], dx: float) -> float:
    return float(math.sqrt(dx * np.sum(np.abs(values) ** 2)))


def _packet_moments(x: RealArray, state: ComplexArray, dx: float) -> tuple[float, float]:
    density = np.abs(state) ** 2
    norm = discrete_norm(state, dx)
    mean = float(dx * np.sum(x * density) / norm)
    variance = float(dx * np.sum((x - mean) ** 2 * density) / norm)
    return mean, variance


def benchmark_metrics(run: SolverRun) -> BenchmarkMetrics:
    """Compare one numerical run with the exact infinite-line solution."""
    exact = analytic_gaussian_state(run.x, run.config.final_time, run.packet)
    overlap = run.dx * np.vdot(exact, run.final_state)
    aligned = run.final_state * np.exp(-1j * np.angle(overlap))

    initial_norm = discrete_norm(run.initial_state, run.dx)
    final_norm = discrete_norm(run.final_state, run.dx)
    exact_norm = discrete_norm(exact, run.dx)
    initial_energy = discrete_energy(
        run.initial_state, run.laplacian, run.dx, run.packet
    )
    final_energy = discrete_energy(run.final_state, run.laplacian, run.dx, run.packet)
    exact_energy = run.packet.exact_energy

    numerical_density = np.abs(run.final_state) ** 2
    exact_density = np.abs(exact) ** 2
    numerical_current = probability_current(run.final_state, run.dx, run.packet)
    exact_current = analytic_gaussian_current(run.x, run.config.final_time, run.packet)
    current_scale = _l2_norm(exact_current, run.dx)

    mean, variance = _packet_moments(run.x, run.final_state, run.dx)
    beta = run.packet.hbar * run.config.final_time / (
        2.0 * run.packet.mass * run.packet.sigma**2
    )
    exact_mean = run.packet.center + run.packet.group_velocity * run.config.final_time
    exact_variance = run.packet.sigma**2 * (1.0 + beta**2)

    edge_count = max(1, run.config.points // 10)
    edge_probability = run.dx * (
        np.sum(numerical_density[:edge_count])
        + np.sum(numerical_density[-edge_count:])
    )

    return BenchmarkMetrics(
        points=run.config.points,
        dx=run.dx,
        dt=run.dt,
        steps=run.steps,
        initial_norm=initial_norm,
        final_norm=final_norm,
        norm_drift=abs(final_norm - initial_norm),
        initial_discrete_energy=initial_energy,
        final_discrete_energy=final_energy,
        discrete_energy_drift=abs(final_energy - initial_energy),
        exact_continuum_energy=exact_energy,
        continuum_energy_relative_error=abs(final_energy - exact_energy) / exact_energy,
        phase_aligned_l2_error=_l2_norm(aligned - exact, run.dx),
        direct_l2_error=_l2_norm(run.final_state - exact, run.dx),
        density_l1_error=float(run.dx * np.sum(np.abs(numerical_density - exact_density))),
        current_relative_l2_error=_l2_norm(numerical_current - exact_current, run.dx)
        / current_scale,
        overlap_fidelity=float(abs(overlap) ** 2 / (final_norm * exact_norm)),
        overlap_phase_error=float(np.angle(overlap)),
        mean_position_error=abs(mean - exact_mean),
        variance_error=abs(variance - exact_variance),
        edge_probability=float(edge_probability),
    )


def _observed_orders(levels: Sequence[BenchmarkMetrics], field: str) -> list[float]:
    orders: list[float] = []
    for coarse, fine in zip(levels[:-1], levels[1:], strict=True):
        coarse_error = float(getattr(coarse, field))
        fine_error = float(getattr(fine, field))
        orders.append(math.log(coarse_error / fine_error, 2.0))
    return orders


def run_refinement_study(
    points: Sequence[int] = (128, 256, 512),
    packet: GaussianPacket | None = None,
    *,
    half_width: float = 20.0,
    final_time: float = 2.0,
    dt_over_dx: float = 0.1,
) -> RefinementResult:
    """Run the deterministic M9.2 benchmark and evaluate its frozen gates."""
    selected_packet = packet or GaussianPacket()
    if len(points) < 3:
        raise ValueError("at least three refinement levels are required")
    if any(
        fine != 2 * coarse
        for coarse, fine in zip(points[:-1], points[1:], strict=True)
    ):
        raise ValueError("refinement points must double at each level")

    metrics = [
        benchmark_metrics(
            evolve_free_packet(
                selected_packet,
                SolverConfig(
                    half_width=half_width,
                    points=level_points,
                    final_time=final_time,
                    dt_over_dx=dt_over_dx,
                ),
            )
        )
        for level_points in points
    ]

    phase_orders = _observed_orders(metrics, "phase_aligned_l2_error")
    density_orders = _observed_orders(metrics, "density_l1_error")
    current_orders = _observed_orders(metrics, "current_relative_l2_error")
    finest = metrics[-1]

    acceptance = {
        "discrete_norm_conserved": max(level.norm_drift for level in metrics) <= 1.0e-12,
        "discrete_energy_conserved": max(
            level.discrete_energy_drift for level in metrics
        )
        <= 1.0e-12,
        "second_order_phase_convergence": min(phase_orders) >= 1.8,
        "second_order_density_convergence": min(density_orders) >= 1.8,
        "second_order_current_convergence": min(current_orders) >= 1.8,
        "finest_density_l1_below_1e-2": finest.density_l1_error <= 1.0e-2,
        "finest_current_relative_l2_below_1e-2": (
            finest.current_relative_l2_error <= 1.0e-2
        ),
        "finest_fidelity_above_0_9999": finest.overlap_fidelity >= 0.9999,
        "finest_phase_error_below_1e-2": abs(finest.overlap_phase_error) <= 1.0e-2,
        "finest_energy_relative_error_below_5e-3": (
            finest.continuum_energy_relative_error <= 5.0e-3
        ),
        "packet_does_not_reach_periodic_edge": finest.edge_probability <= 1.0e-12,
    }

    return RefinementResult(
        model="M9-CAT-EPT",
        equation="i hbar d_t psi = -(hbar^2 / 2m) d_xx psi",
        method="periodic second-order finite differences + Crank--Nicolson",
        packet=asdict(selected_packet),
        common_config={
            "half_width": half_width,
            "final_time": final_time,
            "dt_over_dx": dt_over_dx,
        },
        levels=[asdict(level) for level in metrics],
        observed_orders={
            "phase_aligned_l2": phase_orders,
            "density_l1": density_orders,
            "current_relative_l2": current_orders,
        },
        acceptance=acceptance,
        passed=all(acceptance.values()),
        scope={
            "establishes": (
                "Second-order convergence to the analytic free Gaussian packet, with "
                "discrete norm and energy conservation for the tested solver."
            ),
            "does_not_establish": [
                "a localized stationary particle",
                "a nonlinear CAT/EPT dynamics",
                "a monotone entropic clock",
                "charge, spin, mass prediction, or experimental agreement",
            ],
        },
    )
