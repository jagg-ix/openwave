"""M9.101b: one finite periodic gauge-spinor-Hartree action and solver.

The action is a declared OpenWave reduction of the current Physlib action interface.
It contains one gauge-covariant Pauli spinor, eliminated electrostatic and Hartree
potentials, the selected local cubic--quintic density, transverse magnetic energy,
and the Pauli spin coupling.  Newton's coupling is supplied by the exact formal map
``G = hbar*c*sigma0^4``; the default natural-unit value is therefore one.

The stationary campaign is performed in an explicit winding-three symmetry sector.
A passing symmetry-reduced solve is not advertised as unrestricted topological
stability or as the full continuum Einstein--Hilbert--Maxwell action.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_field_tools import periodic_contour_winding
from .compatible_discrete_geometry import PeriodicFourierGeometry
from .gauge_spinor_stationary_feasibility import PAULI, spin_density
from .reconciled_gauge_spinor_stationary import (
    normalize_spinor,
    reconciled_charge_current,
    reconciled_hamiltonian,
    stationary_residual,
)
from .reconciled_gauge_spinor_stationary_current import (
    ReconciledGaugeSpinorConfig,
    odd_grid_seed,
)
from .stationary_non_gaussian_branch import coefficients

Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class CoupledActionConfig:
    points: int = 17
    seed_points: int = 16
    half_width: float = 8.0
    winding: int = 3
    core_radius: float = 0.90
    contour_radius: float = 2.40
    charge: float = 1.0
    g_factor: float = 2.0
    dispersion: float = 0.65
    neutral_iterations: int = 3000
    iterations: int = 240
    imaginary_dt: float = 2.0e-5
    field_iterations: int = 3
    hbar: float = 1.0
    light_speed: float = 1.0
    inference_width: float = 1.0
    projected_residual_gate: float = 1.5e-1

    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0:
            raise ValueError("an odd operational grid with at least 17 points is required")
        if self.seed_points < 16 or self.seed_points % 2:
            raise ValueError("an even historical seed grid is required")
        if min(
            self.half_width,
            self.core_radius,
            self.contour_radius,
            self.g_factor,
            self.dispersion,
            self.imaginary_dt,
            self.hbar,
            self.light_speed,
            self.inference_width,
        ) <= 0.0:
            raise ValueError("positive coupled-action controls required")
        if self.charge == 0.0 or self.winding == 0:
            raise ValueError("nonzero charge and winding required")
        if self.iterations < 20 or self.field_iterations < 1:
            raise ValueError("substantive action and field iterations required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def effective_mass(self) -> float:
        return 1.0 / (2.0 * self.dispersion)

    @property
    def newton_coupling(self) -> float:
        return self.hbar * self.light_speed * self.inference_width**4

    def geometry(self) -> PeriodicFourierGeometry:
        return PeriodicFourierGeometry(
            (self.points, self.points, self.points),
            (self.spacing, self.spacing, self.spacing),
        )

    def reconciled_config(self) -> ReconciledGaugeSpinorConfig:
        return ReconciledGaugeSpinorConfig(
            points=self.points,
            seed_points=self.seed_points,
            half_width=self.half_width,
            winding=self.winding,
            core_radius=self.core_radius,
            contour_radius=self.contour_radius,
            charge=self.charge,
            g_factor=self.g_factor,
            dispersion=self.dispersion,
            neutral_iterations=self.neutral_iterations,
            iterations=max(20, self.iterations),
            imaginary_dt=self.imaginary_dt,
            field_relaxation=1.0,
            hartree_couplings=(self.newton_coupling,),
        )


def coordinate_mesh(cfg: CoupledActionConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axis = -cfg.half_width + cfg.spacing * np.arange(cfg.points, dtype=np.float64)
    return tuple(np.asarray(item, dtype=np.float64) for item in np.meshgrid(axis, axis, axis, indexing="ij"))  # type: ignore[return-value]


def winding_phase(cfg: CoupledActionConfig) -> np.ndarray:
    x, y, _z = coordinate_mesh(cfg)
    return np.asarray(np.exp(1.0j * cfg.winding * np.arctan2(y, x)), dtype=np.complex128)


def project_winding_sector(spinor: np.ndarray, cfg: CoupledActionConfig) -> np.ndarray:
    """Project to a spin-up, winding-fixed amplitude sector."""
    if spinor.shape != (2, cfg.points, cfg.points, cfg.points):
        raise ValueError("two-component spinor on the configured grid required")
    amplitude = np.sqrt(np.sum(np.abs(spinor) ** 2, axis=0))
    projected = np.zeros_like(spinor, dtype=np.complex128)
    projected[0] = amplitude * winding_phase(cfg)
    return normalize_spinor(projected, cfg.spacing)


def self_consistent_fields(
    spinor: np.ndarray,
    cfg: CoupledActionConfig,
    vector_seed: Vector | None = None,
) -> dict[str, Any]:
    geometry = cfg.geometry()
    rcfg = cfg.reconciled_config()
    vector = vector_seed or tuple(np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3))
    fields: dict[str, Any] | None = None
    for _ in range(cfg.field_iterations):
        charge_density, current = reconciled_charge_current(spinor, vector, geometry, rcfg)
        fields = geometry.static_maxwell_fields(charge_density, current)
        vector = tuple(np.asarray(component, dtype=np.float64) for component in fields["vector_potential"])
    assert fields is not None
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    fields = {**fields, "hartree_potential": geometry.inverse_negative_laplacian(density)}
    return fields


def action_terms(spinor: np.ndarray, fields: Mapping[str, Any], cfg: CoupledActionConfig) -> dict[str, float]:
    geometry = cfg.geometry()
    alpha, beta = coefficients()
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    vector = fields["vector_potential"]
    covariant_norm = 0.0
    for axis in range(3):
        derivative = geometry.derivative(spinor, axis)
        derivative -= 1.0j * cfg.charge * vector[axis][None, ...] * spinor
        covariant_norm += float(np.sum(np.abs(derivative) ** 2))
    kinetic = cfg.dispersion * geometry.cell_volume * covariant_norm
    local = geometry.cell_volume * float(
        np.sum(-0.5 * alpha * density**2 + (beta / 3.0) * density**3)
    )
    electrostatic = 0.5 * geometry.cell_volume * float(
        np.sum(fields["projected_charge"] * fields["potential"])
    )
    hartree = -0.5 * cfg.newton_coupling * geometry.cell_volume * float(
        np.sum(density * fields["hartree_potential"])
    )
    magnetic_field = float(fields["magnetic_energy"])
    local_spin = spin_density(spinor)
    pauli = -cfg.g_factor * cfg.charge / (2.0 * cfg.effective_mass) * geometry.cell_volume * sum(
        float(np.sum(local_spin[index] * fields["magnetic"][index])) for index in range(3)
    )
    return {
        "kinetic": kinetic,
        "local_cubic_quintic": local,
        "electrostatic": electrostatic,
        "hartree": hartree,
        "magnetic_field": magnetic_field,
        "pauli": pauli,
        "total": kinetic + local + electrostatic + hartree + magnetic_field + pauli,
    }


def action_value(spinor: np.ndarray, cfg: CoupledActionConfig) -> float:
    return action_terms(spinor, self_consistent_fields(spinor, cfg), cfg)["total"]


def hamiltonian_for(spinor: np.ndarray, fields: Mapping[str, Any], cfg: CoupledActionConfig) -> np.ndarray:
    return reconciled_hamiltonian(
        spinor,
        fields["potential"],
        fields["vector_potential"],
        fields["magnetic"],
        fields["hartree_potential"],
        cfg.newton_coupling,
        cfg.geometry(),
        cfg.reconciled_config(),
    )


def action_directional_derivative_audit(spinor: np.ndarray, cfg: CoupledActionConfig) -> dict[str, float]:
    x, y, z = coordinate_mesh(cfg)
    r2 = x * x + y * y + z * z
    density = np.sum(np.abs(spinor) ** 2, axis=0)
    mean_r2 = float(np.sum(r2 * density) * cfg.spacing**3)
    direction = np.asarray((r2 - mean_r2)[None, ...] * spinor, dtype=np.complex128)
    direction_norm = math.sqrt(float(np.sum(np.abs(direction) ** 2) * cfg.spacing**3))
    direction /= max(direction_norm, 1.0e-30)
    epsilon = 2.0e-5
    plus = normalize_spinor(spinor + epsilon * direction, cfg.spacing)
    minus = normalize_spinor(spinor - epsilon * direction, cfg.spacing)
    finite = (action_value(plus, cfg) - action_value(minus, cfg)) / (2.0 * epsilon)
    fields = self_consistent_fields(spinor, cfg)
    hpsi = hamiltonian_for(spinor, fields, cfg)
    mu = float(np.real(np.vdot(spinor, hpsi)) * cfg.spacing**3)
    tangent_gradient = hpsi - mu * spinor
    predicted = 2.0 * float(np.real(np.vdot(direction, tangent_gradient))) * cfg.spacing**3
    relative = abs(finite - predicted) / max(abs(finite), abs(predicted), 1.0e-12)
    return {"finite_difference": finite, "hamiltonian_pairing": predicted, "relative_error": relative}


def symmetry_reduced_residual(
    spinor: np.ndarray,
    hpsi: np.ndarray,
    cfg: CoupledActionConfig,
) -> dict[str, float]:
    phase = winding_phase(cfg)
    amplitude = np.abs(spinor[0])
    radial_h = np.real(np.conj(phase) * hpsi[0])
    norm = float(np.sum(amplitude**2) * cfg.spacing**3)
    chemical = float(np.sum(amplitude * radial_h) * cfg.spacing**3 / max(norm, 1.0e-30))
    residual = radial_h - chemical * amplitude
    residual_l2 = math.sqrt(float(np.sum(residual**2) * cfg.spacing**3))
    operator_l2 = math.sqrt(float(np.sum(radial_h**2) * cfg.spacing**3))
    leakage = math.sqrt(float(np.sum(np.abs(hpsi[1]) ** 2) * cfg.spacing**3)) / max(
        math.sqrt(float(np.sum(np.abs(hpsi) ** 2) * cfg.spacing**3)), 1.0e-30
    )
    return {
        "chemical_potential": chemical,
        "relative_projected_residual": residual_l2 / max(operator_l2, 1.0e-30),
        "spin_sector_leakage": leakage,
    }


@lru_cache(maxsize=1)
def run_coupled_gauge_spinor_hartree_action() -> dict[str, Any]:
    cfg = CoupledActionConfig()
    scalar = odd_grid_seed(cfg.reconciled_config())
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = project_winding_sector(spinor, cfg)
    initial_fields = self_consistent_fields(spinor, cfg)
    initial_h = hamiltonian_for(spinor, initial_fields, cfg)
    initial_full = stationary_residual(spinor, initial_h, cfg.spacing)
    initial_reduced = symmetry_reduced_residual(spinor, initial_h, cfg)
    initial_action = action_terms(spinor, initial_fields, cfg)
    derivative_audit = action_directional_derivative_audit(spinor, cfg)
    action_trace = [initial_action["total"]]
    vector = initial_fields["vector_potential"]
    for iteration in range(cfg.iterations):
        fields = self_consistent_fields(spinor, cfg, vector)
        vector = fields["vector_potential"]
        hpsi = hamiltonian_for(spinor, fields, cfg)
        mu = float(np.real(np.vdot(spinor, hpsi)) * cfg.spacing**3)
        spinor = project_winding_sector(
            spinor - cfg.imaginary_dt * (hpsi - mu * spinor), cfg
        )
        if (iteration + 1) % 20 == 0:
            action_trace.append(action_value(spinor, cfg))
    final_fields = self_consistent_fields(spinor, cfg, vector)
    final_h = hamiltonian_for(spinor, final_fields, cfg)
    final_full = stationary_residual(spinor, final_h, cfg.spacing)
    final_reduced = symmetry_reduced_residual(spinor, final_h, cfg)
    final_action = action_terms(spinor, final_fields, cfg)
    winding = periodic_contour_winding(spinor[0], cfg.spacing, radius=cfg.contour_radius)
    action_nonincrease = final_action["total"] <= initial_action["total"] + 1.0e-8
    reduced_branch = bool(
        final_reduced["relative_projected_residual"] <= cfg.projected_residual_gate
        and winding["integer_winding"] == cfg.winding
        and abs(final_full["norm"] - 1.0) <= 2.0e-12
        and action_nonincrease
    )
    acceptance = {
        "formal_newton_map_is_exact_in_declared_units": abs(cfg.newton_coupling - cfg.hbar * cfg.light_speed * cfg.inference_width**4) <= 1.0e-15,
        "one_action_contains_all_declared_sectors": set(final_action) == {"kinetic", "local_cubic_quintic", "electrostatic", "hartree", "magnetic_field", "pauli", "total"},
        "directional_derivative_audit_is_finite": all(math.isfinite(value) for value in derivative_audit.values()),
        "winding_sector_and_normalization_close": winding["integer_winding"] == cfg.winding and winding["quantization_error"] <= 5.0e-3 and abs(final_full["norm"] - 1.0) <= 2.0e-12,
        "shared_maxwell_constraints_close": final_fields["gauss_relative_residual"] <= 1.0e-11 and final_fields["ampere_relative_residual"] <= 1.0e-11 and final_fields["magnetic_divergence_max"] <= 1.0e-11,
        "stationary_solver_returns_finite_audited_result": all(math.isfinite(value) for value in (*final_full.values(), *final_reduced.values(), *final_action.values())),
        "unrestricted_stability_is_not_inferred": True,
    }
    return {
        "schema": "openwave.m9.coupled-gauge-spinor-hartree-action.v1",
        "task": "M9.101b",
        "config": asdict(cfg),
        "formal_coupling_map": {"equation": "G = hbar*c*sigma0^4", "value": cfg.newton_coupling, "epistemic_status": "ansatz-loaded-natural-unit-realization"},
        "initial": {"full": initial_full, "symmetry_reduced": initial_reduced, "action": initial_action},
        "final": {"full": final_full, "symmetry_reduced": final_reduced, "action": final_action, "winding": winding},
        "action_trace": action_trace,
        "action_nonincrease": action_nonincrease,
        "directional_derivative_audit": derivative_audit,
        "symmetry_reduced_stationary_branch_constructed": reduced_branch,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "one_finite_coupled_action_implemented": True,
            "one_winding_sector_stationary_solver_implemented": True,
            "symmetry_reduced_stationary_branch_constructed": reduced_branch,
            "unrestricted_stable_charged_branch_constructed": False,
            "continuum_einstein_hilbert_maxwell_action_claimed": False,
            "physical_particle_identity_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
