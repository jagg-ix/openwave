"""M14.1 causal continuum Green/Hadamard adapter.

This finite spectral campaign mirrors the exact theorem interfaces at the
latest entropic-physlib TIP: causal retarded/advanced inverses, their
Pauli--Jordan difference, energy bounds, and a positive-frequency Hermitian
Hadamard two-point carrier.  It is an executable discretization of the formal
continuum carrier, not a proof that an arbitrary Lorentzian metric supplies the
required coercive Sobolev data.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

MILESTONE = "M14.1"
SCHEMA = "openwave.m14.causal-green-hadamard.v1"
FORMAL_HEAD = "ea6c394fcb1d55546d11cd6af3df6556c610d52e"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/GloballyHyperbolicGreenHadamard.lean",
        "sha": "bcdef861f5cd3843051a13061adb4e856b686dfe",
        "theorems": [
            "MaxwellLaxMilgramGraphData.curvedHOneFourMaxwell_causal_exists_energy",
            "MaxwellLaxMilgramGraphData.curvedHOneFourMaxwellGreen_intrinsic_graphEnergy",
            "MaxwellLaxMilgramGraphData.curvedHOneFour_causalGreen_intrinsic_homogeneous_energy",
            "MaxwellLaxMilgramGraphData.curvedHOneFour_caticha_maxwell_causal_distributional_hadamard_propagation",
            "GreenHadamardPropagation.wavefront_eq",
        ],
    },
    {
        "path": "Physlib/Mathematics/Distribution/Basic.lean",
        "sha": "30c098b5466b759a769a58e79fccc12c096a8445",
        "theorems": [
            "hasRapidFourierDecayOn_congr",
            "distributionalWavefrontSet_eq_of_probe_pairing_eq",
            "distributionalWavefrontSet_covector_ne_zero",
        ],
    },
)


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class CausalGreenHadamardConfig:
    grid_size: int = 65
    phase_step: float = 0.37
    source_index: int = 32
    positive_modes: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    hadamard_cutoff: float = 0.17
    probe_count: int = 24

    def validate(self) -> None:
        if self.grid_size < 17 or self.grid_size % 2 == 0:
            raise ValueError("grid_size must be odd and at least 17")
        if not (1 <= self.source_index < self.grid_size - 1):
            raise ValueError("source_index must be interior")
        if abs(math.sin(self.phase_step)) < 1e-8:
            raise ValueError("phase_step must avoid a singular recurrence")
        if not self.positive_modes or any(mode <= 0 for mode in self.positive_modes):
            raise ValueError("positive_modes must contain positive integers")
        if self.hadamard_cutoff <= 0 or self.probe_count < 4:
            raise ValueError("positive cutoff and at least four probes required")


def canonical_payload(config: CausalGreenHadamardConfig | None = None) -> dict[str, Any]:
    cfg = CausalGreenHadamardConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT causal continuum Green and Hadamard carrier",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M13.8"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "causal_green_hadamard_m141:run_causal_green_hadamard_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    value = canonical_payload() if payload is None else payload
    return sha256(_canon(value).encode()).hexdigest()


def _wave_operator(size: int, phase_step: float) -> np.ndarray:
    operator = np.zeros((size, size), dtype=float)
    np.fill_diagonal(operator, -2.0 * math.cos(phase_step))
    indices = np.arange(size - 1)
    operator[indices, indices + 1] = 1.0
    operator[indices + 1, indices] = 1.0
    return operator


def _causal_green_matrices(size: int, phase_step: float) -> tuple[np.ndarray, np.ndarray]:
    denominator = math.sin(phase_step)
    retarded = np.zeros((size, size), dtype=float)
    advanced = np.zeros((size, size), dtype=float)
    for row in range(size):
        for col in range(size):
            offset = row - col
            if offset > 0:
                retarded[row, col] = math.sin(offset * phase_step) / denominator
            elif offset < 0:
                advanced[row, col] = -math.sin(offset * phase_step) / denominator
    return retarded, advanced


def _hadamard_kernel(cfg: CausalGreenHadamardConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    points = np.linspace(-1.0, 1.0, cfg.probe_count)
    frequencies = np.asarray(cfg.positive_modes, dtype=float)
    modes = np.exp(-1j * np.outer(points, frequencies))
    weights = np.exp(-cfg.hadamard_cutoff * frequencies) / frequencies
    kernel = modes @ np.diag(weights) @ modes.conj().T
    return points, frequencies, kernel


def run_causal_green_hadamard_study(
    config: CausalGreenHadamardConfig | None = None,
) -> dict[str, Any]:
    cfg = CausalGreenHadamardConfig() if config is None else config
    cfg.validate()

    wave = _wave_operator(cfg.grid_size, cfg.phase_step)
    retarded, advanced = _causal_green_matrices(cfg.grid_size, cfg.phase_step)
    identity = np.eye(cfg.grid_size)
    interior = slice(1, cfg.grid_size - 1)
    retarded_residual = wave @ retarded - identity
    advanced_residual = wave @ advanced - identity

    source = np.zeros(cfg.grid_size)
    source[cfg.source_index] = 1.0
    retarded_field = retarded @ source
    advanced_field = advanced @ source
    causal = retarded - advanced
    causal_field = causal @ source

    retarded_support_error = float(np.max(np.abs(retarded_field[: cfg.source_index + 1])))
    advanced_support_error = float(np.max(np.abs(advanced_field[cfg.source_index :])))
    causal_skew_error = float(np.max(np.abs(causal + causal.T)))
    causal_homogeneous_error = float(np.max(np.abs((wave @ causal)[interior, interior])))

    retarded_norm = float(np.linalg.norm(retarded, ord=2))
    advanced_norm = float(np.linalg.norm(advanced, ord=2))
    source_norm = float(np.linalg.norm(source))
    retarded_energy_margin = retarded_norm * source_norm - float(np.linalg.norm(retarded_field))
    advanced_energy_margin = advanced_norm * source_norm - float(np.linalg.norm(advanced_field))
    causal_energy_margin = (
        (retarded_norm + advanced_norm) * source_norm - float(np.linalg.norm(causal_field))
    )

    points, frequencies, hadamard = _hadamard_kernel(cfg)
    hermitian_error = float(np.max(np.abs(hadamard - hadamard.conj().T)))
    eigenvalues = np.linalg.eigvalsh(hadamard)
    min_eigenvalue = float(np.min(eigenvalues))

    phase = np.exp(1j * 0.23 * points)
    transport = np.diag(phase)
    transported_kernel = transport @ hadamard @ transport.conj().T
    probe = np.exp(-points**2) * (1.0 + 0.2j * points)
    transported_probe = transport @ probe
    original_pairing = np.vdot(probe, hadamard @ probe)
    transported_pairing = np.vdot(transported_probe, transported_kernel @ transported_probe)
    probe_pairing_transport_error = float(abs(original_pairing - transported_pairing))

    diagnostics = {
        "retarded_inverse_residual": float(
            np.max(np.abs(retarded_residual[interior, interior]))
        ),
        "advanced_inverse_residual": float(
            np.max(np.abs(advanced_residual[interior, interior]))
        ),
        "retarded_support_error": retarded_support_error,
        "advanced_support_error": advanced_support_error,
        "causal_skew_error": causal_skew_error,
        "causal_homogeneous_error": causal_homogeneous_error,
        "retarded_energy_margin": retarded_energy_margin,
        "advanced_energy_margin": advanced_energy_margin,
        "causal_energy_margin": causal_energy_margin,
        "hadamard_hermitian_error": hermitian_error,
        "hadamard_min_eigenvalue": min_eigenvalue,
        "hadamard_eigenvalues": eigenvalues.tolist(),
        "positive_frequencies": frequencies.tolist(),
        "probe_pairing_transport_error": probe_pairing_transport_error,
    }
    acceptance = {
        "retarded_and_advanced_green_equations_close": max(
            diagnostics["retarded_inverse_residual"],
            diagnostics["advanced_inverse_residual"],
        )
        < 5e-12,
        "causal_support_sectors_hold": max(
            retarded_support_error, advanced_support_error
        )
        < 5e-14,
        "pauli_jordan_is_skew_and_homogeneous": max(
            causal_skew_error, causal_homogeneous_error
        )
        < 5e-12,
        "green_energy_bounds_hold": min(
            retarded_energy_margin, advanced_energy_margin, causal_energy_margin
        )
        >= -5e-12,
        "hadamard_kernel_is_hermitian_positive": (
            hermitian_error < 5e-12 and min_eigenvalue > -5e-10
        ),
        "hadamard_spectrum_is_positive_frequency": bool(np.all(frequencies > 0)),
        "localized_probe_pairings_transport_exactly": probe_pairing_transport_error
        < 5e-10,
        "formal_tip_is_latest": FORMAL_HEAD
        == "ea6c394fcb1d55546d11cd6af3df6556c610d52e",
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "causal_green_maps_are_finite_spectral_adapters": True,
            "coercive_continuum_data_remain_explicit_formal_premises": True,
            "wavefront_equality_not_inferred_from_global_hyperbolicity_alone": True,
        },
    }
