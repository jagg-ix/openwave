"""Fixed coarse-graining maps and distinct entropic-clock diagnostics for M9.3.

The physical field-to-probability map is fixed as cell probability
``p_i = dx |psi_i|^2 / sum_j dx |psi_j|^2``.  Irreversible ordering is then
measured along repeated applications of one explicitly declared, doubly
stochastic Markov channel.  Channel depth is not identified with physical time.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .free_solver import GaussianPacket, SolverConfig, evolve_free_packet

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class PeriodicCoarseGraining:
    """Nearest-neighbor periodic Markov channel fixed before inspecting results."""

    left: float = 0.25
    center: float = 0.50
    right: float = 0.25
    steps: int = 64
    gamma: float = 1.0

    def __post_init__(self) -> None:
        weights = (self.left, self.center, self.right)
        if any(weight < 0.0 for weight in weights):
            raise ValueError("channel weights must be nonnegative")
        if not math.isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1.0e-15):
            raise ValueError("channel weights must sum to 1")
        if self.steps < 1:
            raise ValueError("steps must be positive")
        if self.gamma <= 0.0:
            raise ValueError("gamma must be positive")


def state_probability(state: NDArray[np.complex128], dx: float) -> RealArray:
    """Map a lattice wave function to normalized cell probabilities."""
    mass = np.asarray(dx * np.abs(state) ** 2, dtype=np.float64)
    total = float(np.sum(mass))
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("state must have finite positive norm")
    probability = mass / total
    if np.any(probability < 0.0):
        raise ValueError("probability must be nonnegative")
    return probability


def uniform_reference(size: int) -> RealArray:
    """Return the uniform probability on the periodic lattice."""
    if size < 2:
        raise ValueError("size must be at least 2")
    return np.full(size, 1.0 / size, dtype=np.float64)


def apply_periodic_channel(
    probability: RealArray,
    channel: PeriodicCoarseGraining,
) -> RealArray:
    """Apply ``K = 1/4 shift_left + 1/2 id + 1/4 shift_right``."""
    p = np.asarray(probability, dtype=np.float64)
    if p.ndim != 1 or p.size < 2:
        raise ValueError("probability must be a one-dimensional vector")
    if np.any(p < 0.0):
        raise ValueError("probability must be nonnegative")
    total = float(np.sum(p))
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("probability must sum to 1")

    q = (
        channel.left * np.roll(p, 1)
        + channel.center * p
        + channel.right * np.roll(p, -1)
    )
    q = np.asarray(q, dtype=np.float64)
    q /= float(np.sum(q))
    return q


def kl_divergence(probability: RealArray, reference: RealArray) -> float:
    """Return finite discrete ``D_KL(probability || reference)``."""
    p = np.asarray(probability, dtype=np.float64)
    q = np.asarray(reference, dtype=np.float64)
    if p.shape != q.shape:
        raise ValueError("probability and reference must have the same shape")
    if np.any(p < 0.0) or np.any(q <= 0.0):
        raise ValueError("invalid KL inputs")
    mask = p > 0.0
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def shannon_entropy(probability: RealArray) -> float:
    """Return the natural-log Shannon entropy."""
    p = np.asarray(probability, dtype=np.float64)
    mask = p > 0.0
    return float(-np.sum(p[mask] * np.log(p[mask])))


def channel_total_correlation(
    probability: RealArray,
    channel: PeriodicCoarseGraining,
) -> float:
    """Return ``I(X;Y)`` for ``p(x) K(y|x)`` without a dense joint table."""
    p = np.asarray(probability, dtype=np.float64)
    q = apply_periodic_channel(p, channel)
    total = 0.0
    for offset, weight in (
        (-1, channel.left),
        (0, channel.center),
        (1, channel.right),
    ):
        if weight == 0.0:
            continue
        destination = np.roll(q, -offset)
        mask = p > 0.0
        total += float(
            np.sum(p[mask] * weight * np.log(weight / destination[mask]))
        )
    return 0.0 if abs(total) < 1.0e-14 else total


def snapshot_clock_trajectory(
    probability: RealArray,
    channel: PeriodicCoarseGraining,
) -> dict[str, Any]:
    """Measure three distinct clocks along repeated channel application."""
    uniform = uniform_reference(probability.size)
    initial_remaining = kl_divergence(probability, uniform)
    current = np.asarray(probability, dtype=np.float64).copy()
    records: list[dict[str, float | int]] = []

    for depth in range(channel.steps + 1):
        remaining = kl_divergence(current, uniform)
        gain = initial_remaining - remaining
        correlation = channel_total_correlation(current, channel)
        records.append(
            {
                "depth": depth,
                "remaining_disequilibrium": remaining,
                "accumulated_gain": gain,
                "total_correlation_next_step": correlation,
                "entropy": shannon_entropy(current),
                "remaining_weight_norm": math.exp(-channel.gamma * remaining),
                "accumulated_weight_norm": math.exp(-channel.gamma * gain),
            }
        )
        if depth < channel.steps:
            current = apply_periodic_channel(current, channel)

    remaining_values = [record["remaining_disequilibrium"] for record in records]
    gain_values = [record["accumulated_gain"] for record in records]
    correlation_values = [record["total_correlation_next_step"] for record in records]
    closure = max(
        abs(initial_remaining - (remaining + gain))
        for remaining, gain in zip(
            remaining_values,
            gain_values,
            strict=True,
        )
    )

    return {
        "initial_remaining_disequilibrium": initial_remaining,
        "terminal_remaining_disequilibrium": remaining_values[-1],
        "terminal_accumulated_gain": gain_values[-1],
        "terminal_total_correlation": correlation_values[-1],
        "max_ledger_closure_error": closure,
        "remaining_nonincreasing": all(
            later <= earlier + 1.0e-13
            for earlier, later in zip(
                remaining_values[:-1],
                remaining_values[1:],
                strict=True,
            )
        ),
        "gain_nondecreasing": all(
            later + 1.0e-13 >= earlier
            for earlier, later in zip(
                gain_values[:-1],
                gain_values[1:],
                strict=True,
            )
        ),
        "correlation_nonnegative": all(
            value >= -1.0e-12 for value in correlation_values
        ),
        "trajectory": records,
    }


def run_entropic_clock_study() -> dict[str, Any]:
    """Run the frozen M9.3 map on the initial and final M9.2 snapshots."""
    packet = GaussianPacket()
    config = SolverConfig(
        points=512,
        half_width=20.0,
        final_time=2.0,
        dt_over_dx=0.1,
    )
    run = evolve_free_packet(packet, config)
    channel = PeriodicCoarseGraining()
    initial_probability = state_probability(run.initial_state, run.dx)
    final_probability = state_probability(run.final_state, run.dx)
    uniform = uniform_reference(config.points)
    uniform_after = apply_periodic_channel(uniform, channel)

    snapshots = {
        "initial": snapshot_clock_trajectory(initial_probability, channel),
        "final": snapshot_clock_trajectory(final_probability, channel),
    }
    acceptance = {
        "channel_preserves_uniform": (
            float(np.max(np.abs(uniform_after - uniform))) <= 1.0e-15
        ),
        "initial_remaining_contracts": snapshots["initial"][
            "remaining_nonincreasing"
        ],
        "final_remaining_contracts": snapshots["final"][
            "remaining_nonincreasing"
        ],
        "initial_gain_accumulates": snapshots["initial"]["gain_nondecreasing"],
        "final_gain_accumulates": snapshots["final"]["gain_nondecreasing"],
        "initial_correlation_nonnegative": snapshots["initial"][
            "correlation_nonnegative"
        ],
        "final_correlation_nonnegative": snapshots["final"][
            "correlation_nonnegative"
        ],
        "initial_ledger_closes": (
            snapshots["initial"]["max_ledger_closure_error"] <= 1.0e-12
        ),
        "final_ledger_closes": (
            snapshots["final"]["max_ledger_closure_error"] <= 1.0e-12
        ),
        "initial_terminal_gain_positive": (
            snapshots["initial"]["terminal_accumulated_gain"] > 0.0
        ),
        "final_terminal_gain_positive": (
            snapshots["final"]["terminal_accumulated_gain"] > 0.0
        ),
    }

    return {
        "schema": "openwave.m9.entropic-clock-result.v1",
        "model": "M9-CAT-EPT",
        "field_to_probability": (
            "p_i = dx |psi_i|^2 / sum_j dx |psi_j|^2"
        ),
        "coarse_graining": (
            "(Kp)_i = 1/4 p_{i-1} + 1/2 p_i + 1/4 p_{i+1}, periodic"
        ),
        "channel": asdict(channel),
        "solver": {
            "points": config.points,
            "half_width": config.half_width,
            "final_time": config.final_time,
            "dt_over_dx": config.dt_over_dx,
        },
        "snapshots": snapshots,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "scope": {
            "establishes": (
                "Data-processing clocks along a fixed coarse-graining depth "
                "for two unitary snapshots."
            ),
            "does_not_establish": [
                "monotonicity in physical time",
                "irreversible back-reaction",
                "particle localization",
                "a unique coarse-graining map",
            ],
        },
    }
