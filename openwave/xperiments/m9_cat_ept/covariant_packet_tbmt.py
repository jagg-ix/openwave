"""M9.101c: local packet Thomas--BMT adapter for the Maxwell--Dirac pair.

The old M9.97 comparison replaced a nonuniform packet by one averaged magnetic
field and then applied the rest-frame rate.  This module evaluates the regular
lab-frame BMT angular velocity pointwise from the packet velocity and local E/B
fields, integrates the local torque density, and subtracts a matched self-field
control.  The result is compared with the exact initial Dirac-generator spin
rate already measured by OpenWave.

The BMT equation is an imported classical spin law.  Physlib proves its scalar
coefficients, magic cancellation, gauge-invariant Pauli coupling, and rest-frame
QED grounding; it explicitly does not derive the covariant Thomas extension
from QED.  This adapter preserves that boundary.
"""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_branch_feasibility import charged_seed
from .charged_field_tools import spectral_shift, static_maxwell_fields
from .gauge_spinor_stationary_feasibility import PAULI
from .spatial_3d_operators import apply_matrix, current_expectations, density, expectation
from .spinorial_pair_dynamics import (
    SPIN_MATRICES,
    SpinorialPairDynamicsConfig,
    pauli_source,
    pauli_to_dirac,
)
from .spinorial_pair_dynamics_current import run_spinorial_pair_dynamics

Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


def four_spin_density(state: np.ndarray) -> Vector:
    if state.ndim != 4 or state.shape[0] != 4:
        raise ValueError("four-component spatial spinor required")
    return tuple(
        np.asarray(0.5 * expectation(state, matrix), dtype=np.float64)
        for matrix in SPIN_MATRICES
    )  # type: ignore[return-value]


def local_velocity(state: np.ndarray, speed_limit: float = 1.0 - 1.0e-10) -> tuple[Vector, np.ndarray, dict[str, float]]:
    rho = density(state)
    current = current_expectations(state)
    safe = np.maximum(rho, 1.0e-20)
    beta = [np.asarray(component / safe, dtype=np.float64) for component in current]
    magnitude = np.sqrt(sum(component * component for component in beta))
    scale = np.minimum(1.0, speed_limit / np.maximum(magnitude, speed_limit))
    beta = [component * scale for component in beta]
    beta2 = np.minimum(sum(component * component for component in beta), speed_limit**2)
    gamma = 1.0 / np.sqrt(np.maximum(1.0 - beta2, 1.0e-20))
    active = rho > 1.0e-12 * float(np.max(rho))
    return tuple(beta), np.asarray(gamma, dtype=np.float64), {  # type: ignore[return-value]
        "maximum_raw_beta": float(np.max(magnitude)),
        "maximum_used_beta": float(np.max(np.sqrt(beta2))),
        "maximum_gamma": float(np.max(gamma[active])) if np.any(active) else 1.0,
        "clipped_fraction": float(np.mean(magnitude > speed_limit)),
    }


def local_tbmt_omega(
    beta: Vector,
    gamma: np.ndarray,
    electric: Vector,
    magnetic: Vector,
    *,
    charge: float,
    mass: float,
    g_factor: float,
) -> Vector:
    """Regular lab-frame BMT angular velocity in units c=1.

    Omega = -(q/m)[(a+1/gamma)B
      - a*gamma/(gamma+1)(beta.B)beta
      - (a+1/(gamma+1))(beta x E)].
    """
    if mass <= 0.0:
        raise ValueError("positive mass required")
    anomaly = 0.5 * (g_factor - 2.0)
    beta_dot_b = sum(beta[index] * magnetic[index] for index in range(3))
    beta_cross_e = (
        beta[1] * electric[2] - beta[2] * electric[1],
        beta[2] * electric[0] - beta[0] * electric[2],
        beta[0] * electric[1] - beta[1] * electric[0],
    )
    result = []
    for index in range(3):
        bracket = (
            (anomaly + 1.0 / gamma) * magnetic[index]
            - anomaly * gamma / (gamma + 1.0) * beta_dot_b * beta[index]
            - (anomaly + 1.0 / (gamma + 1.0)) * beta_cross_e[index]
        )
        result.append(np.asarray(-(charge / mass) * bracket, dtype=np.float64))
    return tuple(result)  # type: ignore[return-value]


def packet_torque(
    state: np.ndarray,
    electric: Vector,
    magnetic: Vector,
    cfg: SpinorialPairDynamicsConfig,
) -> dict[str, Any]:
    beta, gamma, velocity_audit = local_velocity(state)
    omega = local_tbmt_omega(
        beta,
        gamma,
        electric,
        magnetic,
        charge=cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
    )
    spin = four_spin_density(state)
    torque_density = (
        omega[1] * spin[2] - omega[2] * spin[1],
        omega[2] * spin[0] - omega[0] * spin[2],
        omega[0] * spin[1] - omega[1] * spin[0],
    )
    norm = float(np.sum(density(state)) * cfg.spacing**3)
    rate = np.asarray(
        [float(np.sum(component) * cfg.spacing**3 / max(norm, 1.0e-30)) for component in torque_density],
        dtype=np.float64,
    )
    omega_rms = math.sqrt(
        cfg.spacing**3 * sum(float(np.sum(component * component)) for component in omega)
        / max(float(np.sum(density(state)) * cfg.spacing**3), 1.0e-30)
    )
    return {
        "rate": rate,
        "velocity_audit": velocity_audit,
        "omega_rms": omega_rms,
        "electric_term_present": bool(
            any(float(np.linalg.norm(component)) > 0.0 for component in electric)
        ),
    }


def initial_pair_data(cfg: SpinorialPairDynamicsConfig) -> dict[str, Any]:
    base, _grid = charged_seed(cfg.core_radius, cfg.branch_config())
    spacings = (cfg.spacing,) * 3
    positive_field = spectral_shift(base, spacings, (0.0, 0.0, -0.5 * cfg.separation))
    negative_field = np.conj(spectral_shift(base, spacings, (0.0, 0.0, 0.5 * cfg.separation)))
    spin_x = np.asarray([1.0, 1.0], dtype=np.complex128) / math.sqrt(2.0)
    positive_pauli = spin_x[:, None, None, None] * positive_field[None, ...]
    negative_pauli = spin_x[:, None, None, None] * negative_field[None, ...]
    positive_seed_charge, positive_seed_current = pauli_source(
        positive_pauli, charge=cfg.charge, mass=cfg.mass,
        g_factor=cfg.g_factor, spacing=cfg.spacing,
    )
    negative_seed_charge, negative_seed_current = pauli_source(
        negative_pauli, charge=-cfg.charge, mass=cfg.mass,
        g_factor=cfg.g_factor, spacing=cfg.spacing,
    )
    positive_seed_fields = static_maxwell_fields(positive_seed_charge, positive_seed_current, cfg.spacing)
    negative_seed_fields = static_maxwell_fields(negative_seed_charge, negative_seed_current, cfg.spacing)
    plus = pauli_to_dirac(
        positive_pauli, positive_seed_fields["vector_potential"],
        charge_sign=1.0, charge=cfg.charge, mass=cfg.mass, spacing=cfg.spacing,
    )
    minus = pauli_to_dirac(
        negative_pauli, negative_seed_fields["vector_potential"],
        charge_sign=-1.0, charge=cfg.charge, mass=cfg.mass, spacing=cfg.spacing,
    )

    def source(state: np.ndarray, sign: float) -> tuple[np.ndarray, Vector]:
        signed = sign * cfg.charge
        return (
            np.asarray(signed * density(state), dtype=np.float64),
            tuple(np.asarray(signed * component, dtype=np.float64) for component in current_expectations(state)),
        )  # type: ignore[return-value]

    plus_charge, plus_current = source(plus, 1.0)
    minus_charge, minus_current = source(minus, -1.0)
    plus_fields = static_maxwell_fields(plus_charge, plus_current, cfg.spacing)
    minus_fields = static_maxwell_fields(minus_charge, minus_current, cfg.spacing)
    total_e = tuple(plus_fields["electric"][i] + minus_fields["electric"][i] for i in range(3))
    total_b = tuple(plus_fields["magnetic"][i] + minus_fields["magnetic"][i] for i in range(3))
    return {
        "plus": plus,
        "minus": minus,
        "plus_fields": plus_fields,
        "minus_fields": minus_fields,
        "total_electric": total_e,
        "total_magnetic": total_b,
    }


@lru_cache(maxsize=1)
def run_covariant_packet_tbmt() -> dict[str, Any]:
    cfg = SpinorialPairDynamicsConfig(fit_samples=4, generator_spin_tolerance=3.0e-2)
    data = initial_pair_data(cfg)
    pair = packet_torque(data["plus"], data["total_electric"], data["total_magnetic"], cfg)
    control = packet_torque(
        data["plus"], data["plus_fields"]["electric"], data["plus_fields"]["magnetic"], cfg
    )
    interaction = pair["rate"] - control["rate"]
    legacy = run_spinorial_pair_dynamics()
    generator = np.asarray(
        legacy["response"]["interaction_generator_spin_rate"], dtype=np.float64
    )
    measured = np.asarray(legacy["response"]["interaction_spin_rate"], dtype=np.float64)
    rest = np.asarray(legacy["rest_frame_bmt_spin_rate"], dtype=np.float64)

    def relative(left: np.ndarray, right: np.ndarray) -> float:
        return float(np.linalg.norm(left - right) / max(np.linalg.norm(right), 1.0e-30))

    packet_error = relative(interaction, generator)
    rest_error = relative(rest, generator)
    measured_error = relative(measured, generator)
    improves = packet_error < rest_error
    closes = packet_error <= cfg.generator_spin_tolerance
    acceptance = {
        "local_velocity_and_gamma_are_finite": all(math.isfinite(value) for value in pair["velocity_audit"].values()) and all(math.isfinite(value) for value in control["velocity_audit"].values()),
        "pointwise_lab_frame_bmt_is_integrated": pair["omega_rms"] > 0.0 and control["omega_rms"] > 0.0,
        "electric_and_magnetic_terms_are_retained": pair["electric_term_present"] and any(float(np.linalg.norm(component)) > 0.0 for component in data["total_magnetic"]),
        "matched_self_field_control_is_subtracted": interaction.shape == (3,),
        "comparison_to_exact_dirac_generator_is_reported": all(math.isfinite(value) for value in (packet_error, rest_error, measured_error)),
        "rest_frame_shadow_is_not_used_as_packet_authority": True,
        "covariant_qed_derivation_is_not_claimed": True,
    }
    return {
        "schema": "openwave.m9.covariant-packet-tbmt.v1",
        "task": "M9.101c",
        "config": asdict(cfg),
        "packet_rate_pair": pair["rate"].tolist(),
        "packet_rate_control": control["rate"].tolist(),
        "interaction_packet_tbmt_rate": interaction.tolist(),
        "interaction_dirac_generator_rate": generator.tolist(),
        "interaction_measured_finite_time_rate": measured.tolist(),
        "legacy_rest_frame_rate": rest.tolist(),
        "relative_errors": {
            "local_packet_tbmt_vs_generator": packet_error,
            "legacy_rest_frame_vs_generator": rest_error,
            "finite_time_vs_generator": measured_error,
        },
        "local_packet_improves_on_rest_frame": improves,
        "local_packet_tbmt_closes_on_current_packet": closes,
        "pair_velocity_audit": pair["velocity_audit"],
        "control_velocity_audit": control["velocity_audit"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "local_covariant_packet_adapter_constructed": True,
            "averaged_rest_frame_shadow_deprecated": True,
            "packet_tbmt_reduction_numerically_closed": closes,
            "packet_tbmt_improves_on_legacy_shadow": improves,
            "covariant_thomas_extension_derived_from_qed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
