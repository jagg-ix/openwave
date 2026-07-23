"""M9.12 three-dimensional Dirac and Maxwell control studies."""

from __future__ import annotations

from functools import lru_cache
import math
from typing import Any, Sequence

import numpy as np

from .spatial_3d_types import (
    ALPHAS, BETA, ComplexArray, Spatial3DGrid, Spatial3DParameters, clifford_residuals,
)
from .spatial_3d_initial import initial_state
from .spatial_3d_evolution import evolve_spatial_3d, run_summary

def _relative_spinor_l2(
    actual_plus: ComplexArray,
    actual_minus: ComplexArray,
    expected_plus: ComplexArray,
    expected_minus: ComplexArray,
    cell_volume: float,
) -> float:
    numerator = np.sum(np.abs(actual_plus - expected_plus) ** 2)
    numerator += np.sum(np.abs(actual_minus - expected_minus) ** 2)
    denominator = np.sum(np.abs(expected_plus) ** 2) + np.sum(np.abs(expected_minus) ** 2)
    return math.sqrt(cell_volume * float(numerator)) / math.sqrt(
        cell_volume * float(denominator)
    )


def exact_discrete_free_evolution(
    state: ComplexArray,
    spacings: tuple[float, float, float],
    mass: float,
    time: float,
) -> ComplexArray:
    shape = state.shape[1:]
    symbols = []
    for count, spacing in zip(shape, spacings, strict=True):
        wave_numbers = 2.0 * math.pi * np.fft.fftfreq(count, d=spacing)
        symbols.append(np.sin(wave_numbers * spacing) / spacing)
    sx, sy, sz = np.meshgrid(*symbols, indexing="ij")
    energy = np.sqrt(mass**2 + sx**2 + sy**2 + sz**2)
    transformed = np.fft.fftn(state, axes=(1, 2, 3))
    h_state = mass * np.einsum("ab,bxyz->axyz", BETA, transformed, optimize=True)
    for symbol, alpha in zip((sx, sy, sz), ALPHAS, strict=True):
        h_state += symbol * np.einsum("ab,bxyz->axyz", alpha, transformed, optimize=True)
    evolved = np.cos(energy * time)[None, ...] * transformed
    evolved += -1j * (np.sin(energy * time) / energy)[None, ...] * h_state
    return np.asarray(np.fft.ifftn(evolved, axes=(1, 2, 3)), dtype=np.complex128)


def run_free_time_refinement(
    ratios: Sequence[float] = (0.08, 0.04, 0.02),
) -> dict[str, Any]:
    records = []
    for ratio in ratios:
        parameters = Spatial3DParameters(
            gauge_charge=0.0,
            gauge_seed_amplitude=0.0,
        )
        grid = Spatial3DGrid(
            half_width_x=10.0,
            half_width_y=10.0,
            half_width_z=10.0,
            points_x=20,
            points_y=20,
            points_z=20,
            final_time=0.8,
            dt_over_spacing=ratio,
            absorber_strength=0.0,
            samples=9,
        )
        run = evolve_spatial_3d(parameters, grid)
        exact_plus = exact_discrete_free_evolution(
            run.initial_plus, (run.dx, run.dy, run.dz), parameters.mass, grid.final_time
        )
        exact_minus = exact_discrete_free_evolution(
            run.initial_minus, (run.dx, run.dy, run.dz), parameters.mass, grid.final_time
        )
        records.append(
            {
                "dt_over_spacing": ratio,
                "dt": run.dt,
                "spinor_relative_l2": _relative_spinor_l2(
                    run.final_plus,
                    run.final_minus,
                    exact_plus,
                    exact_minus,
                    run.dx * run.dy * run.dz,
                ),
                "max_norm_drift": run_summary(run)["max_norm_drift"],
            }
        )
    errors = [record["spinor_relative_l2"] for record in records]
    orders = [
        math.log(errors[index] / errors[index + 1], 2.0)
        for index in range(len(errors) - 1)
    ]
    return {"records": records, "observed_orders": orders}


def run_vacuum_maxwell_control() -> dict[str, Any]:
    parameters = Spatial3DParameters(
        gauge_charge=0.0,
        gauge_seed_amplitude=0.0,
    )
    grid = Spatial3DGrid(
        half_width_x=math.pi,
        half_width_y=4.0,
        half_width_z=4.0,
        points_x=48,
        points_y=12,
        points_z=12,
        final_time=1.1,
        dt_over_spacing=0.04,
        absorber_strength=0.0,
        samples=13,
    )
    x, _, _, _, _, _, plus, minus, _, _ = initial_state(parameters, grid)
    amplitude = 0.05
    ay = amplitude * np.cos(x)
    ey = -amplitude * np.sin(x)
    zero = np.zeros_like(x)
    run = evolve_spatial_3d(
        parameters,
        grid,
        matter_enabled=False,
        initial_override=(
            np.zeros_like(plus),
            np.zeros_like(minus),
            (zero.copy(), ay.copy(), zero.copy()),
            (zero.copy(), ey.copy(), zero.copy()),
        ),
    )
    expected_ay = amplitude * np.cos(x - grid.final_time)
    expected_ey = -amplitude * np.sin(x - grid.final_time)
    cell_volume = run.dx * run.dy * run.dz
    ay_error = math.sqrt(cell_volume * float(np.sum((run.final_a[1] - expected_ay) ** 2)))
    ay_norm = math.sqrt(cell_volume * float(np.sum(expected_ay**2)))
    ey_error = math.sqrt(cell_volume * float(np.sum((run.final_e[1] - expected_ey) ** 2)))
    ey_norm = math.sqrt(cell_volume * float(np.sum(expected_ey**2)))
    initial_energy = run.records[0]["field_energy"]
    field_drift = max(
        abs(record["field_energy"] - initial_energy) for record in run.records
    ) / initial_energy
    return {
        "a_relative_l2": ay_error / ay_norm,
        "e_relative_l2": ey_error / ey_norm,
        "field_energy_relative_drift": field_drift,
        "steps": run.steps,
        "dt": run.dt,
    }


@lru_cache(maxsize=1)
def run_spatial_3d_control_study() -> dict[str, Any]:
    clifford = clifford_residuals()
    free = run_free_time_refinement()
    vacuum = run_vacuum_maxwell_control()
    acceptance = {
        "dirac_clifford_closes": max(clifford.values()) <= 1.0e-14,
        "free_time_fourth_order": min(free["observed_orders"]) >= 3.5,
        "free_norm_conserved": max(
            record["max_norm_drift"] for record in free["records"]
        )
        <= 3.0e-7,
        "vacuum_vector_potential_accurate": vacuum["a_relative_l2"] <= 2.0e-2,
        "vacuum_electric_field_accurate": vacuum["e_relative_l2"] <= 2.0e-2,
        "vacuum_energy_conserved": vacuum["field_energy_relative_drift"] <= 2.0e-5,
    }
    return {
        "schema": "openwave.m9.spatial-3d-controls-result.v1",
        "task": "M9.12",
        "clifford": clifford,
        "free_time_refinement": free,
        "vacuum_maxwell": vacuum,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a four-component Dirac representation in three transported dimensions",
                "an exact-discrete free-spinor control for the RK4 evolution",
                "a propagating three-dimensional vacuum Maxwell control",
                "bounded norm and field-energy control ledgers",
            ],
            "does_not_establish": [
                "coupled three-dimensional Maxwell-Dirac transport",
                "a localized charged particle or physical calibration",
            ],
        },
    }
