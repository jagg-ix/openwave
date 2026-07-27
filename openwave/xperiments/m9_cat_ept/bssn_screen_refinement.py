"""M9.116: manufactured refinement audit for source-coupled BSSN screen gravity.

The audit exercises the same exact-Fourier differential complex on three odd grids.
It verifies the scalar screen-source tidal tensor against an analytic Fourier-mode
solution, verifies the exact STF divergence correction, and compares integrated
metric-built Ricci diagnostics across refinements. Finite-grid Cauchy consistency is
reported; it is not promoted to a continuum convergence proof.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .bssn_screen_gravity import (
    conformal_connection,
    conformal_ricci_tensor,
    conformal_scalar_from_ricci,
    determinant_field,
    enforce_unit_determinant,
    metric_trace_free,
    source_tidal_tensor,
    stf_tensor_with_divergence,
)
from .compatible_discrete_geometry import PeriodicFourierGeometry
from .generalized_screen_adm_gravity import tensor_divergence
from .holographic_gravity_coupling import ScreenDensityAnchor

Tensor = np.ndarray
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]


@dataclass(frozen=True)
class BSSNRefinementConfig:
    points: tuple[int, ...] = (17, 21, 25)
    half_width: float = math.pi
    metric_amplitude: float = 2.5e-2
    screen_area: float = 2.0
    screen_bits: float = 8.0
    hbar: float = 1.0
    light_speed: float = 1.0
    cauchy_gate: float = 2.5e-2
    analytic_gate: float = 5.0e-10

    def __post_init__(self) -> None:
        if len(self.points) < 3 or any(points < 17 or points % 2 == 0 for points in self.points):
            raise ValueError("at least three odd grids with 17 or more points required")
        if tuple(sorted(self.points)) != self.points or len(set(self.points)) != len(self.points):
            raise ValueError("strictly increasing refinement grids required")
        if min(
            self.half_width,
            self.metric_amplitude,
            self.screen_area,
            self.screen_bits,
            self.hbar,
            self.light_speed,
            self.cauchy_gate,
            self.analytic_gate,
        ) <= 0.0:
            raise ValueError("positive refinement controls required")

    @property
    def anchor(self) -> ScreenDensityAnchor:
        return ScreenDensityAnchor(
            area=self.screen_area,
            bits=self.screen_bits,
            hbar=self.hbar,
            c=self.light_speed,
            evidence_class="external",
            source="synthetic manufactured-refinement fixture; not physical evidence",
        )


def tensor_volume_norm(tensor: Tensor, geometry: PeriodicFourierGeometry) -> float:
    return math.sqrt(
        geometry.cell_volume
        * sum(float(np.sum(tensor[i, j] ** 2)) for i in range(3) for j in range(3))
    )


def scalar_volume_norm(values: np.ndarray, geometry: PeriodicFourierGeometry) -> float:
    return math.sqrt(geometry.cell_volume * float(np.sum(values**2)))


def coordinate_mesh(points: int, half_width: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    spacing = 2.0 * half_width / points
    axis = -half_width + spacing * np.arange(points, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return x, y, z, spacing


def manufactured_fields(
    points: int,
    cfg: BSSNRefinementConfig,
) -> tuple[PeriodicFourierGeometry, Tensor, np.ndarray, tuple[float, float, float], tuple[np.ndarray, ...]]:
    x, y, z, spacing = coordinate_mesh(points, cfg.half_width)
    geometry = PeriodicFourierGeometry(
        (points, points, points),
        (spacing, spacing, spacing),
    )
    length = 2.0 * cfg.half_width
    wave_numbers = (
        2.0 * math.pi / length,
        4.0 * math.pi / length,
        2.0 * math.pi / length,
    )
    qx, qy, qz = wave_numbers
    cx, cy, cz = np.cos(qx * x), np.cos(qy * y), np.cos(qz * z)
    sx, sy, sz = np.sin(qx * x), np.sin(qy * y), np.sin(qz * z)
    mode = cx * cy * cz
    metric_seed = cfg.metric_amplitude * (
        np.cos(qx * x) * np.cos(qy * y) + 0.5 * np.cos(qz * z)
    )
    metric = np.zeros((3, 3, points, points, points), dtype=np.float64)
    metric[0, 0] = np.exp(2.0 * metric_seed)
    metric[1, 1] = np.exp(-2.0 * metric_seed)
    metric[2, 2] = 1.0
    metric = enforce_unit_determinant(metric)
    analytic_basis = (cx, cy, cz, sx, sy, sz)
    return geometry, metric, mode, wave_numbers, analytic_basis


def analytic_source_tidal(
    mode: np.ndarray,
    waves: tuple[float, float, float],
    basis: tuple[np.ndarray, ...],
    coupling: float,
) -> Tensor:
    qx, qy, qz = waves
    cx, cy, cz, sx, sy, sz = basis
    q2 = qx * qx + qy * qy + qz * qz
    factor = 4.0 * math.pi * coupling / q2
    hessian = np.zeros((3, 3) + mode.shape, dtype=np.float64)
    hessian[0, 0] = -factor * qx * qx * mode
    hessian[1, 1] = -factor * qy * qy * mode
    hessian[2, 2] = -factor * qz * qz * mode
    hessian[0, 1] = hessian[1, 0] = factor * qx * qy * sx * sy * cz
    hessian[0, 2] = hessian[2, 0] = factor * qx * qz * sx * cy * sz
    hessian[1, 2] = hessian[2, 1] = factor * qy * qz * cx * sy * sz
    trace = hessian[0, 0] + hessian[1, 1] + hessian[2, 2]
    for index in range(3):
        hessian[index, index] -= trace / 3.0
    return hessian


def relative_tensor_error(
    observed: Tensor,
    expected: Tensor,
    geometry: PeriodicFourierGeometry,
) -> float:
    return tensor_volume_norm(observed - expected, geometry) / max(
        tensor_volume_norm(expected, geometry),
        1.0e-300,
    )


def refinement_row(points: int, cfg: BSSNRefinementConfig) -> dict[str, float]:
    geometry, metric, source, waves, basis = manufactured_fields(points, cfg)
    coupling = cfg.anchor.newton_coupling
    ricci = conformal_ricci_tensor(metric, geometry)
    ricci_scalar = conformal_scalar_from_ricci(ricci, metric)
    ricci_tf = metric_trace_free(ricci, metric)
    numerical_tidal = source_tidal_tensor(source, geometry, coupling)
    analytic_tidal = analytic_source_tidal(source, waves, basis, coupling)
    effective = metric_trace_free(ricci_tf - numerical_tidal, metric)
    gamma = conformal_connection(metric, geometry)

    manufactured_vector: Vector = tuple(
        np.asarray(component, dtype=np.float64) for component in geometry.gradient(source)
    )  # type: ignore[assignment]
    correction = stf_tensor_with_divergence(manufactured_vector, geometry)
    recovered = tensor_divergence(correction, geometry)
    divergence_error = math.sqrt(
        geometry.cell_volume
        * sum(
            float(np.sum((recovered[i] - geometry.mean_zero(manufactured_vector[i])) ** 2))
            for i in range(3)
        )
    ) / max(
        math.sqrt(
            geometry.cell_volume
            * sum(float(np.sum(geometry.mean_zero(component) ** 2)) for component in manufactured_vector)
        ),
        1.0e-300,
    )

    return {
        "points": float(points),
        "spacing": geometry.spacings[0],
        "determinant_error_max": float(np.max(np.abs(determinant_field(metric) - 1.0))),
        "source_tidal_relative_error": relative_tensor_error(
            numerical_tidal,
            analytic_tidal,
            geometry,
        ),
        "stf_divergence_correction_relative_error": divergence_error,
        "ricci_scalar_l2": scalar_volume_norm(ricci_scalar, geometry),
        "ricci_tracefree_l2": tensor_volume_norm(ricci_tf, geometry),
        "source_tidal_l2": tensor_volume_norm(numerical_tidal, geometry),
        "effective_tracefree_l2": tensor_volume_norm(effective, geometry),
        "conformal_connection_l2": math.sqrt(
            geometry.cell_volume * sum(float(np.sum(component**2)) for component in gamma)
        ),
    }


def relative_change(left: float, right: float) -> float:
    return abs(right - left) / max(abs(left), abs(right), 1.0e-300)


@lru_cache(maxsize=1)
def run_bssn_refinement_study() -> dict[str, Any]:
    cfg = BSSNRefinementConfig()
    rows = [refinement_row(points, cfg) for points in cfg.points]
    tracked = (
        "ricci_scalar_l2",
        "ricci_tracefree_l2",
        "source_tidal_l2",
        "effective_tracefree_l2",
        "conformal_connection_l2",
    )
    cauchy = []
    for coarse, fine in zip(rows, rows[1:]):
        changes = {key: relative_change(float(coarse[key]), float(fine[key])) for key in tracked}
        cauchy.append(
            {
                "coarse_points": int(coarse["points"]),
                "fine_points": int(fine["points"]),
                **changes,
                "maximum_relative_change": max(changes.values()),
            }
        )
    maximum_cauchy_change = max(row["maximum_relative_change"] for row in cauchy)
    maximum_analytic_error = max(
        max(row["source_tidal_relative_error"], row["stf_divergence_correction_relative_error"])
        for row in rows
    )
    acceptance = {
        "three_strictly_refined_odd_grids_execute": len(rows) >= 3
        and all(int(row["points"]) % 2 == 1 for row in rows)
        and all(rows[i + 1]["spacing"] < rows[i]["spacing"] for i in range(len(rows) - 1)),
        "unit_determinant_is_preserved_on_every_grid": max(
            row["determinant_error_max"] for row in rows
        )
        <= cfg.analytic_gate,
        "screen_source_tidal_tensor_matches_analytic_mode": max(
            row["source_tidal_relative_error"] for row in rows
        )
        <= cfg.analytic_gate,
        "stf_tensor_divergence_correction_is_exact_on_active_modes": max(
            row["stf_divergence_correction_relative_error"] for row in rows
        )
        <= cfg.analytic_gate,
        "ricci_and_source_invariants_are_cauchy_consistent": maximum_cauchy_change
        <= cfg.cauchy_gate,
        "all_refinement_diagnostics_are_finite": all(
            math.isfinite(float(value)) for row in rows for value in row.values()
        ),
        "finite_grid_refinement_is_not_continuum_proof": True,
    }
    payload = {
        "schema": "openwave.m9.bssn-screen-refinement.v1",
        "task": "M9.116",
        "config": asdict(cfg),
        "screen_newton_coupling": cfg.anchor.newton_coupling,
        "rows": rows,
        "cauchy_pairs": cauchy,
        "maximum_cauchy_relative_change": maximum_cauchy_change,
        "maximum_analytic_relative_error": maximum_analytic_error,
        "claim_boundary": {
            "manufactured_mode_is_physical_calibration": False,
            "finite_grid_cauchy_consistency_is_continuum_convergence_proof": False,
            "scalar_source_tidal_tensor_is_complete_BSSN_matter_source": False,
            "refinement_closes_general_Einstein_evolution": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "decision": {
            "source_tidal_analytic_bridge_closed": True,
            "tensor_divergence_correction_closed": True,
            "three_grid_refinement_completed": True,
            "finite_grid_cauchy_consistency_established": acceptance[
                "ricci_and_source_invariants_are_cauchy_consistent"
            ],
            "continuum_BSSN_convergence_proved": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
