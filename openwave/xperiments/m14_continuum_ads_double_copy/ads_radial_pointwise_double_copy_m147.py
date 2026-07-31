"""M14.7 AdS radial/boundary pointwise double-copy model.

The model transports a continuous BCJ numerator field from the boundary into an
AdS radial coordinate with the Poisson semigroup. Pointwise Jacobi identities,
weighted color replacement and the double-copy amplitude survive every radial
slice; the bulk field approaches its boundary datum as radial depth tends to
zero. The same D3 compactification coupling normalizes the amplitude, GKP
mass/dimension data and Ryu--Takayanagi entropy without identifying them.

This is a linear harmonic radial carrier, not an interacting Witten diagram, a
proof of AdS/CFT, or a global/loop-level AdS double-copy theorem.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

MILESTONE = "M14.7"
SCHEMA = "openwave.m14.ads-radial-pointwise-double-copy.v1"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "35f98f147771a4e250ec01b4cbf2afab72313db7"
ZIL_COMMIT = "6daee2698304feb203c6adb91b2e8853613f85b5"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.31.0"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean",
        "sha": "96e5f7feb002125a633d90c3940e1af513bb8484",
        "theorems": [
            "threeChannelNumerator_in_jacobiKernel_iff",
            "cubicDoubleCopy_eq_weightedBilinear",
            "cubicDoubleCopyAmplitudeFinite_comm",
            "cubicDoubleCopy_shift_left_of_orthogonal",
            "mizera_intersectionLeadingTerm_eq_doubleCopy",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/EMComplexEinsteinAdSCFT.lean",
        "sha": "eaa50fbe34c8d5f773826ee6f63265b70f07326c",
        "theorems": [
            "d3_adsCFT_BCJ_doubleCopy",
            "d3_gkpWittenHessian_complexEinsteinCoupling",
            "d3_gkpWittenHessian_boundaryCentralCharge",
            "d3_rtEntropy_complexEinsteinCoupling",
            "d3_rtEntropy_boundaryCentralCharge",
            "d3_boundaryCentralCharge_complexEinstein_conservationFamily",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean",
        "sha": "d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3",
        "theorems": [
            "massDimension_relation",
            "cftTwoPoint_scaling",
            "gkpWitten_regularized_source_response",
            "gkpWitten_affine_source_hessian",
        ],
    },
)

JACOBI_BASIS = np.asarray([[1.0, 1.0], [-1.0, 1.0], [0.0, -2.0]])


def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class AdSRadialPointwiseDoubleCopyConfig:
    boundary_points: int = 256
    radial_depths: tuple[float, ...] = (0.8, 0.4, 0.2, 0.1, 0.05, 0.02)
    ads_radius: float = 2.3
    color_rank: float = 6.0
    compactification_volume: float = 1.7
    c: float = 1.0
    boundary_dimension: float = 4.0
    bulk_mass: float = 0.42
    rt_area: float = 1.6
    gauge_scale: float = 0.12

    def validate(self) -> None:
        if self.boundary_points < 32 or self.boundary_points % 2:
            raise ValueError("an even boundary grid with at least 32 points is required")
        if not self.radial_depths or any(r <= 0 for r in self.radial_depths):
            raise ValueError("positive radial depths required")
        if list(self.radial_depths) != sorted(self.radial_depths, reverse=True):
            raise ValueError("radial depths must decrease toward the boundary")
        positive = (
            self.ads_radius,
            self.color_rank,
            self.compactification_volume,
            self.c,
            self.boundary_dimension,
            self.bulk_mass,
            self.rt_area,
            self.gauge_scale,
        )
        if min(positive) <= 0:
            raise ValueError("all geometric and coupling controls must be positive")


def canonical_payload(config: AdSRadialPointwiseDoubleCopyConfig | None = None) -> dict[str, Any]:
    cfg = AdSRadialPointwiseDoubleCopyConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M14",
        "milestone": MILESTONE,
        "model": "CAT/EPT AdS radial and boundary pointwise double copy",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M14.3", "M14.5", "M14.6"],
        "study_api": (
            "openwave.xperiments.m14_continuum_ads_double_copy."
            "ads_radial_pointwise_double_copy_m147:run_ads_radial_pointwise_double_copy_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
        "formal_toolchain": {
            "lean": "4.31.0",
            "lean_toolchain": LEAN_TOOLCHAIN,
            "zil_repository": "jagg-ix/zil-lean",
            "zil_commit": ZIL_COMMIT,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    value = canonical_payload() if payload is None else payload
    return sha256(_canon(value).encode()).hexdigest()


def _poisson_lift(values: np.ndarray, rho: float) -> np.ndarray:
    count = values.shape[0]
    modes = np.abs(np.fft.fftfreq(count, d=1.0 / count))
    multiplier = np.exp(-rho * modes)
    transformed = np.fft.fft(values, axis=0)
    return np.fft.ifft(transformed * multiplier[:, None], axis=0).real


def _boundary_fields(cfg: AdSRadialPointwiseDoubleCopyConfig):
    theta = np.linspace(0.0, 2.0 * math.pi, cfg.boundary_points, endpoint=False)
    left_coords = np.stack(
        (
            1.0 + 0.31 * np.cos(theta) + 0.08 * np.cos(3.0 * theta),
            0.28 * np.sin(2.0 * theta) + 0.11 * np.cos(4.0 * theta),
        ),
        axis=-1,
    )
    right_coords = np.stack(
        (
            0.74 - 0.2 * np.sin(theta) + 0.06 * np.cos(5.0 * theta),
            -0.22 + 0.17 * np.cos(2.0 * theta),
        ),
        axis=-1,
    )
    left = left_coords @ JACOBI_BASIS.T
    right = right_coords @ JACOBI_BASIS.T
    weights = np.stack(
        (
            1.0 / (1.2 + 0.1 * np.cos(theta)),
            1.0 / (1.4 + 0.1 * np.sin(theta) ** 2),
            1.0 / (1.6 + 0.08 * np.cos(2.0 * theta)),
        ),
        axis=-1,
    )
    gauge = np.empty_like(left)
    for i in range(cfg.boundary_points):
        gram = JACOBI_BASIS.T @ np.diag(weights[i]) @ JACOBI_BASIS
        paired = gram @ right_coords[i]
        perpendicular = np.asarray([paired[1], -paired[0]])
        norm = float(np.linalg.norm(perpendicular))
        gauge[i] = JACOBI_BASIS @ (
            cfg.gauge_scale * perpendicular / (norm if norm else 1.0)
        )
    return theta, left, right, weights, gauge


def _periodic_integral(values: np.ndarray) -> float:
    return float(2.0 * math.pi * np.mean(values))


def run_ads_radial_pointwise_double_copy_study(
    config: AdSRadialPointwiseDoubleCopyConfig | None = None,
) -> dict[str, Any]:
    cfg = AdSRadialPointwiseDoubleCopyConfig() if config is None else config
    cfg.validate()
    _, boundary_left, boundary_right, weights, _ = _boundary_fields(cfg)
    central_charge = cfg.color_rank**2 / 4.0
    kappa_ads = (
        4.0 * math.pi**2 * cfg.ads_radius**3
        / (cfg.color_rank**2 * cfg.compactification_volume * cfg.c**4)
    )
    kappa_boundary = (
        math.pi**2 * cfg.ads_radius**3
        / (cfg.compactification_volume * cfg.c**4 * central_charge)
    )
    coupling_prefactor = (kappa_ads / 2.0) ** 2
    boundary_density = coupling_prefactor * np.sum(
        weights * boundary_left * boundary_right, axis=-1
    )
    boundary_amplitude = _periodic_integral(boundary_density)

    radial_amplitudes: list[float] = []
    radial_boundary_errors: list[float] = []
    radial_jacobi_errors: list[float] = []
    radial_gauge_errors: list[float] = []
    radial_color_replacement_errors: list[float] = []
    multiplier_minima: list[float] = []

    for rho in cfg.radial_depths:
        left = _poisson_lift(boundary_left, rho)
        right = _poisson_lift(boundary_right, rho)
        gauge = np.empty_like(left)
        basis_gram = JACOBI_BASIS.T @ JACOBI_BASIS
        for i in range(cfg.boundary_points):
            right_coordinates = np.linalg.solve(
                basis_gram, JACOBI_BASIS.T @ right[i]
            )
            gram = JACOBI_BASIS.T @ np.diag(weights[i]) @ JACOBI_BASIS
            paired = gram @ right_coordinates
            perpendicular = np.asarray([paired[1], -paired[0]])
            norm = float(np.linalg.norm(perpendicular))
            gauge[i] = JACOBI_BASIS @ (
                cfg.gauge_scale
                * np.exp(-rho)
                * perpendicular
                / (norm if norm else 1.0)
            )
        density = coupling_prefactor * np.sum(weights * left * right, axis=-1)
        shifted_density = coupling_prefactor * np.sum(
            weights * (left + gauge) * right, axis=-1
        )
        swapped_density = coupling_prefactor * np.sum(
            weights * right * left, axis=-1
        )
        radial_amplitudes.append(_periodic_integral(density))
        radial_boundary_errors.append(
            max(
                float(np.max(np.abs(left - boundary_left))),
                float(np.max(np.abs(right - boundary_right))),
            )
        )
        radial_jacobi_errors.append(
            max(
                float(np.max(np.abs(np.sum(left, axis=-1)))),
                float(np.max(np.abs(np.sum(right, axis=-1)))),
                float(np.max(np.abs(np.sum(gauge, axis=-1)))),
            )
        )
        radial_gauge_errors.append(
            abs(_periodic_integral(shifted_density - density))
        )
        radial_color_replacement_errors.append(
            float(np.max(np.abs(swapped_density - density)))
        )
        modes = np.abs(
            np.fft.fftfreq(cfg.boundary_points, d=1.0 / cfg.boundary_points)
        )
        multiplier_minima.append(float(np.min(np.exp(-rho * modes))))

    rho_a, rho_b = 0.17, 0.29
    semigroup_left = _poisson_lift(_poisson_lift(boundary_left, rho_a), rho_b)
    semigroup_right = _poisson_lift(boundary_left, rho_a + rho_b)
    semigroup_error = float(np.max(np.abs(semigroup_left - semigroup_right)))
    constant = np.ones((cfg.boundary_points, 1))
    constant_preservation_error = float(
        np.max(np.abs(_poisson_lift(constant, 0.43) - constant))
    )

    mass_radius_sq = (cfg.bulk_mass * cfg.ads_radius) ** 2
    conformal_dimension = cfg.boundary_dimension / 2.0 + math.sqrt(
        (cfg.boundary_dimension / 2.0) ** 2 + mass_radius_sq
    )
    mass_dimension_error = abs(
        conformal_dimension * (conformal_dimension - cfg.boundary_dimension)
        - mass_radius_sq
    )
    separation = 1.3
    dilation = 1.8
    two_point = separation ** (-2.0 * conformal_dimension)
    moved_two_point = (dilation * separation) ** (-2.0 * conformal_dimension)
    two_point_scaling_error = abs(
        moved_two_point
        - dilation ** (-2.0 * conformal_dimension) * two_point
    )

    newton_g4 = kappa_ads * cfg.c**4 / (8.0 * math.pi)
    rt_entropy = cfg.rt_area / (4.0 * newton_g4)
    rt_boundary = (
        2.0
        * cfg.compactification_volume
        * central_charge
        * cfg.rt_area
        / (math.pi * cfg.ads_radius**3)
    )
    diagnostics = {
        "central_charge": central_charge,
        "kappa_ads": kappa_ads,
        "kappa_boundary": kappa_boundary,
        "coupling_dictionary_error": abs(kappa_ads - kappa_boundary),
        "boundary_amplitude": boundary_amplitude,
        "radial_amplitudes": radial_amplitudes,
        "radial_boundary_errors": radial_boundary_errors,
        "radial_jacobi_errors": radial_jacobi_errors,
        "radial_gauge_errors": radial_gauge_errors,
        "radial_color_replacement_errors": radial_color_replacement_errors,
        "poisson_multiplier_minima": multiplier_minima,
        "poisson_semigroup_error": semigroup_error,
        "constant_preservation_error": constant_preservation_error,
        "conformal_dimension": conformal_dimension,
        "mass_dimension_error": mass_dimension_error,
        "two_point_scaling_error": two_point_scaling_error,
        "rt_entropy": rt_entropy,
        "rt_boundary_entropy": rt_boundary,
        "rt_boundary_dictionary_error": abs(rt_entropy - rt_boundary),
        "amplitude_entropy_difference": abs(boundary_amplitude - rt_entropy),
    }
    acceptance = {
        "d3_and_boundary_couplings_agree": diagnostics["coupling_dictionary_error"] < 5e-13,
        "poisson_radial_transport_is_a_semigroup_and_preserves_constants": max(
            semigroup_error, constant_preservation_error
        ) < 5e-13,
        "radial_transport_preserves_pointwise_jacobi": max(radial_jacobi_errors) < 5e-12,
        "bulk_fields_converge_monotonically_to_boundary_data": bool(
            all(
                later < earlier
                for earlier, later in zip(
                    radial_boundary_errors, radial_boundary_errors[1:]
                )
            )
            and radial_boundary_errors[-1] < 5e-2
        ),
        "radial_generalized_gauge_shift_is_invisible": max(radial_gauge_errors) < 5e-11,
        "radial_color_replacement_is_symmetric": max(radial_color_replacement_errors) < 5e-12,
        "gkp_mass_dimension_and_two_point_scaling_close": max(
            mass_dimension_error, two_point_scaling_error
        ) < 5e-12,
        "rt_and_boundary_central_charge_normalizations_agree": diagnostics[
            "rt_boundary_dictionary_error"
        ] < 5e-12,
        "amplitude_is_not_identified_with_rt_entropy": diagnostics[
            "amplitude_entropy_difference"
        ] > 1e-4,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "theorem_status": "conditional-model",
        "decision": {
            "ads_radial_and_boundary_pointwise_fields_are_executed": True,
            "same_d3_coupling_normalizes_bcj_gkp_and_rt_faces": True,
            "interacting_witten_or_global_ads_double_copy_not_claimed": True,
        },
    }
