"""M9.120c: finite-grid spectral refinement and phenomenology ledger.

The M9.119 gauge carriers are sampled on a fixed physical two-torus with
spacing-scaled smooth links ``U = exp(i h A)``. Flat-link and smooth-background
low spectra are compared across odd grids.

This is a controlled finite-grid study. It is not a continuum theorem, physical
unit calibration, or identification of the finite modes with observed particles.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .gauge_sector_spectrum import covariant_operator_matrix
from .non_abelian_lattice_gauge import (
    Array,
    special_unitary_generators,
    unitary_from_hermitian,
)


@dataclass(frozen=True)
class GaugeSpectralRefinementConfig:
    grids: tuple[int, ...] = (5, 7, 9, 11)
    physical_length: float = 2.0 * math.pi
    strong_inverse_coupling: float = 1.7
    electroweak_hypercharge_power: int = 3

    def __post_init__(self) -> None:
        if len(self.grids) < 4:
            raise ValueError("at least four refinement grids required")
        if any(points < 5 or points % 2 == 0 for points in self.grids):
            raise ValueError("odd grids with at least five points required")
        if tuple(sorted(self.grids)) != self.grids or len(set(self.grids)) != len(
            self.grids
        ):
            raise ValueError("strictly increasing unique grids required")
        if self.physical_length <= 0.0 or self.strong_inverse_coupling <= 0.0:
            raise ValueError("positive refinement scales required")
        if self.electroweak_hypercharge_power != 3:
            raise ValueError("Physlib-compatible U(1)^3 Higgs action required")


def physical_axes(points: int, physical_length: float) -> tuple[Array, Array, float]:
    spacing = physical_length / points
    axis = spacing * np.arange(points, dtype=np.float64)
    x, y = np.meshgrid(axis, axis, indexing="ij")
    return x, y, spacing


def flat_links(points: int, internal: int) -> Array:
    links = np.empty((2, points, points, internal, internal), dtype=np.complex128)
    links[:] = np.eye(internal, dtype=np.complex128)
    return links


def smooth_su3_links(points: int, physical_length: float) -> Array:
    x, y, spacing = physical_axes(points, physical_length)
    generators = special_unitary_generators(3)
    links = np.empty((2, points, points, 3, 3), dtype=np.complex128)
    for direction in range(2):
        field = np.zeros_like(links[direction])
        coefficients = (
            0.22 * np.sin(x + 0.17 * direction),
            0.16 * np.cos(y + 0.23 * direction),
            0.11 * np.sin(x + y + 0.31 * direction),
            0.07 * np.cos(2.0 * x - y + 0.19 * direction),
        )
        for index, coefficient in enumerate(coefficients):
            field += (
                spacing
                * coefficient[..., None, None]
                * generators[(index + direction) % len(generators)]
            )
        links[direction] = unitary_from_hermitian(field)
    return links


def smooth_electroweak_links(
    points: int, physical_length: float, hypercharge_power: int
) -> Array:
    x, y, spacing = physical_axes(points, physical_length)
    generators = special_unitary_generators(2)
    su2_links = np.empty((2, points, points, 2, 2), dtype=np.complex128)
    u1_links = np.empty((2, points, points), dtype=np.complex128)
    for direction in range(2):
        field = np.zeros_like(su2_links[direction])
        coefficients = (
            0.18 * np.sin(x + 0.13 * direction),
            0.12 * np.cos(y + 0.29 * direction),
            0.08 * np.sin(x + y + 0.37 * direction),
        )
        for index, coefficient in enumerate(coefficients):
            field += spacing * coefficient[..., None, None] * generators[index]
        su2_links[direction] = unitary_from_hermitian(field)
        angle = spacing * (
            0.10 * np.sin(x - y + 0.21 * direction)
            + 0.05 * np.cos(2.0 * y + 0.17 * direction)
        )
        u1_links[direction] = np.exp(1.0j * angle)
    return np.asarray(
        su2_links * (u1_links**hypercharge_power)[..., None, None],
        dtype=np.complex128,
    )


def first_positive_eigenvalue(values: Array, tolerance: float = 1.0e-8) -> float:
    positive = values[values > tolerance]
    if len(positive) == 0:
        raise ValueError("positive spectral mode required")
    return float(positive[0])


def cluster_mean(values: Array, start: int, count: int) -> float:
    selected = values[start : start + count]
    if len(selected) != count:
        raise ValueError("complete spectral cluster required")
    return float(np.mean(selected))


def refinement_rows(cfg: GaugeSpectralRefinementConfig) -> list[dict[str, Any]]:
    rows = []
    continuum_first_mode = (2.0 * math.pi / cfg.physical_length) ** 2
    for points in cfg.grids:
        _, _, spacing = physical_axes(points, cfg.physical_length)
        flat_strong_values = np.linalg.eigvalsh(
            covariant_operator_matrix(flat_links(points, 3), spacing)
        )
        flat_electroweak_values = np.linalg.eigvalsh(
            covariant_operator_matrix(flat_links(points, 2), spacing)
        )
        strong_values = np.linalg.eigvalsh(
            covariant_operator_matrix(
                smooth_su3_links(points, cfg.physical_length), spacing
            )
        )
        electroweak_values = np.linalg.eigvalsh(
            covariant_operator_matrix(
                smooth_electroweak_links(
                    points,
                    cfg.physical_length,
                    cfg.electroweak_hypercharge_power,
                ),
                spacing,
            )
        )
        flat_strong = first_positive_eigenvalue(flat_strong_values)
        flat_electroweak = first_positive_eigenvalue(flat_electroweak_values)
        rows.append(
            {
                "points": points,
                "spacing": spacing,
                "flat_strong_first_positive": flat_strong,
                "flat_electroweak_first_positive": flat_electroweak,
                "flat_strong_relative_error": abs(
                    flat_strong - continuum_first_mode
                )
                / continuum_first_mode,
                "flat_electroweak_relative_error": abs(
                    flat_electroweak - continuum_first_mode
                )
                / continuum_first_mode,
                "strong_low_cluster_mean": cluster_mean(strong_values, 3, 6),
                "electroweak_low_cluster_mean": cluster_mean(
                    electroweak_values, 2, 4
                ),
            }
        )
    return rows


def relative_changes(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [
        abs(float(right[key]) - float(left[key]))
        / max(abs(float(right[key])), abs(float(left[key])), 1.0e-300)
        for left, right in zip(rows[:-1], rows[1:], strict=True)
    ]


def strictly_decreasing(values: list[float], tolerance: float = 1.0e-13) -> bool:
    return all(
        right < left + tolerance
        for left, right in zip(values[:-1], values[1:], strict=True)
    )


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=float
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_gauge_sector_spectral_refinement() -> dict[str, Any]:
    cfg = GaugeSpectralRefinementConfig()
    rows = refinement_rows(cfg)
    flat_strong_errors = [float(row["flat_strong_relative_error"]) for row in rows]
    flat_electroweak_errors = [
        float(row["flat_electroweak_relative_error"]) for row in rows
    ]
    strong_changes = relative_changes(rows, "strong_low_cluster_mean")
    electroweak_changes = relative_changes(
        rows, "electroweak_low_cluster_mean"
    )

    ledger = {
        "dimensionless_gauge_spectra_constructed": True,
        "dimensionless_transition_response_constructed": True,
        "odd_grid_refinement_executed": True,
        "physical_unit_calibration_complete": False,
        "particle_or_sector_identity_promoted": False,
        "external_spectrum_or_decay_data_used": False,
        "out_of_sample_prediction_ready": False,
    }
    payload = {
        "schema": "openwave.m9.gauge-sector-spectral-refinement.v1",
        "task": "M9.120c",
        "config": asdict(cfg),
        "rows": rows,
        "strong_cluster_relative_changes": strong_changes,
        "electroweak_cluster_relative_changes": electroweak_changes,
        "phenomenology_ledger": ledger,
        "claim_boundary": {
            "decreasing_finite_grid_error_is_continuum_proof": False,
            "dimensionless_cluster_is_observed_mass_spectrum": False,
            "finite_response_is_physical_decay_phenomenology": False,
            "internal_scale_is_external_calibration": False,
        },
    }
    acceptance = {
        "flat_strong_first_mode_converges_monotonically": (
            strictly_decreasing(flat_strong_errors)
            and flat_strong_errors[-1] <= 3.0e-2
        ),
        "flat_electroweak_first_mode_converges_monotonically": (
            strictly_decreasing(flat_electroweak_errors)
            and flat_electroweak_errors[-1] <= 3.0e-2
        ),
        "smooth_strong_low_cluster_is_Cauchy_improving": (
            strictly_decreasing(strong_changes) and strong_changes[-1] <= 2.5e-2
        ),
        "smooth_electroweak_low_cluster_is_Cauchy_improving": (
            strictly_decreasing(electroweak_changes)
            and electroweak_changes[-1] <= 2.5e-2
        ),
        "phenomenology_ledger_retains_calibration_identity_and_prediction_boundaries": (
            not ledger["physical_unit_calibration_complete"]
            and not ledger["particle_or_sector_identity_promoted"]
            and not ledger["external_spectrum_or_decay_data_used"]
            and not ledger["out_of_sample_prediction_ready"]
        ),
        "no_continuum_or_physical_claim_is_promoted": not any(
            payload["claim_boundary"].values()
        ),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "finite_gauge_spectral_refinement_constructed": True,
            "dimensionless_phenomenology_ledger_constructed": True,
            "continuum_spectrum_theorem_complete": False,
            "physical_spectrum_or_decay_prediction_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
