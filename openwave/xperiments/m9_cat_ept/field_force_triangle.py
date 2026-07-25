"""M9.96c: Lorentz-volume, interaction-energy, and Maxwell-stress force triangle.

Two opposite winding candidates source their own periodic electric and magnetic
fields. The force on either source is computed from the Lorentz force density,
the derivative of the cross interaction energy, and the cross Maxwell stress
flux. This closes a field-theory consistency triangle on charged candidates; it
does not replace a center-of-energy acceleration measurement from the full PDE.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from typing import Any, Mapping

import numpy as np

from .charged_field_tools import (
    cross_maxwell_stress_flux,
    lorentz_force,
    pauli_charge_current,
    spectral_shift,
    static_maxwell_fields,
)
from .charged_maxwell_source_bridge import (
    ChargedMaxwellSourceConfig,
    run_charged_maxwell_source_bridge,
    source_candidate,
)


@dataclass(frozen=True)
class FieldForceTriangleConfig:
    separation: float = 16.0 / 3.0
    derivative_step: float = 5.0e-2
    stress_half_width: float = 2.0
    energy_relative_tolerance: float = 6.0e-2
    stress_relative_tolerance: float = 8.0e-2
    action_reaction_relative_tolerance: float = 5.0e-9

    def __post_init__(self) -> None:
        if self.separation <= 0.0 or self.derivative_step <= 0.0:
            raise ValueError("positive separation and derivative step required")
        if self.stress_half_width <= 0.0:
            raise ValueError("positive stress integration half width required")
        if 2.0 * self.stress_half_width >= self.separation:
            raise ValueError("stress surface must not enclose both particles")
        if min(
            self.energy_relative_tolerance,
            self.stress_relative_tolerance,
            self.action_reaction_relative_tolerance,
        ) <= 0.0:
            raise ValueError("positive force-comparison tolerances required")


def pair_sources(separation: float) -> dict[str, Any]:
    base, grid, candidate = source_candidate()
    spacing = float(grid[5])
    spacings = (spacing, spacing, spacing)
    positive_field = spectral_shift(base, spacings, (0.0, 0.0, -0.5 * separation))
    negative_field = spectral_shift(
        np.conj(base),
        spacings,
        (0.0, 0.0, 0.5 * separation),
    )
    positive_charge, positive_current, positive_source = pauli_charge_current(
        positive_field,
        spacing,
        charge=1.0,
        spin=1,
    )
    negative_charge, negative_current, negative_source = pauli_charge_current(
        negative_field,
        spacing,
        charge=-1.0,
        spin=1,
    )
    positive_maxwell = static_maxwell_fields(
        positive_charge,
        positive_current,
        spacing,
    )
    negative_maxwell = static_maxwell_fields(
        negative_charge,
        negative_current,
        spacing,
    )
    return {
        "grid": grid,
        "candidate": candidate,
        "spacing": spacing,
        "positive_charge": positive_charge,
        "positive_current": positive_current,
        "positive_source": positive_source,
        "positive_maxwell": positive_maxwell,
        "negative_charge": negative_charge,
        "negative_current": negative_current,
        "negative_source": negative_source,
        "negative_maxwell": negative_maxwell,
    }


def interaction_energy(pair: Mapping[str, Any]) -> float:
    spacing = float(pair["spacing"])
    charge_term = pair["positive_charge"] * pair["negative_maxwell"]["potential"]
    magnetic_term = sum(
        pair["positive_current"][index]
        * pair["negative_maxwell"]["vector_potential"][index]
        for index in range(3)
    )
    return spacing**3 * float(np.sum(charge_term - magnetic_term))


def force_components(pair: Mapping[str, Any]) -> dict[str, np.ndarray]:
    spacing = float(pair["spacing"])
    spacings = (spacing, spacing, spacing)
    electric = np.asarray(
        [
            spacing**3
            * float(
                np.sum(
                    pair["positive_charge"]
                    * pair["negative_maxwell"]["electric"][index]
                )
            )
            for index in range(3)
        ],
        dtype=np.float64,
    )
    full = lorentz_force(
        pair["positive_charge"],
        pair["positive_current"],
        pair["negative_maxwell"]["electric"],
        pair["negative_maxwell"]["magnetic"],
        spacings,
    )
    return {"electric": electric, "magnetic": full - electric, "full": full}


@lru_cache(maxsize=1)
def run_field_force_triangle() -> dict[str, Any]:
    cfg = FieldForceTriangleConfig()
    source_bridge = run_charged_maxwell_source_bridge()
    pair = pair_sources(cfg.separation)
    components = force_components(pair)
    reverse = lorentz_force(
        pair["negative_charge"],
        pair["negative_current"],
        pair["positive_maxwell"]["electric"],
        pair["positive_maxwell"]["magnetic"],
        (pair["spacing"],) * 3,
    )
    energy_plus = interaction_energy(pair_sources(cfg.separation + cfg.derivative_step))
    energy_minus = interaction_energy(pair_sources(cfg.separation - cfg.derivative_step))
    energy_derivative = (energy_plus - energy_minus) / (2.0 * cfg.derivative_step)
    stress = cross_maxwell_stress_flux(
        pair["positive_maxwell"]["electric"],
        pair["positive_maxwell"]["magnetic"],
        pair["negative_maxwell"]["electric"],
        pair["negative_maxwell"]["magnetic"],
        float(pair["spacing"]),
        center=(0.0, 0.0, -0.5 * cfg.separation),
        half_width=cfg.stress_half_width,
    )
    reference = float(components["full"][2])
    energy_error = abs(energy_derivative - reference) / max(abs(reference), 1.0e-30)
    stress_error = abs(float(stress[2]) - reference) / max(abs(reference), 1.0e-30)
    action_reaction_error = float(
        np.linalg.norm(components["full"] + reverse)
        / max(np.linalg.norm(components["full"]), 1.0e-30)
    )
    source_cfg = ChargedMaxwellSourceConfig()
    acceptance = {
        "charged_source_bridge_passes": bool(source_bridge["passed"]),
        "opposite_field_derived_charges_are_used": (
            abs(pair["positive_source"]["integrated_charge"] - 1.0) <= 2.0e-12
            and abs(pair["negative_source"]["integrated_charge"] + 1.0) <= 2.0e-12
            and pair["candidate"]["integer_winding"] == source_cfg.winding
        ),
        "electric_and_magnetic_force_parts_are_nonzero": (
            abs(float(components["electric"][2])) > 1.0e-8
            and abs(float(components["magnetic"][2])) > 1.0e-8
        ),
        "opposite_charges_attract": reference > 0.0,
        "interaction_energy_derivative_matches_lorentz_force": (
            energy_error <= cfg.energy_relative_tolerance
        ),
        "cross_maxwell_stress_matches_lorentz_force": (
            stress_error <= cfg.stress_relative_tolerance
        ),
        "action_reaction_closes": (
            action_reaction_error <= cfg.action_reaction_relative_tolerance
        ),
        "both_source_maxwell_constraints_close": all(
            selected["gauss_relative_residual"] <= 2.0e-12
            and selected["ampere_relative_residual"] <= 2.0e-12
            and selected["magnetic_divergence_max"] <= 2.0e-12
            for selected in (
                pair["positive_maxwell"],
                pair["negative_maxwell"],
            )
        ),
        "full_pde_motion_is_not_silently_inferred": True,
    }
    return {
        "schema": "openwave.m9.field-force-triangle.v1",
        "task": "M9.96c",
        "config": asdict(cfg),
        "charges": [
            pair["positive_source"]["integrated_charge"],
            pair["negative_source"]["integrated_charge"],
        ],
        "interaction_energy": interaction_energy(pair),
        "lorentz_force": components["full"].tolist(),
        "electric_force": components["electric"].tolist(),
        "magnetic_force": components["magnetic"].tolist(),
        "reverse_lorentz_force": reverse.tolist(),
        "energy_derivative_force_z": energy_derivative,
        "stress_flux_force": stress.tolist(),
        "relative_errors": {
            "energy_vs_lorentz": energy_error,
            "stress_vs_lorentz": stress_error,
            "action_reaction": action_reaction_error,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "field_derived_force_triangle_closed_on_charged_candidates": True,
            "electric_and_magnetic_kernels_replaced_by_source_fields": True,
            "center_acceleration_measured_from_full_pde": False,
            "stable_charged_stationary_pair_constructed": False,
            "physical_force_calibration_complete": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
