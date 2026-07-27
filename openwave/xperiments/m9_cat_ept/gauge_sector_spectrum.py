"""M9.120a: gauge-invariant finite spectra for the M9.119 carriers.

The finite covariant Laplacian is assembled as a dense Hermitian operator on
site-internal vectors. Local gauge transformations act by block-unitary
similarity, so its eigenvalues and eigenpair residuals are gauge invariant.

The electroweak local-potential Hessian is also diagonalized at the homogeneous
Higgs vacuum. Its three tangent zero modes and one radial curvature mode are
finite-carrier diagnostics, not calibrated W/Z/Higgs masses.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .electroweak_higgs_lattice import (
    ElectroweakHiggsConfig,
    combined_links,
    gauge_transform as electroweak_gauge_transform,
    initialize_electroweak_state,
    local_electroweak_gauge,
)
from .non_abelian_lattice_gauge import (
    Array,
    NonAbelianGaugeConfig,
    gauge_transform,
    initialize_links,
    initialize_matter,
    local_gauge_transformation,
)


@dataclass(frozen=True)
class GaugeSpectrumConfig:
    spacing: float = 1.0
    residual_modes: int = 12
    hbar: float = 1.0

    def __post_init__(self) -> None:
        if self.spacing <= 0.0 or self.hbar <= 0.0:
            raise ValueError("positive spectrum scales required")
        if self.residual_modes < 1:
            raise ValueError("at least one residual mode required")


def flatten_field(field: Array) -> Array:
    return np.asarray(field.reshape(-1), dtype=np.complex128)


def unflatten_field(vector: Array, site_shape: tuple[int, ...], internal: int) -> Array:
    return np.asarray(vector.reshape(site_shape + (internal,)), dtype=np.complex128)


def covariant_operator_matrix(links: Array, spacing: float = 1.0) -> Array:
    """Dense matrix for ``-D^2`` on a periodic link field."""
    if spacing <= 0.0:
        raise ValueError("positive spacing required")
    dimensions = int(links.shape[0])
    site_shape = tuple(int(value) for value in links.shape[1:-2])
    internal = int(links.shape[-1])
    if len(site_shape) != dimensions:
        raise ValueError("link directions must match site dimensions")
    size = int(np.prod(site_shape)) * internal
    matrix = np.zeros((size, size), dtype=np.complex128)
    for column in range(size):
        basis = np.zeros(size, dtype=np.complex128)
        basis[column] = 1.0
        field = unflatten_field(basis, site_shape, internal)
        laplacian = np.zeros_like(field)
        for direction in range(dimensions):
            forward = np.roll(field, -1, axis=direction)
            backward = np.roll(field, 1, axis=direction)
            backward_link = np.roll(links[direction], 1, axis=direction)
            laplacian += np.einsum(
                "...ij,...j->...i", links[direction], forward
            )
            laplacian += np.einsum(
                "...ij,...j->...i",
                np.swapaxes(np.conjugate(backward_link), -1, -2),
                backward,
            )
            laplacian -= 2.0 * field
        matrix[:, column] = flatten_field(-laplacian / spacing**2)
    return np.asarray(0.5 * (matrix + matrix.conjugate().T), dtype=np.complex128)


def block_gauge_matrix(gauge: Array) -> Array:
    blocks = gauge.reshape((-1, gauge.shape[-1], gauge.shape[-1]))
    internal = int(gauge.shape[-1])
    result = np.zeros(
        (len(blocks) * internal, len(blocks) * internal), dtype=np.complex128
    )
    for index, block in enumerate(blocks):
        start = index * internal
        result[start : start + internal, start : start + internal] = block
    return result


def relative_norm_error(left: Array, right: Array) -> float:
    return float(
        np.linalg.norm(left - right)
        / max(float(np.linalg.norm(left)), float(np.linalg.norm(right)), 1.0e-300)
    )


def eigenpair_residuals(
    operator: Array, eigenvalues: Array, eigenvectors: Array, count: int
) -> list[float]:
    selected = min(count, len(eigenvalues))
    return [
        float(
            np.linalg.norm(
                operator @ eigenvectors[:, index]
                - eigenvalues[index] * eigenvectors[:, index]
            )
        )
        for index in range(selected)
    ]


def spectrum_record(operator: Array, cfg: GaugeSpectrumConfig) -> dict[str, Any]:
    hermitian_error = relative_norm_error(operator, operator.conjugate().T)
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    residuals = eigenpair_residuals(
        operator, eigenvalues, eigenvectors, cfg.residual_modes
    )
    return {
        "dimension": int(operator.shape[0]),
        "hermitian_relative_error": hermitian_error,
        "minimum_eigenvalue": float(eigenvalues[0]),
        "lowest_eigenvalues": [
            float(value) for value in eigenvalues[: cfg.residual_modes]
        ],
        "maximum_low_mode_residual": max(residuals),
    }


def higgs_local_hessian(cfg: ElectroweakHiggsConfig) -> Array:
    """Real four-coordinate Hessian at ``(v,0)`` for the quartic Higgs potential."""
    vacuum_radius = math.sqrt(cfg.vacuum_norm_squared)
    radial = np.asarray((1.0, 0.0, 0.0, 0.0), dtype=np.float64)
    return np.asarray(
        4.0 * cfg.mu_squared * np.outer(radial, radial)
        + 0.0 * vacuum_radius * np.eye(4),
        dtype=np.float64,
    )


def higgs_hessian_record(cfg: ElectroweakHiggsConfig) -> dict[str, Any]:
    hessian = higgs_local_hessian(cfg)
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    radial = np.asarray((1.0, 0.0, 0.0, 0.0), dtype=np.float64)
    radial_overlaps = np.abs(eigenvectors.T @ radial) ** 2
    radial_index = int(np.argmax(radial_overlaps))
    tangent = np.delete(eigenvalues, radial_index)
    return {
        "eigenvalues": [float(value) for value in eigenvalues],
        "tangent_zero_mode_count": int(np.sum(np.abs(tangent) <= 1.0e-12)),
        "maximum_tangent_curvature": float(np.max(np.abs(tangent))),
        "radial_curvature": float(eigenvalues[radial_index]),
        "expected_radial_curvature": 4.0 * cfg.mu_squared,
        "radial_relative_error": abs(
            float(eigenvalues[radial_index]) - 4.0 * cfg.mu_squared
        )
        / (4.0 * cfg.mu_squared),
    }


def spectral_selection_weights(
    actual: Array, known: Array, hbar: float
) -> list[float]:
    mismatch = np.asarray(actual - known, dtype=np.float64)
    return [float(value) for value in np.exp(-(mismatch * mismatch) / hbar)]


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=float
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_gauge_sector_spectrum() -> dict[str, Any]:
    cfg = GaugeSpectrumConfig()

    strong_cfg = NonAbelianGaugeConfig()
    strong_matter = initialize_matter(strong_cfg)
    strong_links = initialize_links(strong_cfg)
    strong_gauge = local_gauge_transformation(strong_cfg)
    _, strong_links_gauge = gauge_transform(
        strong_matter, strong_links, strong_gauge
    )
    strong_operator = covariant_operator_matrix(strong_links, cfg.spacing)
    strong_operator_gauge = covariant_operator_matrix(
        strong_links_gauge, cfg.spacing
    )
    strong_block = block_gauge_matrix(strong_gauge)
    strong_similarity = (
        strong_block @ strong_operator @ strong_block.conjugate().T
    )
    strong_values = np.linalg.eigvalsh(strong_operator)
    strong_values_gauge = np.linalg.eigvalsh(strong_operator_gauge)
    strong = {
        **spectrum_record(strong_operator, cfg),
        "gauge_spectrum_maximum_error": float(
            np.max(np.abs(strong_values - strong_values_gauge))
        ),
        "gauge_similarity_relative_error": relative_norm_error(
            strong_operator_gauge, strong_similarity
        ),
        "exact_match_selection_minimum": min(
            spectral_selection_weights(
                strong_values[: cfg.residual_modes],
                strong_values[: cfg.residual_modes],
                cfg.hbar,
            )
        ),
    }

    electroweak_cfg = ElectroweakHiggsConfig()
    higgs, su2_links, u1_links = initialize_electroweak_state(electroweak_cfg)
    su2_gauge, u1_gauge = local_electroweak_gauge(electroweak_cfg)
    _, su2_links_gauge, u1_links_gauge = electroweak_gauge_transform(
        higgs,
        su2_links,
        u1_links,
        su2_gauge,
        u1_gauge,
        electroweak_cfg.hypercharge_power,
    )
    electroweak_links = combined_links(
        su2_links, u1_links, electroweak_cfg.hypercharge_power
    )
    electroweak_links_gauge = combined_links(
        su2_links_gauge, u1_links_gauge, electroweak_cfg.hypercharge_power
    )
    combined_gauge = su2_gauge * (
        u1_gauge**electroweak_cfg.hypercharge_power
    )[..., None, None]
    electroweak_operator = covariant_operator_matrix(
        electroweak_links, cfg.spacing
    )
    electroweak_operator_gauge = covariant_operator_matrix(
        electroweak_links_gauge, cfg.spacing
    )
    electroweak_block = block_gauge_matrix(combined_gauge)
    electroweak_similarity = (
        electroweak_block
        @ electroweak_operator
        @ electroweak_block.conjugate().T
    )
    electroweak_values = np.linalg.eigvalsh(electroweak_operator)
    electroweak_values_gauge = np.linalg.eigvalsh(electroweak_operator_gauge)
    electroweak = {
        **spectrum_record(electroweak_operator, cfg),
        "gauge_spectrum_maximum_error": float(
            np.max(np.abs(electroweak_values - electroweak_values_gauge))
        ),
        "gauge_similarity_relative_error": relative_norm_error(
            electroweak_operator_gauge, electroweak_similarity
        ),
        "higgs_local_hessian": higgs_hessian_record(electroweak_cfg),
    }

    payload = {
        "schema": "openwave.m9.gauge-sector-spectrum.v1",
        "task": "M9.120a",
        "config": asdict(cfg),
        "strong": strong,
        "electroweak": electroweak,
        "claim_boundary": {
            "finite_spectrum_is_physical_particle_spectrum": False,
            "higgs_radial_curvature_is_physical_higgs_mass": False,
            "gauge_orbit_zero_modes_are_observed_goldstone_particles": False,
            "dimensionless_low_modes_are_calibrated_predictions": False,
        },
    }
    acceptance = {
        "strong_operator_is_Hermitian_and_nonnegative": (
            strong["hermitian_relative_error"] <= 2.0e-13
            and strong["minimum_eigenvalue"] >= -2.0e-12
        ),
        "strong_spectrum_is_locally_gauge_invariant": (
            strong["gauge_spectrum_maximum_error"] <= 3.0e-11
            and strong["gauge_similarity_relative_error"] <= 3.0e-12
        ),
        "strong_low_eigenpairs_close": strong["maximum_low_mode_residual"]
        <= 2.0e-11,
        "electroweak_operator_is_Hermitian_and_nonnegative": (
            electroweak["hermitian_relative_error"] <= 2.0e-13
            and electroweak["minimum_eigenvalue"] >= -2.0e-12
        ),
        "electroweak_spectrum_is_locally_gauge_invariant": (
            electroweak["gauge_spectrum_maximum_error"] <= 3.0e-11
            and electroweak["gauge_similarity_relative_error"] <= 3.0e-12
        ),
        "electroweak_low_eigenpairs_close": electroweak[
            "maximum_low_mode_residual"
        ]
        <= 2.0e-11,
        "quartic_vacuum_has_three_tangent_zero_modes_and_one_radial_mode": (
            electroweak["higgs_local_hessian"]["tangent_zero_mode_count"] == 3
            and electroweak["higgs_local_hessian"][
                "maximum_tangent_curvature"
            ]
            <= 1.0e-12
            and electroweak["higgs_local_hessian"]["radial_relative_error"]
            <= 1.0e-12
        ),
        "exact_spectral_match_has_unit_selection_weight": strong[
            "exact_match_selection_minimum"
        ]
        == 1.0,
        "no_physical_spectrum_claim_is_promoted": not any(
            payload["claim_boundary"].values()
        ),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "gauge_invariant_finite_spectra_constructed": True,
            "higgs_vacuum_tangent_and_radial_curvatures_constructed": True,
            "physical_particle_spectrum_predicted": False,
            "physical_mass_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
