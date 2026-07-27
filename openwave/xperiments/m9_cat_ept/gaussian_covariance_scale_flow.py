"""M9.117b: Gaussian covariance and semigroup consistency across screen scales.

The finite-dimensional adapters mirror the formal Physlib Hamiltonian-renormalisation
interfaces: Gaussian pullback ``C_coarse = I^T C_fine I``, composable injections,
heat-semigroup damping, and principal/image coupling limits.  They are numerical
witnesses for the interface, not a proof of an interacting CAT/EPT fixed point.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class GaussianScaleFlowConfig:
    fine_points: int = 64
    block_factor: int = 2
    levels: int = 2
    half_width: float = math.pi
    mass: float = 0.8
    heat_time_one: float = 0.07
    heat_time_two: float = 0.11
    image_modes: tuple[int, ...] = (-2, -1, 1, 2)
    limit_samples: tuple[float, ...] = (0.4, 0.2, 0.1, 0.05, 0.025)

    def __post_init__(self) -> None:
        if self.fine_points < 16 or self.fine_points & (self.fine_points - 1):
            raise ValueError("power-of-two covariance grid required")
        if self.block_factor < 2 or self.levels < 2:
            raise ValueError("at least two composable scale steps required")
        if self.fine_points % (self.block_factor**self.levels):
            raise ValueError("scale tower must divide the fine grid")
        if min(
            self.half_width,
            self.mass,
            self.heat_time_one,
            self.heat_time_two,
            *self.limit_samples,
        ) <= 0.0:
            raise ValueError("positive Gaussian-flow controls required")
        if any(mode == 0 for mode in self.image_modes):
            raise ValueError("image modes must exclude the principal branch")


def piecewise_constant_injection(coarse_points: int, factor: int) -> np.ndarray:
    """Isometric piecewise-constant embedding from coarse to fine fields."""
    if coarse_points < 2 or factor < 2:
        raise ValueError("substantive injection dimensions required")
    fine_points = coarse_points * factor
    injection = np.zeros((fine_points, coarse_points), dtype=np.float64)
    weight = 1.0 / math.sqrt(factor)
    for coarse in range(coarse_points):
        injection[coarse * factor : (coarse + 1) * factor, coarse] = weight
    return injection


def periodic_covariance(points: int, half_width: float, mass: float) -> np.ndarray:
    """Real circulant covariance with eigenvalues ``1/(m^2+k^2)``."""
    spacing = 2.0 * half_width / points
    waves = 2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
    eigenvalues = 1.0 / (mass * mass + waves * waves)
    kernel = np.fft.ifft(eigenvalues).real
    covariance = np.empty((points, points), dtype=np.float64)
    for i in range(points):
        for j in range(points):
            covariance[i, j] = kernel[(i - j) % points]
    return np.asarray(0.5 * (covariance + covariance.T), dtype=np.float64)


def gaussian_weyl(covariance: np.ndarray, vector: np.ndarray) -> float:
    if covariance.shape != (vector.size, vector.size):
        raise ValueError("matching covariance and test vector required")
    return math.exp(-0.25 * float(vector @ covariance @ vector))


def heat_apply(values: np.ndarray, time: float, half_width: float) -> np.ndarray:
    spacing = 2.0 * half_width / values.size
    waves = 2.0 * math.pi * np.fft.fftfreq(values.size, d=spacing)
    result = np.fft.ifft(np.exp(-(waves**2) * time) * np.fft.fft(values))
    return np.asarray(np.real_if_close(result, tol=1000).real, dtype=np.float64)


def coupling_function(t: float, image: int) -> float:
    denominator = (t + 2.0 * math.pi * image) ** 2
    if denominator == 0.0:
        raise ValueError("coupling function denominator must be nonzero")
    return 2.0 * (1.0 - math.cos(t)) / denominator


def run_covariance_tower(cfg: GaussianScaleFlowConfig) -> dict[str, Any]:
    fine = cfg.fine_points
    middle = fine // cfg.block_factor
    coarse = middle // cfg.block_factor
    i_fm = piecewise_constant_injection(middle, cfg.block_factor)
    i_mc = piecewise_constant_injection(coarse, cfg.block_factor)
    i_fc = i_fm @ i_mc
    covariance_fine = periodic_covariance(fine, cfg.half_width, cfg.mass)
    covariance_middle = i_fm.T @ covariance_fine @ i_fm
    covariance_coarse_nested = i_mc.T @ covariance_middle @ i_mc
    covariance_coarse_direct = i_fc.T @ covariance_fine @ i_fc

    rng = np.random.default_rng(117)
    test_middle = rng.normal(size=middle)
    test_coarse = rng.normal(size=coarse)
    middle_pullback_error = abs(
        gaussian_weyl(covariance_fine, i_fm @ test_middle)
        - gaussian_weyl(covariance_middle, test_middle)
    )
    coarse_pullback_error = abs(
        gaussian_weyl(covariance_fine, i_fc @ test_coarse)
        - gaussian_weyl(covariance_coarse_direct, test_coarse)
    )
    fixed_point_error = float(
        np.linalg.norm(covariance_coarse_nested - covariance_coarse_direct)
        / max(float(np.linalg.norm(covariance_coarse_direct)), 1.0e-300)
    )
    isometry_error = max(
        float(np.linalg.norm(i_fm.T @ i_fm - np.eye(middle))),
        float(np.linalg.norm(i_mc.T @ i_mc - np.eye(coarse))),
        float(np.linalg.norm(i_fc.T @ i_fc - np.eye(coarse))),
    )
    return {
        "fine_points": fine,
        "middle_points": middle,
        "coarse_points": coarse,
        "middle_gaussian_pullback_error": middle_pullback_error,
        "coarse_gaussian_pullback_error": coarse_pullback_error,
        "composed_covariance_fixed_point_relative_error": fixed_point_error,
        "maximum_injection_isometry_error": isometry_error,
        "minimum_fine_covariance_eigenvalue": float(
            np.min(np.linalg.eigvalsh(covariance_fine))
        ),
        "minimum_coarse_covariance_eigenvalue": float(
            np.min(np.linalg.eigvalsh(covariance_coarse_direct))
        ),
    }


def run_semigroup_and_mode_limits(cfg: GaussianScaleFlowConfig) -> dict[str, Any]:
    rng = np.random.default_rng(9117)
    field = rng.normal(size=cfg.fine_points)
    composed = heat_apply(
        heat_apply(field, cfg.heat_time_one, cfg.half_width),
        cfg.heat_time_two,
        cfg.half_width,
    )
    direct = heat_apply(
        field, cfg.heat_time_one + cfg.heat_time_two, cfg.half_width
    )
    semigroup_error = float(np.linalg.norm(composed - direct) / np.linalg.norm(direct))

    principal = [coupling_function(t, 0) for t in cfg.limit_samples]
    images = {
        str(mode): [coupling_function(t, mode) for t in cfg.limit_samples]
        for mode in cfg.image_modes
    }
    principal_errors = [abs(value - 1.0) for value in principal]
    image_magnitudes = {
        mode: [abs(value) for value in values] for mode, values in images.items()
    }
    return {
        "heat_semigroup_relative_error": semigroup_error,
        "limit_samples": list(cfg.limit_samples),
        "principal_couplings": principal,
        "principal_errors": principal_errors,
        "image_couplings": images,
        "image_magnitudes": image_magnitudes,
        "principal_error_decreases": all(
            right <= left + 1.0e-15
            for left, right in zip(principal_errors[:-1], principal_errors[1:], strict=True)
        ),
        "every_image_magnitude_decreases": all(
            all(
                right <= left + 1.0e-15
                for left, right in zip(values[:-1], values[1:], strict=True)
            )
            for values in image_magnitudes.values()
        ),
        "final_principal_error": principal_errors[-1],
        "maximum_final_image_magnitude": max(
            values[-1] for values in image_magnitudes.values()
        ),
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_gaussian_covariance_scale_flow() -> dict[str, Any]:
    cfg = GaussianScaleFlowConfig()
    covariance = run_covariance_tower(cfg)
    limits = run_semigroup_and_mode_limits(cfg)
    acceptance = {
        "Gaussian_pullback_matches_projected_covariance": max(
            covariance["middle_gaussian_pullback_error"],
            covariance["coarse_gaussian_pullback_error"],
        )
        <= 2.0e-14,
        "composable_injections_give_automatic_fixed_point": covariance[
            "composed_covariance_fixed_point_relative_error"
        ]
        <= 2.0e-14,
        "piecewise_constant_injections_are_isometries": covariance[
            "maximum_injection_isometry_error"
        ]
        <= 3.0e-14,
        "projected_covariances_remain_positive": covariance[
            "minimum_fine_covariance_eigenvalue"
        ]
        > 0.0
        and covariance["minimum_coarse_covariance_eigenvalue"] > 0.0,
        "heat_transfer_is_a_semigroup": limits["heat_semigroup_relative_error"]
        <= 2.0e-14,
        "principal_mode_converges_toward_one": limits["principal_error_decreases"]
        and limits["final_principal_error"] <= 6.0e-5,
        "image_modes_decouple_toward_zero": limits[
            "every_image_magnitude_decreases"
        ]
        and limits["maximum_final_image_magnitude"] <= 2.0e-5,
        "interacting_CAT_EPT_fixed_point_is_not_inferred": True,
    }
    payload = {
        "schema": "openwave.m9.gaussian-covariance-scale-flow.v1",
        "task": "M9.117b",
        "config": asdict(cfg),
        "covariance_tower": covariance,
        "semigroup_and_mode_limits": limits,
        "formal_correspondence": {
            "Gaussian_pullback": "Physlib.QFT.HamiltonianRenormalisation.gaussianWeyl_flow",
            "automatic_fixed_point": "Physlib.QFT.HamiltonianRenormalisation.covariance_fixedPoint_automatic",
            "principal_mode_limit": "Physlib.QFT.HamiltonianRenormalisation.couplingFunction_tendsto_one",
            "image_mode_limit": "Physlib.QFT.HamiltonianRenormalisation.couplingFunction_tendsto_zero",
            "continuum_covariance": "Physlib.QFT.HamiltonianRenormalisation.continuum_covariance_dictionary",
        },
        "claim_boundary": {
            "finite_matrix_adapter_is_Lean_proof": False,
            "free_Gaussian_fixed_point_is_interacting_CAT_EPT_fixed_point": False,
            "image_mode_decoupling_selects_particle_spectrum": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "Gaussian_covariance_flow_adapter_constructed": True,
            "coarse_graining_semigroup_constructed": True,
            "principal_and_image_mode_limits_reproduced": True,
            "interacting_fixed_point_constructed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
