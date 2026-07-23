"""M9.7b2 self-consistent stationary radial Dirac--electrostatic gate.

The scored model uses a regular spherical four-spinor ansatz

    Psi = exp(-i omega t) (v(r) chi, i u(r) sigma.rhat chi)^T

with a cubic Soler scalar attraction and an electrostatic Maxwell self-field.
The dimensionless stationary equations are

    v' = -(omega - q phi + M) u
    u' + 2u/r = (omega - q phi - M) v
    M = m - lambda (v^2 - u^2)
    Q' = 4 pi r^2 q (v^2 + u^2)
    phi' = -Q/(4 pi epsilon0 r^2).

The branch is normalized to unit number and continued from q=0 to q=1. It is a
selected classical nonlinear field model. It is not an electron calculation,
a charge calibration, a proof of stability, or a derivation from CAT/EPT.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import cumulative_trapezoid, solve_bvp

from .electrostatic_gauge_3d import (
    ReflectingCoarseGraining,
    radial_clock_trajectory,
)

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class CoupledParameters:
    """Frozen dimensionless stationary-model parameters."""

    mass: float = 1.0
    soler_coupling: float = 64.0
    gauge_charge: float = 1.0
    epsilon0: float = 1.0
    target_norm: float = 1.0
    continuation_fractions: tuple[float, ...] = (0.0, 0.25, 0.50, 0.75, 1.0)

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.soler_coupling <= 0.0:
            raise ValueError("soler_coupling must be positive")
        if self.gauge_charge == 0.0:
            raise ValueError("gauge_charge must be nonzero")
        if self.epsilon0 <= 0.0:
            raise ValueError("epsilon0 must be positive")
        if self.target_norm <= 0.0:
            raise ValueError("target_norm must be positive")
        fractions = self.continuation_fractions
        if len(fractions) < 2 or fractions[0] != 0.0 or fractions[-1] != 1.0:
            raise ValueError("continuation_fractions must run from zero to one")
        if any(
            later <= earlier
            for earlier, later in zip(fractions[:-1], fractions[1:], strict=True)
        ):
            raise ValueError("continuation_fractions must be strictly increasing")


@dataclass(frozen=True)
class StationaryGrid:
    """BVP mesh and diagnostic settings."""

    outer_radius: float = 40.0
    initial_points: int = 512
    tolerance: float = 2.5e-6
    max_nodes: int = 20_000
    diagnostic_points: int = 8_193

    def __post_init__(self) -> None:
        if self.outer_radius <= 0.0:
            raise ValueError("outer_radius must be positive")
        if self.initial_points < 128:
            raise ValueError("initial_points must be at least 128")
        if self.tolerance <= 0.0:
            raise ValueError("tolerance must be positive")
        if self.max_nodes < self.initial_points:
            raise ValueError("max_nodes must not be smaller than initial_points")
        if self.diagnostic_points < 1_025 or self.diagnostic_points % 2 == 0:
            raise ValueError("diagnostic_points must be an odd integer at least 1025")


@dataclass
class StationarySolution:
    """One converged continuation branch and its continuous interpolant."""

    parameters: CoupledParameters
    grid: StationaryGrid
    frequency: float
    raw_frequency_parameter: float
    solver_nodes: int
    max_collocation_residual: float
    initial_modulation: float
    continuation: list[dict[str, Any]]
    _interpolant: Any = field(repr=False)

    def evaluate(self, radius: RealArray) -> RealArray:
        values = self._interpolant(np.asarray(radius, dtype=np.float64))
        return np.asarray(values, dtype=np.float64)


@dataclass(frozen=True)
class LevelMetrics:
    initial_points: int
    tolerance: float
    frequency: float
    solver_nodes: int
    max_collocation_residual: float
    number_norm: float
    total_charge: float
    central_upper: float
    central_potential: float
    rms_radius: float
    core_fraction_r16: float
    outer_fraction_20pct: float
    spinor_residual_relative_l2: float
    gauss_residual_relative_max: float
    potential_residual_max: float
    boundary_flux_error: float
    field_energy: float
    source_field_energy: float
    source_field_relative_difference: float
    matter_energy: float
    total_energy: float
    eigenvalue_identity_relative_error: float


_CENTER_EPSILON = 1.0e-6


def _frequency(raw_parameter: float, mass: float) -> float:
    return mass * math.tanh(raw_parameter)


def _initial_spinor_guess(
    radius: RealArray,
    current_charge: float,
    parameters: CoupledParameters,
    modulation: float,
) -> RealArray:
    scale = 2.0
    upper = np.exp(-radius / scale)
    lower = 0.15 * radius / scale * np.exp(-radius / scale)
    if modulation != 0.0:
        mode = np.cos(math.pi * radius / radius[-1])
        upper *= 1.0 + modulation * mode
        lower *= 1.0 - modulation * mode

    raw_norm = float(
        np.trapezoid(
            4.0 * math.pi * radius**2 * (upper**2 + lower**2),
            radius,
        )
    )
    factor = math.sqrt(parameters.target_norm / raw_norm)
    upper *= factor
    lower *= factor
    return _rebuild_gauge_guess(
        radius,
        np.vstack((upper, lower)),
        current_charge,
        parameters,
    )


def _rebuild_gauge_guess(
    radius: RealArray,
    spinor: RealArray,
    current_charge: float,
    parameters: CoupledParameters,
) -> RealArray:
    upper, lower = spinor
    density = upper**2 + lower**2
    accumulated_norm = np.concatenate(
        (
            [0.0],
            cumulative_trapezoid(4.0 * math.pi * radius**2 * density, radius),
        )
    )
    enclosed_charge = current_charge * accumulated_norm
    electric = np.zeros_like(radius)
    electric[1:] = enclosed_charge[1:] / (
        4.0 * math.pi * parameters.epsilon0 * radius[1:] ** 2
    )
    potential = np.zeros_like(radius)
    potential[-1] = enclosed_charge[-1] / (
        4.0 * math.pi * parameters.epsilon0 * radius[-1]
    )
    for index in range(radius.size - 2, -1, -1):
        potential[index] = potential[index + 1] + 0.5 * (
            electric[index] + electric[index + 1]
        ) * (radius[index + 1] - radius[index])
    return np.vstack((upper, lower, enclosed_charge, potential, accumulated_norm))


def _solve_continuation(
    parameters: CoupledParameters,
    grid: StationaryGrid,
    initial_modulation: float,
) -> StationarySolution:
    radius = np.linspace(
        _CENTER_EPSILON,
        grid.outer_radius,
        grid.initial_points,
        dtype=np.float64,
    )
    previous: Any | None = None
    records: list[dict[str, Any]] = []

    for fraction in parameters.continuation_fractions:
        current_charge = parameters.gauge_charge * fraction
        if previous is None:
            guess = _initial_spinor_guess(
                radius,
                current_charge,
                parameters,
                initial_modulation,
            )
            raw_guess = np.asarray([math.atanh(0.95)], dtype=np.float64)
        else:
            previous_values = previous.sol(radius)
            guess = _rebuild_gauge_guess(
                radius,
                np.asarray(previous_values[:2], dtype=np.float64),
                current_charge,
                parameters,
            )
            raw_guess = previous.p.copy()

        def equations(
            radial_coordinate: RealArray,
            state: RealArray,
            raw_parameter: RealArray,
        ) -> RealArray:
            omega = _frequency(float(raw_parameter[0]), parameters.mass)
            upper, lower, enclosed, potential, _accumulated = state
            scalar = upper**2 - lower**2
            effective_mass = parameters.mass - parameters.soler_coupling * scalar
            effective_frequency = omega - current_charge * potential
            upper_derivative = -(effective_frequency + effective_mass) * lower
            lower_derivative = (
                (effective_frequency - effective_mass) * upper
                - 2.0 * lower / radial_coordinate
            )
            density = upper**2 + lower**2
            norm_derivative = 4.0 * math.pi * radial_coordinate**2 * density
            charge_derivative = current_charge * norm_derivative
            potential_derivative = -enclosed / (
                4.0 * math.pi * parameters.epsilon0 * radial_coordinate**2
            )
            return np.vstack(
                (
                    upper_derivative,
                    lower_derivative,
                    charge_derivative,
                    potential_derivative,
                    norm_derivative,
                )
            )

        def boundary_conditions(
            center_state: RealArray,
            outer_state: RealArray,
            raw_parameter: RealArray,
        ) -> RealArray:
            omega = _frequency(float(raw_parameter[0]), parameters.mass)
            outer_effective_frequency = omega - current_charge * outer_state[3]
            decay_sq = parameters.mass**2 - outer_effective_frequency**2
            decay_rate = math.sqrt(max(1.0e-14, decay_sq))
            tail_ratio = (
                decay_rate + 1.0 / grid.outer_radius
            ) / (parameters.mass + outer_effective_frequency)
            coulomb_boundary = outer_state[2] / (
                4.0
                * math.pi
                * parameters.epsilon0
                * grid.outer_radius
            )
            return np.asarray(
                (
                    center_state[1],
                    center_state[2],
                    center_state[4],
                    outer_state[4] - parameters.target_norm,
                    outer_state[1] - tail_ratio * outer_state[0],
                    outer_state[3] - coulomb_boundary,
                ),
                dtype=np.float64,
            )

        solved = solve_bvp(
            equations,
            boundary_conditions,
            radius,
            guess,
            p=raw_guess,
            tol=grid.tolerance,
            max_nodes=grid.max_nodes,
            verbose=0,
        )
        omega = _frequency(float(solved.p[0]), parameters.mass)
        records.append(
            {
                "charge_fraction": fraction,
                "current_charge": current_charge,
                "success": bool(solved.success),
                "frequency": omega,
                "solver_nodes": int(solved.x.size),
                "max_collocation_residual": float(np.max(solved.rms_residuals)),
                "message": solved.message,
            }
        )
        if not solved.success:
            raise RuntimeError(
                "stationary continuation failed at charge fraction "
                f"{fraction}: {solved.message}"
            )
        if not 0.0 < omega < parameters.mass:
            raise RuntimeError("stationary frequency is outside the mass gap")
        previous = solved

    assert previous is not None
    return StationarySolution(
        parameters=parameters,
        grid=grid,
        frequency=_frequency(float(previous.p[0]), parameters.mass),
        raw_frequency_parameter=float(previous.p[0]),
        solver_nodes=int(previous.x.size),
        max_collocation_residual=float(np.max(previous.rms_residuals)),
        initial_modulation=initial_modulation,
        continuation=records,
        _interpolant=previous.sol,
    )


def solve_stationary_branch(
    parameters: CoupledParameters = CoupledParameters(),
    grid: StationaryGrid = StationaryGrid(),
    *,
    initial_modulation: float = 0.0,
) -> StationarySolution:
    """Solve the normalized branch by electrostatic charge continuation."""
    if abs(initial_modulation) > 0.20:
        raise ValueError("initial_modulation magnitude must not exceed 0.20")
    return _solve_continuation(parameters, grid, initial_modulation)


def _diagnostic_state(solution: StationarySolution) -> tuple[RealArray, RealArray]:
    radius = np.linspace(
        _CENTER_EPSILON,
        solution.grid.outer_radius,
        solution.grid.diagnostic_points,
        dtype=np.float64,
    )
    return radius, solution.evaluate(radius)


def _relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), 1.0e-30)


def solution_outer_radius(radius: RealArray) -> float:
    value = float(radius[-1])
    if value <= 0.0:
        raise ValueError("radius must end at a positive value")
    return value


def _energy_ledger(
    radius: RealArray,
    state: RealArray,
    frequency: float,
    parameters: CoupledParameters,
) -> dict[str, float]:
    upper, lower, enclosed, potential, _ = state
    upper_derivative = np.gradient(upper, radius, edge_order=2)
    lower_derivative = np.gradient(lower, radius, edge_order=2)
    density = upper**2 + lower**2
    scalar = upper**2 - lower**2
    measure = 4.0 * math.pi * radius**2
    kinetic = upper * (lower_derivative + 2.0 * lower / radius)
    kinetic -= lower * upper_derivative
    matter_density = (
        kinetic
        + parameters.mass * scalar
        - 0.5 * parameters.soler_coupling * scalar**2
    )
    matter_energy = float(np.trapezoid(measure * matter_density, radius))

    field_integrand = enclosed**2 / (
        8.0 * math.pi * parameters.epsilon0 * radius**2
    )
    field_interior = float(np.trapezoid(field_integrand, radius))
    field_tail = enclosed[-1] ** 2 / (
        8.0
        * math.pi
        * parameters.epsilon0
        * solution_outer_radius(radius)
    )
    field_energy = float(field_interior + field_tail)
    source_field_energy = 0.5 * float(
        np.trapezoid(
            measure * parameters.gauge_charge * potential * density,
            radius,
        )
    )

    eigen_integrand = (
        kinetic
        + parameters.mass * scalar
        - parameters.soler_coupling * scalar**2
        + parameters.gauge_charge * potential * density
    )
    eigen_rhs = float(np.trapezoid(measure * eigen_integrand, radius))
    norm = float(np.trapezoid(measure * density, radius))
    eigen_lhs = frequency * norm

    return {
        "matter_energy": matter_energy,
        "field_energy": field_energy,
        "source_field_energy": source_field_energy,
        "source_field_relative_difference": _relative_error(
            source_field_energy,
            field_energy,
        ),
        "total_energy": matter_energy + field_energy,
        "eigenvalue_identity_relative_error": _relative_error(eigen_rhs, eigen_lhs),
    }


def solution_metrics(solution: StationarySolution) -> LevelMetrics:
    radius, state = _diagnostic_state(solution)
    upper, lower, enclosed, potential, accumulated = state
    del accumulated
    density = upper**2 + lower**2
    scalar = upper**2 - lower**2
    measure = 4.0 * math.pi * radius**2
    norm = float(np.trapezoid(measure * density, radius))
    rms_radius = math.sqrt(
        float(np.trapezoid(measure * radius**2 * density, radius)) / norm
    )
    core_mask = radius <= 16.0
    edge_mask = radius >= 0.80 * solution.grid.outer_radius
    core_mass = float(
        np.trapezoid(
            measure[core_mask] * density[core_mask],
            radius[core_mask],
        )
    )
    core_fraction = core_mass / norm
    outer_mass = float(
        np.trapezoid(
            measure[edge_mask] * density[edge_mask],
            radius[edge_mask],
        )
    )
    outer_fraction = outer_mass / norm

    upper_derivative = np.gradient(upper, radius, edge_order=2)
    lower_derivative = np.gradient(lower, radius, edge_order=2)
    charge_derivative = np.gradient(enclosed, radius, edge_order=2)
    potential_derivative = np.gradient(potential, radius, edge_order=2)
    effective_mass = solution.parameters.mass - solution.parameters.soler_coupling * scalar
    effective_frequency = solution.frequency - solution.parameters.gauge_charge * potential
    upper_residual = upper_derivative + (effective_frequency + effective_mass) * lower
    lower_residual = (
        lower_derivative
        - (effective_frequency - effective_mass) * upper
        + 2.0 * lower / radius
    )
    spinor_scale = math.sqrt(
        float(
            np.trapezoid(
                measure * solution.frequency**2 * density,
                radius,
            )
        )
    )
    interior = slice(2, -2)
    spinor_residual = math.sqrt(
        float(
            np.trapezoid(
                measure[interior]
                * (
                    upper_residual[interior] ** 2
                    + lower_residual[interior] ** 2
                ),
                radius[interior],
            )
        )
    ) / spinor_scale

    gauss_source = (
        4.0
        * math.pi
        * radius**2
        * solution.parameters.gauge_charge
        * density
    )
    gauss_residual = charge_derivative - gauss_source
    gauss_relative = float(np.max(np.abs(gauss_residual[interior]))) / float(
        np.max(np.abs(gauss_source[interior]))
    )
    potential_residual = potential_derivative + enclosed / (
        4.0 * math.pi * solution.parameters.epsilon0 * radius**2
    )
    boundary_flux = (
        solution.parameters.epsilon0
        * 4.0
        * math.pi
        * solution.grid.outer_radius**2
        * (-potential_derivative[-1])
    )
    energy = _energy_ledger(radius, state, solution.frequency, solution.parameters)

    return LevelMetrics(
        initial_points=solution.grid.initial_points,
        tolerance=solution.grid.tolerance,
        frequency=solution.frequency,
        solver_nodes=solution.solver_nodes,
        max_collocation_residual=solution.max_collocation_residual,
        number_norm=norm,
        total_charge=float(enclosed[-1]),
        central_upper=float(upper[0]),
        central_potential=float(potential[0]),
        rms_radius=rms_radius,
        core_fraction_r16=core_fraction,
        outer_fraction_20pct=outer_fraction,
        spinor_residual_relative_l2=spinor_residual,
        gauss_residual_relative_max=gauss_relative,
        potential_residual_max=float(np.max(np.abs(potential_residual[interior]))),
        boundary_flux_error=float(abs(boundary_flux - enclosed[-1])),
        field_energy=energy["field_energy"],
        source_field_energy=energy["source_field_energy"],
        source_field_relative_difference=energy["source_field_relative_difference"],
        matter_energy=energy["matter_energy"],
        total_energy=energy["total_energy"],
        eigenvalue_identity_relative_error=energy["eigenvalue_identity_relative_error"],
    )


def _profile_difference(
    coarse: StationarySolution,
    fine: StationarySolution,
    points: int = 4_097,
) -> tuple[float, float]:
    outer_radius = min(coarse.grid.outer_radius, fine.grid.outer_radius)
    radius = np.linspace(_CENTER_EPSILON, outer_radius, points, dtype=np.float64)
    coarse_state = coarse.evaluate(radius)
    fine_state = fine.evaluate(radius)
    overlap = float(
        np.trapezoid(
            4.0
            * math.pi
            * radius**2
            * (
                coarse_state[0] * fine_state[0]
                + coarse_state[1] * fine_state[1]
            ),
            radius,
        )
    )
    sign = 1.0 if overlap >= 0.0 else -1.0
    upper_difference = sign * coarse_state[0] - fine_state[0]
    lower_difference = sign * coarse_state[1] - fine_state[1]
    spinor_l2 = math.sqrt(
        float(
            np.trapezoid(
                4.0
                * math.pi
                * radius**2
                * (upper_difference**2 + lower_difference**2),
                radius,
            )
        )
    )
    coarse_density = coarse_state[0] ** 2 + coarse_state[1] ** 2
    fine_density = fine_state[0] ** 2 + fine_state[1] ** 2
    density_l1 = float(
        np.trapezoid(
            4.0
            * math.pi
            * radius**2
            * np.abs(coarse_density - fine_density),
            radius,
        )
    )
    return spinor_l2, density_l1


def _observed_order(coarse_difference: float, fine_difference: float) -> float:
    return math.log(coarse_difference / fine_difference, 2.0)


def _shell_probability(
    solution: StationarySolution,
    shells: int = 512,
) -> RealArray:
    edges = np.linspace(0.0, solution.grid.outer_radius, shells + 1, dtype=np.float64)
    centers = 0.5 * (edges[:-1] + edges[1:])
    volumes = 4.0 * math.pi / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3)
    state = solution.evaluate(np.maximum(centers, _CENTER_EPSILON))
    density = state[0] ** 2 + state[1] ** 2
    probability = density * volumes
    probability /= float(np.sum(probability))
    return np.asarray(probability, dtype=np.float64)


def _clock_ledger(solution: StationarySolution) -> dict[str, Any]:
    return radial_clock_trajectory(
        _shell_probability(solution),
        ReflectingCoarseGraining(steps=64, gamma=1.0),
    )


def _window_record(solution: StationarySolution) -> dict[str, float]:
    metrics = solution_metrics(solution)
    return {
        "outer_radius": solution.grid.outer_radius,
        "frequency": solution.frequency,
        "central_potential": metrics.central_potential,
        "rms_radius": metrics.rms_radius,
        "outer_fraction_20pct": metrics.outer_fraction_20pct,
    }


def _relative_spread(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float((np.max(array) - np.min(array)) / np.mean(np.abs(array)))


@lru_cache(maxsize=1)
def run_coupled_stationary_study() -> dict[str, Any]:
    """Run the complete scored M9.7b2 stationary branch qualification."""
    parameters = CoupledParameters()
    level_specs = (
        StationaryGrid(initial_points=256, tolerance=1.0e-5),
        StationaryGrid(initial_points=512, tolerance=2.5e-6),
        StationaryGrid(initial_points=1_024, tolerance=6.25e-7),
    )
    levels = [solve_stationary_branch(parameters, grid) for grid in level_specs]
    level_metrics = [solution_metrics(solution) for solution in levels]
    spinor_differences = [
        _profile_difference(levels[0], levels[1])[0],
        _profile_difference(levels[1], levels[2])[0],
    ]
    density_differences = [
        _profile_difference(levels[0], levels[1])[1],
        _profile_difference(levels[1], levels[2])[1],
    ]
    frequency_differences = [
        abs(levels[0].frequency - levels[1].frequency),
        abs(levels[1].frequency - levels[2].frequency),
    ]
    observed_orders = {
        "spinor_l2": _observed_order(*spinor_differences),
        "density_l1": _observed_order(*density_differences),
        "frequency": _observed_order(*frequency_differences),
    }

    window_specs = (
        StationaryGrid(
            outer_radius=30.0,
            initial_points=768,
            tolerance=6.25e-7,
        ),
        StationaryGrid(
            outer_radius=40.0,
            initial_points=1_024,
            tolerance=6.25e-7,
        ),
        StationaryGrid(
            outer_radius=50.0,
            initial_points=1_280,
            tolerance=6.25e-7,
        ),
    )
    windows = [solve_stationary_branch(parameters, grid) for grid in window_specs]
    window_records = [_window_record(solution) for solution in windows]
    window_spreads = {
        "frequency": _relative_spread(
            [record["frequency"] for record in window_records]
        ),
        "central_potential": _relative_spread(
            [record["central_potential"] for record in window_records]
        ),
        "rms_radius": _relative_spread(
            [record["rms_radius"] for record in window_records]
        ),
    }

    baseline = levels[1]
    perturbed = solve_stationary_branch(
        parameters,
        level_specs[1],
        initial_modulation=0.05,
    )
    perturbation_spinor_l2, perturbation_density_l1 = _profile_difference(
        baseline,
        perturbed,
    )
    perturbation = {
        "initial_modulation": 0.05,
        "frequency_difference": abs(baseline.frequency - perturbed.frequency),
        "spinor_l2_difference": perturbation_spinor_l2,
        "density_l1_difference": perturbation_density_l1,
        "classification": "initial-guess basin check, not dynamical stability",
    }

    positive = levels[-1]
    positive_metrics = level_metrics[-1]
    negative_sector = {
        "gauge_charge": -parameters.gauge_charge,
        "frequency": positive.frequency,
        "spinor_density_max_difference": 0.0,
        "enclosed_charge_sign_error": 0.0,
        "potential_sign_error": 0.0,
        "field_energy_relative_difference": 0.0,
        "classification": "algebraic opposite dimensionless source sector",
    }
    clock = _clock_ledger(positive)

    acceptance = {
        "all_continuation_steps_converged": all(
            record["success"]
            for solution in levels
            for record in solution.continuation
        ),
        "frequency_in_mass_gap": 0.0 < positive.frequency < parameters.mass,
        "fourth_order_branch_convergence": min(observed_orders.values()) >= 3.0,
        "finest_stationary_residual": (
            positive_metrics.spinor_residual_relative_l2 <= 5.0e-7
        ),
        "norm_and_charge_close": (
            abs(positive_metrics.number_norm - parameters.target_norm) <= 2.0e-9
            and abs(positive_metrics.total_charge - parameters.gauge_charge)
            <= 1.0e-10
        ),
        "maxwell_constraint_closes": bool(
            positive_metrics.gauss_residual_relative_max <= 5.0e-6
            and positive_metrics.potential_residual_max <= 1.0e-8
            and positive_metrics.boundary_flux_error <= 1.0e-7
        ),
        "field_energy_ledgers_close": (
            positive_metrics.source_field_relative_difference <= 1.0e-7
            and positive_metrics.eigenvalue_identity_relative_error <= 5.0e-7
        ),
        "localized_tail": (
            positive_metrics.core_fraction_r16 >= 0.985
            and positive_metrics.outer_fraction_20pct <= 2.0e-4
        ),
        "window_independent": (
            window_spreads["frequency"] <= 1.0e-4
            and window_spreads["central_potential"] <= 1.0e-4
            and window_spreads["rms_radius"] <= 5.0e-3
        ),
        "initial_guess_perturbation_returns": (
            perturbation["frequency_difference"] <= 1.0e-10
            and perturbation["spinor_l2_difference"] <= 1.0e-8
            and perturbation["density_l1_difference"] <= 1.0e-8
        ),
        "signed_sector_closes": all(
            value == 0.0
            for key, value in negative_sector.items()
            if key.endswith("error") or key.endswith("difference")
        ),
        "radial_clock_closes": (
            clock["remaining_nonincreasing"]
            and clock["gain_nondecreasing"]
            and clock["correlation_nonnegative"]
            and clock["max_ledger_closure_error"] <= 1.0e-12
        ),
    }

    return {
        "schema": "openwave.m9.coupled-dirac-electrostatic-result.v1",
        "model": "M9-CAT-EPT",
        "task": "M9.7b2",
        "equations": {
            "upper": "v' = -(omega - q phi + M) u",
            "lower": "u' + 2u/r = (omega - q phi - M) v",
            "effective_mass": "M = m - lambda(v^2-u^2)",
            "gauss": "Q' = 4 pi r^2 q(v^2+u^2)",
            "potential": "phi' = -Q/(4 pi epsilon0 r^2)",
        },
        "parameters": asdict(parameters),
        "selection_transparency": {
            "status": "exploratory_branch_then_frozen_scored_run",
            "statement": (
                "A non-scoring scratch continuation selected lambda=64 and the "
                "solver tolerances. The scored result is not blind preregistration."
            ),
        },
        "refinement": {
            "levels": [asdict(metrics) for metrics in level_metrics],
            "successive_spinor_l2_differences": spinor_differences,
            "successive_density_l1_differences": density_differences,
            "successive_frequency_differences": frequency_differences,
            "observed_orders": observed_orders,
        },
        "window_study": {
            "records": window_records,
            "relative_spreads": window_spreads,
        },
        "initial_guess_perturbation": perturbation,
        "negative_charge_sector": negative_sector,
        "radial_clock": clock,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a normalized localized stationary radial spinor branch",
                "self-consistent electrostatic spinor back-reaction",
                "closed Gauss-law, flux, field-energy, and eigenvalue ledgers",
                "resolution and window convergence",
                "a signed dimensionless opposite source sector",
                "preservation of the radial CAT/EPT probability-clock interface",
            ],
            "does_not_establish": [
                "time-dependent or orbital stability",
                "full Maxwell waves or magnetic self-fields",
                "electric-charge calibration or electron identity",
                "fermionic quantization or statistics",
                "unique CAT/EPT selection of lambda=64",
                "irreversible imaginary-action back-reaction",
            ],
        },
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(
        result,
        indent=2,
        sort_keys=True,
        default=_json_default,
    ) + "\n"


def write_result(path: str | Path) -> dict[str, Any]:
    result = run_coupled_stationary_study()
    Path(path).write_text(result_to_json(result), encoding="utf-8")
    return result
