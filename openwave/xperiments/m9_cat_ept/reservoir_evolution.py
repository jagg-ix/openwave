"""Evolution and diagnostics for M9.17 reservoir accounting."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from .reservoir_core import (
    ComplexArray, RealArray, ReservoirGrid, ReservoirParameters, ReservoirRun,
    SIGMA_X, SIGMA_Z, current, density, initial_state, loss_profile,
    spectral_derivative,
)

def spinor_rhs(
    state: ComplexArray,
    profile: RealArray,
    parameters: ReservoirParameters,
    dx: float,
) -> ComplexArray:
    derivative = spectral_derivative(state, dx)
    transport = -(SIGMA_X @ derivative)
    mass_term = -1j * parameters.mass * (SIGMA_Z @ state)
    loss = -0.5 * parameters.coupling * profile[None, :] * state
    return np.asarray(transport + mass_term + loss, dtype=np.complex128)


def full_rhs(
    plus: ComplexArray,
    minus: ComplexArray,
    reservoir_plus: RealArray,
    reservoir_minus: RealArray,
    profile: RealArray,
    parameters: ReservoirParameters,
    dx: float,
) -> tuple[ComplexArray, ComplexArray, RealArray, RealArray]:
    del reservoir_plus, reservoir_minus
    plus_rhs = spinor_rhs(plus, profile, parameters, dx)
    minus_rhs = spinor_rhs(minus, profile, parameters, dx)
    reservoir_plus_rhs = parameters.coupling * profile * density(plus)
    reservoir_minus_rhs = parameters.coupling * profile * density(minus)
    return plus_rhs, minus_rhs, reservoir_plus_rhs, reservoir_minus_rhs


def rk4_step(
    state: tuple[ComplexArray, ComplexArray, RealArray, RealArray],
    dt: float,
    profile: RealArray,
    parameters: ReservoirParameters,
    dx: float,
) -> tuple[ComplexArray, ComplexArray, RealArray, RealArray]:
    def rhs(values):
        return full_rhs(*values, profile, parameters, dx)

    def combine(values, increments, factor):
        return tuple(value + factor * increment for value, increment in zip(values, increments, strict=True))

    k1 = rhs(state)
    k2 = rhs(combine(state, k1, 0.5 * dt))
    k3 = rhs(combine(state, k2, 0.5 * dt))
    k4 = rhs(combine(state, k3, dt))
    return tuple(
        value + dt * (a + 2.0 * b + 2.0 * c + d) / 6.0
        for value, a, b, c, d in zip(state, k1, k2, k3, k4, strict=True)
    )


def ledger(
    plus: ComplexArray,
    minus: ComplexArray,
    reservoir_plus: RealArray,
    reservoir_minus: RealArray,
    parameters: ReservoirParameters,
    dx: float,
) -> dict[str, float]:
    matter_plus = dx * float(np.sum(density(plus)))
    matter_minus = dx * float(np.sum(density(minus)))
    reservoir_plus_total = dx * float(np.sum(reservoir_plus))
    reservoir_minus_total = dx * float(np.sum(reservoir_minus))
    matter = matter_plus + matter_minus
    reservoir = reservoir_plus_total + reservoir_minus_total
    extended = matter + reservoir
    matter_charge = parameters.charge * (matter_plus - matter_minus)
    reservoir_charge = parameters.charge * (reservoir_plus_total - reservoir_minus_total)
    tau = -0.5 * math.log(max(matter, np.finfo(float).tiny))
    return {
        "matter_probability": matter,
        "reservoir_probability": reservoir,
        "extended_probability": extended,
        "matter_charge": matter_charge,
        "reservoir_charge": reservoir_charge,
        "extended_charge": matter_charge + reservoir_charge,
        "tau_ent": tau,
        "minimum_reservoir_density": float(min(np.min(reservoir_plus), np.min(reservoir_minus))),
    }


def continuity_residual(
    state: ComplexArray,
    profile: RealArray,
    parameters: ReservoirParameters,
    dx: float,
) -> float:
    state_rhs = spinor_rhs(state, profile, parameters, dx)
    matter_rate = 2.0 * np.real(np.sum(np.conj(state) * state_rhs, axis=0))
    reservoir_rate = parameters.coupling * profile * density(state)
    residual = matter_rate + reservoir_rate + np.real(spectral_derivative(current(state), dx))
    return float(np.max(np.abs(residual)))


def packet_center(x: RealArray, state: ComplexArray, dx: float) -> float:
    rho = density(state)
    norm = dx * float(np.sum(rho))
    return dx * float(np.sum(x * rho)) / norm


def evolve_reservoir(
    parameters: ReservoirParameters = ReservoirParameters(),
    grid: ReservoirGrid = ReservoirGrid(),
) -> ReservoirRun:
    x, dx, plus, minus, reservoir_plus, reservoir_minus = initial_state(parameters, grid)
    initial_plus = plus.copy()
    initial_minus = minus.copy()
    profile = loss_profile(x, grid.half_width)
    target_dt = grid.dt_over_dx * dx
    steps = max(1, math.ceil(grid.final_time / target_dt))
    dt = grid.final_time / steps
    sample_steps = set(np.linspace(0, steps, grid.samples, dtype=int).tolist())
    records: list[dict[str, float]] = []

    def record(step: int) -> None:
        values = ledger(plus, minus, reservoir_plus, reservoir_minus, parameters, dx)
        values.update(
            {
                "time": step * dt,
                "plus_center": packet_center(x, plus, dx),
                "minus_center": packet_center(x, minus, dx),
                "plus_continuity_residual": continuity_residual(plus, profile, parameters, dx),
                "minus_continuity_residual": continuity_residual(minus, profile, parameters, dx),
            }
        )
        records.append(values)

    record(0)
    for step in range(1, steps + 1):
        plus, minus, reservoir_plus, reservoir_minus = rk4_step(
            (plus, minus, reservoir_plus, reservoir_minus),
            dt,
            profile,
            parameters,
            dx,
        )
        if step in sample_steps:
            record(step)

    return ReservoirRun(
        x=x,
        dx=dx,
        dt=dt,
        steps=steps,
        parameters=parameters,
        grid=grid,
        initial_plus=initial_plus,
        initial_minus=initial_minus,
        final_plus=plus,
        final_minus=minus,
        final_reservoir_plus=reservoir_plus,
        final_reservoir_minus=reservoir_minus,
        records=tuple(records),
    )


