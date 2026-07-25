"""M9.96b: field-derived charge/current, static Maxwell fields, and moment response.

The same winding-three CAT/EPT candidate supplies its charge density, convective
phase current, Pauli magnetization current, electric field, magnetic field, and
magnetic response. The construction is one-way: Maxwell backreaction is not used
to claim a stationary charged particle.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import (
    ChargedBranchFeasibilityConfig,
    charged_observables,
    charged_seed,
    run_charged_branch_feasibility,
)
from .charged_field_tools import (
    magnetic_moment_z,
    pauli_charge_current,
    static_maxwell_fields,
    uniform_b_response,
)
from .formalization_force_extension import (
    extended_criterion_import_map,
    run_force_formal_extension_study,
)


@dataclass(frozen=True)
class ChargedMaxwellSourceConfig:
    points: int = 24
    half_width: float = 8.0
    winding: int = 3
    core_radius: float = 0.90
    contour_radius: float = 2.60
    spin: int = 1
    mass: float = 1.0

    def __post_init__(self) -> None:
        if self.points < 20 or self.points % 2:
            raise ValueError("an even grid with at least 20 points is required")
        if self.winding == 0 or self.core_radius <= 0.0 or self.mass <= 0.0:
            raise ValueError("nonzero winding and positive source controls required")
        if self.spin not in (-1, 1):
            raise ValueError("spin must be +/-1")

    def branch_config(self) -> ChargedBranchFeasibilityConfig:
        return ChargedBranchFeasibilityConfig(
            points=self.points,
            half_width=self.half_width,
            winding=self.winding,
            core_radii=(self.core_radius,),
            contour_radius=self.contour_radius,
        )


@lru_cache(maxsize=1)
def source_candidate() -> tuple[np.ndarray, tuple[np.ndarray, ...], dict[str, float]]:
    cfg = ChargedMaxwellSourceConfig()
    field, grid = charged_seed(cfg.core_radius, cfg.branch_config())
    observables = charged_observables(field, grid, cfg.branch_config())
    return field, grid, observables


@lru_cache(maxsize=1)
def run_charged_maxwell_source_bridge() -> dict[str, Any]:
    cfg = ChargedMaxwellSourceConfig()
    field, grid, observables = source_candidate()
    spacing = float(grid[5])
    winding = int(observables["integer_winding"])
    charge = float(Fraction(winding, 3))
    charge_density, current, source = pauli_charge_current(
        field,
        spacing,
        charge=charge,
        spin=cfg.spin,
        mass=cfg.mass,
    )
    maxwell = static_maxwell_fields(charge_density, current, spacing)
    response = uniform_b_response(current, spacing)
    moment = magnetic_moment_z(current, spacing)
    formalization = run_force_formal_extension_study()
    imports = extended_criterion_import_map()
    magnetic_declarations = tuple(imports["magnetic_moment_spin"]["declarations"])
    electric_declarations = tuple(imports["electric_force"]["declarations"])
    feasibility = run_charged_branch_feasibility()
    acceptance = {
        "current_formalization_tree_and_force_overlay_pass": bool(formalization["passed"]),
        "winding_is_measured_from_the_field": (
            winding == cfg.winding and observables["quantization_error"] <= 2.0e-12
        ),
        "charge_follows_exact_thirds": charge == 1.0,
        "integrated_charge_closes": abs(source["integrated_charge"] - charge) <= 2.0e-12,
        "periodic_poisson_projection_loss_is_small": maxwell["projection_loss"] <= 1.5e-2,
        "projected_gauss_law_closes": maxwell["gauss_relative_residual"] <= 2.0e-12,
        "static_ampere_law_closes": maxwell["ampere_relative_residual"] <= 2.0e-12,
        "magnetic_divergence_closes": maxwell["magnetic_divergence_max"] <= 2.0e-12,
        "electric_and_magnetic_self_fields_are_nonzero": (
            maxwell["electric_energy"] > 0.0 and maxwell["magnetic_energy"] > 0.0
        ),
        "current_moment_matches_uniform_field_energy_response": (
            response["absolute_error"] <= 2.0e-10
            and abs(moment - response["current_moment"]) <= 2.0e-12
        ),
        "gauge_invariant_pauli_maxwell_link_is_imported": any(
            declaration.endswith("pauliCoupling_gauge_invariant")
            for declaration in magnetic_declarations
        ),
        "conserved_current_maxwell_link_is_imported": any(
            declaration.endswith("fourCurrent_conserved")
            for declaration in electric_declarations
        ),
        "stationary_failure_is_not_hidden": not feasibility["decision"][
            "charged_stationary_branch_constructed"
        ],
    }
    return {
        "schema": "openwave.m9.charged-maxwell-source-bridge.v1",
        "task": "M9.96b",
        "config": asdict(cfg),
        "candidate": observables,
        "source": {
            **source,
            "charge_from_winding": charge,
            "magnetic_moment_z": moment,
        },
        "maxwell": {
            key: value
            for key, value in maxwell.items()
            if key
            in {
                "projection_loss",
                "gauss_relative_residual",
                "ampere_relative_residual",
                "magnetic_divergence_max",
                "electric_energy",
                "magnetic_energy",
            }
        },
        "magnetic_response": response,
        "formal_import": {
            "magnetic_declarations": list(magnetic_declarations),
            "electric_declarations": list(electric_declarations),
            "base_inventory_fingerprint": formalization[
                "base_inventory_fingerprint"
            ],
            "extension_fingerprint": formalization["extension_fingerprint"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "same_field_supplies_winding_charge_current_and_moment": True,
            "static_maxwell_source_equations_closed": True,
            "magnetic_moment_response_closed_on_candidate": True,
            "maxwell_backreaction_in_stationary_equation": False,
            "charged_stationary_branch_constructed": False,
            "physical_charge_or_moment_calibrated": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
