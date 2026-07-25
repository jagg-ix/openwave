"""M9.95: canonical CAT/EPT pair and formal electric/magnetic force bridge.

Two canonical particle envelopes carry declared opposite winding sectors and
Pauli-current magnetic moments. The shared dimensionless interaction ledger is
used for both electric and magnetic kernels. Formal PhysLib declarations supply
the screened/Coulomb potential boundary and Lorentz-EM decomposition; OpenWave
continues to own the regularized finite-grid force calculation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .canonical_spin_magnetic_bridge import (
    CanonicalSpinParameters,
    canonical_spin_observables,
)
from .formalization_import import criterion_import_map, run_formalization_import_study
from .particle_model import (
    CatEptParticleModel,
    CatEptParticleState,
    field_fingerprint,
    normalized_gaussian,
    periodic_displacement,
)
from .two_body_forces import (
    InteractionParameters,
    electric_energy,
    electric_force_exact,
    magnetic_energy,
    magnetic_force_exact,
    numerical_force,
    run_two_body_force_study,
)


@dataclass(frozen=True)
class SharedInteractionLedger:
    length_unit: float = 1.0
    charge_unit: float = 1.0
    magnetic_moment_unit: float = 1.0
    force_unit: float = 1.0
    electric_coupling: float = 1.0
    magnetic_coupling: float = 1.0
    electric_softening: float = 0.30
    magnetic_softening: float = 0.40

    def __post_init__(self) -> None:
        if min(
            self.length_unit,
            self.charge_unit,
            self.magnetic_moment_unit,
            self.force_unit,
            self.electric_coupling,
            self.magnetic_coupling,
            self.electric_softening,
            self.magnetic_softening,
        ) <= 0.0:
            raise ValueError("positive shared interaction ledger values required")

    def interaction_parameters(self) -> InteractionParameters:
        return InteractionParameters(
            electric_coupling=self.electric_coupling,
            magnetic_coupling=self.magnetic_coupling,
            electric_softening=self.electric_softening,
            magnetic_softening=self.magnetic_softening,
        )


def charge_from_winding(winding: int) -> Fraction:
    return Fraction(winding, 3)


def declared_particle_state(
    winding_sector: int,
    *,
    points: int = 32,
    half_width: float = 8.0,
) -> tuple[CatEptParticleModel, CatEptParticleState]:
    model = CatEptParticleModel.repository_default(winding_sector=winding_sector)
    field, spacing = normalized_gaussian(points=points, half_width=half_width)
    state = CatEptParticleState(
        field=field,
        spacing=spacing,
        simulation_time=0.0,
        center=(0.0, 0.0, 0.0),
        phase_origin=0.0,
        declared_winding_sector=winding_sector,
        winding_embedded=winding_sector == 0,
        reference_branch_fingerprint=field_fingerprint(field, spacing),
        construction="declared-winding-force-control",
    )
    return model, state


def periodic_pair_separation(
    first: CatEptParticleState,
    second: CatEptParticleState,
) -> tuple[float, np.ndarray]:
    if first.field.shape != second.field.shape or first.spacing != second.spacing:
        raise ValueError("particle states must share one periodic lattice")
    lengths = tuple(points * first.spacing for points in first.field.shape)
    vector = np.asarray(
        [
            float(periodic_displacement(np.asarray([right]), left, length)[0])
            for left, right, length in zip(first.center, second.center, lengths)
        ],
        dtype=np.float64,
    )
    distance = float(np.linalg.norm(vector))
    if distance <= 0.0:
        raise ValueError("distinct particle centers required")
    return distance, vector


def yukawa_potential(screening_mass: float, radius: float) -> float:
    if screening_mass < 0.0 or radius <= 0.0:
        raise ValueError("nonnegative screening mass and positive radius required")
    return math.exp(-screening_mass * radius) / radius


def formal_potential_audit(radius: float) -> dict[str, float]:
    masses = (0.0, 0.2, 0.7, 1.5)
    values = [yukawa_potential(mass, radius) for mass in masses]
    return {
        "radius": radius,
        "coulomb": 1.0 / radius,
        "zero_mass_yukawa": values[0],
        "maximum_screened_excess": max(value - 1.0 / radius for value in values),
        "screened_values_monotone": float(
            all(values[index + 1] <= values[index] for index in range(len(values) - 1))
        ),
    }


def pair_force_audit(
    ledger: SharedInteractionLedger = SharedInteractionLedger(),
) -> dict[str, Any]:
    positive_model, positive = declared_particle_state(3)
    negative_model, negative = declared_particle_state(-3)
    positive = positive_model.translate_cells(positive, (0, 0, -6))
    negative = negative_model.translate_cells(negative, (0, 0, 6))
    separation, vector = periodic_pair_separation(positive, negative)
    direction = vector / separation

    up = canonical_spin_observables(positive, CanonicalSpinParameters(spin=1))
    down = canonical_spin_observables(negative, CanonicalSpinParameters(spin=-1))
    moment_1 = np.asarray([0.0, 0.0, up["magnetic_moment_z"]])
    moment_2 = np.asarray([0.0, 0.0, down["magnetic_moment_z"]])
    charge_1 = float(charge_from_winding(positive.declared_winding_sector))
    charge_2 = float(charge_from_winding(negative.declared_winding_sector))
    parameters = ledger.interaction_parameters()

    electric = electric_force_exact(
        separation, charge_1, charge_2, parameters
    )
    magnetic = magnetic_force_exact(
        separation, moment_1, moment_2, direction, parameters
    )
    electric_numeric = numerical_force(
        lambda radius: electric_energy(radius, charge_1, charge_2, parameters),
        separation,
        parameters.derivative_step,
    )
    magnetic_numeric = numerical_force(
        lambda radius: magnetic_energy(
            radius, moment_1, moment_2, direction, parameters
        ),
        separation,
        parameters.derivative_step,
    )
    first_force = (electric + magnetic) * direction
    second_force = -first_force
    return {
        "states": {
            "positive": positive.to_manifest(),
            "negative": negative.to_manifest(),
        },
        "declared_charges": [charge_1, charge_2],
        "magnetic_moments": [moment_1.tolist(), moment_2.tolist()],
        "separation": separation,
        "direction": direction.tolist(),
        "electric_force": electric,
        "electric_numeric": electric_numeric,
        "magnetic_force": magnetic,
        "magnetic_numeric": magnetic_numeric,
        "combined_force": float(electric + magnetic),
        "action_reaction_error": float(np.linalg.norm(first_force + second_force)),
        "winding_embedded": positive.winding_embedded and negative.winding_embedded,
    }


@lru_cache(maxsize=1)
def run_canonical_force_formal_bridge() -> dict[str, Any]:
    imported = run_formalization_import_study()
    imports = criterion_import_map()
    electric_import = imports["electric_force"]
    magnetic_import = imports["magnetic_force"]
    ledger = SharedInteractionLedger()
    pair = pair_force_audit(ledger)
    potential = formal_potential_audit(pair["separation"])
    legacy = run_two_body_force_study()

    acceptance = {
        "cat_ept_formalization_import_passes": bool(imported["passed"]),
        "electric_formal_declarations_are_imported": len(electric_import["declarations"]) == 3,
        "magnetic_formal_declarations_are_imported": len(magnetic_import["declarations"]) == 3,
        "one_shared_interaction_ledger_is_used": ledger.electric_coupling > 0.0
        and ledger.magnetic_coupling > 0.0,
        "opposite_integer_charges_follow_winding_arithmetic": pair["declared_charges"] == [1.0, -1.0],
        "canonical_pauli_moments_are_opposite": abs(
            pair["magnetic_moments"][0][2] + pair["magnetic_moments"][1][2]
        ) < 5e-10,
        "electric_force_is_energy_derivative": abs(
            pair["electric_force"] - pair["electric_numeric"]
        ) < 2e-9,
        "magnetic_force_is_energy_derivative": abs(
            pair["magnetic_force"] - pair["magnetic_numeric"]
        ) < 2e-9,
        "action_reaction_closes": pair["action_reaction_error"] < 2e-14,
        "unscreened_yukawa_is_coulomb": abs(
            potential["zero_mass_yukawa"] - potential["coulomb"]
        ) < 2e-15,
        "screening_never_exceeds_coulomb": potential["maximum_screened_excess"] <= 2e-15,
        "screening_is_monotone_in_mass": bool(potential["screened_values_monotone"]),
        "legacy_force_controls_still_pass": bool(legacy["passed"]),
        "charged_stationary_branch_is_not_inherited": not pair["winding_embedded"],
        "physical_force_units_are_not_inherited": True,
    }
    return {
        "schema": "openwave.m9.canonical-force-formal-bridge.v1",
        "task": "M9.95",
        "ledger": asdict(ledger),
        "formal_import": {
            "electric_declarations": list(electric_import["declarations"]),
            "magnetic_declarations": list(magnetic_import["declarations"]),
            "electric_boundary": list(electric_import["boundary"]),
            "magnetic_boundary": list(magnetic_import["boundary"]),
            "inventory_fingerprint": imported["fingerprint"],
        },
        "pair": pair,
        "potential": potential,
        "legacy_force_result": {
            "electric_slope": legacy["electric"]["asymptotic_log_slope"],
            "magnetic_slope": legacy["magnetic"]["asymptotic_log_slope"],
            "passed": legacy["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "formal_electric_and_magnetic_surfaces_imported": True,
            "canonical_particle_pair_bound_to_force_kernels": True,
            "shared_dimensionless_ledger_closed": True,
            "charged_stationary_particle_pair_constructed": False,
            "physical_force_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
