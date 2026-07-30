"""M11.5 coupled soliton-center dynamics, decoherence, and model registration."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .liouville_soliton_tensor_m112 import construct_liouville_tensor, run_liouville_tensor_study
from .optional_qcd_coupling_m114 import run_optional_qcd_study
from .pointwise_soliton_carrier_m111 import run_pointwise_soliton_study
from .qdo_lj_atm_interaction_m113 import (
    QDOLJATMConfig,
    lj_potential,
    qdo_c9,
    run_qdo_lj_atm_study,
    trimer_atm_energy,
)

MILESTONE = "M11.5"
SCHEMA = "openwave.m11.coupled-dynamics-registration.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticMildFlow.lean",
        "sha": "82a89eabf1179eff2373b2f005317e63cbd62cba",
        "theorem": "target_tendsto_and_normalized_of_minimizing_energySplit",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
        "sha": "fb47b98296a771eee44570ce42b5c2ab03d450a3",
        "theorem": "exists_constrained_hOne_minimizer_of_bounded_minimizingSequence",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorem": "spacePointwiseKernelOperator_apply_ae",
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class CoupledDynamicsConfig:
    steps: int = 160
    timestep: float = 2.0e-3
    mass: float = 1.0
    entropic_gamma: float = 0.035
    hbar: float = 1.0
    finite_difference_step: float = 2.0e-5
    decoherence_strength: float = 0.8

    def validate(self) -> None:
        if self.steps < 20 or self.timestep <= 0 or self.mass <= 0:
            raise ValueError("positive integration settings required")
        if self.entropic_gamma < 0 or self.hbar <= 0:
            raise ValueError("nonnegative gamma and positive hbar required")
        if self.finite_difference_step <= 0:
            raise ValueError("positive finite-difference step required")


def initial_centers() -> np.ndarray:
    return np.asarray(
        [[-0.85, -0.32], [0.82, -0.28], [0.05, 1.04]], dtype=np.float64
    )


def total_interaction_energy(points: np.ndarray, qdo: QDOLJATMConfig) -> float:
    pair = 0.0
    for i in range(points.shape[0]):
        for j in range(i + 1, points.shape[0]):
            distance = float(np.linalg.norm(points[i] - points[j]))
            pair += lj_potential(
                qdo.epsilon,
                qdo.equilibrium_distance,
                distance,
                qdo.repulsive_exponent,
            )
    three = trimer_atm_energy(points, qdo_c9(qdo.alpha1, qdo.hbar_omega))
    return float(pair + three)


def numerical_forces(points: np.ndarray, qdo: QDOLJATMConfig, step: float) -> np.ndarray:
    forces = np.zeros_like(points)
    for particle in range(points.shape[0]):
        for axis in range(points.shape[1]):
            plus = points.copy()
            minus = points.copy()
            plus[particle, axis] += step
            minus[particle, axis] -= step
            derivative = (
                total_interaction_energy(plus, qdo)
                - total_interaction_energy(minus, qdo)
            ) / (2.0 * step)
            forces[particle, axis] = -derivative
    return forces


def velocity_verlet(
    config: CoupledDynamicsConfig,
    qdo: QDOLJATMConfig,
    damping: float,
) -> dict[str, Any]:
    points = initial_centers()
    velocities = np.asarray([[0.0, 0.08], [-0.03, -0.04], [0.03, -0.04]], dtype=np.float64)
    velocities -= velocities.mean(axis=0)
    force = numerical_forces(points, qdo, config.finite_difference_step)
    energies: list[float] = []
    entropic_times: list[float] = [0.0]
    for _ in range(config.steps):
        velocities += 0.5 * config.timestep * force / config.mass
        points += config.timestep * velocities
        new_force = numerical_forces(points, qdo, config.finite_difference_step)
        velocities += 0.5 * config.timestep * new_force / config.mass
        if damping > 0.0:
            kinetic_before = 0.5 * config.mass * float(np.sum(velocities**2))
            velocities *= math.exp(-damping * config.timestep)
            kinetic_after = 0.5 * config.mass * float(np.sum(velocities**2))
            entropic_times.append(
                entropic_times[-1] + max(0.0, kinetic_before - kinetic_after) / config.hbar
            )
        else:
            entropic_times.append(entropic_times[-1])
        force = new_force
        kinetic = 0.5 * config.mass * float(np.sum(velocities**2))
        energies.append(kinetic + total_interaction_energy(points, qdo))
    return {
        "points": points,
        "velocities": velocities,
        "energies": np.asarray(energies),
        "entropic_times": np.asarray(entropic_times),
    }


def dephased_density(strength: float) -> tuple[np.ndarray, np.ndarray]:
    state = construct_liouville_tensor()
    rho = state.density_matrix
    indices = np.arange(rho.shape[0], dtype=np.float64)
    distance_sq = (indices[:, None] - indices[None, :]) ** 2 / rho.shape[0] ** 2
    dephased = rho * np.exp(-strength * distance_sq)
    dephased /= np.trace(dephased)
    return rho, np.asarray(dephased, dtype=np.complex128)


def offdiagonal_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix - np.diag(np.diag(matrix))))


def canonical_payload(config: CoupledDynamicsConfig | None = None) -> dict[str, Any]:
    cfg = CoupledDynamicsConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M11",
        "milestone": MILESTONE,
        "model": "CAT/EPT pointwise soliton--Liouville--QDO particle model",
        "configuration": asdict(cfg),
        "lineage": ["M11.1", "M11.2", "M11.3", "M11.4", "M11.5"],
        "study_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "coupled_dynamics_registration_m115:run_m11_model_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


def run_m11_model_study(config: CoupledDynamicsConfig | None = None) -> dict[str, Any]:
    cfg = CoupledDynamicsConfig() if config is None else config
    cfg.validate()
    qdo_cfg = QDOLJATMConfig()
    conservative = velocity_verlet(cfg, qdo_cfg, damping=0.0)
    dissipative = velocity_verlet(cfg, qdo_cfg, damping=cfg.entropic_gamma)
    conservative_energies = conservative["energies"]
    dissipative_energies = dissipative["energies"]
    initial_energy_scale = max(abs(float(conservative_energies[0])), 1.0)
    conservative_drift = float(
        np.max(np.abs(conservative_energies - conservative_energies[0])) / initial_energy_scale
    )
    entropic = dissipative["entropic_times"]
    rho, dephased = dephased_density(cfg.decoherence_strength)
    dephased_eigenvalues = np.linalg.eigvalsh(dephased)
    substudies = {
        "pointwise": run_pointwise_soliton_study(),
        "liouville": run_liouville_tensor_study(),
        "qdo_lj_atm": run_qdo_lj_atm_study(qdo_cfg),
        "optional_qcd": run_optional_qcd_study(),
    }
    diagnostics = {
        "conservative_relative_energy_drift": conservative_drift,
        "dissipative_energy_change": float(dissipative_energies[-1] - dissipative_energies[0]),
        "final_entropic_time": float(entropic[-1]),
        "minimum_entropic_increment": float(np.min(np.diff(entropic))),
        "dephased_trace_error": abs(np.trace(dephased) - 1.0),
        "dephased_hermiticity_error": float(np.linalg.norm(dephased - dephased.conj().T)),
        "dephased_minimum_eigenvalue": float(dephased_eigenvalues.min()),
        "offdiagonal_reduction": offdiagonal_norm(rho) - offdiagonal_norm(dephased),
        "minimum_final_pair_distance": float(
            min(
                np.linalg.norm(dissipative["points"][i] - dissipative["points"][j])
                for i in range(3)
                for j in range(i + 1, 3)
            )
        ),
        "substudies_passed": {name: bool(result["passed"]) for name, result in substudies.items()},
    }
    acceptance = {
        "all_prior_layers_pass": all(diagnostics["substudies_passed"].values()),
        "conservative_verlet_is_stable": diagnostics["conservative_relative_energy_drift"] < 2.0e-5,
        "dissipation_lowers_energy": diagnostics["dissipative_energy_change"] < 0.0,
        "entropic_time_is_monotone": diagnostics["minimum_entropic_increment"] >= -1.0e-15,
        "entropic_time_advances": diagnostics["final_entropic_time"] > 0.0,
        "dephased_tensor_trace_one": diagnostics["dephased_trace_error"] < 5.0e-13,
        "dephased_tensor_hermitian": diagnostics["dephased_hermiticity_error"] < 5.0e-13,
        "dephased_tensor_positive": diagnostics["dephased_minimum_eigenvalue"] > -5.0e-13,
        "environment_reduces_interference": diagnostics["offdiagonal_reduction"] > 0.0,
        "centers_avoid_collision": diagnostics["minimum_final_pair_distance"] > 0.5,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M11.5",
        "diagnostics": diagnostics,
        "substudy_fingerprints": {
            name: result["fingerprint"] for name, result in substudies.items()
        },
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "m11_registered_as_separate_model": True,
            "pointwise_and_infinite_mode_layers_are_distinct": True,
            "qdo_coefficients_are_not_independently_floated": True,
            "qcd_sector_is_optional": True,
        },
    }
