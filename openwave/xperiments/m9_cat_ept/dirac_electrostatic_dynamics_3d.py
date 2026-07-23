"""M9.7b3 constrained time-dependent spherical spinor--gauge evolution.

The model evolves the M9.7b2 radial spinor in the selected spherical Soler model.
The longitudinal electrostatic field is recomputed from Gauss law after every local
substep.  The radial kinetic operator is discretized as a weighted adjoint pair,
so its Crank--Nicolson step is unitary in the physical shell-volume norm.

Spherical electrostatics has no transverse Maxwell or magnetic degree of freedom.
Its electromagnetic Poynting flux is therefore exactly zero.  The module records
that negative result explicitly and does not claim radiative Maxwell dynamics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline
from scipy.sparse import bmat, csc_matrix, diags, eye, lil_matrix
from scipy.sparse.linalg import splu

from .dirac_electrostatic_3d import (
    CoupledParameters,
    StationaryGrid,
    StationarySolution,
    solve_stationary_branch,
)
from .electrostatic_gauge_3d import (
    ReflectingCoarseGraining,
    radial_clock_trajectory,
)

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class DynamicGrid:
    """Frozen radial shell grid and time-step controls."""

    outer_radius: float = 40.0
    cells: int = 512
    final_time: float = 5.0
    dt_over_dr: float = 0.10
    samples: int = 41

    def __post_init__(self) -> None:
        if self.outer_radius <= 0.0:
            raise ValueError("outer_radius must be positive")
        if self.cells < 64:
            raise ValueError("cells must be at least 64")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_dr <= 0.25:
            raise ValueError("dt_over_dr must lie in (0, 0.25]")
        if self.samples < 2:
            raise ValueError("samples must be at least 2")


@dataclass(frozen=True)
class Perturbation:
    """Fixed component-opposite amplitude and phase perturbation."""

    amplitude: float = 0.02
    phase: float = 0.02

    def __post_init__(self) -> None:
        if abs(self.amplitude) > 0.10:
            raise ValueError("amplitude magnitude must not exceed 0.10")
        if abs(self.phase) > 0.10:
            raise ValueError("phase magnitude must not exceed 0.10")


@dataclass(frozen=True)
class ElectrostaticState:
    """One finite-volume longitudinal gauge solution."""

    shell_charge: RealArray
    enclosed_charge_edges: RealArray
    electric_field_edges: RealArray
    potential_edges: RealArray
    potential_centers: RealArray


@dataclass
class DynamicRun:
    """One complete time evolution and its sampled conservation ledger."""

    grid: DynamicGrid
    parameters: CoupledParameters
    centers: RealArray
    edges: RealArray
    volumes: RealArray
    initial_upper: ComplexArray
    initial_lower: ComplexArray
    final_upper: ComplexArray
    final_lower: ComplexArray
    dt: float
    steps: int
    perturbation: Perturbation
    records: list[dict[str, float]]


class _WeightedKineticStepper:
    """Weighted-unitary radial kinetic Crank--Nicolson substep."""

    def __init__(self, grid: DynamicGrid, dt: float) -> None:
        self.grid = grid
        self.dt = dt
        self.edges, self.centers, self.volumes, self.dr = radial_shell_grid(grid)
        derivative = _derivative_matrix(grid.cells, self.dr)
        weights = diags(self.volumes)
        inverse_weights = diags(1.0 / self.volumes)
        radial_adjoint = -inverse_weights @ derivative.T @ weights
        kinetic = bmat(
            [[None, radial_adjoint], [-derivative, None]],
            format="csc",
            dtype=np.complex128,
        )
        sqrt_weights = np.sqrt(self.volumes)
        scale = diags(np.concatenate((sqrt_weights, sqrt_weights)))
        inverse_scale = diags(1.0 / np.concatenate((sqrt_weights, sqrt_weights)))
        self.transformed_kinetic = (scale @ kinetic @ inverse_scale).tocsc()
        self.sqrt_weights = sqrt_weights
        identity = eye(2 * grid.cells, format="csc", dtype=np.complex128)
        left = identity + 0.5j * dt * self.transformed_kinetic
        self._solve_left = splu(csc_matrix(left)).solve
        self._right = (identity - 0.5j * dt * self.transformed_kinetic).tocsr()

    def apply(
        self,
        upper: ComplexArray,
        lower: ComplexArray,
    ) -> tuple[ComplexArray, ComplexArray]:
        state = np.concatenate(
            (self.sqrt_weights * upper, self.sqrt_weights * lower)
        )
        evolved = self._solve_left(self._right @ state)
        cells = self.grid.cells
        return (
            np.asarray(evolved[:cells] / self.sqrt_weights, dtype=np.complex128),
            np.asarray(evolved[cells:] / self.sqrt_weights, dtype=np.complex128),
        )


def radial_shell_grid(
    grid: DynamicGrid,
) -> tuple[RealArray, RealArray, RealArray, float]:
    """Return shell edges, centers, exact shell volumes, and spacing."""
    edges = np.linspace(0.0, grid.outer_radius, grid.cells + 1, dtype=np.float64)
    centers = 0.5 * (edges[:-1] + edges[1:])
    volumes = 4.0 * math.pi / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3)
    return edges, centers, volumes, grid.outer_radius / grid.cells


def _derivative_matrix(cells: int, dr: float) -> csc_matrix:
    """Return a second-order derivative with one-sided boundary closures."""
    derivative = lil_matrix((cells, cells), dtype=np.float64)
    derivative[0, 0] = -3.0 / (2.0 * dr)
    derivative[0, 1] = 4.0 / (2.0 * dr)
    derivative[0, 2] = -1.0 / (2.0 * dr)
    derivative[-1, -1] = 3.0 / (2.0 * dr)
    derivative[-1, -2] = -4.0 / (2.0 * dr)
    derivative[-1, -3] = 1.0 / (2.0 * dr)
    for index in range(1, cells - 1):
        derivative[index, index - 1] = -1.0 / (2.0 * dr)
        derivative[index, index + 1] = 1.0 / (2.0 * dr)
    return derivative.tocsc()


def spinor_density(upper: ComplexArray, lower: ComplexArray) -> RealArray:
    return np.asarray(np.abs(upper) ** 2 + np.abs(lower) ** 2, dtype=np.float64)


def lorentz_scalar(upper: ComplexArray, lower: ComplexArray) -> RealArray:
    return np.asarray(np.abs(upper) ** 2 - np.abs(lower) ** 2, dtype=np.float64)


def number_norm(
    upper: ComplexArray,
    lower: ComplexArray,
    volumes: RealArray,
) -> float:
    return float(np.sum(spinor_density(upper, lower) * volumes))


def electrostatic_constraint(
    density: RealArray,
    edges: RealArray,
    centers: RealArray,
    volumes: RealArray,
    parameters: CoupledParameters,
) -> ElectrostaticState:
    """Solve the spherical longitudinal Maxwell constraint from shell density."""
    if density.shape != centers.shape:
        raise ValueError("density must match the radial shell grid")
    shell_charge = parameters.gauge_charge * density * volumes
    enclosed = np.concatenate(([0.0], np.cumsum(shell_charge)))
    electric = np.zeros_like(edges)
    electric[1:] = enclosed[1:] / (
        4.0 * math.pi * parameters.epsilon0 * edges[1:] ** 2
    )
    potential = np.empty_like(edges)
    potential[-1] = enclosed[-1] / (
        4.0 * math.pi * parameters.epsilon0 * edges[-1]
    )
    dr = edges[1] - edges[0]
    for index in range(edges.size - 2, -1, -1):
        potential[index] = potential[index + 1] + 0.5 * (
            electric[index] + electric[index + 1]
        ) * dr
    return ElectrostaticState(
        shell_charge=np.asarray(shell_charge, dtype=np.float64),
        enclosed_charge_edges=np.asarray(enclosed, dtype=np.float64),
        electric_field_edges=np.asarray(electric, dtype=np.float64),
        potential_edges=np.asarray(potential, dtype=np.float64),
        potential_centers=np.asarray(
            0.5 * (potential[:-1] + potential[1:]),
            dtype=np.float64,
        ),
    )


def _local_step(
    upper: ComplexArray,
    lower: ComplexArray,
    duration: float,
    stepper: _WeightedKineticStepper,
    parameters: CoupledParameters,
) -> tuple[ComplexArray, ComplexArray]:
    density = spinor_density(upper, lower)
    scalar = lorentz_scalar(upper, lower)
    gauge = electrostatic_constraint(
        density,
        stepper.edges,
        stepper.centers,
        stepper.volumes,
        parameters,
    )
    effective_mass = parameters.mass - parameters.soler_coupling * scalar
    upper_phase = parameters.gauge_charge * gauge.potential_centers + effective_mass
    lower_phase = parameters.gauge_charge * gauge.potential_centers - effective_mass
    return (
        np.asarray(upper * np.exp(-1j * duration * upper_phase), dtype=np.complex128),
        np.asarray(lower * np.exp(-1j * duration * lower_phase), dtype=np.complex128),
    )


def _split_step(
    upper: ComplexArray,
    lower: ComplexArray,
    stepper: _WeightedKineticStepper,
    parameters: CoupledParameters,
) -> tuple[ComplexArray, ComplexArray]:
    upper, lower = _local_step(
        upper,
        lower,
        0.5 * stepper.dt,
        stepper,
        parameters,
    )
    upper, lower = stepper.apply(upper, lower)
    return _local_step(
        upper,
        lower,
        0.5 * stepper.dt,
        stepper,
        parameters,
    )


def _initial_state(
    stationary: StationarySolution,
    stepper: _WeightedKineticStepper,
    perturbation: Perturbation,
) -> tuple[ComplexArray, ComplexArray]:
    values = stationary.evaluate(np.maximum(stepper.centers, 1.0e-6))
    upper = np.asarray(values[0], dtype=np.complex128)
    lower = np.asarray(values[1], dtype=np.complex128)
    if perturbation.amplitude != 0.0:
        mode = np.cos(math.pi * stepper.centers / stepper.grid.outer_radius)
        upper *= 1.0 + perturbation.amplitude * mode
        lower *= 1.0 - perturbation.amplitude * mode
        factor = math.sqrt(
            stationary.parameters.target_norm
            / number_norm(upper, lower, stepper.volumes)
        )
        upper *= factor
        lower *= factor
    if perturbation.phase != 0.0:
        phase = perturbation.phase * np.sin(
            math.pi * stepper.centers / stepper.grid.outer_radius
        )
        upper *= np.exp(1j * phase)
        lower *= np.exp(-1j * phase)
    return upper, lower


def _field_energy(
    gauge: ElectrostaticState,
    edges: RealArray,
    parameters: CoupledParameters,
) -> float:
    integrand = (
        0.5
        * parameters.epsilon0
        * 4.0
        * math.pi
        * edges**2
        * gauge.electric_field_edges**2
    )
    interior = float(np.trapezoid(integrand, edges))
    charge = float(gauge.enclosed_charge_edges[-1])
    tail = charge**2 / (
        8.0 * math.pi * parameters.epsilon0 * edges[-1]
    )
    return interior + tail


def total_energy(
    upper: ComplexArray,
    lower: ComplexArray,
    stepper: _WeightedKineticStepper,
    parameters: CoupledParameters,
) -> tuple[float, float, float]:
    """Return total, matter, and electrostatic energy ledgers."""
    transformed = np.concatenate(
        (stepper.sqrt_weights * upper, stepper.sqrt_weights * lower)
    )
    kinetic = float(
        np.real(np.vdot(transformed, stepper.transformed_kinetic @ transformed))
    )
    scalar = lorentz_scalar(upper, lower)
    local = float(
        np.sum(
            stepper.volumes
            * (
                parameters.mass * scalar
                - 0.5 * parameters.soler_coupling * scalar**2
            )
        )
    )
    gauge = electrostatic_constraint(
        spinor_density(upper, lower),
        stepper.edges,
        stepper.centers,
        stepper.volumes,
        parameters,
    )
    field = _field_energy(gauge, stepper.edges, parameters)
    matter = kinetic + local
    return matter + field, matter, field


def gauss_residual_relative(
    gauge: ElectrostaticState,
    edges: RealArray,
    parameters: CoupledParameters,
) -> float:
    flux = (
        parameters.epsilon0
        * 4.0
        * math.pi
        * edges**2
        * gauge.electric_field_edges
    )
    shell_flux = np.diff(flux)
    scale = max(float(np.max(np.abs(gauge.shell_charge))), 1.0e-30)
    return float(np.max(np.abs(shell_flux - gauge.shell_charge)) / scale)


def radial_current(upper: ComplexArray, lower: ComplexArray) -> RealArray:
    """Return the spherical Dirac number current for the selected ansatz."""
    return np.asarray(-2.0 * np.imag(np.conj(upper) * lower), dtype=np.float64)


def _state_record(
    time: float,
    upper: ComplexArray,
    lower: ComplexArray,
    stepper: _WeightedKineticStepper,
    parameters: CoupledParameters,
) -> dict[str, float]:
    density = spinor_density(upper, lower)
    norm = number_norm(upper, lower, stepper.volumes)
    gauge = electrostatic_constraint(
        density,
        stepper.edges,
        stepper.centers,
        stepper.volumes,
        parameters,
    )
    total, matter, field = total_energy(upper, lower, stepper, parameters)
    rms = math.sqrt(
        float(np.sum(stepper.volumes * stepper.centers**2 * density)) / norm
    )
    core_mask = stepper.centers <= 16.0
    core = float(
        np.sum(stepper.volumes[core_mask] * density[core_mask]) / norm
    )
    edge_mask = stepper.centers >= 0.80 * stepper.grid.outer_radius
    outer = float(np.sum(stepper.volumes[edge_mask] * density[edge_mask]) / norm)
    current = radial_current(upper, lower)
    boundary_flux = 4.0 * math.pi * stepper.grid.outer_radius**2 * current[-1]
    return {
        "time": time,
        "norm": norm,
        "total_energy": total,
        "matter_energy": matter,
        "field_energy": field,
        "rms_radius": rms,
        "core_fraction_r16": core,
        "outer_fraction_20pct": outer,
        "central_potential": float(gauge.potential_centers[0]),
        "total_signed_charge": float(gauge.enclosed_charge_edges[-1]),
        "gauss_residual_relative": gauss_residual_relative(
            gauge,
            stepper.edges,
            parameters,
        ),
        "matter_boundary_flux": float(boundary_flux),
        "electromagnetic_poynting_flux": 0.0,
    }


def evolve_constrained_dynamics(
    stationary: StationarySolution,
    grid: DynamicGrid,
    perturbation: Perturbation = Perturbation(0.0, 0.0),
) -> DynamicRun:
    """Evolve one spherical constrained Dirac--electrostatic trajectory."""
    steps = max(
        1,
        math.ceil(
            grid.final_time / (grid.dt_over_dr * grid.outer_radius / grid.cells)
        ),
    )
    dt = grid.final_time / steps
    stepper = _WeightedKineticStepper(grid, dt)
    upper, lower = _initial_state(stationary, stepper, perturbation)
    initial_upper = upper.copy()
    initial_lower = lower.copy()
    sample_indices = set(
        int(round(value))
        for value in np.linspace(0.0, float(steps), grid.samples)
    )
    records: list[dict[str, float]] = []
    if 0 in sample_indices:
        records.append(
            _state_record(0.0, upper, lower, stepper, stationary.parameters)
        )
    for step in range(1, steps + 1):
        upper, lower = _split_step(upper, lower, stepper, stationary.parameters)
        if step in sample_indices:
            records.append(
                _state_record(
                    step * dt,
                    upper,
                    lower,
                    stepper,
                    stationary.parameters,
                )
            )
    return DynamicRun(
        grid=grid,
        parameters=stationary.parameters,
        centers=stepper.centers,
        edges=stepper.edges,
        volumes=stepper.volumes,
        initial_upper=initial_upper,
        initial_lower=initial_lower,
        final_upper=upper,
        final_lower=lower,
        dt=dt,
        steps=steps,
        perturbation=perturbation,
        records=records,
    )


def _phase_aligned_metrics(
    run: DynamicRun,
    stationary: StationarySolution,
) -> dict[str, float]:
    reference = stationary.evaluate(np.maximum(run.centers, 1.0e-6))
    phase_time = np.exp(-1j * stationary.frequency * run.grid.final_time)
    reference_upper = reference[0] * phase_time
    reference_lower = reference[1] * phase_time
    overlap = np.sum(
        run.volumes
        * (
            np.conj(reference_upper) * run.final_upper
            + np.conj(reference_lower) * run.final_lower
        )
    )
    reference_norm = number_norm(reference_upper, reference_lower, run.volumes)
    final_norm = number_norm(run.final_upper, run.final_lower, run.volumes)
    phase = float(np.angle(overlap))
    aligned_upper = run.final_upper * np.exp(-1j * phase)
    aligned_lower = run.final_lower * np.exp(-1j * phase)
    spinor_l2 = math.sqrt(
        float(
            np.sum(
                run.volumes
                * (
                    np.abs(aligned_upper - reference_upper) ** 2
                    + np.abs(aligned_lower - reference_lower) ** 2
                )
            )
        )
    )
    final_density = spinor_density(run.final_upper, run.final_lower)
    reference_density = spinor_density(reference_upper, reference_lower)
    density_l1 = float(
        np.sum(run.volumes * np.abs(final_density - reference_density))
    )
    fidelity = float(abs(overlap) ** 2 / (reference_norm * final_norm))
    return {
        "phase_aligned_spinor_l2": spinor_l2,
        "density_volume_l1": density_l1,
        "fidelity": fidelity,
        "overlap_phase_error": phase,
    }


def _run_summary(
    run: DynamicRun,
    stationary: StationarySolution,
) -> dict[str, Any]:
    initial = run.records[0]
    final = run.records[-1]
    phase = _phase_aligned_metrics(run, stationary)
    max_norm_drift = max(
        abs(record["norm"] - initial["norm"]) for record in run.records
    )
    max_energy_drift = max(
        abs(record["total_energy"] - initial["total_energy"])
        / abs(initial["total_energy"])
        for record in run.records
    )
    max_gauss = max(record["gauss_residual_relative"] for record in run.records)
    max_boundary_flux = max(
        abs(record["matter_boundary_flux"]) for record in run.records
    )
    max_poynting = max(
        abs(record["electromagnetic_poynting_flux"]) for record in run.records
    )
    return {
        "grid": asdict(run.grid),
        "dt": run.dt,
        "steps": run.steps,
        "perturbation": asdict(run.perturbation),
        "phase_metrics": phase,
        "initial": initial,
        "final": final,
        "max_norm_drift": max_norm_drift,
        "max_total_energy_relative_drift": max_energy_drift,
        "max_gauss_residual_relative": max_gauss,
        "max_absolute_matter_boundary_flux": max_boundary_flux,
        "max_absolute_electromagnetic_poynting_flux": max_poynting,
        "sample_count": len(run.records),
    }


def _compare_runs(coarse: DynamicRun, fine: DynamicRun) -> tuple[float, float]:
    coarse_upper = CubicSpline(coarse.centers, coarse.final_upper)(fine.centers)
    coarse_lower = CubicSpline(coarse.centers, coarse.final_lower)(fine.centers)
    overlap = np.sum(
        fine.volumes
        * (
            np.conj(fine.final_upper) * coarse_upper
            + np.conj(fine.final_lower) * coarse_lower
        )
    )
    phase = np.angle(overlap)
    coarse_upper *= np.exp(-1j * phase)
    coarse_lower *= np.exp(-1j * phase)
    spinor_l2 = math.sqrt(
        float(
            np.sum(
                fine.volumes
                * (
                    np.abs(coarse_upper - fine.final_upper) ** 2
                    + np.abs(coarse_lower - fine.final_lower) ** 2
                )
            )
        )
    )
    coarse_density = spinor_density(coarse_upper, coarse_lower)
    fine_density = spinor_density(fine.final_upper, fine.final_lower)
    density_l1 = float(
        np.sum(fine.volumes * np.abs(coarse_density - fine_density))
    )
    return spinor_l2, density_l1


def _relative_spread(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float((np.max(array) - np.min(array)) / np.mean(np.abs(array)))


def _shell_probability(run: DynamicRun) -> RealArray:
    probability = spinor_density(run.final_upper, run.final_lower) * run.volumes
    probability /= float(np.sum(probability))
    return np.asarray(probability, dtype=np.float64)


@lru_cache(maxsize=1)
def run_dynamic_study() -> dict[str, Any]:
    """Run the complete scored M9.7b3 constrained dynamic qualification."""
    parameters = CoupledParameters()
    stationary_grid = StationaryGrid(
        outer_radius=40.0,
        initial_points=1_024,
        tolerance=6.25e-7,
        diagnostic_points=8_193,
    )
    stationary = solve_stationary_branch(parameters, stationary_grid)
    perturbation = Perturbation(amplitude=0.02, phase=0.02)

    refinement_grids = (
        DynamicGrid(cells=256, final_time=5.0, samples=21),
        DynamicGrid(cells=512, final_time=5.0, samples=21),
        DynamicGrid(cells=1_024, final_time=5.0, samples=21),
    )
    refinement_runs = [
        evolve_constrained_dynamics(stationary, grid, perturbation)
        for grid in refinement_grids
    ]
    refinement_summaries = [
        _run_summary(run, stationary) for run in refinement_runs
    ]
    spinor_differences = [
        _compare_runs(refinement_runs[0], refinement_runs[1])[0],
        _compare_runs(refinement_runs[1], refinement_runs[2])[0],
    ]
    density_differences = [
        _compare_runs(refinement_runs[0], refinement_runs[1])[1],
        _compare_runs(refinement_runs[1], refinement_runs[2])[1],
    ]
    observed_orders = {
        "spinor_l2": math.log(spinor_differences[0] / spinor_differences[1], 2.0),
        "density_l1": math.log(
            density_differences[0] / density_differences[1],
            2.0,
        ),
    }

    long_grid = DynamicGrid(cells=512, final_time=20.0, samples=81)
    long_run = evolve_constrained_dynamics(stationary, long_grid, perturbation)
    long_summary = _run_summary(long_run, stationary)

    window_specs = (
        (30.0, 768, 384),
        (40.0, 1_024, 512),
        (50.0, 1_280, 640),
    )
    window_records: list[dict[str, Any]] = []
    for radius, initial_points, cells in window_specs:
        branch = solve_stationary_branch(
            parameters,
            StationaryGrid(
                outer_radius=radius,
                initial_points=initial_points,
                tolerance=6.25e-7,
                diagnostic_points=4_097,
            ),
        )
        run = evolve_constrained_dynamics(
            branch,
            DynamicGrid(
                outer_radius=radius,
                cells=cells,
                final_time=10.0,
                samples=41,
            ),
            perturbation,
        )
        summary = _run_summary(run, branch)
        window_records.append(
            {
                "outer_radius": radius,
                "cells": cells,
                "frequency": branch.frequency,
                "final_rms_radius": summary["final"]["rms_radius"],
                "final_central_potential": summary["final"]["central_potential"],
                "final_core_fraction_r16": summary["final"]["core_fraction_r16"],
                "final_fidelity": summary["phase_metrics"]["fidelity"],
                "max_total_energy_relative_drift": summary[
                    "max_total_energy_relative_drift"
                ],
            }
        )
    window_spreads = {
        "rms_radius": _relative_spread(
            [record["final_rms_radius"] for record in window_records]
        ),
        "central_potential": _relative_spread(
            [record["final_central_potential"] for record in window_records]
        ),
        "core_fraction": _relative_spread(
            [record["final_core_fraction_r16"] for record in window_records]
        ),
    }

    clock = radial_clock_trajectory(
        _shell_probability(long_run),
        ReflectingCoarseGraining(steps=64, gamma=1.0),
    )
    finest = refinement_summaries[-1]
    acceptance = {
        "second_order_dynamic_convergence": min(observed_orders.values()) >= 1.8,
        "norm_conserved": max(
            summary["max_norm_drift"] for summary in refinement_summaries
        )
        <= 1.0e-12,
        "total_energy_conserved": max(
            summary["max_total_energy_relative_drift"]
            for summary in refinement_summaries
        )
        <= 4.0e-7,
        "dynamical_gauss_closes": max(
            summary["max_gauss_residual_relative"]
            for summary in refinement_summaries
        )
        <= 1.0e-12,
        "refined_state_accurate": (
            finest["phase_metrics"]["fidelity"] >= 0.9999
            and finest["phase_metrics"]["density_volume_l1"] <= 5.0e-3
        ),
        "boundary_flux_small": max(
            summary["max_absolute_matter_boundary_flux"]
            for summary in refinement_summaries
        )
        <= 1.0e-5,
        "spherical_poynting_flux_zero": max(
            summary["max_absolute_electromagnetic_poynting_flux"]
            for summary in refinement_summaries
        )
        == 0.0,
        "long_time_localized": (
            long_summary["phase_metrics"]["fidelity"] >= 0.999
            and long_summary["final"]["core_fraction_r16"] >= 0.985
            and long_summary["final"]["outer_fraction_20pct"] <= 2.0e-4
        ),
        "long_time_conservation": (
            long_summary["max_norm_drift"] <= 2.0e-12
            and long_summary["max_total_energy_relative_drift"] <= 2.0e-7
        ),
        "window_independent": (
            window_spreads["rms_radius"] <= 1.0e-2
            and window_spreads["central_potential"] <= 5.0e-3
            and window_spreads["core_fraction"] <= 1.0e-3
        ),
        "radial_clock_closes": (
            clock["remaining_nonincreasing"]
            and clock["gain_nondecreasing"]
            and clock["correlation_nonnegative"]
            and clock["max_ledger_closure_error"] <= 1.0e-12
        ),
    }

    return {
        "schema": "openwave.m9.dirac-electrostatic-dynamics-result.v1",
        "model": "M9-CAT-EPT",
        "task": "M9.7b3",
        "evolution": {
            "spinor": (
                "i V_t=(d_r+2/r)U+(q phi+M)V; "
                "i U_t=-d_r V+(q phi-M)U"
            ),
            "effective_mass": "M=m-lambda(|V|^2-|U|^2)",
            "gauge_constraint": (
                "Q(r,t)=4 pi integral_0^r s^2 q rho(s,t) ds; "
                "E=Q/(4 pi epsilon0 r^2)"
            ),
            "method": (
                "weighted-adjoint radial finite differences; exact local nonlinear "
                "phase; weighted-unitary kinetic Crank--Nicolson; Poisson projection"
            ),
        },
        "parameters": asdict(parameters),
        "perturbation": asdict(perturbation),
        "refinement": {
            "summaries": refinement_summaries,
            "successive_spinor_l2_differences": spinor_differences,
            "successive_density_l1_differences": density_differences,
            "observed_orders": observed_orders,
        },
        "long_time_run": long_summary,
        "window_study": {
            "records": window_records,
            "relative_spreads": window_spreads,
        },
        "radial_clock": clock,
        "radiation_ledger": {
            "electromagnetic_poynting_flux": 0.0,
            "reason": (
                "The spherical electrostatic truncation has B=0 and no transverse "
                "Maxwell degree, so E cross B vanishes identically."
            ),
            "classification": (
                "symmetry-enforced negative radiation result; not evidence for "
                "full Maxwell-wave stability"
            ),
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "time-dependent spherical nonlinear Dirac evolution",
                "longitudinal electrostatic back-reaction at every substep",
                "roundoff-level norm conservation and bounded total-energy drift",
                "dynamical Gauss closure, refinement, window, and perturbation ledgers",
                "long-time localization over the frozen finite interval",
                "preservation of the radial CAT/EPT probability-clock interface",
            ],
            "does_not_establish": [
                "transverse Maxwell waves, magnetic fields, or electromagnetic radiation",
                "non-spherical orbital stability",
                "calibrated charge or electron/positron identity",
                "fermionic quantization or statistics",
                "unique CAT/EPT derivation of lambda=64",
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
    result = run_dynamic_study()
    Path(path).write_text(result_to_json(result), encoding="utf-8")
    return result
