"""RK4 evolution and diagnostics for the bounded M9 3D engine."""

from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any

import numpy as np

from .spatial_3d_types import ComplexArray, RealArray, Spatial3DGrid, Spatial3DParameters, Spatial3DRun
from .spatial_3d_operators import absorber_profile, curl, density, signed_charge_density
from .spatial_3d_initial import initial_state
from .spatial_3d_hamiltonian import (
    Vector, _rhs, _state_add, field_energy, gauss_metrics, matter_energy,
    packet_moments, total_norm,
)

def poynting_flux(
    vector_potential: Vector,
    electric_field: Vector,
    spacings: tuple[float, float, float],
    probe_indices: tuple[int, int, int, int, int, int],
    face_areas: tuple[float, float, float],
) -> float:
    magnetic_field = curl(vector_potential, spacings)
    ex, ey, ez = electric_field
    bx, by, bz = magnetic_field
    sx = ey * bz - ez * by
    sy = ez * bx - ex * bz
    sz = ex * by - ey * bx
    ixm, ixp, iym, iyp, izm, izp = probe_indices
    area_x, area_y, area_z = face_areas
    flux = area_x * (float(np.sum(sx[ixp, :, :])) - float(np.sum(sx[ixm, :, :])))
    flux += area_y * (float(np.sum(sy[:, iyp, :])) - float(np.sum(sy[:, iym, :])))
    flux += area_z * (float(np.sum(sz[:, :, izp])) - float(np.sum(sz[:, :, izm])))
    return flux


def _record(
    time: float,
    plus: ComplexArray,
    minus: ComplexArray,
    vector_potential: Vector,
    electric_field: Vector,
    absorber_charge: RealArray,
    absorbed_energy: float,
    emitted_energy: float,
    x: RealArray,
    y: RealArray,
    z: RealArray,
    parameters: Spatial3DParameters,
    spacings: tuple[float, float, float],
    cell_volume: float,
) -> dict[str, float]:
    plus_moments = packet_moments(x, y, z, plus, cell_volume)
    minus_moments = packet_moments(x, y, z, minus, cell_volume)
    matter = matter_energy(
        plus, minus, vector_potential, parameters, spacings, cell_volume
    )
    field = field_energy(vector_potential, electric_field, spacings, cell_volume)
    gauss_absolute, gauss_relative, gauss_mean = gauss_metrics(
        electric_field, plus, minus, absorber_charge, parameters, spacings
    )
    magnetic_field = curl(vector_potential, spacings)
    return {
        "time": time,
        "norm": total_norm(plus, minus, cell_volume),
        "matter_energy": matter,
        "field_energy": field,
        "absorbed_energy": absorbed_energy,
        "corrected_energy": matter + field + absorbed_energy,
        "emitted_energy": emitted_energy,
        "gauss_residual_absolute": gauss_absolute,
        "gauss_residual_relative": gauss_relative,
        "gauss_residual_mean": gauss_mean,
        "net_matter_charge": cell_volume
        * float(np.sum(signed_charge_density(plus, minus, parameters))),
        "net_absorber_charge": cell_volume * float(np.sum(absorber_charge)),
        "plus_center_x": plus_moments[0],
        "plus_center_y": plus_moments[1],
        "plus_center_z": plus_moments[2],
        "plus_rms_radius": plus_moments[3],
        "minus_center_x": minus_moments[0],
        "minus_center_y": minus_moments[1],
        "minus_center_z": minus_moments[2],
        "minus_rms_radius": minus_moments[3],
        "max_magnetic_field": float(
            max(np.max(np.abs(component)) for component in magnetic_field)
        ),
    }


def evolve_spatial_3d(
    parameters: Spatial3DParameters = Spatial3DParameters(),
    grid: Spatial3DGrid = Spatial3DGrid(),
    *,
    matter_enabled: bool = True,
    initial_override: tuple[
        ComplexArray,
        ComplexArray,
        Vector,
        Vector,
    ]
    | None = None,
) -> Spatial3DRun:
    (
        x,
        y,
        z,
        dx,
        dy,
        dz,
        plus,
        minus,
        vector_potential,
        electric_field,
    ) = initial_state(parameters, grid)
    if initial_override is not None:
        plus, minus, vector_potential, electric_field = initial_override
        plus = plus.copy()
        minus = minus.copy()
        vector_potential = tuple(component.copy() for component in vector_potential)
        electric_field = tuple(component.copy() for component in electric_field)
    if not matter_enabled:
        plus[:] = 0.0
        minus[:] = 0.0
    initial_plus = plus.copy()
    initial_minus = minus.copy()
    initial_a = tuple(component.copy() for component in vector_potential)
    initial_e = tuple(component.copy() for component in electric_field)
    spacings = (dx, dy, dz)
    cell_volume = dx * dy * dz
    sigma = absorber_profile(x, y, z, grid)
    absorber_charge = np.zeros_like(x)
    target_dt = grid.dt_over_spacing * min(spacings)
    steps = max(1, math.ceil(grid.final_time / target_dt))
    dt = grid.final_time / steps
    sample_indices = set(np.linspace(0, steps, grid.samples, dtype=int).tolist())
    index_ranges = []
    for count in (grid.points_x, grid.points_y, grid.points_z):
        center = count // 2
        offset = max(2, count // 4)
        index_ranges.extend((center - offset, center + offset))
    probe_indices = tuple(index_ranges)  # type: ignore[assignment]
    face_areas = (dy * dz, dx * dz, dx * dy)
    absorbed = 0.0
    emitted = 0.0
    records = [
        _record(
            0.0,
            plus,
            minus,
            vector_potential,
            electric_field,
            absorber_charge,
            absorbed,
            emitted,
            x,
            y,
            z,
            parameters,
            spacings,
            cell_volume,
        )
    ]
    state = (plus, minus, vector_potential, electric_field, absorber_charge)
    for step in range(1, steps + 1):
        k1 = _rhs(*state, sigma, parameters, spacings, cell_volume, matter_enabled)
        k2 = _rhs(
            *_state_add(state, 0.5 * dt, k1),
            sigma,
            parameters,
            spacings,
            cell_volume,
            matter_enabled,
        )
        k3 = _rhs(
            *_state_add(state, 0.5 * dt, k2),
            sigma,
            parameters,
            spacings,
            cell_volume,
            matter_enabled,
        )
        k4 = _rhs(
            *_state_add(state, dt, k3),
            sigma,
            parameters,
            spacings,
            cell_volume,
            matter_enabled,
        )
        plus, minus, vector_potential, electric_field, absorber_charge = state
        plus = plus + dt * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0
        minus = minus + dt * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]) / 6.0
        vector_potential = tuple(
            vector_potential[i]
            + dt * (k1[2][i] + 2.0 * k2[2][i] + 2.0 * k3[2][i] + k4[2][i]) / 6.0
            for i in range(3)
        )
        electric_field = tuple(
            electric_field[i]
            + dt * (k1[3][i] + 2.0 * k2[3][i] + 2.0 * k3[3][i] + k4[3][i]) / 6.0
            for i in range(3)
        )
        absorber_charge = absorber_charge + dt * (
            k1[4] + 2.0 * k2[4] + 2.0 * k3[4] + k4[4]
        ) / 6.0
        absorbed += dt * (k1[5] + 2.0 * k2[5] + 2.0 * k3[5] + k4[5]) / 6.0
        flux = poynting_flux(
            vector_potential,
            electric_field,
            spacings,
            probe_indices,
            face_areas,
        )
        emitted += dt * max(flux, 0.0)
        state = (plus, minus, vector_potential, electric_field, absorber_charge)
        if step in sample_indices:
            records.append(
                _record(
                    step * dt,
                    plus,
                    minus,
                    vector_potential,
                    electric_field,
                    absorber_charge,
                    absorbed,
                    emitted,
                    x,
                    y,
                    z,
                    parameters,
                    spacings,
                    cell_volume,
                )
            )
    return Spatial3DRun(
        x=x,
        y=y,
        z=z,
        dx=dx,
        dy=dy,
        dz=dz,
        dt=dt,
        steps=steps,
        parameters=parameters,
        grid=grid,
        initial_plus=initial_plus,
        initial_minus=initial_minus,
        final_plus=plus,
        final_minus=minus,
        initial_a=initial_a,
        initial_e=initial_e,
        final_a=vector_potential,
        final_e=electric_field,
        final_absorber_charge=absorber_charge,
        absorbed_energy=absorbed,
        emitted_energy=emitted,
        records=tuple(records),
    )


def run_summary(run: Spatial3DRun) -> dict[str, Any]:
    initial = run.records[0]
    final = run.records[-1]
    initial_separation = math.sqrt(
        (initial["minus_center_x"] - initial["plus_center_x"]) ** 2
        + (initial["minus_center_y"] - initial["plus_center_y"]) ** 2
        + (initial["minus_center_z"] - initial["plus_center_z"]) ** 2
    )
    final_separation = math.sqrt(
        (final["minus_center_x"] - final["plus_center_x"]) ** 2
        + (final["minus_center_y"] - final["plus_center_y"]) ** 2
        + (final["minus_center_z"] - final["plus_center_z"]) ** 2
    )
    initial_energy = initial["corrected_energy"]
    return {
        "grid": asdict(run.grid),
        "parameters": asdict(run.parameters),
        "dt": run.dt,
        "steps": run.steps,
        "initial": initial,
        "final": final,
        "initial_separation": initial_separation,
        "final_separation": final_separation,
        "max_norm_drift": max(abs(record["norm"] - initial["norm"]) for record in run.records),
        "max_corrected_energy_relative_drift": max(
            abs(record["corrected_energy"] - initial_energy) for record in run.records
        )
        / max(abs(initial_energy), 1.0e-30),
        "max_gauss_residual_absolute": max(record["gauss_residual_absolute"] for record in run.records),
        "max_gauss_residual_relative": max(record["gauss_residual_relative"] for record in run.records),
        "max_net_total_charge": max(
            abs(record["net_matter_charge"] + record["net_absorber_charge"])
            for record in run.records
        ),
        "absorbed_energy": run.absorbed_energy,
        "emitted_energy": run.emitted_energy,
    }
