"""M9.97b--c: Maxwell--Dirac momentum, center, and spin response.

Two opposite winding-three candidates are embedded into positive-energy
four-spinors and evolved with the existing bounded Maxwell--Dirac RK4 engine.
A matched self-field control is evolved in parallel.  Subtracting that control
isolates the partner-induced response without pretending that self-motion or
finite-box drift is an interparticle force.

The campaign compares:

* kinetic-momentum transfer with the M9.96 Lorentz-volume force;
* center acceleration with that same force per unit state norm;
* finite-time spin precession with the instantaneous Dirac generator;
* the interaction-induced spin rate with the rest-frame Pauli/BMT torque.

A mismatch is retained as a model boundary.  In particular, momentum response
can close while the center and rest-frame spin reductions remain open.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import ChargedBranchFeasibilityConfig, charged_seed
from .charged_field_tools import lorentz_force, spectral_shift, static_maxwell_fields
from .gauge_spinor_stationary_feasibility import (
    PAULI,
    run_gauge_spinor_stationary_feasibility,
)
from .spatial_3d_hamiltonian import _rhs, _state_add
from .spatial_3d_operators import apply_matrix, curl, density, derivative, expectation
from .spatial_3d_types import ALPHAS, BETA, Spatial3DParameters

ZERO_TWO = np.zeros((2, 2), dtype=np.complex128)
SPIN_MATRICES = tuple(
    np.block([[matrix, ZERO_TWO], [ZERO_TWO, matrix]]) for matrix in PAULI
)


@dataclass(frozen=True)
class SpinorialPairDynamicsConfig:
    points: int = 16
    half_width: float = 8.0
    winding: int = 3
    core_radius: float = 0.90
    separation: float = 6.0
    mass: float = 1.0
    charge: float = 1.0
    g_factor: float = 2.0
    neutral_iterations: int = 3000
    time_step: float = 4.0e-3
    steps: int = 50
    sample_stride: int = 2
    fit_samples: int = 8
    momentum_force_tolerance: float = 1.0e-1
    generator_spin_tolerance: float = 2.0e-2

    def __post_init__(self) -> None:
        if self.points < 16 or self.points % 2:
            raise ValueError("an even grid with at least 16 points is required")
        if min(
            self.half_width,
            self.core_radius,
            self.separation,
            self.mass,
            self.g_factor,
            self.time_step,
        ) <= 0.0:
            raise ValueError("positive spinorial-pair controls required")
        if self.charge == 0.0 or self.winding == 0:
            raise ValueError("nonzero charge and winding required")
        if self.steps < 10 or self.sample_stride < 1 or self.fit_samples < 4:
            raise ValueError("substantive time and fit campaigns required")
        if self.fit_samples > self.steps // self.sample_stride + 1:
            raise ValueError("fit window exceeds available records")
        if self.separation >= 2.0 * self.half_width:
            raise ValueError("separation must remain inside the periodic box")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    def branch_config(self) -> ChargedBranchFeasibilityConfig:
        return ChargedBranchFeasibilityConfig(
            points=self.points,
            half_width=self.half_width,
            winding=self.winding,
            core_radii=(self.core_radius,),
            neutral_iterations=self.neutral_iterations,
            charged_iterations=100,
        )

    def parameters(self) -> Spatial3DParameters:
        return Spatial3DParameters(
            mass=self.mass,
            gauge_charge=abs(self.charge),
            packet_width=1.0,
            offset_x=0.0,
            offset_y=0.0,
            offset_z=0.0,
            momentum_x=0.0,
            momentum_y=0.0,
            momentum_z=0.0,
            gauge_seed_amplitude=0.0,
            gauge_seed_width=1.0,
            soler_coupling=0.0,
            total_norm=2.0,
        )


def normalize(values: np.ndarray, spacing: float, target: float) -> np.ndarray:
    norm = float(np.sum(np.abs(values) ** 2) * spacing**3)
    if norm <= 0.0 or target <= 0.0:
        raise ValueError("positive state norm and target required")
    return np.asarray(values * math.sqrt(target / norm), dtype=np.complex128)


def spinor_density(pauli_spinor: np.ndarray) -> np.ndarray:
    return np.asarray(np.sum(np.abs(pauli_spinor) ** 2, axis=0), dtype=np.float64)


def pauli_spin_density(
    pauli_spinor: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    result = []
    for matrix in PAULI:
        operated = np.einsum("ab,bxyz->axyz", matrix, pauli_spinor, optimize=True)
        result.append(
            np.asarray(
                0.5
                * np.real(np.sum(np.conj(pauli_spinor) * operated, axis=0)),
                dtype=np.float64,
            )
        )
    return tuple(result)  # type: ignore[return-value]


def pauli_source(
    pauli_spinor: np.ndarray,
    *,
    charge: float,
    mass: float,
    g_factor: float,
    spacing: float,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    if pauli_spinor.ndim != 4 or pauli_spinor.shape[0] != 2:
        raise ValueError("two-component three-dimensional Pauli spinor required")
    rho = spinor_density(pauli_spinor)
    current = []
    for axis in range(3):
        gradient = derivative(pauli_spinor, axis + 1, spacing)
        current.append(
            np.asarray(
                charge
                / mass
                * np.imag(np.sum(np.conj(pauli_spinor) * gradient, axis=0)),
                dtype=np.float64,
            )
        )
    magnetization = tuple(
        g_factor * charge * component / (2.0 * mass)
        for component in pauli_spin_density(pauli_spinor)
    )
    magnetization_current = curl(magnetization, (spacing, spacing, spacing))
    return np.asarray(charge * rho, dtype=np.float64), tuple(
        np.asarray(current[index] + magnetization_current[index], dtype=np.float64)
        for index in range(3)
    )


def pauli_to_dirac(
    pauli_spinor: np.ndarray,
    vector_potential: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    charge_sign: float,
    charge: float,
    mass: float,
    spacing: float,
    target_norm: float = 1.0,
) -> np.ndarray:
    upper = np.asarray(pauli_spinor, dtype=np.complex128)
    lower = np.zeros_like(upper)
    for axis, matrix in enumerate(PAULI):
        mechanical = -1.0j * derivative(upper, axis + 1, spacing)
        mechanical -= charge_sign * charge * vector_potential[axis][None, ...] * upper
        lower += np.einsum("ab,bxyz->axyz", matrix, mechanical, optimize=True) / (
            2.0 * mass
        )
    return normalize(np.concatenate((upper, lower), axis=0), spacing, target_norm)


def spin_vector(state: np.ndarray, spacing: float) -> np.ndarray:
    norm = float(np.sum(density(state)) * spacing**3)
    return np.asarray(
        [
            0.5 * float(np.sum(expectation(state, matrix)) * spacing**3) / norm
            for matrix in SPIN_MATRICES
        ],
        dtype=np.float64,
    )


def state_center(
    state: np.ndarray,
    coordinates: tuple[np.ndarray, np.ndarray, np.ndarray],
    spacing: float,
) -> np.ndarray:
    rho = density(state)
    norm = float(np.sum(rho) * spacing**3)
    return np.asarray(
        [float(np.sum(values * rho) * spacing**3 / norm) for values in coordinates],
        dtype=np.float64,
    )


def kinetic_momentum(
    state: np.ndarray,
    vector_potential: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    charge_sign: float,
    charge: float,
    spacing: float,
) -> np.ndarray:
    norm = float(np.sum(density(state)) * spacing**3)
    values = []
    for axis in range(3):
        mechanical = -1.0j * derivative(state, axis + 1, spacing)
        mechanical -= charge_sign * charge * vector_potential[axis][None, ...] * state
        values.append(
            float(np.real(np.sum(np.conj(state) * mechanical)) * spacing**3 / norm)
        )
    return np.asarray(values, dtype=np.float64)


def velocity(state: np.ndarray, spacing: float) -> np.ndarray:
    norm = float(np.sum(density(state)) * spacing**3)
    return np.asarray(
        [float(np.sum(expectation(state, matrix)) * spacing**3 / norm) for matrix in ALPHAS],
        dtype=np.float64,
    )


def spin_derivative(
    state: np.ndarray,
    state_derivative: np.ndarray,
    spacing: float,
) -> np.ndarray:
    norm = float(np.sum(density(state)) * spacing**3)
    norm_derivative = 2.0 * float(
        np.real(np.sum(np.conj(state) * state_derivative)) * spacing**3
    )
    spin = spin_vector(state, spacing)
    result = []
    for index, matrix in enumerate(SPIN_MATRICES):
        operated = apply_matrix(matrix, state)
        raw = float(
            np.real(np.sum(np.conj(state_derivative) * operated)) * spacing**3 / norm
        )
        result.append(raw - spin[index] * norm_derivative / norm)
    return np.asarray(result, dtype=np.float64)


def _record(
    time: float,
    state: tuple[
        np.ndarray,
        np.ndarray,
        tuple[np.ndarray, np.ndarray, np.ndarray],
        tuple[np.ndarray, np.ndarray, np.ndarray],
        np.ndarray,
    ],
    coordinates: tuple[np.ndarray, np.ndarray, np.ndarray],
    cfg: SpinorialPairDynamicsConfig,
) -> dict[str, Any]:
    plus, minus, vector_potential, _electric, _absorber = state
    return {
        "time": time,
        "plus_norm": float(np.sum(density(plus)) * cfg.spacing**3),
        "minus_norm": float(np.sum(density(minus)) * cfg.spacing**3),
        "plus_center": state_center(plus, coordinates, cfg.spacing).tolist(),
        "plus_spin": spin_vector(plus, cfg.spacing).tolist(),
        "plus_momentum": kinetic_momentum(
            plus,
            vector_potential,
            charge_sign=1.0,
            charge=cfg.charge,
            spacing=cfg.spacing,
        ).tolist(),
        "plus_velocity": velocity(plus, cfg.spacing).tolist(),
    }


def evolve_response(
    plus: np.ndarray,
    minus: np.ndarray,
    vector_potential: tuple[np.ndarray, np.ndarray, np.ndarray],
    electric_field: tuple[np.ndarray, np.ndarray, np.ndarray],
    coordinates: tuple[np.ndarray, np.ndarray, np.ndarray],
    cfg: SpinorialPairDynamicsConfig,
) -> dict[str, Any]:
    parameters = cfg.parameters()
    spacings = (cfg.spacing, cfg.spacing, cfg.spacing)
    cell_volume = cfg.spacing**3
    absorber_charge = np.zeros_like(coordinates[0])
    absorber = np.zeros_like(coordinates[0])
    state = (
        np.asarray(plus, dtype=np.complex128).copy(),
        np.asarray(minus, dtype=np.complex128).copy(),
        tuple(np.asarray(item, dtype=np.float64).copy() for item in vector_potential),
        tuple(np.asarray(item, dtype=np.float64).copy() for item in electric_field),
        absorber_charge,
    )
    records = []
    initial_rhs = _rhs(
        *state,
        absorber,
        parameters,
        spacings,
        cell_volume,
        True,
    )
    initial_spin_derivative = spin_derivative(state[0], initial_rhs[0], cfg.spacing)
    for step in range(cfg.steps + 1):
        if step % cfg.sample_stride == 0:
            records.append(_record(step * cfg.time_step, state, coordinates, cfg))
        if step == cfg.steps:
            break
        k1 = _rhs(*state, absorber, parameters, spacings, cell_volume, True)
        k2 = _rhs(
            *_state_add(state, 0.5 * cfg.time_step, k1),
            absorber,
            parameters,
            spacings,
            cell_volume,
            True,
        )
        k3 = _rhs(
            *_state_add(state, 0.5 * cfg.time_step, k2),
            absorber,
            parameters,
            spacings,
            cell_volume,
            True,
        )
        k4 = _rhs(
            *_state_add(state, cfg.time_step, k3),
            absorber,
            parameters,
            spacings,
            cell_volume,
            True,
        )
        plus_state, minus_state, a_state, e_state, charge_state = state
        state = (
            plus_state
            + cfg.time_step * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]) / 6.0,
            minus_state
            + cfg.time_step * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]) / 6.0,
            tuple(
                a_state[index]
                + cfg.time_step
                * (k1[2][index] + 2.0 * k2[2][index] + 2.0 * k3[2][index] + k4[2][index])
                / 6.0
                for index in range(3)
            ),
            tuple(
                e_state[index]
                + cfg.time_step
                * (k1[3][index] + 2.0 * k2[3][index] + 2.0 * k3[3][index] + k4[3][index])
                / 6.0
                for index in range(3)
            ),
            charge_state
            + cfg.time_step * (k1[4] + 2.0 * k2[4] + 2.0 * k3[4] + k4[4]) / 6.0,
        )
    return {
        "records": records,
        "initial_spin_derivative": initial_spin_derivative.tolist(),
    }


def fit_response(
    pair: Mapping[str, Any],
    control: Mapping[str, Any],
    cfg: SpinorialPairDynamicsConfig,
) -> dict[str, Any]:
    pair_records = pair["records"]
    control_records = control["records"]
    count = cfg.fit_samples
    times = np.asarray([row["time"] for row in pair_records[:count]], dtype=np.float64)

    def component(records: list[dict[str, Any]], key: str, axis: int) -> np.ndarray:
        return np.asarray([row[key][axis] for row in records[:count]], dtype=np.float64)

    momentum_pair = np.polyfit(times, component(pair_records, "plus_momentum", 2), 1)[0]
    momentum_control = np.polyfit(times, component(control_records, "plus_momentum", 2), 1)[0]
    center_pair = 2.0 * np.polyfit(times, component(pair_records, "plus_center", 2), 2)[0]
    center_control = 2.0 * np.polyfit(times, component(control_records, "plus_center", 2), 2)[0]
    spin_pair = np.asarray(
        [np.polyfit(times, component(pair_records, "plus_spin", axis), 1)[0] for axis in range(3)],
        dtype=np.float64,
    )
    spin_control = np.asarray(
        [
            np.polyfit(times, component(control_records, "plus_spin", axis), 1)[0]
            for axis in range(3)
        ],
        dtype=np.float64,
    )
    generator_pair = np.asarray(pair["initial_spin_derivative"], dtype=np.float64)
    generator_control = np.asarray(control["initial_spin_derivative"], dtype=np.float64)
    return {
        "momentum_rate_pair": float(momentum_pair),
        "momentum_rate_control": float(momentum_control),
        "interaction_momentum_rate": float(momentum_pair - momentum_control),
        "center_acceleration_pair": float(center_pair),
        "center_acceleration_control": float(center_control),
        "interaction_center_acceleration": float(center_pair - center_control),
        "spin_rate_pair": spin_pair.tolist(),
        "spin_rate_control": spin_control.tolist(),
        "interaction_spin_rate": (spin_pair - spin_control).tolist(),
        "generator_spin_rate_pair": generator_pair.tolist(),
        "generator_spin_rate_control": generator_control.tolist(),
        "interaction_generator_spin_rate": (generator_pair - generator_control).tolist(),
    }


@lru_cache(maxsize=1)
def run_spinorial_pair_dynamics() -> dict[str, Any]:
    cfg = SpinorialPairDynamicsConfig()
    stationary = run_gauge_spinor_stationary_feasibility()
    base, grid = charged_seed(cfg.core_radius, cfg.branch_config())
    x, y, z = grid[:3]
    coordinates = (x, y, z)
    spacings = (cfg.spacing, cfg.spacing, cfg.spacing)
    positive_field = spectral_shift(base, spacings, (0.0, 0.0, -0.5 * cfg.separation))
    negative_field = np.conj(
        spectral_shift(base, spacings, (0.0, 0.0, 0.5 * cfg.separation))
    )
    spin_x = np.asarray([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    positive_pauli = spin_x[:, None, None, None] * positive_field[None, ...]
    negative_pauli = spin_x[:, None, None, None] * negative_field[None, ...]
    positive_charge, positive_current = pauli_source(
        positive_pauli,
        charge=cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    negative_charge, negative_current = pauli_source(
        negative_pauli,
        charge=-cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    positive_maxwell = static_maxwell_fields(positive_charge, positive_current, cfg.spacing)
    negative_maxwell = static_maxwell_fields(negative_charge, negative_current, cfg.spacing)
    total_vector = tuple(
        positive_maxwell["vector_potential"][index]
        + negative_maxwell["vector_potential"][index]
        for index in range(3)
    )
    total_electric = tuple(
        positive_maxwell["electric"][index] + negative_maxwell["electric"][index]
        for index in range(3)
    )
    pair_plus = pauli_to_dirac(
        positive_pauli,
        total_vector,
        charge_sign=1.0,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    pair_minus = pauli_to_dirac(
        negative_pauli,
        total_vector,
        charge_sign=-1.0,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    control_plus = pauli_to_dirac(
        positive_pauli,
        positive_maxwell["vector_potential"],
        charge_sign=1.0,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    zero_minus = np.zeros_like(pair_minus)
    pair = evolve_response(
        pair_plus,
        pair_minus,
        total_vector,
        total_electric,
        coordinates,
        cfg,
    )
    control = evolve_response(
        control_plus,
        zero_minus,
        positive_maxwell["vector_potential"],
        positive_maxwell["electric"],
        coordinates,
        cfg,
    )
    response = fit_response(pair, control, cfg)
    external_force = lorentz_force(
        positive_charge,
        positive_current,
        negative_maxwell["electric"],
        negative_maxwell["magnetic"],
        spacings,
    )
    initial_spin = spin_vector(pair_plus, cfg.spacing)
    plus_density = density(pair_plus)
    plus_norm = float(np.sum(plus_density) * cfg.spacing**3)
    effective_partner_b = np.asarray(
        [
            float(
                np.sum(plus_density * negative_maxwell["magnetic"][index])
                * cfg.spacing**3
                / plus_norm
            )
            for index in range(3)
        ],
        dtype=np.float64,
    )
    rest_frame_bmt_rate = (
        cfg.g_factor * cfg.charge / (2.0 * cfg.mass)
    ) * np.cross(initial_spin, effective_partner_b)
    predicted_momentum_rate = float(external_force[2] / plus_norm)
    momentum_error = abs(
        response["interaction_momentum_rate"] - predicted_momentum_rate
    ) / max(abs(predicted_momentum_rate), 1.0e-30)
    center_error = abs(
        response["interaction_center_acceleration"] - predicted_momentum_rate
    ) / max(abs(predicted_momentum_rate), 1.0e-30)
    measured_spin = np.asarray(response["interaction_spin_rate"], dtype=np.float64)
    generator_spin = np.asarray(
        response["interaction_generator_spin_rate"], dtype=np.float64
    )
    generator_spin_error = float(
        np.linalg.norm(measured_spin - generator_spin)
        / max(np.linalg.norm(generator_spin), 1.0e-30)
    )
    bmt_spin_error = float(
        np.linalg.norm(measured_spin - rest_frame_bmt_rate)
        / max(np.linalg.norm(rest_frame_bmt_rate), 1.0e-30)
    )
    max_norm_drift = max(
        abs(row["plus_norm"] - pair["records"][0]["plus_norm"])
        for row in pair["records"]
    )
    acceptance = {
        "gauge_spinor_stationary_boundary_is_imported": (
            stationary["passed"]
            and not stationary["decision"]["charged_spinor_stationary_branch_constructed"]
        ),
        "full_maxwell_dirac_pair_and_self_control_are_evolved": (
            len(pair["records"]) == len(control["records"])
            and len(pair["records"]) >= cfg.fit_samples
        ),
        "pair_norm_is_stable": max_norm_drift <= 2.0e-4,
        "interaction_momentum_rate_matches_lorentz_force": (
            momentum_error <= cfg.momentum_force_tolerance
        ),
        "center_acceleration_has_the_attractive_sign": (
            response["interaction_center_acceleration"] > 0.0
            and predicted_momentum_rate > 0.0
        ),
        "center_acceleration_mismatch_is_explicit": center_error > 5.0e-1,
        "finite_time_spin_rate_matches_the_dirac_generator": (
            generator_spin_error <= cfg.generator_spin_tolerance
        ),
        "rest_frame_bmt_reduction_does_not_silently_close": bmt_spin_error > 5.0e-1,
        "no_stable_pair_or_physical_calibration_is_inferred": True,
    }
    return {
        "schema": "openwave.m9.spinorial-pair-dynamics.v1",
        "task": "M9.97b-c",
        "config": asdict(cfg),
        "external_lorentz_force": external_force.tolist(),
        "predicted_momentum_rate": predicted_momentum_rate,
        "effective_partner_magnetic_field": effective_partner_b.tolist(),
        "initial_spin": initial_spin.tolist(),
        "rest_frame_bmt_spin_rate": rest_frame_bmt_rate.tolist(),
        "response": response,
        "relative_errors": {
            "momentum_vs_lorentz": momentum_error,
            "center_acceleration_vs_lorentz": center_error,
            "finite_spin_vs_generator": generator_spin_error,
            "finite_spin_vs_rest_frame_bmt": bmt_spin_error,
        },
        "max_plus_norm_drift": max_norm_drift,
        "pair_records": pair["records"],
        "control_records": control["records"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "full_maxwell_dirac_pair_evolved": True,
            "momentum_transfer_matches_field_lorentz_force": (
                momentum_error <= cfg.momentum_force_tolerance
            ),
            "center_acceleration_closed": center_error <= cfg.momentum_force_tolerance,
            "spin_generator_integration_closed": (
                generator_spin_error <= cfg.generator_spin_tolerance
            ),
            "rest_frame_bmt_torque_closed_on_winding_state": (
                bmt_spin_error <= cfg.generator_spin_tolerance
            ),
            "stable_charged_stationary_pair_constructed": False,
            "criterion_rows_promoted": [],
            "physical_force_or_moment_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
