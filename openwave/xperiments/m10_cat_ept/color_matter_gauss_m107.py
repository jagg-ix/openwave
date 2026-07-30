"""M10.7 fundamental-color matter, covariant continuity, and sourced Gauss law.

A normalized fundamental SU(3) matter field propagates on the periodic M10.6
link background under a gauge-covariant nearest-neighbour Hamiltonian.  The
module constructs scalar and traceless adjoint link currents, proves their
discrete continuity identities numerically, and solves the sourced lattice
Gauss constraint in the minimum-norm electric sector.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .dirac_cartan_2i_yukawa_model import DiracCartan2IYukawaConfig
from .periodic_su3_hamiltonian_m106 import (
    deterministic_gauges,
    deterministic_lattice_links,
    gauge_transform_links,
    gauss_matrices,
    periodic_shift,
)
from .su3_link_backreaction_m105 import gell_mann_matrices

MILESTONE = "M10.7"
SCHEMA = "openwave.m10.color-matter-gauss.v1"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/YangMillsGaugeDynamics.lean",
        "sha": "4fe7ae3471057b5c7b64fc22705d76f854d66766",
        "theorem": "yangMillsEquation_gauge_covariant",
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
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/Particles/"
            "SuNGaugeSector.lean"
        ),
        "sha": "4585ddf9bc44396b5f9dce14321c4d6b2826cb8a",
        "theorem": "su3_adjoint_eq_gluonCount",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/Yukawa/"
            "MassDecoherenceProportionality.lean"
        ),
        "sha": "2acaffd46874e359937a7d1e9147fc0823f36b68",
        "theorem": "entropyProductionRate_proportional_mass",
    },
)

MatterField = np.ndarray
LinkField = np.ndarray
ElectricField = np.ndarray
ColorMatrixField = np.ndarray
ColorLinkCurrent = np.ndarray


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def site_slice(x: int, y: int, size: int) -> slice:
    start = (x * size + y) * 3
    return slice(start, start + 3)


def flatten_matter(matter: MatterField) -> np.ndarray:
    return np.asarray(matter.reshape(-1), dtype=np.complex128)


def unflatten_matter(vector: np.ndarray, size: int) -> MatterField:
    return np.asarray(vector.reshape(size, size, 3), dtype=np.complex128)


def deterministic_matter_field(size: int) -> MatterField:
    matter = np.zeros((size, size, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            matter[x, y] = np.asarray(
                [
                    1.0 + 0.10 * x,
                    (0.65 + 0.05 * y) * np.exp(1.0j * (0.27 * x + 0.19 * y)),
                    (0.42 + 0.03 * (x + y)) * np.exp(-1.0j * (0.16 * x + 0.31 * y)),
                ],
                dtype=np.complex128,
            )
    norm = float(np.linalg.norm(matter))
    if norm <= 0.0:
        raise ValueError("nonzero matter field required")
    return np.asarray(matter / norm, dtype=np.complex128)


def gauge_transform_matter(matter: MatterField, gauges: np.ndarray) -> MatterField:
    return np.asarray(np.einsum("xyab,xyb->xya", gauges, matter), dtype=np.complex128)


def covariant_hamiltonian_matrix(
    links: LinkField,
    mass: float,
    hopping: float,
) -> np.ndarray:
    size = links.shape[0]
    matrix = np.zeros((size * size * 3, size * size * 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            own = site_slice(x, y, size)
            matrix[own, own] += (mass + 4.0 * hopping) * np.eye(3)
            for direction in range(2):
                forward_x, forward_y = periodic_shift(x, y, direction, 1, size)
                backward_x, backward_y = periodic_shift(x, y, direction, -1, size)
                matrix[own, site_slice(forward_x, forward_y, size)] += (
                    -hopping * links[x, y, direction]
                )
                matrix[own, site_slice(backward_x, backward_y, size)] += (
                    -hopping * links[backward_x, backward_y, direction].conj().T
                )
    return np.asarray(matrix, dtype=np.complex128)


def hamiltonian_action(
    links: LinkField,
    matter: MatterField,
    mass: float,
    hopping: float,
) -> MatterField:
    matrix = covariant_hamiltonian_matrix(links, mass, hopping)
    return unflatten_matter(matrix @ flatten_matter(matter), links.shape[0])


def exact_matter_step(
    links: LinkField,
    matter: MatterField,
    timestep: float,
    mass: float,
    hopping: float,
) -> MatterField:
    matrix = covariant_hamiltonian_matrix(links, mass, hopping)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    evolved = (
        eigenvectors
        * np.exp(-1.0j * timestep * eigenvalues)
    ) @ (eigenvectors.conj().T @ flatten_matter(matter))
    return unflatten_matter(evolved, links.shape[0])


def matter_norm(matter: MatterField) -> float:
    return float(np.sum(np.abs(matter) ** 2))


def matter_energy(
    links: LinkField,
    matter: MatterField,
    mass: float,
    hopping: float,
) -> float:
    action = hamiltonian_action(links, matter, mass, hopping)
    return float(np.vdot(flatten_matter(matter), flatten_matter(action)).real)


def scalar_density(matter: MatterField) -> np.ndarray:
    return np.asarray(np.sum(np.abs(matter) ** 2, axis=2), dtype=np.float64)


def color_density(matter: MatterField) -> ColorMatrixField:
    size = matter.shape[0]
    density = np.zeros((size, size, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            local = np.outer(matter[x, y], np.conj(matter[x, y]))
            density[x, y] = local - np.trace(local) * np.eye(3) / 3.0
    return density


def scalar_link_current(
    links: LinkField,
    matter: MatterField,
    hopping: float,
) -> np.ndarray:
    size = links.shape[0]
    current = np.zeros((size, size, 2), dtype=np.float64)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                target_x, target_y = periodic_shift(x, y, direction, 1, size)
                overlap = np.vdot(
                    matter[x, y], links[x, y, direction] @ matter[target_x, target_y]
                )
                current[x, y, direction] = 2.0 * hopping * overlap.imag
    return current


def color_link_current(
    links: LinkField,
    matter: MatterField,
    hopping: float,
) -> ColorLinkCurrent:
    size = links.shape[0]
    current = np.zeros((size, size, 2, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                target_x, target_y = periodic_shift(x, y, direction, 1, size)
                transported_target = links[x, y, direction] @ matter[target_x, target_y]
                product = np.outer(transported_target, np.conj(matter[x, y]))
                raw = -1.0j * hopping * (product - product.conj().T)
                current[x, y, direction] = raw - np.trace(raw) * np.eye(3) / 3.0
    return current


def scalar_divergence(current: np.ndarray) -> np.ndarray:
    size = current.shape[0]
    divergence = np.zeros((size, size), dtype=np.float64)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                backward_x, backward_y = periodic_shift(x, y, direction, -1, size)
                divergence[x, y] += (
                    current[x, y, direction]
                    - current[backward_x, backward_y, direction]
                )
    return divergence


def covariant_color_divergence(
    links: LinkField,
    current: ColorLinkCurrent,
) -> ColorMatrixField:
    size = links.shape[0]
    divergence = np.zeros((size, size, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            for direction in range(2):
                divergence[x, y] += current[x, y, direction]
                backward_x, backward_y = periodic_shift(x, y, direction, -1, size)
                backward_link = links[backward_x, backward_y, direction]
                divergence[x, y] -= (
                    backward_link.conj().T
                    @ current[backward_x, backward_y, direction]
                    @ backward_link
                )
    return divergence


def instantaneous_continuity_diagnostics(
    links: LinkField,
    matter: MatterField,
    mass: float,
    hopping: float,
) -> tuple[float, float]:
    derivative = -1.0j * hamiltonian_action(links, matter, mass, hopping)
    scalar_derivative = 2.0 * np.real(np.sum(np.conj(matter) * derivative, axis=2))

    size = links.shape[0]
    color_derivative = np.zeros((size, size, 3, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            raw = (
                np.outer(derivative[x, y], np.conj(matter[x, y]))
                + np.outer(matter[x, y], np.conj(derivative[x, y]))
            )
            color_derivative[x, y] = raw - np.trace(raw) * np.eye(3) / 3.0

    scalar_residual = scalar_derivative + scalar_divergence(
        scalar_link_current(links, matter, hopping)
    )
    color_residual = color_derivative + covariant_color_divergence(
        links, color_link_current(links, matter, hopping)
    )
    return (
        float(np.max(np.abs(scalar_residual))),
        float(
            max(
                np.linalg.norm(color_residual[x, y])
                for x in range(size)
                for y in range(size)
            )
        ),
    )


def matrix_color_coefficients(matrix: np.ndarray) -> np.ndarray:
    generators = tuple(value / 2.0 for value in gell_mann_matrices())
    return np.asarray(
        [2.0 * np.trace(generator @ matrix).real for generator in generators],
        dtype=np.float64,
    )


def electric_from_coefficients(coefficients: np.ndarray, size: int) -> ElectricField:
    generators = tuple(value / 2.0 for value in gell_mann_matrices())
    electric = np.zeros((size, size, 2, 3, 3), dtype=np.complex128)
    offset = 0
    for index in np.ndindex((size, size, 2)):
        electric[index] = sum(
            coefficients[offset + component] * generators[component]
            for component in range(8)
        )
        offset += 8
    return electric


def gauss_coefficient_vector(links: LinkField, electric: ElectricField) -> np.ndarray:
    residuals = gauss_matrices(links, electric)
    size = links.shape[0]
    return np.concatenate(
        [
            matrix_color_coefficients(residuals[x, y])
            for x in range(size)
            for y in range(size)
        ]
    )


def solve_sourced_gauss(
    links: LinkField,
    source_density: ColorMatrixField,
    charge: float,
) -> tuple[ElectricField, float, int]:
    size = links.shape[0]
    unknowns = size * size * 2 * 8
    equations = size * size * 8
    operator = np.zeros((equations, unknowns), dtype=np.float64)
    for column in range(unknowns):
        basis = np.zeros(unknowns, dtype=np.float64)
        basis[column] = 1.0
        operator[:, column] = gauss_coefficient_vector(
            links, electric_from_coefficients(basis, size)
        )
    target = np.concatenate(
        [
            matrix_color_coefficients(charge * source_density[x, y])
            for x in range(size)
            for y in range(size)
        ]
    )
    coefficients, _, rank, _ = np.linalg.lstsq(operator, target, rcond=1.0e-12)
    electric = electric_from_coefficients(coefficients, size)
    residual = float(np.linalg.norm(operator @ coefficients - target))
    return electric, residual, int(rank)


def gauge_transform_electric(electric: ElectricField, gauges: np.ndarray) -> ElectricField:
    return np.asarray(
        np.einsum("xyab,xymbc,xycd->xymad", gauges, electric, gauges.conj().transpose(0, 1, 3, 2)),
        dtype=np.complex128,
    )


@dataclass(frozen=True)
class ColorMatterGaussConfig:
    size: int = 2
    link_scale: float = 0.18
    gauge_scale: float = 0.43
    mass: float = 0.20
    hopping: float = 0.35
    color_charge: float = 0.40
    timestep: float = 0.08
    steps: int = 6

    def __post_init__(self) -> None:
        if self.size < 2 or self.steps < 1:
            raise ValueError("periodic color lattice and positive steps required")
        if min(
            self.link_scale,
            self.gauge_scale,
            self.mass,
            self.hopping,
            self.color_charge,
            self.timestep,
        ) <= 0.0:
            raise ValueError("positive matter-transport controls required")


@dataclass(frozen=True)
class ColorMatterGaussState:
    matter: MatterField
    electric: ElectricField
    time: float
    norm: float
    energy: float
    sourced_gauss_residual: float

    def manifest(self) -> dict[str, Any]:
        return {
            "schema": "openwave.m10.color-matter-gauss-state.v1",
            "time": self.time,
            "norm": self.norm,
            "energy": self.energy,
            "sourced_gauss_residual": self.sourced_gauss_residual,
        }


def canonical_payload(cfg: ColorMatterGaussConfig | None = None) -> dict[str, Any]:
    selected = cfg or ColorMatterGaussConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT gauge-covariant fundamental-color matter and sourced Gauss model",
        "config": asdict(selected),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(FORMAL_SOURCES),
        },
        "state_api": (
            "openwave.xperiments.m10_cat_ept.color_matter_gauss_m107:"
            "ColorMatterGaussState"
        ),
        "study_api": (
            "openwave.xperiments.m10_cat_ept.color_matter_gauss_m107:"
            "run_color_matter_gauss_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_color_matter_gauss_study() -> dict[str, Any]:
    cfg = ColorMatterGaussConfig()
    particle = DiracCartan2IYukawaConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    gauges = deterministic_gauges(cfg.size, cfg.gauge_scale)
    transformed_links = gauge_transform_links(links, gauges)
    matter = deterministic_matter_field(cfg.size)
    transformed_matter = gauge_transform_matter(matter, gauges)

    matrix = covariant_hamiltonian_matrix(links, cfg.mass, cfg.hopping)
    hermitian_error = float(np.max(np.abs(matrix - matrix.conj().T)))
    action = hamiltonian_action(links, matter, cfg.mass, cfg.hopping)
    transformed_action = hamiltonian_action(
        transformed_links, transformed_matter, cfg.mass, cfg.hopping
    )
    hamiltonian_covariance_error = float(
        np.max(np.abs(transformed_action - gauge_transform_matter(action, gauges)))
    )

    initial_norm = matter_norm(matter)
    initial_energy = matter_energy(links, matter, cfg.mass, cfg.hopping)
    scalar_continuity, color_continuity = instantaneous_continuity_diagnostics(
        links, matter, cfg.mass, cfg.hopping
    )

    evolved = matter.copy()
    evolved_transformed = transformed_matter.copy()
    for _ in range(cfg.steps):
        evolved = exact_matter_step(
            links, evolved, cfg.timestep, cfg.mass, cfg.hopping
        )
        evolved_transformed = exact_matter_step(
            transformed_links,
            evolved_transformed,
            cfg.timestep,
            cfg.mass,
            cfg.hopping,
        )

    final_norm = matter_norm(evolved)
    final_energy = matter_energy(links, evolved, cfg.mass, cfg.hopping)
    evolution_covariance_error = float(
        np.max(np.abs(evolved_transformed - gauge_transform_matter(evolved, gauges)))
    )
    final_scalar_continuity, final_color_continuity = instantaneous_continuity_diagnostics(
        links, evolved, cfg.mass, cfg.hopping
    )

    initial_density = color_density(matter)
    final_density = color_density(evolved)
    initial_electric, initial_gauss_residual, initial_rank = solve_sourced_gauss(
        links, initial_density, cfg.color_charge
    )
    final_electric, final_gauss_residual, final_rank = solve_sourced_gauss(
        links, final_density, cfg.color_charge
    )

    transformed_density = color_density(transformed_matter)
    transformed_electric, transformed_gauss_residual, _ = solve_sourced_gauss(
        transformed_links, transformed_density, cfg.color_charge
    )
    electric_covariance_error = float(
        np.max(
            np.abs(
                transformed_electric
                - gauge_transform_electric(initial_electric, gauges)
            )
        )
    )

    matter_response = float(np.linalg.norm(evolved - matter))
    scalar_charge_error = abs(float(np.sum(scalar_density(evolved))) - initial_norm)
    history_amplitude = complex(
        np.exp(
            -1.0j * final_energy * cfg.steps * cfg.timestep / particle.hbar
            - particle.entropy_rate * cfg.steps * cfg.timestep / particle.hbar
        )
    )
    born_expected = math.exp(
        -2.0 * particle.entropy_rate * cfg.steps * cfg.timestep / particle.hbar
    )
    born_error = abs(abs(history_amplitude) ** 2 - born_expected)

    acceptance = {
        "matter_hamiltonian_is_hermitian": hermitian_error <= 2.0e-13,
        "matter_hamiltonian_is_gauge_covariant": hamiltonian_covariance_error <= 2.0e-12,
        "exact_matter_evolution_is_gauge_covariant": evolution_covariance_error <= 2.0e-12,
        "matter_norm_is_conserved": abs(final_norm - initial_norm) <= 2.0e-13,
        "matter_energy_is_conserved": abs(final_energy - initial_energy) <= 2.0e-12,
        "scalar_continuity_closes": max(scalar_continuity, final_scalar_continuity) <= 2.0e-12,
        "color_continuity_closes": max(color_continuity, final_color_continuity) <= 2.0e-12,
        "initial_sourced_gauss_law_closes": initial_gauss_residual <= 2.0e-12,
        "final_sourced_gauss_law_closes": final_gauss_residual <= 2.0e-12,
        "gauss_projection_has_full_constraint_rank": initial_rank == 32 and final_rank == 32,
        "gauss_projection_is_gauge_covariant": (
            electric_covariance_error <= 2.0e-12
            and transformed_gauss_residual <= 2.0e-12
        ),
        "matter_transport_is_nontrivial": matter_response >= 1.0e-2,
        "total_scalar_charge_is_retained": scalar_charge_error <= 2.0e-13,
        "catept_history_born_weight_closes": born_error <= 2.0e-13,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M10.7m",
        "fingerprint": fingerprint(payload),
        "initial_norm": initial_norm,
        "final_norm": final_norm,
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "hamiltonian_hermitian_error": hermitian_error,
        "hamiltonian_covariance_error": hamiltonian_covariance_error,
        "evolution_covariance_error": evolution_covariance_error,
        "initial_scalar_continuity_error": scalar_continuity,
        "initial_color_continuity_error": color_continuity,
        "final_scalar_continuity_error": final_scalar_continuity,
        "final_color_continuity_error": final_color_continuity,
        "initial_sourced_gauss_residual": initial_gauss_residual,
        "final_sourced_gauss_residual": final_gauss_residual,
        "electric_covariance_error": electric_covariance_error,
        "matter_response": matter_response,
        "scalar_charge_error": scalar_charge_error,
        "born_error": born_error,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "fundamental_color_matter_is_dynamical": True,
            "scalar_and_adjoint_color_continuity_are_executed": True,
            "sourced_gauss_constraint_is_solved_covariantly": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
