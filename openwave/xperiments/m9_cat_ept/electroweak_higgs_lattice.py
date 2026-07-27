"""M9.119b: gauge-covariant finite SU(2)xU(1) Higgs carrier.

The historical M9.107 weak-sector model used flavor amplitudes coupled to one
complex mediator and a scalar reservoir. This module replaces that layer with
local SU(2) and U(1) links acting on a Higgs doublet through the Physlib-compatible
U(1)^3 action, a covariant lattice Laplacian, quartic Higgs potential, and
gauge-covariant matter/link evolution.

This is a finite classical bosonic electroweak carrier. It does not contain full
chiral fermion content, calibrated gauge couplings, the Weinberg angle, or a
physical W/Z/Higgs mass prediction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .non_abelian_lattice_gauge import (
    Array,
    dagger,
    hermitian_traceless,
    link_determinant_error,
    link_unitarity_error,
    matrix_vector,
    special_unitary_generators,
    unitary_from_hermitian,
)


@dataclass(frozen=True)
class ElectroweakHiggsConfig:
    points: int = 7
    dimensions: int = 2
    hypercharge_power: int = 3
    time_step: float = 1.5e-2
    matter_diffusion: float = 0.16
    su2_link_response: float = 0.04
    u1_link_response: float = 0.03
    mu_squared: float = 1.2
    quartic_coupling: float = 0.8
    covariance_steps: int = 16
    relaxation_steps: int = 200

    def __post_init__(self) -> None:
        if self.points < 5 or self.points % 2 == 0:
            raise ValueError("odd periodic lattice with at least five points required")
        if self.dimensions != 2 or self.hypercharge_power != 3:
            raise ValueError("this carrier uses two dimensions and the Physlib U(1)^3 Higgs action")
        if min(
            self.time_step,
            self.matter_diffusion,
            self.su2_link_response,
            self.u1_link_response,
            self.mu_squared,
            self.quartic_coupling,
        ) <= 0.0:
            raise ValueError("positive electroweak carrier controls required")
        if min(self.covariance_steps, self.relaxation_steps) < 1:
            raise ValueError("positive evolution lengths required")

    @property
    def vacuum_norm_squared(self) -> float:
        return self.mu_squared / (2.0 * self.quartic_coupling)


def lattice_axes(cfg: ElectroweakHiggsConfig) -> tuple[Array, Array]:
    axis = np.arange(cfg.points, dtype=np.float64)
    return np.meshgrid(axis, axis, indexing="ij")


def initialize_electroweak_state(cfg: ElectroweakHiggsConfig) -> tuple[Array, Array, Array]:
    generators = special_unitary_generators(2)
    x, y = lattice_axes(cfg)
    su2_links = np.empty((cfg.dimensions, cfg.points, cfg.points, 2, 2), dtype=np.complex128)
    u1_links = np.empty((cfg.dimensions, cfg.points, cfg.points), dtype=np.complex128)
    for direction in range(cfg.dimensions):
        field = np.zeros_like(su2_links[direction])
        for index in range(3):
            coefficient = np.sin(
                2.0 * math.pi * ((index + 1) * x + (direction + 1) * y) / cfg.points
                + 0.20 * index + 0.30 * direction
            )
            field += 0.13 / (index + 1) * coefficient[..., None, None] * generators[index]
        su2_links[direction] = unitary_from_hermitian(field)
        angle = 0.11 * np.sin(
            2.0 * math.pi * ((direction + 1) * x + (2 - direction) * y) / cfg.points + 0.20
        )
        u1_links[direction] = np.exp(1.0j * angle)

    target = math.sqrt(cfg.vacuum_norm_squared)
    higgs = np.zeros((cfg.points, cfg.points, 2), dtype=np.complex128)
    higgs[..., 0] = target * (0.85 + 0.08 * np.sin(2.0 * math.pi * x / cfg.points)) * np.exp(0.20j * y)
    higgs[..., 1] = 0.18 * target * np.cos(2.0 * math.pi * y / cfg.points) * np.exp(-0.10j * x)
    return higgs, su2_links, u1_links


def local_electroweak_gauge(cfg: ElectroweakHiggsConfig) -> tuple[Array, Array]:
    generators = special_unitary_generators(2)
    x, y = lattice_axes(cfg)
    field = np.zeros((cfg.points, cfg.points, 2, 2), dtype=np.complex128)
    field += 0.40 * np.sin(2.0 * math.pi * x / cfg.points)[..., None, None] * generators[0]
    field += 0.24 * np.cos(2.0 * math.pi * y / cfg.points)[..., None, None] * generators[1]
    field += 0.16 * np.sin(2.0 * math.pi * (x + y) / cfg.points)[..., None, None] * generators[2]
    su2_gauge = unitary_from_hermitian(field)
    alpha = 0.35 * np.sin(2.0 * math.pi * (2.0 * x - y) / cfg.points + 0.17)
    return su2_gauge, np.exp(1.0j * alpha)


def combined_links(su2_links: Array, u1_links: Array, hypercharge_power: int) -> Array:
    return np.asarray(su2_links * (u1_links**hypercharge_power)[..., None, None], dtype=np.complex128)


def gauge_transform(
    higgs: Array,
    su2_links: Array,
    u1_links: Array,
    su2_gauge: Array,
    u1_gauge: Array,
    hypercharge_power: int,
) -> tuple[Array, Array, Array]:
    combined_gauge = su2_gauge * (u1_gauge**hypercharge_power)[..., None, None]
    transformed_higgs = matrix_vector(combined_gauge, higgs)
    transformed_su2 = np.empty_like(su2_links)
    transformed_u1 = np.empty_like(u1_links)
    for direction in range(su2_links.shape[0]):
        su2_forward = np.roll(su2_gauge, -1, axis=direction)
        u1_forward = np.roll(u1_gauge, -1, axis=direction)
        transformed_su2[direction] = su2_gauge @ su2_links[direction] @ dagger(su2_forward)
        transformed_u1[direction] = u1_gauge * u1_links[direction] * np.conjugate(u1_forward)
    return transformed_higgs, transformed_su2, transformed_u1


def covariant_laplacian(higgs: Array, su2_links: Array, u1_links: Array, hypercharge_power: int) -> Array:
    links = combined_links(su2_links, u1_links, hypercharge_power)
    result = np.zeros_like(higgs)
    for direction in range(links.shape[0]):
        forward = np.roll(higgs, -1, axis=direction)
        backward = np.roll(higgs, 1, axis=direction)
        backward_link = np.roll(links[direction], 1, axis=direction)
        result += matrix_vector(links[direction], forward) + matrix_vector(
            dagger(backward_link), backward
        ) - 2.0 * higgs
    return np.asarray(result, dtype=np.complex128)


def kinetic_action(higgs: Array, su2_links: Array, u1_links: Array, hypercharge_power: int) -> float:
    links = combined_links(su2_links, u1_links, hypercharge_power)
    action = 0.0
    for direction in range(links.shape[0]):
        transported = matrix_vector(links[direction], np.roll(higgs, -1, axis=direction))
        action += float(np.sum(np.abs(transported - higgs) ** 2))
    return action


def potential_density(higgs: Array, cfg: ElectroweakHiggsConfig) -> Array:
    norm_squared = np.sum(np.abs(higgs) ** 2, axis=-1)
    return np.asarray(
        -cfg.mu_squared * norm_squared + cfg.quartic_coupling * norm_squared * norm_squared,
        dtype=np.float64,
    )


def su2_wilson_action(su2_links: Array) -> float:
    first, second = su2_links[0], su2_links[1]
    plaquette = first @ np.roll(second, -1, axis=0) @ dagger(np.roll(first, -1, axis=1)) @ dagger(second)
    normalized_trace = np.trace(plaquette, axis1=-2, axis2=-1).real / 2.0
    return float(np.sum(1.0 - normalized_trace))


def u1_wilson_action(u1_links: Array) -> float:
    first, second = u1_links[0], u1_links[1]
    plaquette = first * np.roll(second, -1, axis=0) * np.conjugate(np.roll(first, -1, axis=1)) * np.conjugate(second)
    return float(np.sum(1.0 - plaquette.real))


def total_action(higgs: Array, su2_links: Array, u1_links: Array, cfg: ElectroweakHiggsConfig) -> dict[str, float]:
    kinetic = kinetic_action(higgs, su2_links, u1_links, cfg.hypercharge_power)
    potential = float(np.sum(potential_density(higgs, cfg)))
    su2 = su2_wilson_action(su2_links)
    u1 = u1_wilson_action(u1_links)
    return {"kinetic": kinetic, "potential": potential, "su2_wilson": su2, "u1_wilson": u1, "total": kinetic + potential + su2 + u1}


def evolution_step(higgs: Array, su2_links: Array, u1_links: Array, cfg: ElectroweakHiggsConfig) -> tuple[Array, Array, Array]:
    links = combined_links(su2_links, u1_links, cfg.hypercharge_power)
    laplacian = covariant_laplacian(higgs, su2_links, u1_links, cfg.hypercharge_power)
    norm_squared = np.sum(np.abs(higgs) ** 2, axis=-1)
    higgs_rhs = cfg.matter_diffusion * laplacian + cfg.mu_squared * higgs - 2.0 * cfg.quartic_coupling * norm_squared[..., None] * higgs
    next_higgs = np.asarray(higgs + cfg.time_step * higgs_rhs, dtype=np.complex128)
    next_su2 = np.empty_like(su2_links)
    next_u1 = np.empty_like(u1_links)
    for direction in range(cfg.dimensions):
        transported = matrix_vector(links[direction], np.roll(higgs, -1, axis=direction))
        outer = np.einsum("...i,...j->...ij", higgs, np.conjugate(transported))
        next_su2[direction] = unitary_from_hermitian(
            cfg.time_step * cfg.su2_link_response * hermitian_traceless(outer)
        ) @ su2_links[direction]
        u1_current = np.imag(np.einsum("...i,...i->...", np.conjugate(higgs), transported))
        next_u1[direction] = np.exp(
            1.0j * cfg.time_step * cfg.u1_link_response * u1_current
        ) * u1_links[direction]
    return next_higgs, next_su2, next_u1


def flat_vacuum_relaxation(cfg: ElectroweakHiggsConfig) -> dict[str, Any]:
    x, y = lattice_axes(cfg)
    target = math.sqrt(cfg.vacuum_norm_squared)
    higgs = np.zeros((cfg.points, cfg.points, 2), dtype=np.complex128)
    higgs[..., 0] = target * (0.45 + 0.12 * np.sin(2.0 * math.pi * x / cfg.points))
    higgs[..., 1] = 0.07 * target * np.cos(2.0 * math.pi * y / cfg.points)
    su2_links = np.empty((cfg.dimensions, cfg.points, cfg.points, 2, 2), dtype=np.complex128)
    su2_links[:] = np.eye(2, dtype=np.complex128)
    u1_links = np.ones((cfg.dimensions, cfg.points, cfg.points), dtype=np.complex128)
    records = []
    for step in range(cfg.relaxation_steps + 1):
        norm_squared = np.sum(np.abs(higgs) ** 2, axis=-1)
        action = cfg.matter_diffusion * kinetic_action(
            higgs, su2_links, u1_links, cfg.hypercharge_power
        ) + float(np.sum(potential_density(higgs, cfg)))
        records.append({"step": step, "mean_norm_squared": float(np.mean(norm_squared)), "action": action})
        if step < cfg.relaxation_steps:
            laplacian = covariant_laplacian(higgs, su2_links, u1_links, cfg.hypercharge_power)
            rhs = cfg.matter_diffusion * laplacian + cfg.mu_squared * higgs - 2.0 * cfg.quartic_coupling * norm_squared[..., None] * higgs
            higgs = np.asarray(higgs + cfg.time_step * rhs, dtype=np.complex128)
    maximum_action_increase = max(
        next_row["action"] - row["action"]
        for row, next_row in zip(records[:-1], records[1:], strict=True)
    )
    final_error = abs(records[-1]["mean_norm_squared"] - cfg.vacuum_norm_squared) / cfg.vacuum_norm_squared
    return {
        "records": records,
        "target_norm_squared": cfg.vacuum_norm_squared,
        "final_relative_vacuum_error": final_error,
        "maximum_action_increase": maximum_action_increase,
    }


def residual_subgroup_error(cfg: ElectroweakHiggsConfig) -> float:
    alpha = 0.37
    u1 = np.exp(1.0j * alpha)
    su2 = np.diag((
        np.exp(-1.0j * cfg.hypercharge_power * alpha),
        np.exp(1.0j * cfg.hypercharge_power * alpha),
    ))
    vacuum = np.asarray((math.sqrt(cfg.vacuum_norm_squared), 0.0), dtype=np.complex128)
    return float(np.linalg.norm(u1**cfg.hypercharge_power * (su2 @ vacuum) - vacuum))


def relative_error(left: float, right: float) -> float:
    return abs(left - right) / max(abs(left), abs(right), 1.0e-300)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_electroweak_higgs_lattice() -> dict[str, Any]:
    cfg = ElectroweakHiggsConfig()
    higgs, su2_links, u1_links = initialize_electroweak_state(cfg)
    su2_gauge, u1_gauge = local_electroweak_gauge(cfg)
    transformed_higgs, transformed_su2, transformed_u1 = gauge_transform(
        higgs, su2_links, u1_links, su2_gauge, u1_gauge, cfg.hypercharge_power
    )
    initial_action = total_action(higgs, su2_links, u1_links, cfg)
    transformed_action = total_action(transformed_higgs, transformed_su2, transformed_u1, cfg)
    maximum_higgs_covariance_error = 0.0
    maximum_su2_covariance_error = 0.0
    maximum_u1_covariance_error = 0.0
    records = []
    for step in range(cfg.covariance_steps + 1):
        expected = gauge_transform(
            higgs, su2_links, u1_links, su2_gauge, u1_gauge, cfg.hypercharge_power
        )
        higgs_error = float(np.linalg.norm(transformed_higgs - expected[0]) / max(float(np.linalg.norm(expected[0])), 1.0e-300))
        su2_error = float(np.linalg.norm(transformed_su2 - expected[1]) / max(float(np.linalg.norm(expected[1])), 1.0e-300))
        u1_error = float(np.linalg.norm(transformed_u1 - expected[2]) / max(float(np.linalg.norm(expected[2])), 1.0e-300))
        maximum_higgs_covariance_error = max(maximum_higgs_covariance_error, higgs_error)
        maximum_su2_covariance_error = max(maximum_su2_covariance_error, su2_error)
        maximum_u1_covariance_error = max(maximum_u1_covariance_error, u1_error)
        records.append(
            {
                "step": step,
                "mean_higgs_norm_squared": float(np.mean(np.sum(np.abs(higgs) ** 2, axis=-1))),
                "total_action": total_action(higgs, su2_links, u1_links, cfg)["total"],
                "higgs_covariance_error": higgs_error,
                "su2_link_covariance_error": su2_error,
                "u1_link_covariance_error": u1_error,
            }
        )
        if step < cfg.covariance_steps:
            higgs, su2_links, u1_links = evolution_step(higgs, su2_links, u1_links, cfg)
            transformed_higgs, transformed_su2, transformed_u1 = evolution_step(
                transformed_higgs, transformed_su2, transformed_u1, cfg
            )
    relaxation = flat_vacuum_relaxation(cfg)
    diagnostics = {
        "kinetic_gauge_relative_error": relative_error(initial_action["kinetic"], transformed_action["kinetic"]),
        "potential_gauge_relative_error": relative_error(initial_action["potential"], transformed_action["potential"]),
        "su2_wilson_gauge_relative_error": relative_error(initial_action["su2_wilson"], transformed_action["su2_wilson"]),
        "u1_wilson_gauge_relative_error": relative_error(initial_action["u1_wilson"], transformed_action["u1_wilson"]),
        "maximum_higgs_trajectory_covariance_error": maximum_higgs_covariance_error,
        "maximum_su2_trajectory_covariance_error": maximum_su2_covariance_error,
        "maximum_u1_trajectory_covariance_error": maximum_u1_covariance_error,
        "maximum_su2_unitarity_error": link_unitarity_error(su2_links),
        "maximum_su2_determinant_error": link_determinant_error(su2_links),
        "maximum_u1_norm_error": float(np.max(np.abs(np.abs(u1_links) - 1.0))),
        "vacuum_target_norm_squared": cfg.vacuum_norm_squared,
        "vacuum_final_relative_error": relaxation["final_relative_vacuum_error"],
        "vacuum_maximum_action_increase": relaxation["maximum_action_increase"],
        "residual_subgroup_error": residual_subgroup_error(cfg),
    }
    acceptance = {
        "local_SU2xU1_gauge_invariants_close": max(
            diagnostics["kinetic_gauge_relative_error"],
            diagnostics["potential_gauge_relative_error"],
            diagnostics["su2_wilson_gauge_relative_error"],
            diagnostics["u1_wilson_gauge_relative_error"],
        ) <= 2.0e-12,
        "Higgs_and_link_evolution_is_gauge_covariant": max(
            maximum_higgs_covariance_error,
            maximum_su2_covariance_error,
            maximum_u1_covariance_error,
        ) <= 2.0e-11,
        "links_remain_in_SU2_and_U1": max(
            diagnostics["maximum_su2_unitarity_error"],
            diagnostics["maximum_su2_determinant_error"],
            diagnostics["maximum_u1_norm_error"],
        ) <= 2.0e-11,
        "quartic_Higgs_flow_reaches_declared_vacuum_orbit": diagnostics["vacuum_final_relative_error"] <= 5.0e-3
        and diagnostics["vacuum_maximum_action_increase"] <= 1.0e-10,
        "canonical_vacuum_has_residual_U1_subgroup": diagnostics["residual_subgroup_error"] <= 1.0e-12,
        "full_electroweak_theory_is_not_inferred": True,
    }
    payload = {
        "schema": "openwave.m9.electroweak-higgs-lattice.v1",
        "task": "M9.119b",
        "config": asdict(cfg),
        "records": records,
        "relaxation": relaxation,
        "diagnostics": diagnostics,
        "claim_boundary": {
            "finite_bosonic_carrier_is_complete_electroweak_theory": False,
            "Higgs_vacuum_relaxation_predicts_physical_Higgs_mass": False,
            "residual_subgroup_test_derives_Weinberg_angle": False,
            "full_chiral_fermion_content_constructed": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "local_SU2xU1_link_carrier_constructed": True,
            "gauge_covariant_Higgs_evolution_constructed": True,
            "quartic_Higgs_vacuum_orbit_constructed": True,
            "complete_electroweak_theory_constructed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
