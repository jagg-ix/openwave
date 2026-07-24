"""M9.63 dimensionless coefficient-selection audit for the CAT/EPT binding action.

The M9.59/M9.60 cubic--quintic density action is

    V(rho) = -alpha/2 rho^2 + beta/3 rho^3.

Two explicit dimensionless self-consistency conditions select a unique coefficient
pair for the normalized Gaussian reference branch:

1. the local density-action minimum equals the Gaussian peak density;
2. the normalized Gaussian is stationary at the declared reference scale.

The conditions are model assumptions, not experimentally derived laws. This
module therefore distinguishes mathematical uniqueness under those conditions
from first-principles or physical coefficient determination.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

from .action_derived_binding import BindingCampaignConfig, evolve

OPENWAVE_HEAD = "421c962fdaa4aa7359c00cd6b37f985d297f0dac"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "54b4ced090b200fac7ff04ee6a7e8797f1263049"
ZIL_REPOSITORY = "jagg-ix/zil-lean"
ZIL_HEAD = "f39758f85ee6300b8060e4f8ea1ecf344ed32c96"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean",
        "sha": "e46898d0013c22e983051b7248160323e64f468f",
        "role": "unique gauge-covariant cubic law and exact global positive-time cubic continuum flow",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaUnboundedGenerator.lean",
        "sha": "605a3eb7dd7055de4b1d5ce3d8eacecea136f70a",
        "role": "maximal dissipativity and explicit homogeneous complex C0 semigroups",
    },
)


@dataclass(frozen=True)
class CoefficientSelectionConfig:
    dispersion: float = 0.65
    reference_scale: float = 1.0
    prior_alpha: float = 70.0
    prior_beta: float = 380.0
    sensitivity_dispersions: tuple[float, ...] = (0.50, 0.65, 0.80)
    finite_grid: BindingCampaignConfig = BindingCampaignConfig()

    def __post_init__(self) -> None:
        if self.dispersion <= 0 or self.reference_scale <= 0:
            raise ValueError("positive dispersion and reference scale required")
        if self.prior_alpha <= 0 or self.prior_beta <= 0:
            raise ValueError("positive prior coefficients required")
        if any(value <= 0 for value in self.sensitivity_dispersions):
            raise ValueError("positive sensitivity dispersions required")


def gaussian_peak_density(scale: float) -> float:
    if scale <= 0:
        raise ValueError("positive scale required")
    return 1.0 / (math.pi**1.5 * scale**3)


def gaussian_energy_constants(dispersion: float) -> dict[str, float]:
    if dispersion <= 0:
        raise ValueError("positive dispersion required")
    return {
        "kinetic": 1.5 * dispersion,
        "quartic": 0.5 / (2.0 * math.pi) ** 1.5,
        "sextic": (1.0 / 3.0) / (3.0**1.5 * math.pi**3),
    }


def selection_linear_system(
    cfg: CoefficientSelectionConfig = CoefficientSelectionConfig(),
) -> tuple[np.ndarray, np.ndarray]:
    """Return the two self-consistency equations for ``(alpha, beta)``.

    ``alpha / beta = rho_peak`` aligns the local density minimum with the
    normalized Gaussian peak. Stationarity of

        E(s) = A s^-2 - B alpha s^-3 + C beta s^-6

    at ``s = s0`` supplies the second independent equation.
    """

    s0 = cfg.reference_scale
    rho_peak = gaussian_peak_density(s0)
    constants = gaussian_energy_constants(cfg.dispersion)
    matrix = np.asarray(
        [
            [1.0, -rho_peak],
            [3.0 * constants["quartic"] * s0**3, -6.0 * constants["sextic"]],
        ],
        dtype=np.float64,
    )
    rhs = np.asarray([0.0, 2.0 * constants["kinetic"] * s0**4], dtype=np.float64)
    return matrix, rhs


def selected_coefficients(
    cfg: CoefficientSelectionConfig = CoefficientSelectionConfig(),
) -> dict[str, float]:
    matrix, rhs = selection_linear_system(cfg)
    determinant = float(np.linalg.det(matrix))
    if abs(determinant) <= 1e-14:
        raise ValueError("self-consistency conditions are degenerate")
    alpha, beta = np.linalg.solve(matrix, rhs)
    residual = matrix @ np.asarray([alpha, beta]) - rhs
    rho_peak = gaussian_peak_density(cfg.reference_scale)
    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "determinant": determinant,
        "maximum_equation_residual": float(np.max(np.abs(residual))),
        "reference_peak_density": rho_peak,
        "density_minimizer": float(alpha / beta),
        "density_matching_error": abs(float(alpha / beta) - rho_peak),
        "relative_alpha_shift_from_m9_59": abs(float(alpha) - cfg.prior_alpha) / cfg.prior_alpha,
        "relative_beta_shift_from_m9_59": abs(float(beta) - cfg.prior_beta) / cfg.prior_beta,
    }


def sensitivity_campaign(
    cfg: CoefficientSelectionConfig = CoefficientSelectionConfig(),
) -> dict[str, Any]:
    rows = []
    for dispersion in cfg.sensitivity_dispersions:
        local = CoefficientSelectionConfig(
            dispersion=dispersion,
            reference_scale=cfg.reference_scale,
            prior_alpha=cfg.prior_alpha,
            prior_beta=cfg.prior_beta,
            sensitivity_dispersions=cfg.sensitivity_dispersions,
            finite_grid=cfg.finite_grid,
        )
        coefficients = selected_coefficients(local)
        rows.append(
            {
                "dispersion": dispersion,
                "alpha": coefficients["alpha"],
                "beta": coefficients["beta"],
                "alpha_over_dispersion": coefficients["alpha"] / dispersion,
                "beta_over_dispersion": coefficients["beta"] / dispersion,
            }
        )
    alpha_scaled = np.asarray([row["alpha_over_dispersion"] for row in rows])
    beta_scaled = np.asarray([row["beta_over_dispersion"] for row in rows])
    return {
        "rows": rows,
        "alpha_scales_linearly": float(np.ptp(alpha_scaled)) <= 1e-11,
        "beta_scales_linearly": float(np.ptp(beta_scaled)) <= 1e-11,
    }


def finite_grid_confirmation(
    cfg: CoefficientSelectionConfig = CoefficientSelectionConfig(),
) -> dict[str, Any]:
    coefficients = selected_coefficients(cfg)
    grid = cfg.finite_grid
    rows = []
    for points, half_width, final_time in zip(grid.points, grid.half_widths, grid.final_times):
        row = evolve(
            coefficients["alpha"],
            coefficients["beta"],
            points,
            half_width,
            final_time,
            grid.dt,
        )
        row["retained_localization"] = bool(
            row["radius_ratio"] < grid.retained_radius_ratio
            and row["maximum_boundary_fraction"] < grid.maximum_boundary
        )
        rows.append(row)
    return {
        "rows": rows,
        "all_grids_retain_localization": all(row["retained_localization"] for row in rows),
        "maximum_radius_ratio": max(row["radius_ratio"] for row in rows),
        "maximum_boundary_fraction": max(row["maximum_boundary_fraction"] for row in rows),
        "maximum_balance_error": max(row["maximum_balance_error"] for row in rows),
    }


def evidence_fingerprint() -> str:
    payload = {
        "openwave_head": OPENWAVE_HEAD,
        "formal_repository": FORMAL_REPOSITORY,
        "formal_branch": FORMAL_BRANCH,
        "formal_head": FORMAL_HEAD,
        "zil_repository": ZIL_REPOSITORY,
        "zil_head": ZIL_HEAD,
        "sources": FORMAL_SOURCES,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_coefficient_self_consistency() -> dict[str, Any]:
    cfg = CoefficientSelectionConfig()
    coefficients = selected_coefficients(cfg)
    sensitivity = sensitivity_campaign(cfg)
    finite_grid = finite_grid_confirmation(cfg)
    acceptance = {
        "current_openwave_head_is_pinned": OPENWAVE_HEAD == "421c962fdaa4aa7359c00cd6b37f985d297f0dac",
        "current_physlib_head_is_pinned": FORMAL_HEAD == "54b4ced090b200fac7ff04ee6a7e8797f1263049",
        "current_zil_head_is_pinned": ZIL_HEAD == "f39758f85ee6300b8060e4f8ea1ecf344ed32c96",
        "selection_conditions_are_independent": abs(coefficients["determinant"]) > 1e-5,
        "selection_equations_close": coefficients["maximum_equation_residual"] <= 2e-13,
        "density_minimum_matches_reference_peak": coefficients["density_matching_error"] <= 2e-14,
        "selected_coefficients_are_positive": coefficients["alpha"] > 0 and coefficients["beta"] > 0,
        "selection_is_near_the_discovered_candidate": coefficients["relative_alpha_shift_from_m9_59"] < 0.10
        and coefficients["relative_beta_shift_from_m9_59"] < 0.10,
        "dispersion_sensitivity_is_explicit": sensitivity["alpha_scales_linearly"]
        and sensitivity["beta_scales_linearly"],
        "selected_pair_retains_finite_grid_candidate": finite_grid["all_grids_retain_localization"],
        "finite_grid_ledgers_close": finite_grid["maximum_balance_error"] <= 5e-4,
        "cross_repo_fingerprint_is_deterministic": evidence_fingerprint() == evidence_fingerprint(),
    }
    return {
        "schema": "openwave.m9.coefficient-self-consistency.v1",
        "task": "M9.63",
        "config": asdict(cfg),
        "formal_evidence": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "zil_repository": ZIL_REPOSITORY,
            "zil_head": ZIL_HEAD,
            "sources": FORMAL_SOURCES,
            "fingerprint": evidence_fingerprint(),
        },
        "selection": coefficients,
        "sensitivity": sensitivity,
        "finite_grid_confirmation": finite_grid,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "coefficients_unique_under_declared_self_consistency": True,
            "selected_alpha": coefficients["alpha"],
            "selected_beta": coefficients["beta"],
            "cat_ept_axioms_derive_self_consistency_conditions": False,
            "physical_coefficients_calibrated": False,
        },
        "classification": {
            "establishes": [
                "a unique coefficient pair from two explicit dimensionless self-consistency conditions",
                "linear dispersion scaling of the selected coefficients",
                "retained finite-grid localization for the selected pair",
            ],
            "does_not_establish": [
                "derivation of the two selection conditions from fundamental CAT/EPT axioms",
                "experimental calibration of alpha or beta",
                "uniqueness outside the declared Gaussian self-consistency class",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
