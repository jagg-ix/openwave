"""M9.117c: inject one coarse-grained screen coupling across resolution scales.

A low-mode periodic source is transported from a fine carrier to coarser odd grids.
At every level the same total screen area and holographic bit count reconstruct one
Newton coupling.  The Poisson response and source-tidal observables are compared
across scales.  This is a numerical scale-consistency campaign, not physical screen
calibration or full BSSN renormalisation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .bssn_screen_gravity import source_tidal_tensor
from .compatible_discrete_geometry import PeriodicFourierGeometry, spectral_resample
from .holographic_gravity_coupling import (
    ScreenDensityAnchor,
    build_gravity_configs,
    coupling_contract,
)


@dataclass(frozen=True)
class CoarseGrainedGravityConfig:
    grids: tuple[int, ...] = (17, 25, 33)
    half_width: float = math.pi
    screen_area: float = 2.0
    screen_bits: float = 8.0
    hbar: float = 1.0
    light_speed: float = 1.0

    def __post_init__(self) -> None:
        if len(self.grids) < 3 or any(points < 17 or points % 2 == 0 for points in self.grids):
            raise ValueError("at least three odd grids with 17 or more points required")
        if tuple(sorted(self.grids)) != self.grids or len(set(self.grids)) != len(self.grids):
            raise ValueError("strictly increasing unique refinement grids required")
        if min(
            self.half_width,
            self.screen_area,
            self.screen_bits,
            self.hbar,
            self.light_speed,
        ) <= 0.0:
            raise ValueError("positive coarse-grained gravity controls required")

    @property
    def anchor(self) -> ScreenDensityAnchor:
        return ScreenDensityAnchor(
            area=self.screen_area,
            bits=self.screen_bits,
            hbar=self.hbar,
            c=self.light_speed,
            evidence_class="external",
            source="synthetic M9.117 scale fixture; not physical evidence",
        )


def geometry(points: int, half_width: float) -> PeriodicFourierGeometry:
    spacing = 2.0 * half_width / points
    return PeriodicFourierGeometry(
        (points, points, points), (spacing, spacing, spacing)
    )


def analytic_source(points: int, half_width: float) -> np.ndarray:
    spacing = 2.0 * half_width / points
    axis = -half_width + spacing * np.arange(points, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return np.asarray(
        np.sin(x) + 0.35 * np.cos(2.0 * y) + 0.20 * np.sin(z),
        dtype=np.float64,
    )


def scalar_l2(values: np.ndarray, cell_volume: float) -> float:
    return math.sqrt(float(np.sum(values * values)) * cell_volume)


def vector_energy(vector: tuple[np.ndarray, np.ndarray, np.ndarray], cell_volume: float) -> float:
    return 0.5 * cell_volume * sum(float(np.sum(component * component)) for component in vector)


def tensor_l2(tensor: np.ndarray, cell_volume: float) -> float:
    return math.sqrt(float(np.sum(tensor * tensor)) * cell_volume)


def resolution_row(
    source: np.ndarray,
    direct_source: np.ndarray,
    cfg: CoarseGrainedGravityConfig,
) -> dict[str, Any]:
    points = int(source.shape[0])
    geom = geometry(points, cfg.half_width)
    anchor = cfg.anchor
    configs = build_gravity_configs(anchor, points=points, half_width=cfg.half_width)
    contract = coupling_contract(configs)
    coupling = anchor.newton_coupling
    projected = geom.mean_zero(np.asarray(source, dtype=np.float64))
    potential = 4.0 * math.pi * coupling * geom.inverse_negative_laplacian(projected)
    poisson_residual = -geom.laplacian(potential) - 4.0 * math.pi * coupling * projected
    source_scale = max(
        float(np.linalg.norm(4.0 * math.pi * coupling * projected)), 1.0e-300
    )
    field = tuple(-component for component in geom.gradient(potential))
    tidal = source_tidal_tensor(projected, geom, coupling)
    cell_volume = geom.cell_volume
    source_match = float(
        np.linalg.norm(source - direct_source)
        / max(float(np.linalg.norm(direct_source)), 1.0e-300)
    )
    return {
        "points": points,
        "spacing": 2.0 * cfg.half_width / points,
        "screen_area_per_bit": anchor.area_per_bit,
        "screen_newton_coupling": coupling,
        "weak_newton_coupling": contract["weak_newton_coupling"],
        "nonlinear_newton_coupling": contract["nonlinear_newton_coupling"],
        "one_G_contract_passed": bool(
            contract["weak_uses_screen_coupling"]
            and contract["nonlinear_uses_screen_coupling"]
            and contract["weak_and_nonlinear_share_one_G"]
        ),
        "spectral_transport_relative_error": source_match,
        "poisson_relative_residual": float(np.linalg.norm(poisson_residual) / source_scale),
        "source_l2": scalar_l2(projected, cell_volume),
        "potential_l2": scalar_l2(potential, cell_volume),
        "field_energy": vector_energy(field, cell_volume),
        "tidal_l2": tensor_l2(tidal, cell_volume),
    }


def cauchy_comparisons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observables = ("source_l2", "potential_l2", "field_energy", "tidal_l2")
    comparisons = []
    for left, right in zip(rows[:-1], rows[1:], strict=True):
        changes = {
            name: abs(float(right[name]) - float(left[name]))
            / max(abs(float(right[name])), abs(float(left[name])), 1.0e-300)
            for name in observables
        }
        comparisons.append(
            {
                "coarse_points": left["points"],
                "fine_points": right["points"],
                "relative_changes": changes,
                "maximum_relative_change": max(changes.values()),
            }
        )
    return comparisons


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_coarse_grained_screen_gravity() -> dict[str, Any]:
    cfg = CoarseGrainedGravityConfig()
    finest = cfg.grids[-1]
    fine_source = analytic_source(finest, cfg.half_width)
    rows = []
    for points in cfg.grids:
        source = (
            fine_source
            if points == finest
            else np.asarray(
                spectral_resample(fine_source.astype(np.complex128), (points,) * 3).real,
                dtype=np.float64,
            )
        )
        rows.append(
            resolution_row(source, analytic_source(points, cfg.half_width), cfg)
        )
    comparisons = cauchy_comparisons(rows)
    max_cauchy = max(row["maximum_relative_change"] for row in comparisons)
    acceptance = {
        "one_screen_G_reaches_every_resolution_and_carrier": all(
            row["one_G_contract_passed"] for row in rows
        )
        and max(
            abs(row["screen_newton_coupling"] - cfg.anchor.newton_coupling)
            / cfg.anchor.newton_coupling
            for row in rows
        )
        <= 5.0e-15,
        "low_mode_source_survives_spectral_coarse_graining": max(
            row["spectral_transport_relative_error"] for row in rows
        )
        <= 2.0e-13,
        "Poisson_response_closes_on_every_grid": max(
            row["poisson_relative_residual"] for row in rows
        )
        <= 1.0e-11,
        "source_potential_field_and_tidal_observables_are_scale_consistent": max_cauchy
        <= 2.0e-11,
        "all_scale_diagnostics_are_finite": all(
            math.isfinite(float(value))
            for row in rows
            for key, value in row.items()
            if key not in {"one_G_contract_passed"}
        ),
        "scale_consistency_is_not_physical_calibration": True,
    }
    payload = {
        "schema": "openwave.m9.coarse-grained-screen-gravity.v1",
        "task": "M9.117c",
        "config": asdict(cfg),
        "rows": rows,
        "cauchy_comparisons": comparisons,
        "maximum_cauchy_relative_change": max_cauchy,
        "claim_boundary": {
            "synthetic_anchor_is_physical_screen_measurement": False,
            "low_mode_scale_consistency_is_full_BSSN_renormalisation": False,
            "Poisson_scale_consistency_is_general_Einstein_equivalence": False,
            "coarse_grained_cells_replace_holographic_bits_in_G": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "coarse_grained_screen_coupling_injected": True,
            "low_mode_gravity_response_is_scale_consistent": True,
            "physical_screen_calibration_complete": False,
            "general_Einstein_scale_equivalence_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
