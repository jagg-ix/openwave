"""Evolution and diagnostics for the M9.10 two-dimensional reduction."""

from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any

import numpy as np

from .planar_2d_core import (
    ComplexArray,
    Planar2DGrid,
    Planar2DParameters,
    Planar2DRun,
    RealArray,
    absorber_profile,
    currents,
    density,
    derivative_x,
    derivative_y,
    initial_state,
    pauli_expectations,
    signed_charge_density,
    wave_numbers,
)


def _effective_mass(
    state: ComplexArray,
    parameters: Planar2DParameters,
) -> RealArray:
    _, _, scalar = pauli_expectations(state)
    return parameters.mass - parameters.soler_coupling * scalar


def _hamiltonian_action(
    state: ComplexArray,
    charge_sign: float,
    ax: RealArray,
    ay: RealArray,
    parameters: Planar2DParameters,
    kx: RealArray,
    ky: RealArray,
) -> ComplexArray:
    d_x = derivative_x(state, kx)
    d_y = derivative_y(state, ky)
    upper, lower = state
    du_x, dl_x = d_x
    du_y, dl_y = d_y
    q = charge_sign * parameters.gauge_charge
    mass = _effective_mass(state, parameters)
    h0 = (
        -1j * dl_x
        - dl_y
        + mass * upper
        - q * ax * lower
        + 1j * q * ay * lower
    )
    h1 = (
        -1j * du_x
        + du_y
        - mass * lower
        - q * ax * upper
        - 1j * q * ay * upper
    )
    return np.asarray([h0, h1], dtype=np.complex128)


def magnetic_field(
    ax: RealArray,
    ay: RealArray,
    kx: RealArray,
    ky: RealArray,
) -> RealArray:
    value = derivative_x(ay, kx) - derivative_y(ax, ky)
    return np.asarray(np.real(value), dtype=np.float64)


def _rhs(
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ay: RealArray,
    ex: RealArray,
    ey: RealArray,
    absorber_charge: RealArray,
    sigma: RealArray,
    parameters: Planar2DParameters,
    kx: RealArray,
    ky: RealArray,
    cell_area: float,
):
    jx, jy = currents(plus, minus, parameters)
    dplus = -1j * _hamiltonian_action(
        plus, 1.0, ax, ay, parameters, kx, ky
    )
    dminus = -1j * _hamiltonian_action(
        minus, -1.0, ax, ay, parameters, kx, ky
    )
    bz = magnetic_field(ax, ay, kx, ky)
    dax = -ex
    day = -ey
    dex = np.real(derivative_y(bz, ky)) - jx - sigma * ex
    dey = -np.real(derivative_x(bz, kx)) - jy - sigma * ey
    d_absorber_charge = -np.real(
        derivative_x(sigma * ex, kx) + derivative_y(sigma * ey, ky)
    )
    loss = cell_area * float(np.sum(sigma * (ex**2 + ey**2)))
    return dplus, dminus, dax, day, dex, dey, d_absorber_charge, loss


def _combine(state, factor: float, derivative):
    return tuple(
        value + factor * delta
        for value, delta in zip(state, derivative[:7], strict=True)
    )


def total_norm(
    plus: ComplexArray,
    minus: ComplexArray,
    cell_area: float,
) -> float:
    return cell_area * float(np.sum(density(plus) + density(minus)))


def matter_energy(
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ay: RealArray,
    parameters: Planar2DParameters,
    kx: RealArray,
    ky: RealArray,
    cell_area: float,
) -> float:
    hplus = _hamiltonian_action(plus, 1.0, ax, ay, parameters, kx, ky)
    hminus = _hamiltonian_action(minus, -1.0, ax, ay, parameters, kx, ky)
    value = np.sum(np.conj(plus) * hplus)
    value += np.sum(np.conj(minus) * hminus)
    if parameters.soler_coupling:
        _, _, scalar_plus = pauli_expectations(plus)
        _, _, scalar_minus = pauli_expectations(minus)
        value += 0.5 * parameters.soler_coupling * np.sum(
            scalar_plus**2 + scalar_minus**2
        )
    return cell_area * float(np.real(value))


def field_energy(
    ax: RealArray,
    ay: RealArray,
    ex: RealArray,
    ey: RealArray,
    kx: RealArray,
    ky: RealArray,
    cell_area: float,
) -> float:
    bz = magnetic_field(ax, ay, kx, ky)
    return 0.5 * cell_area * float(np.sum(ex**2 + ey**2 + bz**2))


def gauss_metrics(
    ex: RealArray,
    ey: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: Planar2DParameters,
    kx: RealArray,
    ky: RealArray,
    absorber_charge: RealArray | None = None,
) -> tuple[float, float]:
    charge = signed_charge_density(plus, minus, parameters)
    total_charge = charge if absorber_charge is None else charge + absorber_charge
    divergence = np.real(derivative_x(ex, kx) + derivative_y(ey, ky))
    residual = divergence - total_charge
    absolute = float(np.max(np.abs(residual)))
    relative = absolute / max(float(np.max(np.abs(total_charge))), 1.0e-12)
    return absolute, relative


def packet_moments(
    xx: RealArray,
    yy: RealArray,
    state: ComplexArray,
    cell_area: float,
) -> tuple[float, float, float]:
    probability = density(state)
    norm = cell_area * float(np.sum(probability))
    center_x = cell_area * float(np.sum(xx * probability)) / norm
    center_y = cell_area * float(np.sum(yy * probability)) / norm
    radius2 = (xx - center_x) ** 2 + (yy - center_y) ** 2
    rms = math.sqrt(cell_area * float(np.sum(radius2 * probability)) / norm)
    return center_x, center_y, rms


def _outward_flux(
    ex: RealArray,
    ey: RealArray,
    bz: RealArray,
    x_index: int,
    y_index: int,
    dx: float,
    dy: float,
) -> float:
    sx = ey * bz
    sy = -ex * bz
    left = (-x_index) % ex.shape[1]
    bottom = (-y_index) % ex.shape[0]
    vertical = dy * float(np.sum(sx[:, x_index] - sx[:, left]))
    horizontal = dx * float(np.sum(sy[y_index, :] - sy[bottom, :]))
    return vertical + horizontal


def _record(
    time: float,
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ay: RealArray,
    ex: RealArray,
    ey: RealArray,
    absorber_charge: RealArray,
    absorbed: float,
    emitted: float,
    parameters: Planar2DParameters,
    kx: RealArray,
    ky: RealArray,
    xx: RealArray,
    yy: RealArray,
    cell_area: float,
) -> dict[str, float]:
    matter = matter_energy(
        plus, minus, ax, ay, parameters, kx, ky, cell_area
    )
    field = field_energy(ax, ay, ex, ey, kx, ky, cell_area)
    gauss_absolute, gauss_relative = gauss_metrics(
        ex, ey, plus, minus, parameters, kx, ky, absorber_charge
    )
    plus_x, plus_y, plus_rms = packet_moments(xx, yy, plus, cell_area)
    minus_x, minus_y, minus_rms = packet_moments(xx, yy, minus, cell_area)
    charge = signed_charge_density(plus, minus, parameters)
    bz = magnetic_field(ax, ay, kx, ky)
    return {
        "time": time,
        "norm": total_norm(plus, minus, cell_area),
        "matter_energy": matter,
        "field_energy": field,
        "absorbed_energy": absorbed,
        "corrected_energy": matter + field + absorbed,
        "emitted_energy": emitted,
        "gauss_residual_absolute": gauss_absolute,
        "gauss_residual_relative": gauss_relative,
        "net_charge": cell_area * float(np.sum(charge + absorber_charge)),
        "plus_center_x": plus_x,
        "plus_center_y": plus_y,
        "minus_center_x": minus_x,
        "minus_center_y": minus_y,
        "plus_rms_radius": plus_rms,
        "minus_rms_radius": minus_rms,
        "max_magnetic_field": float(np.max(np.abs(bz))),
    }


def evolve_planar_2d(
    parameters: Planar2DParameters = Planar2DParameters(),
    grid: Planar2DGrid = Planar2DGrid(),
) -> Planar2DRun:
    (
        xx,
        yy,
        dx,
        dy,
        plus,
        minus,
        ax,
        ay,
        ex,
        ey,
    ) = initial_state(parameters, grid)
    absorber_charge = np.zeros_like(ex)
    initial = tuple(
        value.copy() for value in (plus, minus, ax, ay, ex, ey, absorber_charge)
    )
    kx, ky = wave_numbers(grid, dx, dy)
    sigma = absorber_profile(xx, yy, grid)
    cell_area = dx * dy
    target_dt = grid.dt_over_spacing * min(dx, dy)
    steps = max(1, math.ceil(grid.final_time / target_dt))
    dt = grid.final_time / steps
    sample_indices = set(
        np.linspace(0, steps, grid.samples, dtype=int).tolist()
    )
    x_probe = int(np.argmin(np.abs(xx[0] - 0.55 * grid.half_width_x)))
    y_probe = int(np.argmin(np.abs(yy[:, 0] - 0.55 * grid.half_width_y)))
    absorbed = 0.0
    emitted = 0.0
    records = [
        _record(
            0.0,
            plus,
            minus,
            ax,
            ay,
            ex,
            ey,
            absorber_charge,
            absorbed,
            emitted,
            parameters,
            kx,
            ky,
            xx,
            yy,
            cell_area,
        )
    ]
    for step in range(1, steps + 1):
        state = (plus, minus, ax, ay, ex, ey, absorber_charge)
        k1 = _rhs(*state, sigma, parameters, kx, ky, cell_area)
        k2 = _rhs(
            *_combine(state, 0.5 * dt, k1),
            sigma,
            parameters,
            kx,
            ky,
            cell_area,
        )
        k3 = _rhs(
            *_combine(state, 0.5 * dt, k2),
            sigma,
            parameters,
            kx,
            ky,
            cell_area,
        )
        k4 = _rhs(
            *_combine(state, dt, k3),
            sigma,
            parameters,
            kx,
            ky,
            cell_area,
        )
        increments = tuple(
            dt * (a + 2.0 * b + 2.0 * c + d) / 6.0
            for a, b, c, d in zip(
                k1[:7], k2[:7], k3[:7], k4[:7], strict=True
            )
        )
        plus, minus, ax, ay, ex, ey, absorber_charge = tuple(
            value + increment
            for value, increment in zip(state, increments, strict=True)
        )
        absorbed += (
            dt * (k1[7] + 2.0 * k2[7] + 2.0 * k3[7] + k4[7]) / 6.0
        )
        bz_old = magnetic_field(state[2], state[3], kx, ky)
        bz_new = magnetic_field(ax, ay, kx, ky)
        flux_old = _outward_flux(
            state[4], state[5], bz_old, x_probe, y_probe, dx, dy
        )
        flux_new = _outward_flux(
            ex, ey, bz_new, x_probe, y_probe, dx, dy
        )
        emitted += 0.5 * dt * (flux_old + flux_new)
        if step in sample_indices:
            records.append(
                _record(
                    step * dt,
                    plus,
                    minus,
                    ax,
                    ay,
                    ex,
                    ey,
                    absorber_charge,
                    absorbed,
                    emitted,
                    parameters,
                    kx,
                    ky,
                    xx,
                    yy,
                    cell_area,
                )
            )
    return Planar2DRun(
        x=xx,
        y=yy,
        dx=dx,
        dy=dy,
        dt=dt,
        steps=steps,
        parameters=parameters,
        grid=grid,
        initial_plus=initial[0],
        initial_minus=initial[1],
        final_plus=plus,
        final_minus=minus,
        initial_ax=initial[2],
        initial_ay=initial[3],
        initial_ex=initial[4],
        initial_ey=initial[5],
        final_ax=ax,
        final_ay=ay,
        final_ex=ex,
        final_ey=ey,
        initial_absorber_charge=initial[6],
        final_absorber_charge=absorber_charge,
        absorbed_energy=absorbed,
        emitted_energy=emitted,
        records=tuple(records),
    )


def run_summary(run: Planar2DRun) -> dict[str, Any]:
    initial = run.records[0]
    corrected_initial = initial["corrected_energy"]
    final = run.records[-1]
    initial_vector = np.asarray(
        [
            initial["minus_center_x"] - initial["plus_center_x"],
            initial["minus_center_y"] - initial["plus_center_y"],
        ]
    )
    final_vector = np.asarray(
        [
            final["minus_center_x"] - final["plus_center_x"],
            final["minus_center_y"] - final["plus_center_y"],
        ]
    )
    return {
        "grid": asdict(run.grid),
        "parameters": asdict(run.parameters),
        "dt": run.dt,
        "steps": run.steps,
        "initial": initial,
        "final": final,
        "initial_separation": float(np.linalg.norm(initial_vector)),
        "final_separation": float(np.linalg.norm(final_vector)),
        "max_norm_drift": max(
            abs(item["norm"] - initial["norm"]) for item in run.records
        ),
        "max_corrected_energy_relative_drift": max(
            abs(item["corrected_energy"] - corrected_initial)
            for item in run.records
        )
        / max(abs(corrected_initial), 1.0e-30),
        "max_net_charge": max(
            abs(item["net_charge"]) for item in run.records
        ),
        "max_gauss_residual_absolute": max(
            item["gauss_residual_absolute"] for item in run.records
        ),
        "max_gauss_residual_relative": max(
            item["gauss_residual_relative"] for item in run.records
        ),
        "emitted_energy": run.emitted_energy,
        "absorbed_energy": run.absorbed_energy,
    }
