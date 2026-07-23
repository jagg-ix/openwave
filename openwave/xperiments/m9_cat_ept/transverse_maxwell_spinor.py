"""Bounded M9.7c transverse Maxwell--spinor radiation qualification.

The model is a planar 1D reduction of a transverse gauge mode A_y(x,t) coupled
self-consistently to a neutral charge-conjugate pair of local two-component
spinors.  It is deliberately not a full spatial Maxwell--Dirac solver.

Equations (c = epsilon0 = mu0 = 1):

    A_t = -E
    E_t = -A_xx - J - sigma(x) E
    B = A_x

    i psi_s,t = [m sigma_z - s q A sigma_y] psi_s,  s in {+1,-1}
    J = sum_s s q psi_s^dagger sigma_y psi_s.

The pair starts with equal pointwise densities, so the signed charge density
rho_q = q(|psi_+|^2-|psi_-|^2) is zero and remains zero under the exact local
spinor propagator.  Hence transverse Gauss law is preserved without projection.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class TransverseParameters:
    mass: float = 1.0
    gauge_charge: float = 0.35
    polarization_angle: float = 0.45
    envelope_width: float = 2.5
    matter_norm: float = 1.0
    gauge_seed_amplitude: float = 0.01
    gauge_seed_width: float = 4.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.gauge_charge <= 0.0:
            raise ValueError("gauge_charge must be positive")
        if not 0.0 < self.polarization_angle < 0.5 * math.pi:
            raise ValueError("polarization_angle must lie in (0, pi/2)")
        if self.envelope_width <= 0.0:
            raise ValueError("envelope_width must be positive")
        if self.matter_norm <= 0.0:
            raise ValueError("matter_norm must be positive")
        if self.gauge_seed_amplitude < 0.0:
            raise ValueError("gauge_seed_amplitude must be nonnegative")
        if self.gauge_seed_width <= 0.0:
            raise ValueError("gauge_seed_width must be positive")


@dataclass(frozen=True)
class TransverseGrid:
    half_width: float = 60.0
    points: int = 1024
    final_time: float = 30.0
    dt_over_dx: float = 0.20
    absorber_fraction: float = 0.20
    absorber_strength: float = 0.45
    samples: int = 121

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 128 or self.points % 2:
            raise ValueError("points must be an even integer at least 128")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_dx <= 0.30:
            raise ValueError("dt_over_dx must lie in (0, 0.30]")
        if not 0.05 <= self.absorber_fraction <= 0.35:
            raise ValueError("absorber_fraction must lie in [0.05, 0.35]")
        if self.absorber_strength < 0.0:
            raise ValueError("absorber_strength must be nonnegative")
        if self.samples < 2:
            raise ValueError("samples must be at least 2")


@dataclass(frozen=True)
class TransverseRun:
    x: RealArray
    dx: float
    dt: float
    steps: int
    parameters: TransverseParameters
    grid: TransverseGrid
    initial_a: RealArray
    initial_e: RealArray
    initial_plus: ComplexArray
    initial_minus: ComplexArray
    final_a: RealArray
    final_e: RealArray
    final_plus: ComplexArray
    final_minus: ComplexArray
    records: tuple[dict[str, float], ...]
    absorbed_energy: float
    emitted_energy: float
    probe_radius: float


def periodic_grid(grid: TransverseGrid) -> tuple[RealArray, float]:
    dx = 2.0 * grid.half_width / grid.points
    x = -grid.half_width + dx * np.arange(grid.points, dtype=np.float64)
    return x, dx


def absorber_profile(x: RealArray, grid: TransverseGrid) -> RealArray:
    start = grid.half_width * (1.0 - grid.absorber_fraction)
    scaled = np.clip((np.abs(x) - start) / (grid.half_width - start), 0.0, 1.0)
    return grid.absorber_strength * scaled**4


def first_derivative(values: RealArray, dx: float) -> RealArray:
    return np.asarray((np.roll(values, -1) - np.roll(values, 1)) / (2.0 * dx))


def second_derivative(values: RealArray, dx: float) -> RealArray:
    return np.asarray(
        (np.roll(values, -1) - 2.0 * values + np.roll(values, 1)) / dx**2
    )


def _normalize_envelope(
    x: RealArray,
    parameters: TransverseParameters,
    dx: float,
) -> RealArray:
    raw = np.exp(-0.5 * (x / parameters.envelope_width) ** 2)
    factor = math.sqrt(parameters.matter_norm / (2.0 * dx * np.sum(raw**2)))
    return np.asarray(factor * raw, dtype=np.float64)


def initial_spinors(
    x: RealArray,
    dx: float,
    parameters: TransverseParameters,
) -> tuple[ComplexArray, ComplexArray]:
    envelope = _normalize_envelope(x, parameters, dx)
    theta = parameters.polarization_angle
    plus_state = np.asarray(
        [math.cos(0.5 * theta), math.sin(0.5 * theta)], dtype=np.complex128
    )
    minus_state = np.asarray(
        [math.cos(0.5 * theta), -math.sin(0.5 * theta)], dtype=np.complex128
    )
    return (
        np.asarray(plus_state[:, None] * envelope[None, :], dtype=np.complex128),
        np.asarray(minus_state[:, None] * envelope[None, :], dtype=np.complex128),
    )


def sigma_y_expectation(state: ComplexArray) -> RealArray:
    upper = state[0]
    lower = state[1]
    return np.asarray(2.0 * np.imag(np.conj(upper) * lower), dtype=np.float64)


def sigma_z_expectation(state: ComplexArray) -> RealArray:
    return np.asarray(np.abs(state[0]) ** 2 - np.abs(state[1]) ** 2, dtype=np.float64)


def species_density(state: ComplexArray) -> RealArray:
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def signed_charge_density(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransverseParameters,
) -> RealArray:
    return np.asarray(
        parameters.gauge_charge * (species_density(plus) - species_density(minus)),
        dtype=np.float64,
    )


def transverse_current(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransverseParameters,
) -> RealArray:
    q = parameters.gauge_charge
    return np.asarray(
        q * sigma_y_expectation(plus) - q * sigma_y_expectation(minus),
        dtype=np.float64,
    )


def matter_energy(
    a: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransverseParameters,
    dx: float,
) -> float:
    m = parameters.mass
    q = parameters.gauge_charge
    density = (
        m * sigma_z_expectation(plus)
        - q * a * sigma_y_expectation(plus)
        + m * sigma_z_expectation(minus)
        + q * a * sigma_y_expectation(minus)
    )
    return float(dx * np.sum(density))


def field_energy(a: RealArray, e: RealArray, dx: float) -> float:
    b = first_derivative(a, dx)
    return float(0.5 * dx * np.sum(e**2 + b**2))


def pointwise_pair_norm_error(plus: ComplexArray, minus: ComplexArray) -> float:
    return float(np.max(np.abs(species_density(plus) - species_density(minus))))


def _sample_record(
    time: float,
    a: RealArray,
    e: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    absorbed: float,
    emitted: float,
    parameters: TransverseParameters,
    grid: TransverseGrid,
    x: RealArray,
    dx: float,
    probe_index: int,
) -> dict[str, float]:
    b = first_derivative(a, dx)
    m_energy = matter_energy(a, plus, minus, parameters, dx)
    f_energy = field_energy(a, e, dx)
    poynting_right = e[probe_index] * b[probe_index]
    left_index = (-probe_index) % grid.points
    poynting_left = e[left_index] * b[left_index]
    charge = signed_charge_density(plus, minus, parameters)
    central_mask = np.abs(x) <= 4.0 * parameters.envelope_width
    field_density = 0.5 * (e**2 + b**2)
    total_field = dx * np.sum(field_density)
    central_field = dx * np.sum(field_density[central_mask])
    return {
        "time": float(time),
        "matter_energy": m_energy,
        "field_energy": f_energy,
        "total_energy": m_energy + f_energy,
        "absorbed_energy": float(absorbed),
        "corrected_energy": m_energy + f_energy + absorbed,
        "emitted_energy": float(emitted),
        "right_poynting": float(poynting_right),
        "left_poynting": float(poynting_left),
        "max_charge_density": float(np.max(np.abs(charge))),
        "pair_norm_error": pointwise_pair_norm_error(plus, minus),
        "field_energy_central_fraction": (
            0.0 if total_field == 0.0 else float(central_field / total_field)
        ),
        "max_field": float(max(np.max(np.abs(e)), np.max(np.abs(b)))),
        "current_l2": float(
            math.sqrt(dx * np.sum(transverse_current(plus, minus, parameters) ** 2))
        ),
    }


def _rhs(
    a: RealArray,
    e: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    sigma: RealArray,
    parameters: TransverseParameters,
    dx: float,
    matter_enabled: bool,
) -> tuple[RealArray, RealArray, ComplexArray, ComplexArray, float]:
    current = transverse_current(plus, minus, parameters) if matter_enabled else np.zeros_like(a)
    da = -e
    de = -second_derivative(a, dx) - current - sigma * e
    if matter_enabled:
        m = parameters.mass
        q_a = parameters.gauge_charge * a
        plus_h0 = m * plus[0] + 1j * q_a * plus[1]
        plus_h1 = -1j * q_a * plus[0] - m * plus[1]
        minus_h0 = m * minus[0] - 1j * q_a * minus[1]
        minus_h1 = 1j * q_a * minus[0] - m * minus[1]
        dplus = -1j * np.asarray([plus_h0, plus_h1])
        dminus = -1j * np.asarray([minus_h0, minus_h1])
    else:
        dplus = np.zeros_like(plus)
        dminus = np.zeros_like(minus)
    loss_rate = dx * float(np.sum(sigma * e**2))
    return da, de, dplus, dminus, loss_rate


def _state_add(
    a: RealArray,
    e: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    factor: float,
    derivative: tuple[RealArray, RealArray, ComplexArray, ComplexArray, float],
) -> tuple[RealArray, RealArray, ComplexArray, ComplexArray]:
    return (
        a + factor * derivative[0],
        e + factor * derivative[1],
        plus + factor * derivative[2],
        minus + factor * derivative[3],
    )


def _outward_flux(
    a: RealArray,
    e: RealArray,
    dx: float,
    right_index: int,
    left_index: int,
) -> float:
    b = first_derivative(a, dx)
    return float(e[right_index] * b[right_index] - e[left_index] * b[left_index])


def evolve_transverse_system(
    parameters: TransverseParameters = TransverseParameters(),
    grid: TransverseGrid = TransverseGrid(),
    *,
    initial_a: RealArray | None = None,
    initial_e: RealArray | None = None,
    initial_plus: ComplexArray | None = None,
    initial_minus: ComplexArray | None = None,
    matter_enabled: bool = True,
) -> TransverseRun:
    x, dx = periodic_grid(grid)
    a = np.zeros(grid.points, dtype=np.float64) if initial_a is None else np.asarray(initial_a, dtype=np.float64).copy()
    e = np.zeros(grid.points, dtype=np.float64) if initial_e is None else np.asarray(initial_e, dtype=np.float64).copy()
    if a.shape != (grid.points,) or e.shape != (grid.points,):
        raise ValueError("initial fields must match the grid")
    if initial_plus is None or initial_minus is None:
        plus, minus = initial_spinors(x, dx, parameters)
    else:
        plus = np.asarray(initial_plus, dtype=np.complex128).copy()
        minus = np.asarray(initial_minus, dtype=np.complex128).copy()
    if plus.shape != (2, grid.points) or minus.shape != (2, grid.points):
        raise ValueError("spinors must have shape (2, points)")
    if not matter_enabled:
        plus[:] = 0.0
        minus[:] = 0.0

    initial_a_copy = a.copy()
    initial_e_copy = e.copy()
    initial_plus_copy = plus.copy()
    initial_minus_copy = minus.copy()

    target_dt = grid.dt_over_dx * dx
    steps = max(1, math.ceil(grid.final_time / target_dt))
    dt = grid.final_time / steps
    sigma = absorber_profile(x, grid)
    sample_indices = set(np.linspace(0, steps, grid.samples, dtype=int).tolist())
    probe_radius = min(20.0, 0.5 * grid.half_width)
    probe_index = int(np.argmin(np.abs(x - probe_radius)))
    left_index = int(np.argmin(np.abs(x + probe_radius)))

    absorbed = 0.0
    emitted = 0.0
    records: list[dict[str, float]] = []
    records.append(
        _sample_record(
            0.0,
            a,
            e,
            plus,
            minus,
            absorbed,
            emitted,
            parameters,
            grid,
            x,
            dx,
            probe_index,
        )
    )

    for step in range(1, steps + 1):
        k1 = _rhs(a, e, plus, minus, sigma, parameters, dx, matter_enabled)
        s2 = _state_add(a, e, plus, minus, 0.5 * dt, k1)
        k2 = _rhs(*s2, sigma, parameters, dx, matter_enabled)
        s3 = _state_add(a, e, plus, minus, 0.5 * dt, k2)
        k3 = _rhs(*s3, sigma, parameters, dx, matter_enabled)
        s4 = _state_add(a, e, plus, minus, dt, k3)
        k4 = _rhs(*s4, sigma, parameters, dx, matter_enabled)

        flux1 = _outward_flux(a, e, dx, probe_index, left_index)
        flux2 = _outward_flux(s2[0], s2[1], dx, probe_index, left_index)
        flux3 = _outward_flux(s3[0], s3[1], dx, probe_index, left_index)
        flux4 = _outward_flux(s4[0], s4[1], dx, probe_index, left_index)

        a = a + dt * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0
        e = e + dt * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]) / 6.0
        plus = plus + dt * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]) / 6.0
        minus = minus + dt * (k1[3] + 2.0 * k2[3] + 2.0 * k3[3] + k4[3]) / 6.0
        absorbed += dt * (k1[4] + 2.0 * k2[4] + 2.0 * k3[4] + k4[4]) / 6.0
        emitted += dt * (flux1 + 2.0 * flux2 + 2.0 * flux3 + flux4) / 6.0

        if step in sample_indices:
            records.append(
                _sample_record(
                    step * dt,
                    a,
                    e,
                    plus,
                    minus,
                    absorbed,
                    emitted,
                    parameters,
                    grid,
                    x,
                    dx,
                    probe_index,
                )
            )

    return TransverseRun(
        x=x,
        dx=dx,
        dt=dt,
        steps=steps,
        parameters=parameters,
        grid=grid,
        initial_a=initial_a_copy,
        initial_e=initial_e_copy,
        initial_plus=initial_plus_copy,
        initial_minus=initial_minus_copy,
        final_a=a,
        final_e=e,
        final_plus=plus,
        final_minus=minus,
        records=tuple(records),
        absorbed_energy=float(absorbed),
        emitted_energy=float(emitted),
        probe_radius=float(probe_radius),
    )


def coupled_initial_fields(
    x: RealArray,
    parameters: TransverseParameters,
) -> tuple[RealArray, RealArray]:
    a = parameters.gauge_seed_amplitude * np.exp(-(x / parameters.gauge_seed_width) ** 2)
    e = np.zeros_like(a)
    return np.asarray(a, dtype=np.float64), np.asarray(e, dtype=np.float64)


def vacuum_pulse_initial_state(
    x: RealArray,
    center: float = -20.0,
    width: float = 3.0,
    amplitude: float = 0.08,
) -> tuple[RealArray, RealArray]:
    shifted = (x - center) / width
    a = amplitude * np.exp(-shifted**2)
    e = -2.0 * amplitude * shifted / width * np.exp(-shifted**2)
    return np.asarray(a), np.asarray(e)


def vacuum_reference(
    x: RealArray,
    time: float,
    center: float = -20.0,
    width: float = 3.0,
    amplitude: float = 0.08,
) -> tuple[RealArray, RealArray]:
    shifted = (x - center - time) / width
    a = amplitude * np.exp(-shifted**2)
    e = -2.0 * amplitude * shifted / width * np.exp(-shifted**2)
    return np.asarray(a), np.asarray(e)


def relative_l2(actual: RealArray, expected: RealArray, dx: float) -> float:
    numerator = math.sqrt(dx * float(np.sum((actual - expected) ** 2)))
    denominator = math.sqrt(dx * float(np.sum(expected**2)))
    return numerator / denominator


def run_vacuum_refinement(
    points: Sequence[int] = (256, 512, 1024),
) -> dict[str, Any]:
    records: list[dict[str, float]] = []
    for count in points:
        grid = TransverseGrid(
            half_width=60.0,
            points=count,
            final_time=12.0,
            dt_over_dx=0.20,
            absorber_fraction=0.15,
            absorber_strength=0.0,
            samples=5,
        )
        x, dx = periodic_grid(grid)
        a0, e0 = vacuum_pulse_initial_state(x)
        run = evolve_transverse_system(
            grid=grid,
            initial_a=a0,
            initial_e=e0,
            matter_enabled=False,
        )
        a_ref, e_ref = vacuum_reference(x, grid.final_time)
        records.append(
            {
                "points": count,
                "a_relative_l2": relative_l2(run.final_a, a_ref, dx),
                "e_relative_l2": relative_l2(run.final_e, e_ref, dx),
                "energy_relative_drift": abs(
                    run.records[-1]["field_energy"] - run.records[0]["field_energy"]
                )
                / run.records[0]["field_energy"],
            }
        )
    a_errors = [record["a_relative_l2"] for record in records]
    e_errors = [record["e_relative_l2"] for record in records]
    return {
        "records": records,
        "observed_orders": {
            "a": [
                math.log(a_errors[i] / a_errors[i + 1], 2.0)
                for i in range(len(a_errors) - 1)
            ],
            "e": [
                math.log(e_errors[i] / e_errors[i + 1], 2.0)
                for i in range(len(e_errors) - 1)
            ],
        },
    }


def run_coupled_refinement(
    points: Sequence[int] = (256, 512, 1024),
    final_time: float = 18.0,
) -> dict[str, Any]:
    runs: list[TransverseRun] = []
    for count in points:
        grid = TransverseGrid(
            half_width=60.0,
            points=count,
            final_time=final_time,
            dt_over_dx=0.18,
            absorber_fraction=0.20,
            absorber_strength=0.45,
            samples=73,
        )
        x, _ = periodic_grid(grid)
        a0, e0 = coupled_initial_fields(x, TransverseParameters())
        runs.append(evolve_transverse_system(grid=grid, initial_a=a0, initial_e=e0))

    differences_a: list[float] = []
    differences_e: list[float] = []
    for coarse, fine in zip(runs[:-1], runs[1:], strict=True):
        fine_a = fine.final_a[::2]
        fine_e = fine.final_e[::2]
        differences_a.append(relative_l2(coarse.final_a, fine_a, coarse.dx))
        differences_e.append(relative_l2(coarse.final_e, fine_e, coarse.dx))

    summaries = [run_summary(run) for run in runs]
    return {
        "summaries": summaries,
        "successive_differences": {"a": differences_a, "e": differences_e},
        "observed_orders": {
            "a": math.log(differences_a[0] / differences_a[1], 2.0),
            "e": math.log(differences_e[0] / differences_e[1], 2.0),
        },
    }


def run_summary(run: TransverseRun) -> dict[str, Any]:
    initial = run.records[0]
    final = run.records[-1]
    corrected_initial = initial["corrected_energy"]
    corrected_drift = max(
        abs(record["corrected_energy"] - corrected_initial) for record in run.records
    ) / max(abs(corrected_initial), 1.0e-30)
    max_charge = max(record["max_charge_density"] for record in run.records)
    max_pair_error = max(record["pair_norm_error"] for record in run.records)
    max_boundary_field = max(
        max(abs(record["left_poynting"]), abs(record["right_poynting"]))
        for record in run.records
    )
    return {
        "grid": asdict(run.grid),
        "parameters": asdict(run.parameters),
        "dt": run.dt,
        "steps": run.steps,
        "initial": initial,
        "final": final,
        "absorbed_energy": run.absorbed_energy,
        "emitted_energy": run.emitted_energy,
        "corrected_energy_relative_drift": corrected_drift,
        "max_charge_density": max_charge,
        "max_pair_norm_error": max_pair_error,
        "max_probe_poynting_magnitude": max_boundary_field,
    }


def run_absorber_study() -> dict[str, Any]:
    cases = (
        (50.0, 0.18, 0.40),
        (60.0, 0.20, 0.45),
        (70.0, 0.22, 0.50),
    )
    records: list[dict[str, float]] = []
    dx = 120.0 / 1024.0
    for half_width, fraction, strength in cases:
        points = int(round(2.0 * half_width / dx))
        if points % 2:
            points += 1
        grid = TransverseGrid(
            half_width=half_width,
            points=points,
            final_time=75.0,
            dt_over_dx=0.18,
            absorber_fraction=fraction,
            absorber_strength=strength,
            samples=129,
        )
        x, _ = periodic_grid(grid)
        a0, e0 = coupled_initial_fields(x, TransverseParameters())
        run = evolve_transverse_system(grid=grid, initial_a=a0, initial_e=e0)
        summary = run_summary(run)
        records.append(
            {
                "half_width": half_width,
                "points": points,
                "absorber_fraction": fraction,
                "absorber_strength": strength,
                "emitted_energy": summary["emitted_energy"],
                "absorbed_energy": summary["absorbed_energy"],
                "final_field_energy": summary["final"]["field_energy"],
                "final_central_fraction": summary["final"][
                    "field_energy_central_fraction"
                ],
                "corrected_energy_relative_drift": summary[
                    "corrected_energy_relative_drift"
                ],
            }
        )
    emitted = np.asarray([record["emitted_energy"] for record in records])
    return {
        "records": records,
        "emitted_relative_spread": float(
            (np.max(emitted) - np.min(emitted)) / np.mean(np.abs(emitted))
        ),
    }


@lru_cache(maxsize=1)
def run_transverse_study() -> dict[str, Any]:
    vacuum = run_vacuum_refinement()
    coupled = run_coupled_refinement()
    long_grid = TransverseGrid(
        half_width=60.0,
        points=1024,
        final_time=80.0,
        dt_over_dx=0.18,
        absorber_fraction=0.20,
        absorber_strength=0.45,
        samples=161,
    )
    long_x, _ = periodic_grid(long_grid)
    long_a0, long_e0 = coupled_initial_fields(long_x, TransverseParameters())
    long_run = evolve_transverse_system(
        grid=long_grid,
        initial_a=long_a0,
        initial_e=long_e0,
    )
    long_summary = run_summary(long_run)
    absorber = run_absorber_study()

    finest = coupled["summaries"][-1]
    acceptance = {
        "vacuum_second_order": min(
            vacuum["observed_orders"]["a"] + vacuum["observed_orders"]["e"]
        )
        >= 1.7,
        "coupled_convergent": min(
            coupled["observed_orders"]["a"], coupled["observed_orders"]["e"]
        )
        >= 1.5,
        "dynamic_gauss_without_projection": finest["max_charge_density"] <= 2.0e-12,
        "pair_norm_preserved": finest["max_pair_norm_error"] <= 2.0e-12,
        "energy_balance_closes": finest["corrected_energy_relative_drift"] <= 2.0e-4,
        "nonzero_radiation": finest["emitted_energy"] >= 1.0e-5,
        "absorber_removes_radiation": long_summary["absorbed_energy"] >= 1.0e-5,
        "long_time_energy_balance": long_summary[
            "corrected_energy_relative_drift"
        ]
        <= 3.0e-4,
        "absorber_study_stable": absorber["emitted_relative_spread"] <= 0.20,
        "radiation_leaves_core": long_summary["final"][
            "field_energy_central_fraction"
        ]
        <= 0.75,
    }
    return {
        "schema": "openwave.m9.transverse-maxwell-spinor-result.v1",
        "task": "M9.7c",
        "model": "neutral transverse spinor-current pair plus planar Maxwell mode",
        "vacuum_refinement": vacuum,
        "coupled_refinement": coupled,
        "long_run": long_summary,
        "absorber_study": absorber,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a non-spherical transverse Maxwell mode with E_y and B_z",
                "self-consistent two-way exchange with a neutral spinor-current pair",
                "dynamic zero-charge Gauss closure without Poisson projection",
                "nonzero-capable Poynting flux and absorber energy accounting",
                "resolution and absorber-window convergence for the bounded reduction",
            ],
            "does_not_establish": [
                "full spatial Maxwell--Dirac evolution",
                "a localized charged single-particle solution",
                "electron identity, calibrated charge, or fermionic quantization",
                "three-dimensional non-spherical orbital stability",
                "unique CAT/EPT derivation of the transverse reduction",
            ],
        },
    }
