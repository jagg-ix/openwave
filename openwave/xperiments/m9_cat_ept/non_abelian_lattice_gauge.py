"""M9.119a: gauge-covariant finite SU(3) matter and Wilson-link carrier.

The historical M9.107 strong-sector model used color amplitudes coupled to one
real scalar flux field. This module replaces that layer with local SU(3) links,
covariant matter transport, plaquettes, Wilson loops, and a gauge-covariant
matter/link update.

This is a small periodic classical lattice gauge system. It is not lattice QCD,
does not establish an area law, and does not identify its matter carrier with a
physical quark.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

Array = np.ndarray


@dataclass(frozen=True)
class NonAbelianGaugeConfig:
    points: int = 7
    dimensions: int = 2
    colors: int = 3
    time_step: float = 2.0e-2
    matter_diffusion: float = 0.18
    link_response: float = 0.04
    steps: int = 12
    inverse_coupling: float = 1.7

    def __post_init__(self) -> None:
        if self.points < 5 or self.points % 2 == 0:
            raise ValueError("odd periodic lattice with at least five points required")
        if self.dimensions != 2 or self.colors != 3:
            raise ValueError("this carrier is the two-dimensional SU(3) specialization")
        if self.steps < 1:
            raise ValueError("positive evolution length required")
        if min(self.time_step, self.matter_diffusion, self.link_response, self.inverse_coupling) <= 0.0:
            raise ValueError("positive gauge-carrier controls required")


def dagger(values: Array) -> Array:
    return np.swapaxes(np.conjugate(values), -1, -2)


def matrix_vector(matrix: Array, vector: Array) -> Array:
    return np.einsum("...ij,...j->...i", matrix, vector)


def special_unitary_generators(rank: int) -> Array:
    generators: list[Array] = []
    for i in range(rank):
        for j in range(i + 1, rank):
            symmetric = np.zeros((rank, rank), dtype=np.complex128)
            symmetric[i, j] = symmetric[j, i] = 0.5
            antisymmetric = np.zeros((rank, rank), dtype=np.complex128)
            antisymmetric[i, j] = -0.5j
            antisymmetric[j, i] = 0.5j
            generators.extend((symmetric, antisymmetric))
    for k in range(1, rank):
        diagonal = np.zeros((rank, rank), dtype=np.complex128)
        coefficient = 1.0 / math.sqrt(2.0 * k * (k + 1))
        for i in range(k):
            diagonal[i, i] = coefficient
        diagonal[k, k] = -k * coefficient
        generators.append(diagonal)
    return np.asarray(generators, dtype=np.complex128)


def unitary_from_hermitian(generator: Array) -> Array:
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    phases = np.exp(1.0j * eigenvalues)
    return np.asarray((eigenvectors * phases[..., None, :]) @ dagger(eigenvectors), dtype=np.complex128)


def hermitian_traceless(values: Array) -> Array:
    rank = values.shape[-1]
    hermitian = 0.5 * (values + dagger(values))
    trace = np.trace(hermitian, axis1=-2, axis2=-1)[..., None, None] / rank
    return np.asarray(hermitian - trace * np.eye(rank), dtype=np.complex128)


def lattice_axes(cfg: NonAbelianGaugeConfig) -> tuple[Array, Array]:
    axis = np.arange(cfg.points, dtype=np.float64)
    return np.meshgrid(axis, axis, indexing="ij")


def initialize_links(cfg: NonAbelianGaugeConfig) -> Array:
    generators = special_unitary_generators(cfg.colors)
    x, y = lattice_axes(cfg)
    links = np.empty((cfg.dimensions, cfg.points, cfg.points, cfg.colors, cfg.colors), dtype=np.complex128)
    for direction in range(cfg.dimensions):
        field = np.zeros_like(links[direction])
        for index in range(4):
            coefficient = np.sin(
                2.0 * math.pi * ((index + 1) * x + (direction + 1) * y) / cfg.points
                + 0.17 * index + 0.23 * direction
            )
            field += 0.16 / (index + 1) * coefficient[..., None, None] * generators[
                (index + 2 * direction) % len(generators)
            ]
        links[direction] = unitary_from_hermitian(field)
    return links


def initialize_matter(cfg: NonAbelianGaugeConfig) -> Array:
    x, y = lattice_axes(cfg)
    center = 0.5 * (cfg.points - 1)
    amplitude = np.exp(-0.35 * ((x - center) ** 2 + (y - center) ** 2))
    matter = np.empty((cfg.points, cfg.points, cfg.colors), dtype=np.complex128)
    for color in range(cfg.colors):
        matter[..., color] = amplitude * np.exp(
            1.0j * (0.23 * (color + 1) * x - 0.17 * (color + 1) * y)
        )
    return np.asarray(matter / np.linalg.norm(matter), dtype=np.complex128)


def local_gauge_transformation(cfg: NonAbelianGaugeConfig) -> Array:
    generators = special_unitary_generators(cfg.colors)
    x, y = lattice_axes(cfg)
    field = np.zeros((cfg.points, cfg.points, cfg.colors, cfg.colors), dtype=np.complex128)
    coefficients = (
        0.40 * np.sin(2.0 * math.pi * x / cfg.points + 0.30),
        0.31 * np.cos(2.0 * math.pi * y / cfg.points + 0.70),
        0.24 * np.sin(2.0 * math.pi * (x + y) / cfg.points - 0.10),
        0.18 * np.cos(2.0 * math.pi * (2.0 * x - y) / cfg.points + 0.20),
    )
    for index, coefficient in enumerate(coefficients):
        field += coefficient[..., None, None] * generators[index]
    return unitary_from_hermitian(field)


def gauge_transform(matter: Array, links: Array, gauge: Array) -> tuple[Array, Array]:
    transformed_matter = matrix_vector(gauge, matter)
    transformed_links = np.empty_like(links)
    for direction in range(links.shape[0]):
        gauge_forward = np.roll(gauge, -1, axis=direction)
        transformed_links[direction] = gauge @ links[direction] @ dagger(gauge_forward)
    return transformed_matter, transformed_links


def covariant_laplacian(matter: Array, links: Array) -> Array:
    result = np.zeros_like(matter)
    for direction in range(links.shape[0]):
        forward = np.roll(matter, -1, axis=direction)
        backward = np.roll(matter, 1, axis=direction)
        backward_link = np.roll(links[direction], 1, axis=direction)
        result += matrix_vector(links[direction], forward) + matrix_vector(
            dagger(backward_link), backward
        ) - 2.0 * matter
    return np.asarray(result, dtype=np.complex128)


def matter_kinetic_action(matter: Array, links: Array) -> float:
    action = 0.0
    for direction in range(links.shape[0]):
        transported = matrix_vector(links[direction], np.roll(matter, -1, axis=direction))
        action += float(np.sum(np.abs(transported - matter) ** 2))
    return action


def plaquette(links: Array, mu: int = 0, nu: int = 1) -> Array:
    first = links[mu]
    second = links[nu]
    second_forward = np.roll(second, -1, axis=mu)
    first_forward = np.roll(first, -1, axis=nu)
    return first @ second_forward @ dagger(first_forward) @ dagger(second)


def wilson_action(links: Array, inverse_coupling: float) -> tuple[float, float]:
    values = plaquette(links)
    colors = links.shape[-1]
    normalized_trace = np.trace(values, axis1=-2, axis2=-1).real / colors
    action = inverse_coupling * np.sum(1.0 - normalized_trace)
    return float(action), float(np.mean(normalized_trace))


def rectangular_wilson_loop(links: Array, extent_x: int, extent_y: int) -> float:
    if extent_x < 1 or extent_y < 1:
        raise ValueError("positive Wilson-loop extents required")
    points = links.shape[1]
    colors = links.shape[-1]
    result = []
    for x0 in range(points):
        for y0 in range(points):
            product = np.eye(colors, dtype=np.complex128)
            x, y = x0, y0
            for _ in range(extent_x):
                product = product @ links[0, x, y]
                x = (x + 1) % points
            for _ in range(extent_y):
                product = product @ links[1, x, y]
                y = (y + 1) % points
            for _ in range(extent_x):
                x = (x - 1) % points
                product = product @ dagger(links[0, x, y])
            for _ in range(extent_y):
                y = (y - 1) % points
                product = product @ dagger(links[1, x, y])
            result.append(float(np.trace(product).real / colors))
    return float(np.mean(result))


def color_casimir_density(matter: Array) -> float:
    generators = special_unitary_generators(matter.shape[-1])
    components = np.einsum("...i,aij,...j->...a", np.conjugate(matter), generators, matter).real
    return float(np.sum(components * components))


def link_unitarity_error(links: Array) -> float:
    identity = np.eye(links.shape[-1], dtype=np.complex128)
    return float(np.max(np.abs(dagger(links) @ links - identity)))


def link_determinant_error(links: Array) -> float:
    return float(np.max(np.abs(np.linalg.det(links) - 1.0)))


def non_abelian_commutator_norm(links: Array) -> float:
    return float(np.linalg.norm(links[0] @ links[1] - links[1] @ links[0]))


def evolution_step(matter: Array, links: Array, cfg: NonAbelianGaugeConfig) -> tuple[Array, Array]:
    next_matter = matter + cfg.time_step * cfg.matter_diffusion * covariant_laplacian(matter, links)
    next_matter = np.asarray(next_matter / np.linalg.norm(next_matter), dtype=np.complex128)
    next_links = np.empty_like(links)
    for direction in range(cfg.dimensions):
        transported = matrix_vector(links[direction], np.roll(matter, -1, axis=direction))
        outer = np.einsum("...i,...j->...ij", matter, np.conjugate(transported))
        rotation = unitary_from_hermitian(
            cfg.time_step * cfg.link_response * hermitian_traceless(outer)
        )
        next_links[direction] = rotation @ links[direction]
    return next_matter, next_links


def relative_error(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), 1.0e-300)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_non_abelian_lattice_gauge() -> dict[str, Any]:
    cfg = NonAbelianGaugeConfig()
    matter = initialize_matter(cfg)
    links = initialize_links(cfg)
    gauge = local_gauge_transformation(cfg)
    transformed_matter, transformed_links = gauge_transform(matter, links, gauge)

    initial_kinetic = matter_kinetic_action(matter, links)
    transformed_kinetic = matter_kinetic_action(transformed_matter, transformed_links)
    initial_wilson, plaquette_trace = wilson_action(links, cfg.inverse_coupling)
    transformed_wilson, transformed_plaquette_trace = wilson_action(
        transformed_links, cfg.inverse_coupling
    )
    initial_casimir = color_casimir_density(matter)
    transformed_casimir = color_casimir_density(transformed_matter)
    loop_11 = rectangular_wilson_loop(links, 1, 1)
    loop_21 = rectangular_wilson_loop(links, 2, 1)
    loop_11_gauge = rectangular_wilson_loop(transformed_links, 1, 1)
    loop_21_gauge = rectangular_wilson_loop(transformed_links, 2, 1)

    trajectory_matter_error = 0.0
    trajectory_link_error = 0.0
    records = []
    for step in range(cfg.steps + 1):
        expected_matter, expected_links = gauge_transform(matter, links, gauge)
        matter_error = float(
            np.linalg.norm(transformed_matter - expected_matter)
            / max(float(np.linalg.norm(expected_matter)), 1.0e-300)
        )
        link_error = float(
            np.linalg.norm(transformed_links - expected_links)
            / max(float(np.linalg.norm(expected_links)), 1.0e-300)
        )
        trajectory_matter_error = max(trajectory_matter_error, matter_error)
        trajectory_link_error = max(trajectory_link_error, link_error)
        records.append(
            {
                "step": step,
                "matter_norm": float(np.linalg.norm(matter)),
                "kinetic_action": matter_kinetic_action(matter, links),
                "wilson_action": wilson_action(links, cfg.inverse_coupling)[0],
                "matter_covariance_error": matter_error,
                "link_covariance_error": link_error,
            }
        )
        if step < cfg.steps:
            matter, links = evolution_step(matter, links, cfg)
            transformed_matter, transformed_links = evolution_step(
                transformed_matter, transformed_links, cfg
            )

    diagnostics = {
        "kinetic_gauge_relative_error": relative_error(initial_kinetic, transformed_kinetic),
        "wilson_gauge_relative_error": relative_error(initial_wilson, transformed_wilson),
        "plaquette_trace_gauge_relative_error": relative_error(
            plaquette_trace, transformed_plaquette_trace
        ),
        "casimir_gauge_relative_error": relative_error(initial_casimir, transformed_casimir),
        "wilson_loop_1x1_gauge_relative_error": relative_error(loop_11, loop_11_gauge),
        "wilson_loop_2x1_gauge_relative_error": relative_error(loop_21, loop_21_gauge),
        "maximum_matter_trajectory_covariance_error": trajectory_matter_error,
        "maximum_link_trajectory_covariance_error": trajectory_link_error,
        "maximum_link_unitarity_error": link_unitarity_error(links),
        "maximum_link_determinant_error": link_determinant_error(links),
        "non_abelian_commutator_norm": non_abelian_commutator_norm(links),
        "initial_wilson_action": initial_wilson,
        "initial_mean_plaquette_trace": plaquette_trace,
        "wilson_loop_1x1": loop_11,
        "wilson_loop_2x1": loop_21,
    }
    acceptance = {
        "local_SU3_gauge_invariants_close": max(
            diagnostics["kinetic_gauge_relative_error"],
            diagnostics["wilson_gauge_relative_error"],
            diagnostics["plaquette_trace_gauge_relative_error"],
            diagnostics["casimir_gauge_relative_error"],
            diagnostics["wilson_loop_1x1_gauge_relative_error"],
            diagnostics["wilson_loop_2x1_gauge_relative_error"],
        ) <= 2.0e-12,
        "matter_and_link_evolution_is_gauge_covariant": max(
            trajectory_matter_error, trajectory_link_error
        ) <= 2.0e-11,
        "links_remain_special_unitary": max(
            diagnostics["maximum_link_unitarity_error"],
            diagnostics["maximum_link_determinant_error"],
        ) <= 2.0e-11,
        "carrier_is_genuinely_non_abelian": diagnostics["non_abelian_commutator_norm"] > 1.0e-4,
        "finite_wilson_observables_are_reported": all(
            math.isfinite(diagnostics[key])
            for key in (
                "initial_wilson_action",
                "initial_mean_plaquette_trace",
                "wilson_loop_1x1",
                "wilson_loop_2x1",
            )
        ),
        "QCD_and_confinement_are_not_inferred": True,
    }
    payload = {
        "schema": "openwave.m9.non-abelian-lattice-gauge.v1",
        "task": "M9.119a",
        "config": asdict(cfg),
        "records": records,
        "diagnostics": diagnostics,
        "claim_boundary": {
            "finite_SU3_carrier_is_lattice_QCD": False,
            "nonzero_Wilson_action_establishes_confinement": False,
            "finite_Wilson_loops_establish_area_law": False,
            "color_triplet_carrier_is_physical_quark_identity": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "local_SU3_link_carrier_constructed": True,
            "gauge_covariant_color_matter_evolution_constructed": True,
            "Wilson_plaquette_and_loop_observables_constructed": True,
            "QCD_confinement_established": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
