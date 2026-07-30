"""M10.5 non-Abelian SU(3) link transport and color backreaction.

This module replaces the center-only Z3 histories of M10.4 with genuine
matrix-valued SU(3) links.  A four-link plaquette is transformed by independent
local gauge matrices, coupled to quark color-density currents, and advanced by
one gauge-covariant backreaction step.
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
from .qcd_functional_decoherence_m104 import normalized_expectation
from .second_quantized_fock_m103 import run_second_quantized_fock_study

MILESTONE = "M10.5"
SCHEMA = "openwave.m10.su3-link-backreaction.v1"

FORMAL_SOURCES = (
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/Particles/"
            "GellMannStructureConstants.lean"
        ),
        "sha": "b721ea5e04a72430a81d84c6a0a6c20b3f9558a0",
        "theorem": "gellMann_structure_constants",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/ChernSimons/"
            "NonAbelianThreeVertex.lean"
        ),
        "sha": "274cebd3eecdbf3711a31d7717216f959deaeaf2",
        "theorem": "three_vertex_jacobi",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/Particles/"
            "SuNGaugeSector.lean"
        ),
        "sha": "4585ddf9bc44396b5f9dce14321c4d6b2826cb8a",
        "theorem": "su3_adjoint_eq_gluonCount",
    },
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "sha": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "theorem": "sourceCoupledPartition_linearSource_hasDerivAt_zero",
    },
    {
        "path": (
            "Physlib/QuantumMechanics/ComplexAction/HorizonCell/"
            "QCDComplexActionUnification.lean"
        ),
        "sha": "c5d7108ec4781eee3068898d0d844b689230a6fa",
        "theorem": "qcd_theta_confinement_factorization",
    },
)

Matrix3 = np.ndarray
Links = tuple[Matrix3, Matrix3, Matrix3, Matrix3]
ColorVectors = tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
ColorCurrents = tuple[Matrix3, Matrix3, Matrix3, Matrix3]


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@lru_cache(maxsize=1)
def gell_mann_matrices() -> tuple[Matrix3, ...]:
    """Return the eight Hermitian traceless Gell-Mann generators."""
    imaginary = 1.0j
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray(
            [[0, -imaginary, 0], [imaginary, 0, 0], [0, 0, 0]],
            dtype=np.complex128,
        ),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=np.complex128),
        np.asarray(
            [[0, 0, -imaginary], [0, 0, 0], [imaginary, 0, 0]],
            dtype=np.complex128,
        ),
        np.asarray([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=np.complex128),
        np.asarray(
            [[0, 0, 0], [0, 0, -imaginary], [0, imaginary, 0]],
            dtype=np.complex128,
        ),
        np.asarray(
            [[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=np.complex128
        )
        / math.sqrt(3.0),
    )


def commutator(left: Matrix3, right: Matrix3) -> Matrix3:
    return np.asarray(left @ right - right @ left, dtype=np.complex128)


def su3_exponential(generator: Matrix3) -> Matrix3:
    """Exponentiate one Hermitian traceless generator to SU(3)."""
    hermitian = 0.5 * (generator + generator.conj().T)
    hermitian -= np.trace(hermitian).real * np.eye(3) / 3.0
    eigenvalues, eigenvectors = np.linalg.eigh(hermitian)
    unitary = (eigenvectors * np.exp(1.0j * eigenvalues)) @ eigenvectors.conj().T
    determinant = np.linalg.det(unitary)
    unitary *= np.exp(-1.0j * np.angle(determinant) / 3.0)
    return np.asarray(unitary, dtype=np.complex128)


def link_from_coefficients(coefficients: np.ndarray, scale: float) -> Matrix3:
    matrices = gell_mann_matrices()
    generator = sum(
        float(coefficients[index]) * matrices[index] / 2.0 for index in range(8)
    )
    return su3_exponential(scale * generator)


def plaquette_matrix(links: Links) -> Matrix3:
    product = np.eye(3, dtype=np.complex128)
    for link in links:
        product = product @ link
    return np.asarray(product, dtype=np.complex128)


def wilson_action(links: Links) -> float:
    return float(1.0 - np.trace(plaquette_matrix(links)).real / 3.0)


def oriented_plaquette_observable(links: Links) -> float:
    return float(np.trace(plaquette_matrix(links)).imag / 3.0)


def local_gauge_transform(links: Links, gauges: Links) -> Links:
    return tuple(
        np.asarray(
            gauges[index]
            @ links[index]
            @ gauges[(index + 1) % 4].conj().T,
            dtype=np.complex128,
        )
        for index in range(4)
    )  # type: ignore[return-value]


def normalize_color_vector(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0 or not math.isfinite(norm):
        raise ValueError("nonzero finite color vector required")
    return np.asarray(vector / norm, dtype=np.complex128)


def color_current(vector: np.ndarray) -> Matrix3:
    normalized = normalize_color_vector(vector)
    density = np.outer(normalized, np.conj(normalized))
    return np.asarray(density - np.eye(3) * np.trace(density) / 3.0, dtype=np.complex128)


def color_currents(vectors: ColorVectors) -> ColorCurrents:
    return tuple(color_current(vector) for vector in vectors)  # type: ignore[return-value]


def transform_color_vectors(vectors: ColorVectors, gauges: Links) -> ColorVectors:
    return tuple(
        np.asarray(gauges[index] @ vectors[index], dtype=np.complex128)
        for index in range(4)
    )  # type: ignore[return-value]


def current_gradient_on_link(
    link: Matrix3, source_current: Matrix3, target_current: Matrix3
) -> Matrix3:
    transported_target = link @ target_current @ link.conj().T
    return np.asarray(source_current - transported_target, dtype=np.complex128)


def backreaction_step(links: Links, currents: ColorCurrents, step: float) -> Links:
    """Apply one gauge-covariant color-current gradient step to all links."""
    updated = []
    for index, link in enumerate(links):
        gradient = current_gradient_on_link(
            link, currents[index], currents[(index + 1) % 4]
        )
        updated.append(su3_exponential(step * gradient) @ link)
    return tuple(np.asarray(link, dtype=np.complex128) for link in updated)  # type: ignore[return-value]


def source_coupled_partition(
    weights: np.ndarray, source: complex, observable: np.ndarray
) -> complex:
    return complex(np.sum(weights * np.exp(source * observable)))


@dataclass(frozen=True)
class SU3LinkBackreactionConfig:
    samples: int = 24
    seed: int = 105
    link_scale: float = 0.35
    gauge_scale: float = 0.55
    backreaction_step: float = 0.07
    inverse_coupling: float = 0.80
    theta: float = 0.23
    occupation: int = 2
    evolution_time: float = 1.25
    source_step: float = 1.0e-4

    def __post_init__(self) -> None:
        if self.samples < 8 or self.occupation < 0:
            raise ValueError("at least eight samples and nonnegative occupation required")
        if min(
            self.link_scale,
            self.gauge_scale,
            self.backreaction_step,
            self.evolution_time,
            self.source_step,
        ) <= 0.0:
            raise ValueError("positive SU3 campaign controls required")
        if self.inverse_coupling < 0.0:
            raise ValueError("nonnegative inverse coupling required")


@dataclass(frozen=True)
class SU3LinkBackreactionState:
    links: Links
    color_vectors: ColorVectors
    currents: ColorCurrents
    wilson_action_before: float
    wilson_action_after: float
    oriented_observable: float

    def manifest(self) -> dict[str, Any]:
        return {
            "schema": "openwave.m10.su3-link-backreaction-state.v1",
            "wilson_action_before": self.wilson_action_before,
            "wilson_action_after": self.wilson_action_after,
            "oriented_observable": self.oriented_observable,
        }


def deterministic_color_vectors(sample: int) -> ColorVectors:
    vectors = []
    for vertex in range(4):
        raw = np.asarray(
            [
                1.0 + 0.05 * sample,
                np.exp(1.0j * (0.31 * (sample + 1) + 0.20 * vertex)),
                (0.70 + 0.03 * vertex)
                * np.exp(-1.0j * (0.17 * sample + 0.11 * vertex)),
            ],
            dtype=np.complex128,
        )
        vectors.append(normalize_color_vector(raw))
    return tuple(vectors)  # type: ignore[return-value]


def construct_link_state(
    cfg: SU3LinkBackreactionConfig = SU3LinkBackreactionConfig(),
    *,
    sample: int = 0,
) -> SU3LinkBackreactionState:
    if sample < 0 or sample >= cfg.samples:
        raise ValueError("sample index outside the configured ensemble")
    random = np.random.default_rng(cfg.seed)
    coefficients = random.normal(size=(cfg.samples, 4, 8))[sample]
    links = tuple(
        link_from_coefficients(coefficients[index], cfg.link_scale)
        for index in range(4)
    )
    vectors = deterministic_color_vectors(sample)
    currents = color_currents(vectors)
    updated = backreaction_step(links, currents, cfg.backreaction_step)
    return SU3LinkBackreactionState(
        links=links,  # type: ignore[arg-type]
        color_vectors=vectors,
        currents=currents,
        wilson_action_before=wilson_action(links),  # type: ignore[arg-type]
        wilson_action_after=wilson_action(updated),  # type: ignore[arg-type]
        oriented_observable=oriented_plaquette_observable(links),  # type: ignore[arg-type]
    )


def gell_mann_diagnostics() -> dict[str, float]:
    matrices = gell_mann_matrices()
    normalization_error = max(
        abs(np.trace(matrices[left] @ matrices[right]) - (2.0 if left == right else 0.0))
        for left in range(8)
        for right in range(8)
    )
    traceless_error = max(abs(np.trace(matrix)) for matrix in matrices)
    hermitian_error = max(
        float(np.max(np.abs(matrix - matrix.conj().T))) for matrix in matrices
    )
    commutator_error = float(
        np.max(np.abs(commutator(matrices[0], matrices[1]) - 2.0j * matrices[2]))
    )
    jacobi = (
        commutator(matrices[0], commutator(matrices[1], matrices[3]))
        + commutator(matrices[1], commutator(matrices[3], matrices[0]))
        + commutator(matrices[3], commutator(matrices[0], matrices[1]))
    )
    fundamental_casimir = sum((matrix / 2.0) @ (matrix / 2.0) for matrix in matrices)
    casimir_error = float(
        np.max(np.abs(fundamental_casimir - (4.0 / 3.0) * np.eye(3)))
    )
    return {
        "normalization_error": float(normalization_error),
        "traceless_error": float(traceless_error),
        "hermitian_error": hermitian_error,
        "commutator_12_error": commutator_error,
        "jacobi_error": float(np.max(np.abs(jacobi))),
        "fundamental_casimir_error": casimir_error,
    }


def canonical_payload(
    cfg: SU3LinkBackreactionConfig | None = None,
) -> dict[str, Any]:
    selected = cfg or SU3LinkBackreactionConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT non-Abelian SU3 link and color-backreaction model",
        "config": asdict(selected),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(FORMAL_SOURCES),
            "second_quantized_bridge_pr": 42,
        },
        "construction_api": (
            "openwave.xperiments.m10_cat_ept.su3_link_backreaction_m105:"
            "construct_link_state"
        ),
        "study_api": (
            "openwave.xperiments.m10_cat_ept.su3_link_backreaction_m105:"
            "run_su3_link_backreaction_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_su3_link_backreaction_study() -> dict[str, Any]:
    cfg = SU3LinkBackreactionConfig()
    particle = DiracCartan2IYukawaConfig()
    fock = run_second_quantized_fock_study()
    random = np.random.default_rng(cfg.seed)
    link_coefficients = random.normal(size=(cfg.samples, 4, 8))
    gauge_coefficients = random.normal(size=(cfg.samples, 4, 8))

    actions = []
    updated_actions = []
    observables = []
    maximum_unitarity_error = 0.0
    maximum_determinant_error = 0.0
    maximum_plaquette_covariance_error = 0.0
    maximum_wilson_gauge_error = 0.0
    maximum_current_covariance_error = 0.0
    maximum_backreaction_covariance_error = 0.0
    maximum_current_reconstruction_error = 0.0
    minimum_nonabelian_commutator = math.inf
    minimum_action_shift = math.inf

    matrices = gell_mann_matrices()
    for sample in range(cfg.samples):
        links: Links = tuple(
            link_from_coefficients(link_coefficients[sample, index], cfg.link_scale)
            for index in range(4)
        )  # type: ignore[assignment]
        gauges: Links = tuple(
            link_from_coefficients(gauge_coefficients[sample, index], cfg.gauge_scale)
            for index in range(4)
        )  # type: ignore[assignment]
        vectors = deterministic_color_vectors(sample)
        currents = color_currents(vectors)
        transformed_links = local_gauge_transform(links, gauges)
        transformed_vectors = transform_color_vectors(vectors, gauges)
        transformed_currents = color_currents(transformed_vectors)
        updated_links = backreaction_step(links, currents, cfg.backreaction_step)
        updated_transformed = backreaction_step(
            transformed_links, transformed_currents, cfg.backreaction_step
        )

        plaquette = plaquette_matrix(links)
        transformed_plaquette = plaquette_matrix(transformed_links)
        maximum_plaquette_covariance_error = max(
            maximum_plaquette_covariance_error,
            float(
                np.max(
                    np.abs(
                        transformed_plaquette
                        - gauges[0] @ plaquette @ gauges[0].conj().T
                    )
                )
            ),
        )
        maximum_wilson_gauge_error = max(
            maximum_wilson_gauge_error,
            abs(wilson_action(transformed_links) - wilson_action(links)),
        )
        maximum_current_covariance_error = max(
            maximum_current_covariance_error,
            max(
                float(
                    np.max(
                        np.abs(
                            transformed_currents[index]
                            - gauges[index]
                            @ currents[index]
                            @ gauges[index].conj().T
                        )
                    )
                )
                for index in range(4)
            ),
        )
        maximum_backreaction_covariance_error = max(
            maximum_backreaction_covariance_error,
            max(
                float(
                    np.max(
                        np.abs(
                            updated_transformed[index]
                            - gauges[index]
                            @ updated_links[index]
                            @ gauges[(index + 1) % 4].conj().T
                        )
                    )
                )
                for index in range(4)
            ),
        )

        for current in currents:
            coefficients = np.asarray(
                [np.trace(matrix @ current).real for matrix in matrices],
                dtype=np.float64,
            )
            reconstructed = sum(
                coefficients[index] * matrices[index] / 2.0 for index in range(8)
            )
            maximum_current_reconstruction_error = max(
                maximum_current_reconstruction_error,
                float(np.max(np.abs(reconstructed - current))),
            )

        for link in (*links, *updated_links):
            maximum_unitarity_error = max(
                maximum_unitarity_error,
                float(np.max(np.abs(link.conj().T @ link - np.eye(3)))),
            )
            maximum_determinant_error = max(
                maximum_determinant_error, abs(np.linalg.det(link) - 1.0)
            )

        nonabelianity = max(
            float(np.linalg.norm(commutator(links[left], links[right])))
            for left in range(4)
            for right in range(left + 1, 4)
        )
        minimum_nonabelian_commutator = min(
            minimum_nonabelian_commutator, nonabelianity
        )
        before = wilson_action(links)
        after = wilson_action(updated_links)
        minimum_action_shift = min(minimum_action_shift, abs(after - before))
        actions.append(before)
        updated_actions.append(after)
        observables.append(oriented_plaquette_observable(links))

    action_array = np.asarray(actions, dtype=np.float64)
    updated_action_array = np.asarray(updated_actions, dtype=np.float64)
    observable_array = np.asarray(observables, dtype=np.float64)
    entropy_action = cfg.occupation * particle.entropy_rate * cfg.evolution_time
    weights = np.asarray(
        np.exp(
            1.0j * cfg.theta * observable_array
            - cfg.inverse_coupling * action_array / particle.hbar
            - entropy_action / particle.hbar
        ),
        dtype=np.complex128,
    )
    updated_weights = np.asarray(
        np.exp(
            1.0j * cfg.theta * observable_array
            - cfg.inverse_coupling * updated_action_array / particle.hbar
            - entropy_action / particle.hbar
        ),
        dtype=np.complex128,
    )
    expectation = normalized_expectation(weights, observable_array)
    connected = normalized_expectation(weights, observable_array**2) - expectation**2
    step = cfg.source_step
    log_plus = np.log(source_coupled_partition(weights, step, observable_array))
    log_zero = np.log(source_coupled_partition(weights, 0.0, observable_array))
    log_minus = np.log(source_coupled_partition(weights, -step, observable_array))
    first_numerical = (log_plus - log_minus) / (2.0 * step)
    second_numerical = (log_plus - 2.0 * log_zero + log_minus) / (step**2)
    partition = complex(np.sum(weights))
    updated_partition = complex(np.sum(updated_weights))
    relative_partition_shift = abs(updated_partition - partition) / max(abs(partition), 1.0e-30)

    algebra = gell_mann_diagnostics()
    acceptance = {
        "gell_mann_basis_closes": max(algebra.values()) <= 2.0e-12,
        "all_links_are_su3": (
            maximum_unitarity_error <= 2.0e-12
            and maximum_determinant_error <= 2.0e-12
        ),
        "sampled_links_are_genuinely_nonabelian": minimum_nonabelian_commutator >= 1.0e-3,
        "plaquette_transforms_by_local_conjugation": maximum_plaquette_covariance_error <= 2.0e-12,
        "wilson_action_is_locally_gauge_invariant": maximum_wilson_gauge_error <= 2.0e-12,
        "color_current_transforms_in_the_adjoint": maximum_current_covariance_error <= 2.0e-12,
        "color_current_reconstructs_from_eight_generators": maximum_current_reconstruction_error <= 2.0e-12,
        "backreaction_is_gauge_covariant": maximum_backreaction_covariance_error <= 2.0e-12,
        "backreaction_preserves_su3_links": (
            maximum_unitarity_error <= 2.0e-12
            and maximum_determinant_error <= 2.0e-12
        ),
        "backreaction_changes_every_sampled_wilson_action": minimum_action_shift >= 1.0e-7,
        "source_derivative_inserts_oriented_plaquette": abs(first_numerical - expectation) <= 1.0e-8,
        "connected_second_derivative_closes": abs(second_numerical - connected) <= 1.0e-7,
        "color_backreaction_changes_the_partition": relative_partition_shift >= 1.0e-5,
        "second_quantized_dependency_passes": bool(fock["passed"]),
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M10.5a-n",
        "fingerprint": fingerprint(payload),
        "gell_mann": algebra,
        "sample_count": cfg.samples,
        "minimum_wilson_action": float(np.min(action_array)),
        "maximum_wilson_action": float(np.max(action_array)),
        "mean_backreaction_action_shift": float(
            np.mean(updated_action_array - action_array)
        ),
        "minimum_backreaction_action_shift": float(minimum_action_shift),
        "minimum_nonabelian_commutator": float(minimum_nonabelian_commutator),
        "maximum_unitarity_error": maximum_unitarity_error,
        "maximum_determinant_error": float(maximum_determinant_error),
        "maximum_plaquette_covariance_error": maximum_plaquette_covariance_error,
        "maximum_wilson_gauge_error": maximum_wilson_gauge_error,
        "maximum_current_covariance_error": maximum_current_covariance_error,
        "maximum_current_reconstruction_error": maximum_current_reconstruction_error,
        "maximum_backreaction_covariance_error": maximum_backreaction_covariance_error,
        "source_first_derivative_error": float(abs(first_numerical - expectation)),
        "source_second_derivative_error": float(abs(second_numerical - connected)),
        "relative_partition_shift": float(relative_partition_shift),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "matrix_valued_su3_links_are_constructed": True,
            "local_gauge_covariance_is_executed": True,
            "color_fermion_backreaction_is_executed": True,
            "center_only_qcd_has_been_strictly_extended": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
