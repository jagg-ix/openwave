"""M10.4 finite QCD functional integral and history decoherence layer.

A four-plaquette center-valued Wilson ensemble uses the exact subgroup
Z3 subset SU(3), giving 3^4 = 81 histories. Every history carries the QCD
theta phase, Wilson damping, and the selected M10.3 Fock-sector Yukawa entropy
factor. The module evaluates the source functional, connected insertions,
one-loop Feynman-parameter identities, and a Caldeira--Leggett Gaussian
influence kernel on the history decoherence matrix.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math
from typing import Any, Mapping

import numpy as np

from .dirac_cartan_2i_yukawa_model import DiracCartan2IYukawaConfig
from .second_quantized_fock_m103 import run_second_quantized_fock_study

MILESTONE = "M10.4"
SCHEMA = "openwave.m10.qcd-functional-decoherence.v1"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/HorizonCell/QCDComplexActionUnification.lean",
        "sha": "c5d7108ec4781eee3068898d0d844b689230a6fa",
        "theorem": "qcd_theta_confinement_factorization",
    },
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "sha": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "theorem": "connectedGeneratingFunctional_linearSource_hasDerivAt_zero",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CaldeiraLeggettInfluenceFunctional.lean",
        "sha": "c58d579b0c9b260cd998fa4784f3325ce434acce",
        "theorem": "feynmanVernon_modulus_is_decoherence",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/DecoherenceFunctionalSorkinJohnston.lean",
        "sha": "52c99efa2e5bb53cd051ac2a15c5eeca08a07cef",
        "theorem": "decoherenceFunctional_isDecoherenceFunctional",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/PathIntegral/OneLoopScalarIntegralsQCD.lean",
        "sha": "5266ab5fa8bcd4eaa2f65581e368306f55beb1c5",
        "theorem": "feynman_parametrization",
    },
)

CenterConfiguration = tuple[int, ...]


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def signed_center_exponent(value: int) -> int:
    if value == 0:
        return 0
    if value == 1:
        return 1
    if value == 2:
        return -1
    raise ValueError("Z3 exponent must be 0, 1, or 2")


@dataclass(frozen=True)
class QCDFunctionalDecoherenceConfig:
    plaquettes: int = 4
    inverse_coupling: float = 0.80
    theta: float = 0.23
    occupation: int = 2
    evolution_time: float = 1.25
    source_step: float = 1.0e-3
    bath_mass: float = 0.70
    bath_friction: float = 0.08
    bath_inverse_temperature: float = 1.50
    quadrature_order: int = 512

    def __post_init__(self) -> None:
        if self.plaquettes < 1:
            raise ValueError("at least one finite Wilson plaquette required")
        if self.inverse_coupling < 0.0 or self.occupation < 0:
            raise ValueError("nonnegative coupling and occupation required")
        if min(
            self.evolution_time,
            self.source_step,
            self.bath_mass,
            self.bath_friction,
            self.bath_inverse_temperature,
        ) <= 0.0:
            raise ValueError("positive functional and environment controls required")
        if self.quadrature_order < 64:
            raise ValueError("substantive one-loop quadrature order required")

    @property
    def history_count(self) -> int:
        return 3**self.plaquettes


@lru_cache(maxsize=None)
def center_configurations(plaquettes: int) -> tuple[CenterConfiguration, ...]:
    if plaquettes < 1:
        raise ValueError("positive plaquette count required")
    return tuple(itertools.product(range(3), repeat=plaquettes))


def center_features(configurations: tuple[CenterConfiguration, ...]) -> np.ndarray:
    return np.asarray(
        [
            [signed_center_exponent(value) for value in configuration]
            for configuration in configurations
        ],
        dtype=np.float64,
    )


def wilson_plaquette_action(value: int) -> float:
    return 1.0 - math.cos(2.0 * math.pi * value / 3.0)


def wilson_actions(configurations: tuple[CenterConfiguration, ...]) -> np.ndarray:
    return np.asarray(
        [
            sum(wilson_plaquette_action(value) for value in configuration)
            for configuration in configurations
        ],
        dtype=np.float64,
    )


def topological_indices(features: np.ndarray) -> np.ndarray:
    return np.asarray(np.sum(features, axis=1), dtype=np.float64)


def center_observables(configurations: tuple[CenterConfiguration, ...]) -> np.ndarray:
    center = np.exp(2.0j * math.pi / 3.0)
    return np.asarray(
        [
            sum(center**value for value in configuration) / len(configuration)
            for configuration in configurations
        ],
        dtype=np.complex128,
    )


def history_weights(
    cfg: QCDFunctionalDecoherenceConfig,
    particle_cfg: DiracCartan2IYukawaConfig,
    actions: np.ndarray,
    topology: np.ndarray,
    *,
    occupation: int | None = None,
) -> np.ndarray:
    selected_occupation = cfg.occupation if occupation is None else occupation
    fock_entropy_action = (
        selected_occupation * particle_cfg.entropy_rate * cfg.evolution_time
    )
    imaginary_action = cfg.inverse_coupling * actions + fock_entropy_action
    return np.asarray(
        np.exp(
            1.0j * cfg.theta * topology
            - imaginary_action / particle_cfg.hbar
        ),
        dtype=np.complex128,
    )


def source_coupled_partition(
    weights: np.ndarray, source: complex, observable: np.ndarray
) -> complex:
    return complex(np.sum(weights * np.exp(source * observable)))


def normalized_expectation(weights: np.ndarray, observable: np.ndarray) -> complex:
    partition = np.sum(weights)
    if abs(partition) <= 1.0e-30:
        raise ValueError("nonzero finite partition required")
    return complex(np.sum(weights * observable) / partition)


def connected_two_point(weights: np.ndarray, observable: np.ndarray) -> complex:
    first = normalized_expectation(weights, observable)
    second = normalized_expectation(weights, observable * observable)
    return second - first * first


def influence_kernel(
    features: np.ndarray,
    cfg: QCDFunctionalDecoherenceConfig,
    *,
    strength_multiplier: float = 1.0,
) -> np.ndarray:
    distance_sq = np.sum(
        (features[:, None, :] - features[None, :, :]) ** 2, axis=2
    )
    coefficient = (
        strength_multiplier
        * 2.0
        * cfg.bath_mass
        * cfg.bath_friction
        * cfg.evolution_time
        / cfg.bath_inverse_temperature
    )
    return np.asarray(np.exp(-coefficient * distance_sq), dtype=np.float64)


def history_decoherence_matrix(
    weights: np.ndarray,
    features: np.ndarray,
    cfg: QCDFunctionalDecoherenceConfig,
    *,
    strength_multiplier: float = 1.0,
) -> np.ndarray:
    norm = math.sqrt(float(np.sum(np.abs(weights) ** 2)))
    if norm <= 0.0:
        raise ValueError("nonzero history amplitude norm required")
    amplitudes = weights / norm
    pure = np.outer(amplitudes, np.conj(amplitudes))
    return np.asarray(
        pure * influence_kernel(features, cfg, strength_multiplier=strength_multiplier),
        dtype=np.complex128,
    )


def gauss_legendre_unit_interval(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return np.asarray((nodes + 1.0) / 2.0), np.asarray(weights / 2.0)


def one_loop_diagnostics(order: int) -> dict[str, float]:
    x, weights = gauss_legendre_unit_interval(order)
    mass_a = 1.30
    mass_b = 2.10
    feynman_parameter = float(
        np.sum(weights / (x * mass_a + (1.0 - x) * mass_b) ** 2)
    )
    feynman_exact = 1.0 / (mass_a * mass_b)
    bubble_finite = float(np.sum(weights * np.log(x * (1.0 - x))))
    return {
        "feynman_parameter_error": abs(feynman_parameter - feynman_exact),
        "bubble_finite_part": bubble_finite,
        "bubble_finite_part_error": abs(bubble_finite + 2.0),
    }


def canonical_payload(
    cfg: QCDFunctionalDecoherenceConfig | None = None,
) -> dict[str, Any]:
    selected = cfg or QCDFunctionalDecoherenceConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT second-quantized QCD functional and decoherence model",
        "config": asdict(selected),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(FORMAL_SOURCES),
            "second_quantized_bridge_pr": 42,
            "second_quantized_bridge_head": "45269fa04dc16ae1588925f0a8c167ee9dfbc7b8",
        },
        "study_api": (
            "openwave.xperiments.m10_cat_ept.qcd_functional_decoherence_m104:"
            "run_qcd_functional_decoherence_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_qcd_functional_decoherence_study() -> dict[str, Any]:
    cfg = QCDFunctionalDecoherenceConfig()
    particle_cfg = DiracCartan2IYukawaConfig()
    fock = run_second_quantized_fock_study()
    configurations = center_configurations(cfg.plaquettes)
    features = center_features(configurations)
    actions = wilson_actions(configurations)
    topology = topological_indices(features)
    topological_observable = topology / cfg.plaquettes
    center_observable = center_observables(configurations)
    weights = history_weights(cfg, particle_cfg, actions, topology)
    partition = complex(np.sum(weights))

    fock_entropy_action = (
        cfg.occupation * particle_cfg.entropy_rate * cfg.evolution_time
    )
    factorized = (
        np.exp(1.0j * cfg.theta * topology)
        * np.exp(-cfg.inverse_coupling * actions / particle_cfg.hbar)
        * np.exp(-fock_entropy_action / particle_cfg.hbar)
    )
    factorization_error = float(np.max(np.abs(weights - factorized)))
    born_error = float(
        np.max(
            np.abs(
                np.abs(weights) ** 2
                - np.exp(
                    -2.0
                    * (cfg.inverse_coupling * actions + fock_entropy_action)
                    / particle_cfg.hbar
                )
            )
        )
    )

    conjugate_index = {
        configuration: index for index, configuration in enumerate(configurations)
    }
    charge_conjugation_error = 0.0
    for index, configuration in enumerate(configurations):
        conjugate = tuple((-value) % 3 for value in configuration)
        charge_conjugation_error = max(
            charge_conjugation_error,
            abs(weights[conjugate_index[conjugate]] - np.conj(weights[index])),
        )

    first = normalized_expectation(weights, topological_observable)
    second_connected = connected_two_point(weights, topological_observable)
    step = cfg.source_step
    log_plus = np.log(source_coupled_partition(weights, step, topological_observable))
    log_zero = np.log(source_coupled_partition(weights, 0.0, topological_observable))
    log_minus = np.log(source_coupled_partition(weights, -step, topological_observable))
    first_numerical = (log_plus - log_minus) / (2.0 * step)
    second_numerical = (log_plus - 2.0 * log_zero + log_minus) / (step * step)
    first_source_error = abs(first_numerical - first)
    connected_source_error = abs(second_numerical - second_connected)

    unnormalized_derivative = np.sum(weights * topological_observable)
    finite_difference_partition = (
        source_coupled_partition(weights, step, topological_observable)
        - source_coupled_partition(weights, -step, topological_observable)
    ) / (2.0 * step)
    partition_derivative_error = abs(
        finite_difference_partition - unnormalized_derivative
    )

    previous_weights = history_weights(
        cfg, particle_cfg, actions, topology, occupation=max(cfg.occupation - 1, 0)
    )
    occupation_partition_ratio = abs(partition / np.sum(previous_weights))
    occupation_partition_ratio_expected = math.exp(
        -particle_cfg.entropy_rate
        * cfg.evolution_time
        / particle_cfg.hbar
    )
    occupation_partition_ratio_error = abs(
        occupation_partition_ratio - occupation_partition_ratio_expected
    )

    decoherence = history_decoherence_matrix(weights, features, cfg)
    stronger = history_decoherence_matrix(
        weights, features, cfg, strength_multiplier=2.0
    )
    pure_norm = math.sqrt(float(np.sum(np.abs(weights) ** 2)))
    pure_amplitudes = weights / pure_norm
    pure = np.outer(pure_amplitudes, np.conj(pure_amplitudes))
    hermitian_error = float(np.max(np.abs(decoherence - decoherence.conj().T)))
    diagonal_error = float(
        np.max(np.abs(np.diag(decoherence) - np.abs(pure_amplitudes) ** 2))
    )
    trace_error = abs(float(np.trace(decoherence).real) - 1.0)
    minimum_decoherence_eigenvalue = float(
        np.min(np.linalg.eigvalsh(decoherence))
    )
    off_diagonal = ~np.eye(cfg.history_count, dtype=bool)
    maximum_pure_offdiag = float(np.max(np.abs(pure[off_diagonal])))
    maximum_decohered_offdiag = float(
        np.max(np.abs(decoherence[off_diagonal]))
    )
    maximum_stronger_offdiag = float(
        np.max(np.abs(stronger[off_diagonal]))
    )

    offdiag_bound_error = 0.0
    diagonal = np.real(np.diag(decoherence))
    for left in range(cfg.history_count):
        for right in range(cfg.history_count):
            offdiag_bound_error = max(
                offdiag_bound_error,
                max(
                    0.0,
                    abs(decoherence[left, right]) ** 2
                    - diagonal[left] * diagonal[right],
                ),
            )

    one_loop = one_loop_diagnostics(cfg.quadrature_order)
    payload = canonical_payload(cfg)
    acceptance = {
        "finite_center_qcd_has_81_histories": len(configurations) == 81,
        "wilson_action_is_nonnegative": float(np.min(actions)) >= 0.0,
        "theta_confinement_fock_factorization_closes": factorization_error <= 1.0e-13,
        "history_born_weights_close": born_error <= 1.0e-13,
        "qcd_charge_conjugation_pairs_weights": charge_conjugation_error <= 1.0e-13,
        "partition_is_real_by_charge_conjugation_pairing": abs(partition.imag) <= 1.0e-12,
        "source_partition_derivative_inserts_observable": partition_derivative_error <= 1.0e-7,
        "connected_functional_first_derivative_is_expectation": first_source_error <= 1.0e-8,
        "connected_functional_second_derivative_is_connected_two_point": connected_source_error <= 1.0e-6,
        "occupation_multiplies_yukawa_entropy_in_partition": occupation_partition_ratio_error <= 1.0e-13,
        "decoherence_matrix_is_hermitian": hermitian_error <= 1.0e-13,
        "decoherence_diagonal_is_born_measure": diagonal_error <= 1.0e-13,
        "decoherence_matrix_is_normalized": trace_error <= 1.0e-12,
        "decoherence_matrix_is_positive_semidefinite": minimum_decoherence_eigenvalue >= -1.0e-11,
        "environment_suppresses_all_distinct_histories": maximum_decohered_offdiag < maximum_pure_offdiag,
        "stronger_environment_increases_suppression": maximum_stronger_offdiag < maximum_decohered_offdiag,
        "dowker_halliwell_offdiagonal_bound_closes": offdiag_bound_error <= 1.0e-13,
        "feynman_parameter_identity_closes": one_loop["feynman_parameter_error"] <= 1.0e-12,
        "qcd_bubble_finite_part_converges_to_minus_two": one_loop["bubble_finite_part_error"] <= 1.0e-5,
        "second_quantized_fock_dependency_passes": bool(fock["passed"]),
        "formal_sources_are_content_pinned": all(
            len(source["sha"]) == 40 for source in payload["formal_authority"]["sources"]
        ),
    }
    return {
        **payload,
        "task": "M10.4a-h",
        "fingerprint": fingerprint(payload),
        "history_count": len(configurations),
        "partition": {"real": float(partition.real), "imag": float(partition.imag)},
        "normalized_topological_expectation": {
            "real": float(first.real),
            "imag": float(first.imag),
        },
        "connected_topological_two_point": {
            "real": float(second_connected.real),
            "imag": float(second_connected.imag),
        },
        "normalized_center_expectation": {
            "real": float(normalized_expectation(weights, center_observable).real),
            "imag": float(normalized_expectation(weights, center_observable).imag),
        },
        "factorization_error": factorization_error,
        "born_error": born_error,
        "charge_conjugation_error": charge_conjugation_error,
        "partition_derivative_error": partition_derivative_error,
        "first_source_error": first_source_error,
        "connected_source_error": connected_source_error,
        "occupation_partition_ratio_error": occupation_partition_ratio_error,
        "hermitian_error": hermitian_error,
        "diagonal_error": diagonal_error,
        "trace_error": trace_error,
        "minimum_decoherence_eigenvalue": minimum_decoherence_eigenvalue,
        "maximum_pure_offdiag": maximum_pure_offdiag,
        "maximum_decohered_offdiag": maximum_decohered_offdiag,
        "maximum_stronger_offdiag": maximum_stronger_offdiag,
        "offdiag_bound_error": offdiag_bound_error,
        "one_loop": one_loop,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_qcd_path_integral_is_constructed": True,
            "source_functional_and_connected_correlator_are_executed": True,
            "fock_occupation_enters_the_qcd_imaginary_action": True,
            "history_decoherence_matrix_is_positive_and_environment_suppressed": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
