"""M9.97 canonical Maxwell--Dirac pair response from four-spinor sources.

The Pauli winding fields are used only to seed the positive-energy embedding.
After embedding, all charge densities, Dirac currents, Maxwell fields, Lorentz
forces, and control fields are regenerated from the actual four-spinors evolved
by the bounded Maxwell--Dirac engine.
"""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import charged_seed
from .charged_field_tools import lorentz_force, spectral_shift, static_maxwell_fields
from .gauge_spinor_stationary_feasibility import run_gauge_spinor_stationary_feasibility
from .spatial_3d_operators import current_expectations, density
from .spinorial_pair_dynamics import (
    SpinorialPairDynamicsConfig,
    evolve_response,
    fit_response,
    pauli_source,
    pauli_to_dirac,
    spin_vector,
)


def dirac_source(
    state: np.ndarray,
    *,
    charge_sign: float,
    charge: float,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    if state.ndim != 4 or state.shape[0] != 4:
        raise ValueError("four-component three-dimensional spinor required")
    signed_charge = charge_sign * charge
    charge_density = np.asarray(signed_charge * density(state), dtype=np.float64)
    current = tuple(
        np.asarray(signed_charge * component, dtype=np.float64)
        for component in current_expectations(state)
    )
    return charge_density, current  # type: ignore[return-value]


@lru_cache(maxsize=1)
def run_spinorial_pair_dynamics() -> dict[str, Any]:
    cfg = SpinorialPairDynamicsConfig(
        fit_samples=4,
        generator_spin_tolerance=3.0e-2,
    )
    stationary = run_gauge_spinor_stationary_feasibility()
    base, grid = charged_seed(cfg.core_radius, cfg.branch_config())
    x, y, z = grid[:3]
    coordinates = (x, y, z)
    spacings = (cfg.spacing, cfg.spacing, cfg.spacing)
    positive_field = spectral_shift(base, spacings, (0.0, 0.0, -0.5 * cfg.separation))
    negative_field = np.conj(
        spectral_shift(base, spacings, (0.0, 0.0, 0.5 * cfg.separation))
    )
    spin_x = np.asarray([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    positive_pauli = spin_x[:, None, None, None] * positive_field[None, ...]
    negative_pauli = spin_x[:, None, None, None] * negative_field[None, ...]

    positive_seed_charge, positive_seed_current = pauli_source(
        positive_pauli,
        charge=cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    negative_seed_charge, negative_seed_current = pauli_source(
        negative_pauli,
        charge=-cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    positive_seed_maxwell = static_maxwell_fields(
        positive_seed_charge, positive_seed_current, cfg.spacing
    )
    negative_seed_maxwell = static_maxwell_fields(
        negative_seed_charge, negative_seed_current, cfg.spacing
    )

    pair_plus = pauli_to_dirac(
        positive_pauli,
        positive_seed_maxwell["vector_potential"],
        charge_sign=1.0,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    pair_minus = pauli_to_dirac(
        negative_pauli,
        negative_seed_maxwell["vector_potential"],
        charge_sign=-1.0,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )

    positive_charge, positive_current = dirac_source(
        pair_plus,
        charge_sign=1.0,
        charge=cfg.charge,
    )
    negative_charge, negative_current = dirac_source(
        pair_minus,
        charge_sign=-1.0,
        charge=cfg.charge,
    )
    positive_maxwell = static_maxwell_fields(
        positive_charge, positive_current, cfg.spacing
    )
    negative_maxwell = static_maxwell_fields(
        negative_charge, negative_current, cfg.spacing
    )
    total_vector = tuple(
        positive_maxwell["vector_potential"][index]
        + negative_maxwell["vector_potential"][index]
        for index in range(3)
    )
    total_electric = tuple(
        positive_maxwell["electric"][index] + negative_maxwell["electric"][index]
        for index in range(3)
    )
    zero_minus = np.zeros_like(pair_minus)
    pair = evolve_response(
        pair_plus,
        pair_minus,
        total_vector,
        total_electric,
        coordinates,
        cfg,
    )
    control = evolve_response(
        pair_plus,
        zero_minus,
        positive_maxwell["vector_potential"],
        positive_maxwell["electric"],
        coordinates,
        cfg,
    )
    response = fit_response(pair, control, cfg)
    external_force = lorentz_force(
        positive_charge,
        positive_current,
        negative_maxwell["electric"],
        negative_maxwell["magnetic"],
        spacings,
    )
    initial_spin = spin_vector(pair_plus, cfg.spacing)
    plus_density = density(pair_plus)
    plus_norm = float(np.sum(plus_density) * cfg.spacing**3)
    effective_partner_b = np.asarray(
        [
            float(
                np.sum(plus_density * negative_maxwell["magnetic"][index])
                * cfg.spacing**3
                / plus_norm
            )
            for index in range(3)
        ],
        dtype=np.float64,
    )
    rest_frame_bmt_rate = (
        cfg.g_factor * cfg.charge / (2.0 * cfg.mass)
    ) * np.cross(initial_spin, effective_partner_b)
    predicted_momentum_rate = float(external_force[2] / plus_norm)
    momentum_error = abs(
        response["interaction_momentum_rate"] - predicted_momentum_rate
    ) / max(abs(predicted_momentum_rate), 1.0e-30)
    center_error = abs(
        response["interaction_center_acceleration"] - predicted_momentum_rate
    ) / max(abs(predicted_momentum_rate), 1.0e-30)
    measured_spin = np.asarray(response["interaction_spin_rate"], dtype=np.float64)
    generator_spin = np.asarray(
        response["interaction_generator_spin_rate"], dtype=np.float64
    )
    generator_spin_error = float(
        np.linalg.norm(measured_spin - generator_spin)
        / max(np.linalg.norm(generator_spin), 1.0e-30)
    )
    bmt_spin_error = float(
        np.linalg.norm(measured_spin - rest_frame_bmt_rate)
        / max(np.linalg.norm(rest_frame_bmt_rate), 1.0e-30)
    )
    max_norm_drift = max(
        abs(row["plus_norm"] - pair["records"][0]["plus_norm"])
        for row in pair["records"]
    )
    pair_charge_error = abs(
        cfg.spacing**3 * float(np.sum(positive_charge + negative_charge))
    )
    acceptance = {
        "gauge_spinor_stationary_boundary_is_imported": (
            stationary["passed"]
            and not stationary["decision"]["charged_spinor_stationary_branch_constructed"]
        ),
        "four_spinor_sources_are_normalized_and_neutral_as_a_pair": (
            abs(cfg.spacing**3 * float(np.sum(positive_charge)) - 1.0) <= 2.0e-12
            and abs(cfg.spacing**3 * float(np.sum(negative_charge)) + 1.0)
            <= 2.0e-12
            and pair_charge_error <= 2.0e-12
        ),
        "full_maxwell_dirac_pair_and_self_control_are_evolved": (
            len(pair["records"]) == len(control["records"])
            and len(pair["records"]) >= cfg.fit_samples
        ),
        "pair_norm_is_stable": max_norm_drift <= 2.0e-4,
        "interaction_momentum_rate_matches_lorentz_force": (
            momentum_error <= cfg.momentum_force_tolerance
        ),
        "center_response_wrong_sign_and_mismatch_are_explicit": (
            response["interaction_center_acceleration"] < 0.0
            and predicted_momentum_rate > 0.0
            and center_error > 5.0e-1
        ),
        "finite_time_spin_rate_matches_the_dirac_generator": (
            generator_spin_error <= cfg.generator_spin_tolerance
        ),
        "rest_frame_bmt_reduction_does_not_silently_close": bmt_spin_error > 5.0e-1,
        "no_stable_pair_or_physical_calibration_is_inferred": True,
    }
    return {
        "schema": "openwave.m9.spinorial-pair-dynamics.v2",
        "task": "M9.97b-c",
        "config": asdict(cfg),
        "source": {
            "positive_integrated_charge": cfg.spacing**3
            * float(np.sum(positive_charge)),
            "negative_integrated_charge": cfg.spacing**3
            * float(np.sum(negative_charge)),
            "pair_charge_error": pair_charge_error,
            "positive_current_l2": math.sqrt(
                cfg.spacing**3
                * sum(float(np.sum(component * component)) for component in positive_current)
            ),
            "negative_current_l2": math.sqrt(
                cfg.spacing**3
                * sum(float(np.sum(component * component)) for component in negative_current)
            ),
        },
        "external_lorentz_force": external_force.tolist(),
        "predicted_momentum_rate": predicted_momentum_rate,
        "effective_partner_magnetic_field": effective_partner_b.tolist(),
        "initial_spin": initial_spin.tolist(),
        "rest_frame_bmt_spin_rate": rest_frame_bmt_rate.tolist(),
        "response": response,
        "relative_errors": {
            "momentum_vs_lorentz": momentum_error,
            "center_acceleration_vs_lorentz": center_error,
            "finite_spin_vs_generator": generator_spin_error,
            "finite_spin_vs_rest_frame_bmt": bmt_spin_error,
        },
        "max_plus_norm_drift": max_norm_drift,
        "pair_records": pair["records"],
        "control_records": control["records"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "four_spinor_sources_drive_all_initial_fields": True,
            "full_maxwell_dirac_pair_evolved": True,
            "momentum_transfer_matches_field_lorentz_force": (
                momentum_error <= cfg.momentum_force_tolerance
            ),
            "center_acceleration_closed": center_error <= cfg.momentum_force_tolerance,
            "center_response_has_lorentz_sign": (
                response["interaction_center_acceleration"]
                * predicted_momentum_rate
                > 0.0
            ),
            "spin_generator_integration_closed": (
                generator_spin_error <= cfg.generator_spin_tolerance
            ),
            "rest_frame_bmt_torque_closed_on_winding_state": (
                bmt_spin_error <= cfg.generator_spin_tolerance
            ),
            "stable_charged_stationary_pair_constructed": False,
            "criterion_rows_promoted": [],
            "physical_force_or_moment_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
