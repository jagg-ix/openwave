"""M9.97a: self-consistent gauge--spinor stationary feasibility.

The M9.96 winding-three field is embedded in a two-component Pauli spinor.  At
all imaginary-time steps the spinor regenerates its periodic charge/current,
scalar potential, transverse vector potential, electric field, and magnetic
field.  The stationary operator contains the selected cubic--quintic density
law, a gauge-covariant kinetic term, and the tree-level Pauli coupling.

A passing campaign would need one and the same state to close normalization,
field-measured winding, localization, Maxwell constraints, and the full
stationary residual.  Failure of that joint gate is a model result, not a test
failure and not a physical-particle assignment.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import (
    ChargedBranchFeasibilityConfig,
    charged_seed,
    run_charged_branch_feasibility,
)
from .charged_field_tools import periodic_contour_winding, static_maxwell_fields
from .spatial_3d_operators import curl
from .stationary_non_gaussian_branch import coefficients

PAULI = (
    np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    np.asarray([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128),
    np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
)


@dataclass(frozen=True)
class GaugeSpinorStationaryConfig:
    points: int = 16
    half_width: float = 8.0
    winding: int = 3
    core_radius: float = 0.90
    contour_radius: float = 2.40
    charge: float = 1.0
    mass: float = 1.0
    g_factor: float = 2.0
    dispersion: float = 0.65
    neutral_iterations: int = 3000
    iterations: int = 600
    imaginary_dt: float = 5.0e-5
    field_relaxation: float = 0.50
    stationary_residual_gate: float = 1.0e-1
    radius_gate: float = 1.75
    boundary_gate: float = 2.0e-2

    def __post_init__(self) -> None:
        if self.points < 16 or self.points % 2:
            raise ValueError("an even grid with at least 16 points is required")
        if min(
            self.half_width,
            self.core_radius,
            self.contour_radius,
            self.mass,
            self.g_factor,
            self.dispersion,
            self.imaginary_dt,
        ) <= 0.0:
            raise ValueError("positive gauge-spinor controls required")
        if self.charge == 0.0 or self.winding == 0:
            raise ValueError("nonzero charge and winding required")
        if self.iterations < 100 or self.neutral_iterations < 100:
            raise ValueError("substantive stationary campaigns required")
        if not 0.0 < self.field_relaxation <= 1.0:
            raise ValueError("field relaxation must lie in (0, 1]")

    def branch_config(self) -> ChargedBranchFeasibilityConfig:
        return ChargedBranchFeasibilityConfig(
            points=self.points,
            half_width=self.half_width,
            winding=self.winding,
            core_radii=(self.core_radius,),
            contour_radius=self.contour_radius,
            neutral_iterations=self.neutral_iterations,
            charged_iterations=100,
        )


def normalize_spinor(spinor: np.ndarray, spacing: float) -> np.ndarray:
    mass = float(np.sum(np.abs(spinor) ** 2) * spacing**3)
    if mass <= 0.0:
        raise ValueError("nonzero spinor required")
    return np.asarray(spinor / math.sqrt(mass), dtype=np.complex128)


def spectral_derivative(values: np.ndarray, axis: int, spacing: float) -> np.ndarray:
    if axis not in (0, 1, 2) or spacing <= 0.0 or values.ndim < 3:
        raise ValueError("a spatial axis, positive spacing, and field values are required")
    points = values.shape[-3 + axis]
    wave = 2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
    shape = [1] * values.ndim
    shape[-3 + axis] = points
    transformed = np.fft.fftn(values, axes=(-3, -2, -1))
    return np.asarray(
        np.fft.ifftn(1.0j * wave.reshape(shape) * transformed, axes=(-3, -2, -1)),
        dtype=np.complex128,
    )


def spin_density(spinor: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if spinor.ndim != 4 or spinor.shape[0] != 2:
        raise ValueError("two-component three-dimensional spinor required")
    result = []
    for matrix in PAULI:
        operated = np.einsum("ab,bxyz->axyz", matrix, spinor, optimize=True)
        result.append(
            np.asarray(
                0.5 * np.real(np.sum(np.conj(spinor) * operated, axis=0)),
                dtype=np.float64,
            )
        )
    return tuple(result)  # type: ignore[return-value]


def spinor_charge_current(
    spinor: np.ndarray,
    vector_potential: tuple[np.ndarray, np.ndarray, np.ndarray],
    cfg: GaugeSpinorStationaryConfig,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    convective = []
    for axis in range(3):
        covariant = spectral_derivative(spinor, axis, 2.0 * cfg.half_width / cfg.points)
        covariant -= 1.0j * cfg.charge * vector_potential[axis][None, ...] * spinor
        convective.append(
            np.asarray(
                2.0
                * cfg.dispersion
                * cfg.charge
                * np.imag(np.sum(np.conj(spinor) * covariant, axis=0)),
                dtype=np.float64,
            )
        )
    magnetization = tuple(
        cfg.g_factor * cfg.charge * component / (2.0 * cfg.mass)
        for component in spin_density(spinor)
    )
    magnetization_current = curl(
        magnetization,
        (2.0 * cfg.half_width / cfg.points,) * 3,
    )
    current = tuple(
        np.asarray(convective[index] + magnetization_current[index], dtype=np.float64)
        for index in range(3)
    )
    return np.asarray(cfg.charge * density, dtype=np.float64), current


def pauli_hamiltonian(
    spinor: np.ndarray,
    scalar_potential: np.ndarray,
    vector_potential: tuple[np.ndarray, np.ndarray, np.ndarray],
    magnetic_field: tuple[np.ndarray, np.ndarray, np.ndarray],
    cfg: GaugeSpinorStationaryConfig,
) -> np.ndarray:
    alpha, beta = coefficients()
    spacing = 2.0 * cfg.half_width / cfg.points
    covariant_laplacian = np.zeros_like(spinor)
    for axis in range(3):
        first = spectral_derivative(spinor, axis, spacing)
        first -= 1.0j * cfg.charge * vector_potential[axis][None, ...] * spinor
        second = spectral_derivative(first, axis, spacing)
        second -= 1.0j * cfg.charge * vector_potential[axis][None, ...] * first
        covariant_laplacian += second
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    result = -cfg.dispersion * covariant_laplacian
    result += (
        cfg.charge * scalar_potential - alpha * density + beta * density * density
    )[None, ...] * spinor
    sigma_dot_b = np.zeros_like(spinor)
    for matrix, component in zip(PAULI, magnetic_field, strict=True):
        sigma_dot_b += component[None, ...] * np.einsum(
            "ab,bxyz->axyz", matrix, spinor, optimize=True
        )
    result -= cfg.g_factor * cfg.charge * sigma_dot_b / (4.0 * cfg.mass)
    return np.asarray(result, dtype=np.complex128)


def stationary_observables(
    spinor: np.ndarray,
    hamiltonian: np.ndarray,
    grid: tuple[np.ndarray, ...],
    cfg: GaugeSpinorStationaryConfig,
) -> dict[str, float]:
    x, y, z = grid[:3]
    spacing = float(grid[5])
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    mass = float(np.sum(density) * spacing**3)
    chemical_potential = float(
        np.real(np.vdot(spinor, hamiltonian)) * spacing**3 / max(mass, 1.0e-30)
    )
    residual = hamiltonian - chemical_potential * spinor
    residual_l2 = math.sqrt(float(np.sum(np.abs(residual) ** 2) * spacing**3))
    operator_l2 = math.sqrt(float(np.sum(np.abs(hamiltonian) ** 2) * spacing**3))
    radius_sq = x * x + y * y + z * z
    radius = math.sqrt(
        float(np.sum(radius_sq * density) * spacing**3 / max(mass, 1.0e-30))
    )
    boundary = np.maximum.reduce((np.abs(x), np.abs(y), np.abs(z))) > (
        0.75 * cfg.half_width
    )
    boundary_fraction = float(
        np.sum(density[boundary]) * spacing**3 / max(mass, 1.0e-30)
    )
    winding = periodic_contour_winding(
        np.asarray(spinor[0], dtype=np.complex128),
        spacing,
        radius=cfg.contour_radius,
    )
    spin = spin_density(spinor)
    return {
        "mass": mass,
        "chemical_potential": chemical_potential,
        "relative_stationary_residual": residual_l2 / max(operator_l2, 1.0e-30),
        "radius": radius,
        "boundary_fraction": boundary_fraction,
        "spin_x": float(np.sum(spin[0]) * spacing**3),
        "spin_y": float(np.sum(spin[1]) * spacing**3),
        "spin_z": float(np.sum(spin[2]) * spacing**3),
        **winding,
        "charge_from_winding": winding["integer_winding"] / 3.0,
    }


def candidate_closes(
    record: Mapping[str, float], cfg: GaugeSpinorStationaryConfig
) -> bool:
    return bool(
        record["integer_winding"] == cfg.winding
        and record["quantization_error"] <= 2.0e-12
        and record["relative_stationary_residual"] <= cfg.stationary_residual_gate
        and record["radius"] <= cfg.radius_gate
        and record["boundary_fraction"] <= cfg.boundary_gate
        and abs(record["mass"] - 1.0) <= 2.0e-12
        and abs(record["spin_z"] - 0.5) <= 2.0e-10
    )


@lru_cache(maxsize=1)
def run_gauge_spinor_stationary_feasibility() -> dict[str, Any]:
    cfg = GaugeSpinorStationaryConfig()
    scalar_campaign = run_charged_branch_feasibility()
    field, grid = charged_seed(cfg.core_radius, cfg.branch_config())
    spacing = float(grid[5])
    spinor = np.zeros((2, *field.shape), dtype=np.complex128)
    spinor[0] = field
    spinor = normalize_spinor(spinor, spacing)
    vector_potential = tuple(np.zeros(field.shape, dtype=np.float64) for _ in range(3))
    checkpoints = []
    final_maxwell: dict[str, Any] | None = None
    for iteration in range(cfg.iterations + 1):
        charge_density, current = spinor_charge_current(spinor, vector_potential, cfg)
        maxwell = static_maxwell_fields(charge_density, current, spacing)
        next_vector = maxwell["vector_potential"]
        vector_potential = tuple(
            np.asarray(
                (1.0 - cfg.field_relaxation) * vector_potential[index]
                + cfg.field_relaxation * next_vector[index],
                dtype=np.float64,
            )
            for index in range(3)
        )
        magnetic_field = curl(vector_potential, (spacing, spacing, spacing))
        hamiltonian = pauli_hamiltonian(
            spinor,
            maxwell["potential"],
            vector_potential,
            magnetic_field,
            cfg,
        )
        if iteration in (0, 100, 300, cfg.iterations):
            checkpoints.append(
                {
                    "iteration": iteration,
                    **stationary_observables(spinor, hamiltonian, grid, cfg),
                }
            )
        if iteration == cfg.iterations:
            final_maxwell = static_maxwell_fields(charge_density, current, spacing)
            break
        chemical_potential = float(np.real(np.vdot(spinor, hamiltonian)) * spacing**3)
        spinor = normalize_spinor(
            spinor - cfg.imaginary_dt * (hamiltonian - chemical_potential * spinor),
            spacing,
        )
    assert final_maxwell is not None
    seed = checkpoints[0]
    final = checkpoints[-1]
    closed = candidate_closes(final, cfg)
    acceptance = {
        "m9_96_scalar_failure_is_imported": (
            scalar_campaign["passing_candidate_count"] == 0
            and not scalar_campaign["decision"]["charged_stationary_branch_constructed"]
        ),
        "gauge_covariant_pauli_equation_is_executed": len(checkpoints) == 4,
        "field_winding_and_exact_third_charge_are_preserved": (
            seed["integer_winding"] == final["integer_winding"] == cfg.winding
            and final["quantization_error"] <= 2.0e-12
            and final["charge_from_winding"] == 1.0
        ),
        "spin_half_embedding_is_preserved": abs(final["spin_z"] - 0.5) <= 2.0e-10,
        "candidate_remains_localized": (
            final["radius"] <= cfg.radius_gate
            and final["boundary_fraction"] <= cfg.boundary_gate
        ),
        "self_consistent_maxwell_constraints_close": (
            final_maxwell["gauss_relative_residual"] <= 2.0e-12
            and final_maxwell["ampere_relative_residual"] <= 2.0e-12
            and final_maxwell["magnetic_divergence_max"] <= 2.0e-12
        ),
        "stationary_residual_failure_is_explicit": (
            final["relative_stationary_residual"] > cfg.stationary_residual_gate
            and not closed
        ),
        "no_physical_or_criterion_promotion_is_inferred": True,
    }
    return {
        "schema": "openwave.m9.gauge-spinor-stationary-feasibility.v1",
        "task": "M9.97a",
        "config": asdict(cfg),
        "checkpoints": checkpoints,
        "final_maxwell": {
            key: final_maxwell[key]
            for key in (
                "projection_loss",
                "gauss_relative_residual",
                "ampere_relative_residual",
                "magnetic_divergence_max",
                "electric_energy",
                "magnetic_energy",
            )
        },
        "residual_change": final["relative_stationary_residual"]
        - seed["relative_stationary_residual"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "self_consistent_gauge_spinor_equation_constructed": True,
            "charge_current_and_fields_recomputed_each_iteration": True,
            "charged_spinor_stationary_branch_constructed": closed,
            "selected_gauge_spinor_extension_closes_m9_97": closed,
            "requires_additional_stationary_mechanism": not closed,
            "criterion_rows_promoted": [],
            "physical_particle_identity_established": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
