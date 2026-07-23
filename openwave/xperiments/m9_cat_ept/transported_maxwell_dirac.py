
"""M9.9 transported planar Maxwell--Dirac qualification.

This bounded 1+1D temporal-gauge reduction evolves two spatially transported
Dirac packets with opposite dimensionless charges and both longitudinal and
transverse Maxwell degrees of freedom. It is not a full 2D/3D Maxwell--Dirac
model or a particle identification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import math
import json
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


@dataclass(frozen=True)
class TransportParameters:
    mass: float = 1.0
    gauge_charge: float = 0.25
    packet_width: float = 2.5
    packet_offset: float = 8.0
    packet_momentum: float = 0.9
    transverse_seed: float = 0.008
    transverse_width: float = 4.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0:
            raise ValueError("mass must be positive")
        if self.gauge_charge < 0.0:
            raise ValueError("gauge_charge must be nonnegative")
        if self.packet_width <= 0.0 or self.transverse_width <= 0.0:
            raise ValueError("widths must be positive")
        if self.packet_offset <= 0.0:
            raise ValueError("packet_offset must be positive")


@dataclass(frozen=True)
class TransportGrid:
    half_width: float = 40.0
    points: int = 512
    final_time: float = 10.0
    dt_over_dx: float = 0.08
    absorber_fraction: float = 0.18
    absorber_strength: float = 0.35
    samples: int = 81

    def __post_init__(self) -> None:
        if self.half_width <= 0.0:
            raise ValueError("half_width must be positive")
        if self.points < 128 or self.points % 2:
            raise ValueError("points must be an even integer at least 128")
        if self.final_time <= 0.0:
            raise ValueError("final_time must be positive")
        if not 0.0 < self.dt_over_dx <= 0.2:
            raise ValueError("dt_over_dx must lie in (0, 0.2]")
        if not 0.05 <= self.absorber_fraction <= 0.3:
            raise ValueError("absorber_fraction must lie in [0.05, 0.3]")
        if self.absorber_strength < 0.0:
            raise ValueError("absorber_strength must be nonnegative")
        if self.samples < 2:
            raise ValueError("samples must be at least two")


@dataclass
class TransportRun:
    x: RealArray
    dx: float
    dt: float
    steps: int
    parameters: TransportParameters
    grid: TransportGrid
    initial_plus: ComplexArray
    initial_minus: ComplexArray
    final_plus: ComplexArray
    final_minus: ComplexArray
    initial_ax: RealArray
    initial_ex: RealArray
    initial_ay: RealArray
    initial_ey: RealArray
    final_ax: RealArray
    final_ex: RealArray
    final_ay: RealArray
    final_ey: RealArray
    absorbed_energy: float
    emitted_energy: float
    records: tuple[dict[str, float], ...]


def periodic_grid(grid: TransportGrid) -> tuple[RealArray, float]:
    dx = 2.0 * grid.half_width / grid.points
    x = -grid.half_width + dx * np.arange(grid.points, dtype=np.float64)
    return x, dx


def first_derivative(values: RealArray | ComplexArray, dx: float):
    return (
        np.roll(values, -1, axis=-1) - np.roll(values, 1, axis=-1)
    ) / (2.0 * dx)


def second_derivative(values: RealArray, dx: float) -> RealArray:
    return np.asarray(
        (np.roll(values, -1) - 2.0 * values + np.roll(values, 1)) / dx**2,
        dtype=np.float64,
    )


def absorber_profile(x: RealArray, grid: TransportGrid) -> RealArray:
    start = grid.half_width * (1.0 - grid.absorber_fraction)
    scaled = np.clip((np.abs(x) - start) / (grid.half_width - start), 0.0, 1.0)
    return grid.absorber_strength * scaled**4


def density(state: ComplexArray) -> RealArray:
    return np.asarray(np.sum(np.abs(state) ** 2, axis=0), dtype=np.float64)


def pauli_expectations(
    state: ComplexArray,
) -> tuple[RealArray, RealArray, RealArray]:
    upper, lower = state
    sx = 2.0 * np.real(np.conj(upper) * lower)
    sy = 2.0 * np.imag(np.conj(upper) * lower)
    sz = np.abs(upper) ** 2 - np.abs(lower) ** 2
    return np.asarray(sx), np.asarray(sy), np.asarray(sz)


def positive_energy_spinor(momentum: float, mass: float) -> ComplexArray:
    energy = math.sqrt(mass**2 + momentum**2)
    vector = np.asarray([energy + mass, momentum], dtype=np.complex128)
    return vector / np.linalg.norm(vector)


def gaussian_packet(
    x: RealArray,
    center: float,
    momentum: float,
    width: float,
    mass: float,
    norm: float,
    dx: float,
) -> ComplexArray:
    envelope = np.exp(-0.5 * ((x - center) / width) ** 2)
    phase = np.exp(1j * momentum * x)
    spinor = (
        positive_energy_spinor(momentum, mass)[:, None]
        * envelope[None, :]
        * phase[None, :]
    )
    scale = math.sqrt(norm / (dx * float(np.sum(density(spinor)))))
    return np.asarray(scale * spinor, dtype=np.complex128)


def signed_charge_density(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransportParameters,
) -> RealArray:
    return parameters.gauge_charge * (density(plus) - density(minus))


def currents(
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransportParameters,
) -> tuple[RealArray, RealArray]:
    plus_x, plus_y, _ = pauli_expectations(plus)
    minus_x, minus_y, _ = pauli_expectations(minus)
    q = parameters.gauge_charge
    return q * (plus_x - minus_x), q * (plus_y - minus_y)


def longitudinal_field_from_charge(charge: RealArray, dx: float) -> RealArray:
    points = charge.size
    wave_numbers = 2.0 * math.pi * np.fft.fftfreq(points, d=dx)
    symbol = 1j * np.sin(wave_numbers * dx) / dx
    charge_hat = np.fft.fft(charge - np.mean(charge))
    field_hat = np.zeros(points, dtype=np.complex128)
    nonzero = np.abs(symbol) > 1.0e-14
    field_hat[nonzero] = charge_hat[nonzero] / symbol[nonzero]
    return np.asarray(np.real(np.fft.ifft(field_hat)), dtype=np.float64)


def initial_state(
    parameters: TransportParameters,
    grid: TransportGrid,
) -> tuple[
    RealArray,
    float,
    ComplexArray,
    ComplexArray,
    RealArray,
    RealArray,
    RealArray,
    RealArray,
]:
    x, dx = periodic_grid(grid)
    plus = gaussian_packet(
        x,
        -parameters.packet_offset,
        parameters.packet_momentum,
        parameters.packet_width,
        parameters.mass,
        0.5,
        dx,
    )
    minus = gaussian_packet(
        x,
        parameters.packet_offset,
        -parameters.packet_momentum,
        parameters.packet_width,
        parameters.mass,
        0.5,
        dx,
    )
    ax = np.zeros_like(x)
    ex = longitudinal_field_from_charge(
        signed_charge_density(plus, minus, parameters),
        dx,
    )
    ay = parameters.transverse_seed * np.exp(
        -(x / parameters.transverse_width) ** 2
    )
    ey = np.zeros_like(x)
    return x, dx, plus, minus, ax, ex, ay, ey


def _hamiltonian_action(
    state: ComplexArray,
    charge_sign: float,
    ax: RealArray,
    ay: RealArray,
    parameters: TransportParameters,
    dx: float,
) -> ComplexArray:
    derivative = first_derivative(state, dx)
    upper, lower = state
    dupper, dlower = derivative
    q = charge_sign * parameters.gauge_charge
    h0 = (
        -1j * dlower
        + parameters.mass * upper
        - q * ax * lower
        + 1j * q * ay * lower
    )
    h1 = (
        -1j * dupper
        - parameters.mass * lower
        - q * ax * upper
        - 1j * q * ay * upper
    )
    return np.asarray([h0, h1], dtype=np.complex128)


def _rhs(
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ex: RealArray,
    ay: RealArray,
    ey: RealArray,
    sigma: RealArray,
    parameters: TransportParameters,
    dx: float,
) -> tuple[
    ComplexArray,
    ComplexArray,
    RealArray,
    RealArray,
    RealArray,
    RealArray,
    float,
]:
    jx, jy = currents(plus, minus, parameters)
    dplus = -1j * _hamiltonian_action(
        plus, 1.0, ax, ay, parameters, dx
    )
    dminus = -1j * _hamiltonian_action(
        minus, -1.0, ax, ay, parameters, dx
    )
    dax = -ex
    dex = -jx
    day = -ey
    dey = -second_derivative(ay, dx) - jy - sigma * ey
    loss_rate = dx * float(np.sum(sigma * ey**2))
    return dplus, dminus, dax, dex, day, dey, loss_rate


def _combine(
    state: tuple[
        ComplexArray,
        ComplexArray,
        RealArray,
        RealArray,
        RealArray,
        RealArray,
    ],
    factor: float,
    derivative: tuple[
        ComplexArray,
        ComplexArray,
        RealArray,
        RealArray,
        RealArray,
        RealArray,
        float,
    ],
):
    return tuple(
        value + factor * delta
        for value, delta in zip(state, derivative[:6], strict=True)
    )


def field_energy(
    ex: RealArray,
    ay: RealArray,
    ey: RealArray,
    dx: float,
) -> float:
    bz = first_derivative(ay, dx)
    return 0.5 * dx * float(np.sum(ex**2 + ey**2 + bz**2))


def matter_energy(
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ay: RealArray,
    parameters: TransportParameters,
    dx: float,
) -> float:
    hplus = _hamiltonian_action(plus, 1.0, ax, ay, parameters, dx)
    hminus = _hamiltonian_action(minus, -1.0, ax, ay, parameters, dx)
    value = np.sum(np.conj(plus) * hplus)
    value += np.sum(np.conj(minus) * hminus)
    return dx * float(np.real(value))


def total_norm(
    plus: ComplexArray,
    minus: ComplexArray,
    dx: float,
) -> float:
    return dx * float(np.sum(density(plus) + density(minus)))


def gauss_metrics(
    ex: RealArray,
    plus: ComplexArray,
    minus: ComplexArray,
    parameters: TransportParameters,
    dx: float,
) -> tuple[float, float]:
    charge = signed_charge_density(plus, minus, parameters)
    residual = first_derivative(ex, dx) - charge
    absolute = float(np.max(np.abs(residual)))
    relative = absolute / max(float(np.max(np.abs(charge))), 1.0e-12)
    return absolute, relative


def packet_center(
    x: RealArray,
    state: ComplexArray,
    dx: float,
) -> float:
    probability = density(state)
    denominator = dx * float(np.sum(probability))
    return dx * float(np.sum(x * probability)) / denominator


def _record(
    time: float,
    plus: ComplexArray,
    minus: ComplexArray,
    ax: RealArray,
    ex: RealArray,
    ay: RealArray,
    ey: RealArray,
    absorbed: float,
    emitted: float,
    parameters: TransportParameters,
    dx: float,
    x: RealArray,
) -> dict[str, float]:
    matter = matter_energy(plus, minus, ax, ay, parameters, dx)
    field = field_energy(ex, ay, ey, dx)
    charge = signed_charge_density(plus, minus, parameters)
    gauss_absolute, gauss_relative = gauss_metrics(
        ex, plus, minus, parameters, dx
    )
    return {
        "time": time,
        "norm": total_norm(plus, minus, dx),
        "matter_energy": matter,
        "field_energy": field,
        "absorbed_energy": absorbed,
        "corrected_energy": matter + field + absorbed,
        "emitted_energy": emitted,
        "gauss_residual_absolute": gauss_absolute,
        "gauss_residual_relative": gauss_relative,
        "net_charge": dx * float(np.sum(charge)),
        "plus_center": packet_center(x, plus, dx),
        "minus_center": packet_center(x, minus, dx),
        "max_transverse_field": float(
            max(
                np.max(np.abs(ey)),
                np.max(np.abs(first_derivative(ay, dx))),
            )
        ),
    }


def evolve_transport(
    parameters: TransportParameters = TransportParameters(),
    grid: TransportGrid = TransportGrid(),
) -> TransportRun:
    x, dx, plus, minus, ax, ex, ay, ey = initial_state(
        parameters, grid
    )
    initial = tuple(
        value.copy() for value in (plus, minus, ax, ex, ay, ey)
    )
    sigma = absorber_profile(x, grid)
    target_dt = grid.dt_over_dx * dx
    steps = max(1, math.ceil(grid.final_time / target_dt))
    dt = grid.final_time / steps
    sample_indices = set(
        np.linspace(0, steps, grid.samples, dtype=int).tolist()
    )
    probe = int(np.argmin(np.abs(x - 0.5 * grid.half_width)))
    left_probe = int(np.argmin(np.abs(x + 0.5 * grid.half_width)))
    absorbed = 0.0
    emitted = 0.0
    records = [
        _record(
            0.0,
            plus,
            minus,
            ax,
            ex,
            ay,
            ey,
            0.0,
            0.0,
            parameters,
            dx,
            x,
        )
    ]

    for step in range(1, steps + 1):
        state = (plus, minus, ax, ex, ay, ey)
        k1 = _rhs(*state, sigma, parameters, dx)
        k2 = _rhs(
            *_combine(state, 0.5 * dt, k1),
            sigma,
            parameters,
            dx,
        )
        k3 = _rhs(
            *_combine(state, 0.5 * dt, k2),
            sigma,
            parameters,
            dx,
        )
        k4 = _rhs(
            *_combine(state, dt, k3),
            sigma,
            parameters,
            dx,
        )
        increments = tuple(
            dt * (a + 2.0 * b + 2.0 * c + d) / 6.0
            for a, b, c, d in zip(
                k1[:6],
                k2[:6],
                k3[:6],
                k4[:6],
                strict=True,
            )
        )
        plus, minus, ax, ex, ay, ey = tuple(
            value + increment
            for value, increment in zip(
                state, increments, strict=True
            )
        )
        absorbed += (
            dt
            * (k1[6] + 2.0 * k2[6] + 2.0 * k3[6] + k4[6])
            / 6.0
        )
        bz_old = first_derivative(state[4], dx)
        bz_new = first_derivative(ay, dx)
        flux_old = (
            state[5][probe] * bz_old[probe]
            - state[5][left_probe] * bz_old[left_probe]
        )
        flux_new = (
            ey[probe] * bz_new[probe]
            - ey[left_probe] * bz_new[left_probe]
        )
        emitted += 0.5 * dt * (flux_old + flux_new)
        if step in sample_indices:
            records.append(
                _record(
                    step * dt,
                    plus,
                    minus,
                    ax,
                    ex,
                    ay,
                    ey,
                    absorbed,
                    emitted,
                    parameters,
                    dx,
                    x,
                )
            )

    return TransportRun(
        x=x,
        dx=dx,
        dt=dt,
        steps=steps,
        parameters=parameters,
        grid=grid,
        initial_plus=initial[0],
        initial_minus=initial[1],
        final_plus=plus,
        final_minus=minus,
        initial_ax=initial[2],
        initial_ex=initial[3],
        initial_ay=initial[4],
        initial_ey=initial[5],
        final_ax=ax,
        final_ex=ex,
        final_ay=ay,
        final_ey=ey,
        absorbed_energy=absorbed,
        emitted_energy=emitted,
        records=tuple(records),
    )


def run_summary(run: TransportRun) -> dict[str, Any]:
    initial = run.records[0]
    corrected_initial = initial["corrected_energy"]
    return {
        "grid": asdict(run.grid),
        "parameters": asdict(run.parameters),
        "dt": run.dt,
        "steps": run.steps,
        "initial": initial,
        "final": run.records[-1],
        "max_norm_drift": max(
            abs(item["norm"] - initial["norm"])
            for item in run.records
        ),
        "max_corrected_energy_relative_drift": max(
            abs(item["corrected_energy"] - corrected_initial)
            for item in run.records
        )
        / max(abs(corrected_initial), 1.0e-30),
        "max_gauss_residual_absolute": max(
            item["gauss_residual_absolute"]
            for item in run.records
        ),
        "max_gauss_residual_relative": max(
            item["gauss_residual_relative"]
            for item in run.records
        ),
        "max_net_charge": max(
            abs(item["net_charge"]) for item in run.records
        ),
        "absorbed_energy": run.absorbed_energy,
        "emitted_energy": run.emitted_energy,
    }


def _state_difference(
    coarse: TransportRun,
    fine: TransportRun,
) -> float:
    fine_plus = fine.final_plus[:, ::2]
    fine_minus = fine.final_minus[:, ::2]
    value = np.sum(np.abs(coarse.final_plus - fine_plus) ** 2)
    value += np.sum(np.abs(coarse.final_minus - fine_minus) ** 2)
    return math.sqrt(coarse.dx * float(value))


def run_refinement(
    points: Sequence[int] = (128, 256, 512),
) -> dict[str, Any]:
    runs = [
        evolve_transport(
            grid=TransportGrid(
                points=count,
                final_time=6.0,
                samples=31,
            )
        )
        for count in points
    ]
    differences = [
        _state_difference(coarse, fine)
        for coarse, fine in zip(
            runs[:-1],
            runs[1:],
            strict=True,
        )
    ]
    return {
        "summaries": [run_summary(run) for run in runs],
        "successive_spinor_l2_differences": differences,
        "observed_order": math.log(
            differences[0] / differences[1], 2.0
        ),
    }


@lru_cache(maxsize=1)
def run_transport_study() -> dict[str, Any]:
    refinement = run_refinement()
    long_run = evolve_transport(
        grid=TransportGrid(
            points=512,
            final_time=14.0,
            samples=71,
        )
    )
    summary = run_summary(long_run)
    initial_separation = (
        summary["initial"]["minus_center"]
        - summary["initial"]["plus_center"]
    )
    final_separation = (
        summary["final"]["minus_center"]
        - summary["final"]["plus_center"]
    )
    acceptance = {
        "transported_spinor_convergent": (
            refinement["observed_order"] >= 1.6
        ),
        "norm_conserved": (
            summary["max_norm_drift"] <= 2.0e-8
        ),
        "energy_balance_closes": (
            summary["max_corrected_energy_relative_drift"] <= 2.0e-6
        ),
        "dynamic_gauss_closes": (
            summary["final"]["gauss_residual_relative"] <= 5.0e-2
            and summary["final"]["gauss_residual_absolute"] <= 4.0e-4
        ),
        "net_charge_neutral": (
            summary["max_net_charge"] <= 1.0e-10
        ),
        "packets_transport": (
            final_separation < 0.75 * initial_separation
        ),
        "transverse_field_backreacts": (
            summary["final"]["max_transverse_field"] >= 1.0e-4
        ),
        "radiation_emitted": (
            abs(summary["emitted_energy"]) >= 1.0e-7
        ),
    }
    return {
        "schema": (
            "openwave.m9.transported-maxwell-dirac-result.v1"
        ),
        "task": "M9.9",
        "model": (
            "transported opposite-charge planar "
            "Maxwell-Dirac reduction"
        ),
        "refinement": refinement,
        "long_run": summary,
        "transport": {
            "initial_separation": initial_separation,
            "final_separation": final_separation,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "spatially transported opposite-charge Dirac wave packets",
                (
                    "longitudinal charge/current evolution and "
                    "dynamic Gauss monitoring"
                ),
                (
                    "transverse electric/magnetic back-reaction "
                    "and Poynting accounting"
                ),
                "bounded planar convergence and conservation ledgers",
            ],
            "does_not_establish": [
                "a localized stable charged particle",
                (
                    "full two- or three-dimensional "
                    "Maxwell-Dirac evolution"
                ),
                (
                    "electron identity, calibrated units, "
                    "or fermionic quantization"
                ),
                (
                    "unique CAT/EPT derivation of "
                    "the transported reduction"
                ),
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
