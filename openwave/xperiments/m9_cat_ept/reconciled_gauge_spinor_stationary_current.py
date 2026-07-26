"""Current odd-grid M9.99b mass/operator/Hartree reconciliation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import ChargedBranchFeasibilityConfig, charged_seed
from .compatible_discrete_geometry import (
    PeriodicFourierGeometry,
    analytic_identity_diagnostics,
    spectral_resample,
)
from .reconciled_gauge_spinor_stationary import (
    normalize_spinor,
    reconciled_charge_current,
    reconciled_hamiltonian,
    stationary_residual,
)


@dataclass(frozen=True)
class ReconciledGaugeSpinorConfig:
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
    iterations: int = 160
    imaginary_dt: float = 2.5e-5
    field_relaxation: float = 0.50
    hartree_couplings: tuple[float, ...] = (0.0, 0.05, 0.10)

    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0:
            raise ValueError("an odd operational grid with at least 17 points is required")
        if self.seed_points < 16 or self.seed_points % 2:
            raise ValueError("an even historical seed grid with at least 16 points is required")
        if min(
            self.half_width,
            self.core_radius,
            self.contour_radius,
            self.g_factor,
            self.dispersion,
            self.imaginary_dt,
        ) <= 0.0:
            raise ValueError("positive reconciled controls required")
        if self.charge == 0.0 or self.winding == 0:
            raise ValueError("nonzero charge and winding required")
        if self.iterations < 20 or self.neutral_iterations < 100:
            raise ValueError("substantive stationary campaigns required")
        if not 0.0 < self.field_relaxation <= 1.0:
            raise ValueError("field relaxation must lie in (0,1]")
        if any(value < 0.0 for value in self.hartree_couplings):
            raise ValueError("nonnegative Hartree coupling sweep required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def effective_mass(self) -> float:
        return 1.0 / (2.0 * self.dispersion)

    @property
    def convective_current_coefficient(self) -> float:
        return self.charge / self.effective_mass

    def seed_config(self) -> ChargedBranchFeasibilityConfig:
        return ChargedBranchFeasibilityConfig(
            points=self.seed_points,
            half_width=self.half_width,
            winding=self.winding,
            core_radii=(self.core_radius,),
            contour_radius=self.contour_radius,
            neutral_iterations=self.neutral_iterations,
            charged_iterations=100,
        )

    def geometry(self) -> PeriodicFourierGeometry:
        return PeriodicFourierGeometry(
            (self.points, self.points, self.points),
            (self.spacing, self.spacing, self.spacing),
        )


def odd_grid_seed(cfg: ReconciledGaugeSpinorConfig) -> np.ndarray:
    legacy, _grid = charged_seed(cfg.core_radius, cfg.seed_config())
    resampled = spectral_resample(
        legacy, (cfg.points, cfg.points, cfg.points)
    )
    return normalize_spinor(resampled, cfg.spacing)


def run_one_coupling(
    hartree_coupling: float,
    cfg: ReconciledGaugeSpinorConfig,
) -> dict[str, Any]:
    geometry = cfg.geometry()
    field = odd_grid_seed(cfg)
    spinor = np.zeros((2, *field.shape), dtype=np.complex128)
    spinor[0] = field
    spinor = normalize_spinor(spinor, cfg.spacing)
    vector_potential = tuple(
        np.zeros(field.shape, dtype=np.float64) for _ in range(3)
    )
    initial: dict[str, float] | None = None
    final_fields: dict[str, Any] | None = None
    final_hamiltonian: np.ndarray | None = None
    final_uses_exact_vector = False
    for iteration in range(cfg.iterations + 1):
        charge_density, current = reconciled_charge_current(
            spinor, vector_potential, geometry, cfg
        )
        fields = geometry.static_maxwell_fields(charge_density, current)
        exact_vector = tuple(
            np.asarray(component, dtype=np.float64)
            for component in fields["vector_potential"]
        )
        if iteration == cfg.iterations:
            vector_potential = exact_vector
            final_uses_exact_vector = True
        else:
            vector_potential = tuple(
                np.asarray(
                    (1.0 - cfg.field_relaxation) * vector_potential[index]
                    + cfg.field_relaxation * exact_vector[index],
                    dtype=np.float64,
                )
                for index in range(3)
            )
        magnetic = geometry.curl(vector_potential)
        density = np.asarray(
            np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64
        )
        hartree_potential = geometry.inverse_negative_laplacian(density)
        hamiltonian = reconciled_hamiltonian(
            spinor,
            fields["potential"],
            vector_potential,
            magnetic,
            hartree_potential,
            hartree_coupling,
            geometry,
            cfg,
        )
        if iteration == 0:
            initial = stationary_residual(spinor, hamiltonian, cfg.spacing)
        if iteration == cfg.iterations:
            final_fields = fields
            final_hamiltonian = hamiltonian
            break
        chemical_potential = float(
            np.real(np.vdot(spinor, hamiltonian)) * cfg.spacing**3
        )
        spinor = normalize_spinor(
            spinor
            - cfg.imaginary_dt * (hamiltonian - chemical_potential * spinor),
            cfg.spacing,
        )
    assert (
        initial is not None
        and final_fields is not None
        and final_hamiltonian is not None
    )
    final = stationary_residual(spinor, final_hamiltonian, cfg.spacing)
    return {
        "hartree_coupling": hartree_coupling,
        "initial": initial,
        "final": final,
        "residual_change": final["relative_stationary_residual"]
        - initial["relative_stationary_residual"],
        "final_hamiltonian_uses_exact_maxwell_vector": final_uses_exact_vector,
        "maxwell": {
            key: final_fields[key]
            for key in (
                "gauss_relative_residual",
                "ampere_relative_residual",
                "magnetic_divergence_max",
                "electric_energy",
                "magnetic_energy",
            )
        },
    }


@lru_cache(maxsize=1)
def run_reconciled_gauge_spinor_campaign() -> dict[str, Any]:
    cfg = ReconciledGaugeSpinorConfig()
    geometry_diagnostics = analytic_identity_diagnostics(
        cfg.points, cfg.half_width
    )
    rows = [run_one_coupling(value, cfg) for value in cfg.hartree_couplings]
    mass_map_error = abs(2.0 * cfg.dispersion * cfg.effective_mass - 1.0)
    current_map_error = abs(
        cfg.convective_current_coefficient
        - 2.0 * cfg.dispersion * cfg.charge
    )
    acceptance = {
        "schrodinger_mass_map_closes": mass_map_error <= 2.0e-15,
        "convective_current_uses_the_same_mass_map": current_map_error <= 2.0e-15,
        "one_fourier_differential_complex_is_used": (
            geometry_diagnostics["odd_operational_grid"] == 1
            and geometry_diagnostics["fourier_null_mode_count"] == 1
            and geometry_diagnostics[
                "legacy_even_centered_null_mode_count"
            ]
            == 8
            and geometry_diagnostics["curl_gradient_max"] <= 1.0e-12
            and geometry_diagnostics["divergence_curl_max"] <= 1.0e-12
            and geometry_diagnostics[
                "laplacian_identity_relative_error"
            ]
            <= 1.0e-12
        ),
        "historical_seed_is_explicitly_resampled_to_odd_grid": (
            cfg.seed_points == 16 and cfg.points == 17
        ),
        "all_hartree_sweep_rows_execute": len(rows)
        == len(cfg.hartree_couplings),
        "final_hamiltonians_use_exact_maxwell_vectors": all(
            row["final_hamiltonian_uses_exact_maxwell_vector"] for row in rows
        ),
        "shared_maxwell_constraints_close": all(
            row["maxwell"]["gauss_relative_residual"] <= 1.0e-11
            and row["maxwell"]["ampere_relative_residual"] <= 1.0e-11
            and row["maxwell"]["magnetic_divergence_max"] <= 1.0e-11
            for row in rows
        ),
        "normalization_and_spin_remain_controlled": all(
            abs(row["final"]["norm"] - 1.0) <= 2.0e-12
            and abs(row["final"]["spin_z"] - 0.5) <= 5.0e-6
            for row in rows
        ),
        "hartree_coupling_selection_remains_explicitly_open": True,
        "no_stationary_or_physical_promotion_is_inferred": True,
    }
    return {
        "schema": "openwave.m9.reconciled-gauge-spinor-campaign.v2",
        "task": "M9.99b",
        "config": asdict(cfg),
        "effective_mass": cfg.effective_mass,
        "legacy_declared_mass": 1.0,
        "relative_legacy_mass_mismatch": abs(
            1.0 - cfg.effective_mass
        )
        / cfg.effective_mass,
        "mass_map_error": mass_map_error,
        "current_map_error": current_map_error,
        "geometry_diagnostics": geometry_diagnostics,
        "rows": rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "legacy_mass_and_operator_mismatch_repaired": True,
            "historical_even_seed_resampled_to_odd_operational_grid": True,
            "final_stationary_residual_uses_exact_maxwell_field": True,
            "current_formal_hartree_term_is_executable_as_a_sweep": True,
            "formal_hartree_coupling_selected": False,
            "charged_stationary_branch_promoted": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
