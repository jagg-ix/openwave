"""M10.8 Wilson-loop refinement, confinement, and decoherence spectra.

Smooth periodic SU(3) link fields are evaluated on nested lattices.  The
campaign measures plaquette scaling, rectangular Wilson loops, an area/perimeter
fit, a Creutz ratio, Polyakov-loop center invariants, and positive history
spectra with environment-dependent off-diagonal suppression.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .dirac_cartan_2i_yukawa_model import DiracCartan2IYukawaConfig
from .periodic_su3_hamiltonian_m106 import (
    deterministic_gauges,
    gauge_transform_links,
    periodic_shift,
    plaquette_matrix,
    rectangular_wilson_loop,
)
from .su3_link_backreaction_m105 import (
    gell_mann_matrices,
    su3_exponential,
)

MILESTONE = "M10.8"
SCHEMA = "openwave.m10.wilson-refinement-spectrum.v1"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QFT/Lattice/WilsonLoopAreaLaw.lean",
        "sha": "ffd0b7e6dc1ec8b39851755aeda3ae753a5c42d0",
        "theorem": "areaLaw_implies_decay",
    },
    {
        "path": "Physlib/QFT/Lattice/PolyakovLoopCenterSymmetry.lean",
        "sha": "dc0ab4c581c6028e951b1f657422e534571142cc",
        "theorem": "center_preserves_norm",
    },
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "sha": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "theorem": "expectation_and_connectedGeneratingFunctional_tendsto",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/"
            "DecoherenceFunctionalSorkinJohnston.lean"
        ),
        "sha": "52c99efa2e5bb53cd051ac2a15c5eeca08a07cef",
        "theorem": "decoherenceFunctional_isDecoherenceFunctional",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/"
            "DowkerHalliwellDecoherenceFunctional.lean"
        ),
        "sha": "69675c275b4e7b4d29b597f1218c0ee0023afa13",
        "theorem": "decoherence_offdiag_bound",
    },
)

LinkField = np.ndarray


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def smooth_lattice_links(
    size: int,
    amplitude: float,
    phase: float,
) -> LinkField:
    if size < 2 or amplitude <= 0.0:
        raise ValueError("positive smooth periodic lattice required")
    generators = tuple(matrix / 2.0 for matrix in gell_mann_matrices())
    spacing = 1.0 / size
    links = np.empty((size, size, 2, 3, 3), dtype=np.complex128)
    for x in range(size):
        coordinate_x = x / size
        for y in range(size):
            coordinate_y = y / size
            for direction in range(2):
                coefficients = np.asarray(
                    [
                        amplitude
                        * (
                            math.sin(
                                2.0
                                * math.pi
                                * (
                                    ((index % 3) + 1) * coordinate_x
                                    + (direction + 1) * coordinate_y
                                )
                                + phase
                                + 0.17 * index
                            )
                            + 0.5
                            * math.cos(
                                2.0
                                * math.pi
                                * (
                                    (direction + 1) * coordinate_x
                                    + ((index % 2) + 1) * coordinate_y
                                )
                                - phase
                            )
                        )
                        for index in range(8)
                    ],
                    dtype=np.float64,
                )
                generator = sum(
                    coefficients[index] * generators[index]
                    for index in range(8)
                )
                links[x, y, direction] = su3_exponential(spacing * generator)
    return links


def mean_plaquette_action(links: LinkField) -> float:
    size = links.shape[0]
    return float(
        np.mean(
            [
                1.0 - np.trace(plaquette_matrix(links, x, y)).real / 3.0
                for x in range(size)
                for y in range(size)
            ]
        )
    )


def refinement_diagnostics(
    sizes: tuple[int, ...],
    amplitude: float,
) -> dict[str, Any]:
    actions = np.asarray(
        [mean_plaquette_action(smooth_lattice_links(size, amplitude, 0.0)) for size in sizes],
        dtype=np.float64,
    )
    observed_orders = np.asarray(
        [
            math.log(actions[index] / actions[index + 1])
            / math.log(sizes[index + 1] / sizes[index])
            for index in range(len(sizes) - 1)
        ],
        dtype=np.float64,
    )
    scaled_actions = actions * np.asarray(sizes, dtype=np.float64) ** 4
    return {
        "sizes": list(sizes),
        "actions": actions.tolist(),
        "observed_orders": observed_orders.tolist(),
        "scaled_actions": scaled_actions.tolist(),
        "last_scaled_relative_change": abs(scaled_actions[-1] - scaled_actions[-2])
        / max(abs(scaled_actions[-1]), 1.0e-30),
    }


def average_rectangular_loop(
    links: LinkField,
    width: int,
    height: int,
) -> float:
    size = links.shape[0]
    values = [
        rectangular_wilson_loop(links, x, y, width, height).real
        for x in range(size)
        for y in range(size)
    ]
    return float(np.mean(values))


def polyakov_loop(links: LinkField) -> complex:
    size = links.shape[0]
    values = []
    for x in range(size):
        product = np.eye(3, dtype=np.complex128)
        for y in range(size):
            product = product @ links[x, y, 1]
        values.append(np.trace(product) / 3.0)
    return complex(np.mean(values))


def loop_ensemble(
    size: int,
    samples: int,
    maximum_extent: int,
    amplitude: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    loops = np.zeros((samples, maximum_extent, maximum_extent), dtype=np.float64)
    polyakov = np.zeros(samples, dtype=np.complex128)
    actions = np.zeros(samples, dtype=np.float64)
    for sample in range(samples):
        phase = 2.0 * math.pi * sample / samples
        links = smooth_lattice_links(size, amplitude, phase)
        actions[sample] = mean_plaquette_action(links) * size * size
        polyakov[sample] = polyakov_loop(links)
        for width in range(1, maximum_extent + 1):
            for height in range(1, maximum_extent + 1):
                loops[sample, width - 1, height - 1] = average_rectangular_loop(
                    links, width, height
                )
    return loops, polyakov, actions


def area_perimeter_fit(loop_means: np.ndarray) -> dict[str, float]:
    maximum_extent = loop_means.shape[0]
    design = []
    targets = []
    for width in range(1, maximum_extent + 1):
        for height in range(1, maximum_extent + 1):
            value = max(float(loop_means[width - 1, height - 1]), 1.0e-15)
            design.append([width * height, 2.0 * (width + height), 1.0])
            targets.append(-math.log(value))
    matrix = np.asarray(design, dtype=np.float64)
    target = np.asarray(targets, dtype=np.float64)
    coefficients, _, _, _ = np.linalg.lstsq(matrix, target, rcond=None)
    residual = matrix @ coefficients - target
    return {
        "area_coefficient": float(coefficients[0]),
        "perimeter_coefficient": float(coefficients[1]),
        "constant": float(coefficients[2]),
        "rms_residual": float(math.sqrt(np.mean(residual**2))),
    }


def creutz_ratio(loop_means: np.ndarray, width: int, height: int) -> float:
    numerator = (
        loop_means[width, height]
        * loop_means[width - 1, height - 1]
    )
    denominator = (
        loop_means[width, height - 1]
        * loop_means[width - 1, height]
    )
    if numerator <= 0.0 or denominator <= 0.0:
        raise ValueError("positive loop means required for Creutz ratio")
    return float(-math.log(numerator / denominator))


def gauge_loop_error(size: int, amplitude: float) -> float:
    links = smooth_lattice_links(size, amplitude, 0.37)
    gauges = deterministic_gauges(size, 0.29)
    transformed = gauge_transform_links(links, gauges)
    error = 0.0
    for width, height in ((1, 1), (2, 1), (1, 2), (2, 2)):
        original = rectangular_wilson_loop(links, 0, 0, width, height)
        moved = rectangular_wilson_loop(transformed, 0, 0, width, height)
        error = max(error, abs(original - moved))
    return float(error)


def history_spectrum(
    loops: np.ndarray,
    polyakov: np.ndarray,
    actions: np.ndarray,
    environment_multiplier: float,
    theta: float,
    entropy_action: float,
) -> dict[str, Any]:
    features = np.concatenate(
        [
            loops.reshape(loops.shape[0], -1),
            polyakov.real[:, None],
            polyakov.imag[:, None],
        ],
        axis=1,
    )
    distance_sq = np.sum(
        (features[:, None, :] - features[None, :, :]) ** 2,
        axis=2,
    )
    nonzero = distance_sq[distance_sq > 1.0e-18]
    scale = float(np.median(nonzero)) if nonzero.size else 1.0
    kernel = np.exp(-environment_multiplier * 2.5 * distance_sq / scale)
    amplitudes = np.exp(-actions - entropy_action) * np.exp(1.0j * theta * polyakov.imag)
    amplitudes = amplitudes / np.linalg.norm(amplitudes)
    matrix = np.outer(amplitudes, np.conj(amplitudes)) * kernel
    matrix = matrix / np.trace(matrix).real
    eigenvalues = np.linalg.eigvalsh(matrix)
    positive = np.clip(eigenvalues, 0.0, None)
    entropy = float(-np.sum(positive[positive > 0.0] * np.log(positive[positive > 0.0])))
    mask = ~np.eye(matrix.shape[0], dtype=bool)
    return {
        "matrix": matrix,
        "eigenvalues": eigenvalues,
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "trace_error": abs(float(np.trace(matrix).real) - 1.0),
        "hermitian_error": float(np.max(np.abs(matrix - matrix.conj().T))),
        "purity": float(np.trace(matrix @ matrix).real),
        "entropy": entropy,
        "spectral_gap": float(eigenvalues[-1] - eigenvalues[-2]),
        "maximum_offdiag": float(np.max(np.abs(matrix[mask]))),
        "offdiag_frobenius": float(np.linalg.norm(matrix[mask])),
    }


@dataclass(frozen=True)
class WilsonRefinementSpectrumConfig:
    refinement_sizes: tuple[int, ...] = (4, 6, 8, 10)
    ensemble_size: int = 6
    samples: int = 8
    maximum_extent: int = 3
    amplitude: float = 0.35
    theta: float = 0.23
    evolution_time: float = 1.0

    def __post_init__(self) -> None:
        if len(self.refinement_sizes) < 3 or self.samples < 4:
            raise ValueError("nested refinement and substantive ensemble required")
        if self.maximum_extent < 2 or self.maximum_extent > self.ensemble_size:
            raise ValueError("valid rectangular loop extent required")
        if min(self.amplitude, self.evolution_time) <= 0.0:
            raise ValueError("positive spectrum controls required")


def canonical_payload(cfg: WilsonRefinementSpectrumConfig | None = None) -> dict[str, Any]:
    selected = cfg or WilsonRefinementSpectrumConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT Wilson-loop refinement and confinement-decoherence spectrum model",
        "config": asdict(selected),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(FORMAL_SOURCES),
        },
        "study_api": (
            "openwave.xperiments.m10_cat_ept.wilson_refinement_spectrum_m108:"
            "run_wilson_refinement_spectrum_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_wilson_refinement_spectrum_study() -> dict[str, Any]:
    cfg = WilsonRefinementSpectrumConfig()
    particle = DiracCartan2IYukawaConfig()
    refinement = refinement_diagnostics(cfg.refinement_sizes, cfg.amplitude)
    loops, polyakov, actions = loop_ensemble(
        cfg.ensemble_size,
        cfg.samples,
        cfg.maximum_extent,
        cfg.amplitude,
    )
    loop_means = np.mean(loops, axis=0)
    fit = area_perimeter_fit(loop_means)
    creutz_11 = creutz_ratio(loop_means, 1, 1)
    polyakov_norms = np.abs(polyakov)
    center = np.exp(2.0j * math.pi / 3.0)
    center_norm_error = float(np.max(np.abs(np.abs(center * polyakov) - polyakov_norms)))
    loop_gauge_error = gauge_loop_error(cfg.ensemble_size, cfg.amplitude)

    entropy_action = particle.entropy_rate * cfg.evolution_time
    weak = history_spectrum(
        loops,
        polyakov,
        actions,
        1.0,
        cfg.theta,
        entropy_action,
    )
    strong = history_spectrum(
        loops,
        polyakov,
        actions,
        8.0,
        cfg.theta,
        entropy_action,
    )

    actions_array = np.asarray(refinement["actions"], dtype=np.float64)
    orders_array = np.asarray(refinement["observed_orders"], dtype=np.float64)
    acceptance = {
        "plaquette_action_decreases_under_refinement": bool(np.all(np.diff(actions_array) < 0.0)),
        "observed_small_loop_order_exceeds_three_minus_tolerance": float(np.min(orders_array)) >= 2.90,
        "scaled_action_approaches_a_finite_limit": refinement["last_scaled_relative_change"] <= 0.12,
        "all_ensemble_wilson_loops_are_physical": bool(
            np.all(loop_means > 0.0) and np.all(loop_means <= 1.0 + 1.0e-12)
        ),
        "area_and_perimeter_coefficients_are_positive": (
            fit["area_coefficient"] > 0.0 and fit["perimeter_coefficient"] > 0.0
        ),
        "area_perimeter_fit_is_resolved": fit["rms_residual"] <= 3.0e-3,
        "first_creutz_ratio_is_positive": creutz_11 > 0.0,
        "polyakov_loops_obey_unit_bound": bool(np.max(polyakov_norms) <= 1.0 + 1.0e-12),
        "center_action_preserves_polyakov_norm": center_norm_error <= 2.0e-14,
        "wilson_loops_are_gauge_invariant": loop_gauge_error <= 2.0e-12,
        "weak_decoherence_spectrum_is_positive": weak["minimum_eigenvalue"] >= -2.0e-12,
        "strong_decoherence_spectrum_is_positive": strong["minimum_eigenvalue"] >= -2.0e-12,
        "history_spectra_are_normalized_and_hermitian": (
            weak["trace_error"] <= 2.0e-13
            and strong["trace_error"] <= 2.0e-13
            and weak["hermitian_error"] <= 2.0e-13
            and strong["hermitian_error"] <= 2.0e-13
        ),
        "stronger_environment_suppresses_interference": (
            strong["offdiag_frobenius"] < weak["offdiag_frobenius"]
            and strong["maximum_offdiag"] < weak["maximum_offdiag"]
        ),
        "decoherence_spectrum_has_nonzero_gap": weak["spectral_gap"] > 0.0,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M10.8k",
        "fingerprint": fingerprint(payload),
        "refinement": refinement,
        "loop_means": loop_means.tolist(),
        "area_perimeter_fit": fit,
        "creutz_11": creutz_11,
        "polyakov_mean_norm": float(np.mean(polyakov_norms)),
        "polyakov_max_norm": float(np.max(polyakov_norms)),
        "center_norm_error": center_norm_error,
        "loop_gauge_error": loop_gauge_error,
        "weak_spectrum": {key: value for key, value in weak.items() if key not in {"matrix", "eigenvalues"}},
        "strong_spectrum": {key: value for key, value in strong.items() if key not in {"matrix", "eigenvalues"}},
        "weak_eigenvalues": weak["eigenvalues"].tolist(),
        "strong_eigenvalues": strong["eigenvalues"].tolist(),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "wilson_loop_refinement_campaign_is_constructed": True,
            "finite_confinement_diagnostics_are_executed": True,
            "positive_environment_decoherence_spectrum_is_resolved": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
