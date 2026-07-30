"""M11.2 continuum/infinite-mode Liouville tensor of the M11.1 soliton."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

from .pointwise_soliton_carrier_m111 import (
    PointwiseSolitonConfig,
    construct_pointwise_soliton,
)

MILESTONE = "M11.2"
SCHEMA = "openwave.m11.liouville-soliton-tensor.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorem": "leftPointwise_rightPointwise_commute",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorem": "kernelMode_infinite",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorem": "kernelOccupationBasis_particleNumber",
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
        "sha": "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
        "theorem": "continuumKernelNormSq_nonneg",
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class LiouvilleTensorConfig:
    mode_count: int = 96
    refinement_modes: tuple[int, ...] = (16, 32, 64, 96)
    particle_number: int = 3

    def validate(self, grid_points: int) -> None:
        if self.mode_count < 8 or self.mode_count > grid_points:
            raise ValueError("mode_count must fit inside the pointwise grid")
        if any(mode < 4 or mode > self.mode_count for mode in self.refinement_modes):
            raise ValueError("refinement modes must lie in [4, mode_count]")
        if tuple(sorted(self.refinement_modes)) != self.refinement_modes:
            raise ValueError("refinement modes must be increasing")
        if self.particle_number < 0:
            raise ValueError("particle number must be nonnegative")


@dataclass(frozen=True)
class LiouvilleTensorState:
    config: LiouvilleTensorConfig
    full_amplitudes: np.ndarray
    selected_indices: np.ndarray
    amplitudes: np.ndarray
    density_matrix: np.ndarray
    retained_probability: float


def _centered_indices(length: int, count: int) -> np.ndarray:
    shifted = np.arange(length) - length // 2
    order = np.argsort(np.abs(shifted), kind="stable")
    return np.sort(order[:count])


def construct_liouville_tensor(
    config: LiouvilleTensorConfig | None = None,
    soliton_config: PointwiseSolitonConfig | None = None,
) -> LiouvilleTensorState:
    cfg = LiouvilleTensorConfig() if config is None else config
    soliton = construct_pointwise_soliton(soliton_config)
    cfg.validate(soliton.config.grid_points)
    coordinate_vector = np.asarray(soliton.psi * np.sqrt(soliton.dx), dtype=np.complex128)
    coordinate_vector /= np.linalg.norm(coordinate_vector)
    full = np.fft.fftshift(np.fft.fft(coordinate_vector, norm="ortho"))
    indices = _centered_indices(full.size, cfg.mode_count)
    raw = full[indices]
    retained = float(np.vdot(raw, raw).real)
    amplitudes = np.asarray(raw / np.linalg.norm(raw), dtype=np.complex128)
    density = np.outer(amplitudes, np.conj(amplitudes))
    return LiouvilleTensorState(cfg, full, indices, amplitudes, density, retained)


def left_pointwise_action(multiplier: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return np.asarray(multiplier[:, None] * kernel, dtype=np.complex128)


def right_pointwise_action(multiplier: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return np.asarray(kernel * multiplier[None, :], dtype=np.complex128)


def fixed_particle_occupation(mode_count: int, particle_number: int) -> np.ndarray:
    occupation = np.zeros(mode_count, dtype=np.int64)
    for index in range(particle_number):
        occupation[index % mode_count] += 1
    return occupation


def _retained_probability(full: np.ndarray, count: int) -> float:
    indices = _centered_indices(full.size, count)
    values = full[indices]
    return float(np.vdot(values, values).real)


def canonical_payload(config: LiouvilleTensorConfig | None = None) -> dict[str, Any]:
    cfg = LiouvilleTensorConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M11",
        "milestone": MILESTONE,
        "configuration": asdict(cfg),
        "study_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "liouville_soliton_tensor_m112:run_liouville_tensor_study"
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


def run_liouville_tensor_study(
    config: LiouvilleTensorConfig | None = None,
) -> dict[str, Any]:
    state = construct_liouville_tensor(config)
    rho = state.density_matrix
    eigenvalues = np.linalg.eigvalsh(rho)
    multiplier_left = np.exp(0.013j * np.arange(rho.shape[0]))
    multiplier_right = np.exp(-0.017j * np.arange(rho.shape[0]))
    left_right = left_pointwise_action(
        multiplier_left, right_pointwise_action(multiplier_right, rho)
    )
    right_left = right_pointwise_action(
        multiplier_right, left_pointwise_action(multiplier_left, rho)
    )
    occupation = fixed_particle_occupation(
        state.config.mode_count, state.config.particle_number
    )
    retained = [
        _retained_probability(state.full_amplitudes, count)
        for count in state.config.refinement_modes
    ]
    diagnostics = {
        "trace_error": abs(np.trace(rho) - 1.0),
        "hermiticity_error": float(np.linalg.norm(rho - rho.conj().T)),
        "purity_error": float(np.linalg.norm(rho @ rho - rho)),
        "minimum_eigenvalue": float(eigenvalues.min()),
        "largest_eigenvalue_error": abs(float(eigenvalues.max()) - 1.0),
        "pointwise_action_commutator": float(np.linalg.norm(left_right - right_left)),
        "particle_number": int(np.sum(occupation)),
        "retained_probability": state.retained_probability,
        "refinement_retained_probability": retained,
        "continuum_kernel_norm_sq": float(np.vdot(rho, rho).real),
    }
    acceptance = {
        "trace_one": diagnostics["trace_error"] < 5.0e-13,
        "hermitian": diagnostics["hermiticity_error"] < 5.0e-13,
        "rank_one_pure": diagnostics["purity_error"] < 5.0e-13,
        "positive_semidefinite": diagnostics["minimum_eigenvalue"] > -5.0e-13,
        "one_unit_eigenvalue": diagnostics["largest_eigenvalue_error"] < 5.0e-13,
        "pointwise_actions_commute": diagnostics["pointwise_action_commutator"] < 5.0e-13,
        "fixed_particle_number": diagnostics["particle_number"] == state.config.particle_number,
        "mode_refinement_monotone": all(
            later + 1.0e-15 >= earlier for earlier, later in zip(retained, retained[1:])
        ),
        "cutoff_retains_signal": diagnostics["retained_probability"] > 0.999,
    }
    payload = canonical_payload(state.config)
    return {
        **payload,
        "task": "M11.2",
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
    }
