"""M10.6 periodic Hamiltonian SU(3) lattice gauge dynamics.

A two-dimensional periodic lattice carries matrix-valued SU(3) links and
traceless-Hermitian color-electric fields.  The magnetic Wilson action and
electric energy are evolved with a symmetric kick--drift--kick integrator.
The campaign checks local gauge covariance, source-free Gauss law, Hamiltonian
stability, reversibility, and finite Wilson loops.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .su3_link_backreaction_m105 import (
    gell_mann_matrices,
    link_from_coefficients,
    su3_exponential,
)

MILESTONE = "M10.6"
SCHEMA = "openwave.m10.periodic-su3-hamiltonian.v1"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/YangMillsGaugeDynamics.lean",
        "sha": "4fe7ae3471057b5c7b64fc22705d76f854d66766",
        "theorem": "yangMillsEquation_gauge_covariant",
    },
    {
        "path": "Physlib/QFT/Lattice/WilsonLoopAreaLaw.lean",
        "sha": "ffd0b7e6dc1ec8b39851755aeda3ae753a5c42d0",
        "theorem": "wilsonAction_nonneg",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/Particles/"
            "GellMannStructureConstants.lean"
        ),
        "sha": "b721ea5e04a72430a81d84c6a0a6c20b3f9558a0",
        "theorem": "gellMann_structure_constants",
    },
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "sha": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "theorem": "boltzmannFactor_le_one",
    },
)

Matrix3 = np.ndarray
LinkField = np.ndarray
ElectricField = np.ndarray
GaugeField = np.ndarray


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def periodic_shift(x: int, y: int, direction: int, displacement: int, size: int) -> tuple[int, int]:
    if direction == 0:
        return ((x + displacement) % size, y)
    if direction == 1:
        return (x, (y + displacement) % size)
    raise ValueError("two-dimensional lattice direction required")


def deterministic_lattice_links(size: int, scale: float) -> LinkField:
    links = np.empty((size, size, 2, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                coefficients = np.asarray(
                    [
                        math.sin(
                            (index + 1) * (x + 1)
                            + 0.37 * (y + 1)
                            + 0.21 * (direction + 1)
                        )
                        for index in range(8)
                    ],
                    dtype=np.float64,
                )
                links[x, y, direction] = link_from_coefficients(coefficients, scale)
    return links


def zero_electric_field(size: int) -> ElectricField:
    return np.zeros((size, size, 2, 3, 3), dtype=np.complex128)


def plaquette_matrix(links: LinkField, x: int, y: int) -> Matrix3:
    size = links.shape[0]
    x_plus, y_same = periodic_shift(x, y, 0, 1, size)
    x_same, y_plus = periodic_shift(x, y, 1, 1, size)
    return np.asarray(
        links[x, y, 0]
        @ links[x_plus, y_same, 1]
        @ links[x_same, y_plus, 0].conj().T
        @ links[x, y, 1].conj().T,
        dtype=np.complex128,
    )


def normalized_plaquette(links: LinkField, x: int, y: int) -> float:
    return float(np.trace(plaquette_matrix(links, x, y)).real / 3.0)


def magnetic_action(links: LinkField, inverse_coupling: float) -> float:
    size = links.shape[0]
    return float(
        inverse_coupling
        * sum(
            1.0 - normalized_plaquette(links, x, y)
            for x in range(size)
            for y in range(size)
        )
    )


def electric_energy(electric: ElectricField) -> float:
    return float(
        0.5
        * sum(
            np.trace(electric[index] @ electric[index]).real
            for index in np.ndindex(electric.shape[:3])
        )
    )


def hamiltonian(links: LinkField, electric: ElectricField, inverse_coupling: float) -> float:
    return electric_energy(electric) + magnetic_action(links, inverse_coupling)


def deterministic_gauges(size: int, scale: float) -> GaugeField:
    gauges = np.empty((size, size, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            coefficients = np.asarray(
                [
                    math.cos(0.29 * (index + 1) * (x + 1) + 0.17 * (y + 1))
                    for index in range(8)
                ],
                dtype=np.float64,
            )
            gauges[x, y] = link_from_coefficients(coefficients, scale)
    return gauges


def gauge_transform_links(links: LinkField, gauges: GaugeField) -> LinkField:
    size = links.shape[0]
    transformed = np.empty_like(links)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                target_x, target_y = periodic_shift(x, y, direction, 1, size)
                transformed[x, y, direction] = (
                    gauges[x, y]
                    @ links[x, y, direction]
                    @ gauges[target_x, target_y].conj().T
                )
    return transformed


def gauge_transform_electric(electric: ElectricField, gauges: GaugeField) -> ElectricField:
    transformed = np.empty_like(electric)
    size = electric.shape[0]
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                transformed[x, y, direction] = (
                    gauges[x, y]
                    @ electric[x, y, direction]
                    @ gauges[x, y].conj().T
                )
    return transformed


def magnetic_force(
    links: LinkField,
    inverse_coupling: float,
    variation_step: float,
) -> ElectricField:
    """Return the Hamiltonian electric-field kick by central link variations."""
    generators = tuple(matrix / 2.0 for matrix in gell_mann_matrices())
    force = np.zeros_like(links)
    for x, y, direction in np.ndindex(links.shape[:3]):
        original = links[x, y, direction]
        for generator in generators:
            plus = links.copy()
            minus = links.copy()
            plus[x, y, direction] = su3_exponential(variation_step * generator) @ original
            minus[x, y, direction] = su3_exponential(-variation_step * generator) @ original
            derivative = (
                magnetic_action(plus, inverse_coupling)
                - magnetic_action(minus, inverse_coupling)
            ) / (2.0 * variation_step)
            force[x, y, direction] -= derivative * generator
    return np.asarray(force, dtype=np.complex128)


def gauss_matrices(links: LinkField, electric: ElectricField) -> np.ndarray:
    size = links.shape[0]
    residuals = np.zeros((size, size, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            residual = np.zeros((3, 3), dtype=np.complex128)
            for direction in range(2):
                residual += electric[x, y, direction]
                previous_x, previous_y = periodic_shift(x, y, direction, -1, size)
                incoming_link = links[previous_x, previous_y, direction]
                incoming_electric = electric[previous_x, previous_y, direction]
                residual -= (
                    incoming_link.conj().T @ incoming_electric @ incoming_link
                )
            residuals[x, y] = residual
    return residuals


def gauss_residual(links: LinkField, electric: ElectricField) -> float:
    residuals = gauss_matrices(links, electric)
    return float(max(np.linalg.norm(residuals[x, y]) for x in range(links.shape[0]) for y in range(links.shape[0])))


def leapfrog_step(
    links: LinkField,
    electric: ElectricField,
    timestep: float,
    inverse_coupling: float,
    variation_step: float,
) -> tuple[LinkField, ElectricField]:
    first_force = magnetic_force(links, inverse_coupling, variation_step)
    half_electric = electric + 0.5 * timestep * first_force

    advanced_links = links.copy()
    for index in np.ndindex(links.shape[:3]):
        advanced_links[index] = su3_exponential(0.5 * timestep * half_electric[index]) @ links[index]

    second_force = magnetic_force(advanced_links, inverse_coupling, variation_step)
    advanced_electric = half_electric + 0.5 * timestep * second_force
    return np.asarray(advanced_links), np.asarray(advanced_electric)


def evolve(
    links: LinkField,
    electric: ElectricField,
    steps: int,
    timestep: float,
    inverse_coupling: float,
    variation_step: float,
) -> tuple[LinkField, ElectricField]:
    current_links = links.copy()
    current_electric = electric.copy()
    for _ in range(steps):
        current_links, current_electric = leapfrog_step(
            current_links,
            current_electric,
            timestep,
            inverse_coupling,
            variation_step,
        )
    return current_links, current_electric


def rectangular_wilson_loop(
    links: LinkField,
    origin_x: int,
    origin_y: int,
    width: int,
    height: int,
) -> complex:
    if width < 1 or height < 1:
        raise ValueError("positive Wilson-loop dimensions required")
    size = links.shape[0]
    x, y = origin_x % size, origin_y % size
    product = np.eye(3, dtype=np.complex128)
    for _ in range(width):
        product = product @ links[x, y, 0]
        x, y = periodic_shift(x, y, 0, 1, size)
    for _ in range(height):
        product = product @ links[x, y, 1]
        x, y = periodic_shift(x, y, 1, 1, size)
    for _ in range(width):
        x, y = periodic_shift(x, y, 0, -1, size)
        product = product @ links[x, y, 0].conj().T
    for _ in range(height):
        x, y = periodic_shift(x, y, 1, -1, size)
        product = product @ links[x, y, 1].conj().T
    return complex(np.trace(product) / 3.0)


@dataclass(frozen=True)
class PeriodicSU3HamiltonianConfig:
    size: int = 2
    link_scale: float = 0.18
    gauge_scale: float = 0.43
    inverse_coupling: float = 1.0
    timestep: float = 0.01
    steps: int = 8
    variation_step: float = 2.0e-6

    def __post_init__(self) -> None:
        if self.size < 2 or self.steps < 1:
            raise ValueError("periodic lattice and positive trajectory length required")
        if min(
            self.link_scale,
            self.gauge_scale,
            self.inverse_coupling,
            self.timestep,
            self.variation_step,
        ) <= 0.0:
            raise ValueError("positive Hamiltonian lattice controls required")


@dataclass(frozen=True)
class PeriodicSU3HamiltonianState:
    links: LinkField
    electric: ElectricField
    time: float
    hamiltonian: float
    gauss_residual: float

    def manifest(self) -> dict[str, Any]:
        return {
            "schema": "openwave.m10.periodic-su3-hamiltonian-state.v1",
            "time": self.time,
            "hamiltonian": self.hamiltonian,
            "gauss_residual": self.gauss_residual,
        }


def canonical_payload(cfg: PeriodicSU3HamiltonianConfig | None = None) -> dict[str, Any]:
    selected = cfg or PeriodicSU3HamiltonianConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT periodic Hamiltonian SU3 lattice gauge model",
        "config": asdict(selected),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(FORMAL_SOURCES),
        },
        "state_api": (
            "openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106:"
            "PeriodicSU3HamiltonianState"
        ),
        "study_api": (
            "openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106:"
            "run_periodic_su3_hamiltonian_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_periodic_su3_hamiltonian_study() -> dict[str, Any]:
    cfg = PeriodicSU3HamiltonianConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    electric = zero_electric_field(cfg.size)
    gauges = deterministic_gauges(cfg.size, cfg.gauge_scale)

    initial_hamiltonian = hamiltonian(links, electric, cfg.inverse_coupling)
    initial_gauss = gauss_residual(links, electric)
    transformed_links = gauge_transform_links(links, gauges)
    transformed_electric = gauge_transform_electric(electric, gauges)

    plaquette_covariance_error = 0.0
    for x in range(cfg.size):
        for y in range(cfg.size):
            expected = gauges[x, y] @ plaquette_matrix(links, x, y) @ gauges[x, y].conj().T
            plaquette_covariance_error = max(
                plaquette_covariance_error,
                float(np.max(np.abs(plaquette_matrix(transformed_links, x, y) - expected))),
            )
    gauge_action_error = abs(
        magnetic_action(transformed_links, cfg.inverse_coupling)
        - magnetic_action(links, cfg.inverse_coupling)
    )

    final_links, final_electric = evolve(
        links,
        electric,
        cfg.steps,
        cfg.timestep,
        cfg.inverse_coupling,
        cfg.variation_step,
    )
    final_hamiltonian = hamiltonian(final_links, final_electric, cfg.inverse_coupling)
    final_gauss = gauss_residual(final_links, final_electric)

    reversed_links, reversed_electric = evolve(
        final_links,
        final_electric,
        cfg.steps,
        -cfg.timestep,
        cfg.inverse_coupling,
        cfg.variation_step,
    )
    reversibility_link_error = float(
        max(
            np.linalg.norm(reversed_links[index] - links[index])
            for index in np.ndindex(links.shape[:3])
        )
    )
    reversibility_electric_error = float(
        max(
            np.linalg.norm(reversed_electric[index] - electric[index])
            for index in np.ndindex(electric.shape[:3])
        )
    )

    maximum_unitarity_error = float(
        max(
            np.max(np.abs(final_links[index].conj().T @ final_links[index] - np.eye(3)))
            for index in np.ndindex(final_links.shape[:3])
        )
    )
    maximum_determinant_error = float(
        max(
            abs(np.linalg.det(final_links[index]) - 1.0)
            for index in np.ndindex(final_links.shape[:3])
        )
    )
    maximum_electric_hermitian_error = float(
        max(
            np.max(np.abs(final_electric[index] - final_electric[index].conj().T))
            for index in np.ndindex(final_electric.shape[:3])
        )
    )
    maximum_electric_trace_error = float(
        max(abs(np.trace(final_electric[index])) for index in np.ndindex(final_electric.shape[:3]))
    )

    relative_hamiltonian_drift = abs(final_hamiltonian - initial_hamiltonian) / max(
        abs(initial_hamiltonian), 1.0e-30
    )
    magnetic_response = abs(
        magnetic_action(final_links, cfg.inverse_coupling)
        - magnetic_action(links, cfg.inverse_coupling)
    )
    wilson_1x1 = rectangular_wilson_loop(final_links, 0, 0, 1, 1)
    wilson_2x1 = rectangular_wilson_loop(final_links, 0, 0, 2, 1)

    acceptance = {
        "periodic_lattice_has_eight_links": final_links.shape[:3] == (2, 2, 2),
        "links_remain_unitary": maximum_unitarity_error <= 2.0e-12,
        "links_remain_special": maximum_determinant_error <= 2.0e-12,
        "electric_fields_remain_hermitian": maximum_electric_hermitian_error <= 2.0e-12,
        "electric_fields_remain_traceless": maximum_electric_trace_error <= 2.0e-12,
        "plaquette_is_locally_gauge_covariant": plaquette_covariance_error <= 2.0e-12,
        "wilson_action_is_gauge_invariant": gauge_action_error <= 2.0e-12,
        "source_free_gauss_law_starts_closed": initial_gauss <= 1.0e-14,
        "source_free_gauss_law_remains_closed": final_gauss <= 5.0e-9,
        "leapfrog_hamiltonian_drift_is_small": relative_hamiltonian_drift <= 2.0e-6,
        "leapfrog_is_reversible": (
            reversibility_link_error <= 2.0e-9
            and reversibility_electric_error <= 2.0e-8
        ),
        "magnetic_sector_evolves_nontrivially": magnetic_response >= 1.0e-5,
        "wilson_loops_are_finite": (
            math.isfinite(wilson_1x1.real)
            and math.isfinite(wilson_1x1.imag)
            and math.isfinite(wilson_2x1.real)
            and math.isfinite(wilson_2x1.imag)
        ),
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M10.6h",
        "fingerprint": fingerprint(payload),
        "initial_hamiltonian": initial_hamiltonian,
        "final_hamiltonian": final_hamiltonian,
        "relative_hamiltonian_drift": relative_hamiltonian_drift,
        "initial_gauss_residual": initial_gauss,
        "final_gauss_residual": final_gauss,
        "plaquette_covariance_error": plaquette_covariance_error,
        "gauge_action_error": gauge_action_error,
        "maximum_unitarity_error": maximum_unitarity_error,
        "maximum_determinant_error": maximum_determinant_error,
        "maximum_electric_hermitian_error": maximum_electric_hermitian_error,
        "maximum_electric_trace_error": maximum_electric_trace_error,
        "reversibility_link_error": reversibility_link_error,
        "reversibility_electric_error": reversibility_electric_error,
        "magnetic_response": magnetic_response,
        "wilson_1x1": [wilson_1x1.real, wilson_1x1.imag],
        "wilson_2x1": [wilson_2x1.real, wilson_2x1.imag],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "periodic_hamiltonian_su3_lattice_is_constructed": True,
            "source_free_gauss_law_is_evolved": True,
            "symmetric_leapfrog_and_wilson_diagnostics_are_executed": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
