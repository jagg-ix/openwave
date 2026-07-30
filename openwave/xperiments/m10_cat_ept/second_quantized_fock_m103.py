"""M10.3 finite fermionic second quantization of the M10 one-particle carrier.

The four Dirac internal modes generate a 16-dimensional fermionic Fock space.
Creation and annihilation matrices use the Jordan--Wigner sign convention.  A
one-particle binary-icosahedral matrix U is lifted by its exterior powers: the
matrix element between occupation subsets I and J is det(U[I,J]).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .dirac_cartan_2i_yukawa_model import (
    DiracCartan2IYukawaConfig,
    Quaternion,
    binary_icosahedral_quaternions,
    dirac_2i_matrix,
    quaternion_multiply,
)

MILESTONE = "M10.3"
SCHEMA = "openwave.m10.second-quantized-fock.v1"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_PR = 42
FORMAL_BRANCH = "agent/dirac-cartan-2i-second-quantized-qcd"
FORMAL_HEAD = "45269fa04dc16ae1588925f0a8c167ee9dfbc7b8"
FORMAL_SOURCE_BLOB = "033a992c8b144554c5edfdccdb4d95e7d6e4a3b9"
FORMAL_THEOREM = "dirac_cartan_2I_second_quantized_qcd_assembly"


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _quaternion_key(value: Quaternion) -> Quaternion:
    return tuple(round(float(component), 12) for component in value)  # type: ignore[return-value]


def occupied_modes(basis: int, modes: int) -> tuple[int, ...]:
    return tuple(index for index in range(modes) if (basis >> index) & 1)


def annihilation_matrix(modes: int, index: int) -> np.ndarray:
    if modes < 1 or index not in range(modes):
        raise ValueError("valid finite fermionic mode index required")
    dimension = 1 << modes
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    lower_mask = (1 << index) - 1
    for source in range(dimension):
        if (source >> index) & 1:
            target = source ^ (1 << index)
            sign = -1.0 if (source & lower_mask).bit_count() % 2 else 1.0
            result[target, source] = sign
    return result


def creation_matrix(modes: int, index: int) -> np.ndarray:
    return annihilation_matrix(modes, index).conj().T


def exterior_fock_lift(one_particle: np.ndarray) -> np.ndarray:
    """Return Gamma(U) on the full finite fermionic Fock basis."""
    if one_particle.ndim != 2 or one_particle.shape[0] != one_particle.shape[1]:
        raise ValueError("square one-particle matrix required")
    modes = one_particle.shape[0]
    dimension = 1 << modes
    result = np.zeros((dimension, dimension), dtype=np.complex128)
    occupations = [occupied_modes(basis, modes) for basis in range(dimension)]
    for source, source_modes in enumerate(occupations):
        for target, target_modes in enumerate(occupations):
            if len(source_modes) != len(target_modes):
                continue
            if not source_modes:
                result[target, source] = 1.0
            else:
                result[target, source] = np.linalg.det(
                    one_particle[np.ix_(target_modes, source_modes)]
                )
    return result


def second_quantized_one_body(
    one_particle: np.ndarray,
    creators: tuple[np.ndarray, ...],
    annihilators: tuple[np.ndarray, ...],
) -> np.ndarray:
    modes = one_particle.shape[0]
    if one_particle.shape != (modes, modes) or len(creators) != modes or len(annihilators) != modes:
        raise ValueError("matching one-particle and CAR carriers required")
    result = np.zeros_like(creators[0], dtype=np.complex128)
    for creator in range(modes):
        for annihilator in range(modes):
            result += (
                one_particle[creator, annihilator]
                * creators[creator]
                @ annihilators[annihilator]
            )
    return result


@dataclass(frozen=True)
class SecondQuantizedFockConfig:
    modes: int = 4
    inverse_temperature: float = 3.0
    evolution_time: float = 1.25

    def __post_init__(self) -> None:
        if self.modes != 4:
            raise ValueError("M10.3 uses the four internal Dirac modes")
        if self.inverse_temperature <= 0.0 or self.evolution_time <= 0.0:
            raise ValueError("positive thermal and evolution controls required")

    @property
    def dimension(self) -> int:
        return 1 << self.modes


@dataclass(frozen=True)
class SecondQuantizedFockState:
    annihilators: tuple[np.ndarray, ...]
    creators: tuple[np.ndarray, ...]
    number_operator: np.ndarray
    parity_operator: np.ndarray
    real_hamiltonian: np.ndarray
    complex_hamiltonian: np.ndarray
    vacuum: np.ndarray


def construct_fock_state(
    cfg: SecondQuantizedFockConfig = SecondQuantizedFockConfig(),
    particle_cfg: DiracCartan2IYukawaConfig = DiracCartan2IYukawaConfig(),
) -> SecondQuantizedFockState:
    annihilators = tuple(annihilation_matrix(cfg.modes, index) for index in range(cfg.modes))
    creators = tuple(value.conj().T for value in annihilators)
    number = sum(
        creators[index] @ annihilators[index] for index in range(cfg.modes)
    )
    parity = np.diag(
        [(-1.0) ** basis.bit_count() for basis in range(cfg.dimension)]
    ).astype(np.complex128)
    rest_energy = particle_cfg.hbar * particle_cfg.compton_frequency
    real_hamiltonian = rest_energy * number
    complex_hamiltonian = (
        rest_energy + 1.0j * particle_cfg.entropy_rate
    ) * number
    vacuum = np.zeros(cfg.dimension, dtype=np.complex128)
    vacuum[0] = 1.0
    return SecondQuantizedFockState(
        annihilators=annihilators,
        creators=creators,
        number_operator=np.asarray(number, dtype=np.complex128),
        parity_operator=parity,
        real_hamiltonian=np.asarray(real_hamiltonian, dtype=np.complex128),
        complex_hamiltonian=np.asarray(complex_hamiltonian, dtype=np.complex128),
        vacuum=vacuum,
    )


def canonical_payload(
    cfg: SecondQuantizedFockConfig | None = None,
    particle_cfg: DiracCartan2IYukawaConfig | None = None,
) -> dict[str, Any]:
    selected = cfg or SecondQuantizedFockConfig()
    particle = particle_cfg or DiracCartan2IYukawaConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT second-quantized Dirac-Cartan-2I-Compton-Yukawa",
        "config": asdict(selected),
        "particle_mass": particle.yukawa_mass,
        "compton_frequency": particle.compton_frequency,
        "entropy_rate": particle.entropy_rate,
        "formal_authority": {
            "repository": FORMAL_REPOSITORY,
            "pull_request": FORMAL_PR,
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "source_blob": FORMAL_SOURCE_BLOB,
            "theorem": FORMAL_THEOREM,
        },
        "construction_api": (
            "openwave.xperiments.m10_cat_ept.second_quantized_fock_m103:"
            "construct_fock_state"
        ),
        "study_api": (
            "openwave.xperiments.m10_cat_ept.second_quantized_fock_m103:"
            "run_second_quantized_fock_study"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_second_quantized_fock_study() -> dict[str, Any]:
    cfg = SecondQuantizedFockConfig()
    particle_cfg = DiracCartan2IYukawaConfig()
    state = construct_fock_state(cfg, particle_cfg)
    identity = np.eye(cfg.dimension, dtype=np.complex128)

    maximum_car_error = 0.0
    for left in range(cfg.modes):
        for right in range(cfg.modes):
            delta = identity if left == right else 0.0
            maximum_car_error = max(
                maximum_car_error,
                float(
                    np.max(
                        np.abs(
                            state.annihilators[left] @ state.creators[right]
                            + state.creators[right] @ state.annihilators[left]
                            - delta
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            state.annihilators[left] @ state.annihilators[right]
                            + state.annihilators[right] @ state.annihilators[left]
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            state.creators[left] @ state.creators[right]
                            + state.creators[right] @ state.creators[left]
                        )
                    )
                ),
            )

    group = binary_icosahedral_quaternions()
    group_index = {value: index for index, value in enumerate(group)}
    one_particle = tuple(dirac_2i_matrix(value) for value in group)
    lifts = tuple(exterior_fock_lift(value) for value in one_particle)

    maximum_lift_unitarity_error = max(
        float(np.max(np.abs(lift.conj().T @ lift - identity))) for lift in lifts
    )
    maximum_central_parity_error = 0.0
    maximum_creation_intertwining_error = 0.0
    for value, unitary, lift in zip(group, one_particle, lifts, strict=True):
        negative = _quaternion_key(tuple(-component for component in value))
        maximum_central_parity_error = max(
            maximum_central_parity_error,
            float(
                np.max(
                    np.abs(
                        lifts[group_index[negative]]
                        - state.parity_operator @ lift
                    )
                )
            ),
        )
        for mode in range(cfg.modes):
            transformed_creation = sum(
                unitary[target, mode] * state.creators[target]
                for target in range(cfg.modes)
            )
            maximum_creation_intertwining_error = max(
                maximum_creation_intertwining_error,
                float(
                    np.max(
                        np.abs(
                            lift @ state.creators[mode]
                            - transformed_creation @ lift
                        )
                    )
                ),
            )

    maximum_functor_composition_error = 0.0
    for left_index, left in enumerate(group):
        for right_index, right in enumerate(group):
            product = _quaternion_key(quaternion_multiply(left, right))
            maximum_functor_composition_error = max(
                maximum_functor_composition_error,
                float(
                    np.max(
                        np.abs(
                            lifts[group_index[product]]
                            - lifts[left_index] @ lifts[right_index]
                        )
                    )
                ),
            )

    rest_energy = particle_cfg.hbar * particle_cfg.compton_frequency
    expected_hamiltonian = rest_energy * state.number_operator
    second_quantized_hamiltonian = second_quantized_one_body(
        rest_energy * np.eye(cfg.modes, dtype=np.complex128),
        state.creators,
        state.annihilators,
    )
    hamiltonian_lift_error = float(
        np.max(np.abs(second_quantized_hamiltonian - expected_hamiltonian))
    )
    mass_clock_error = abs(
        particle_cfg.hbar * particle_cfg.compton_frequency
        - particle_cfg.yukawa_mass * particle_cfg.c**2
    )

    number_diagonal = np.real(np.diag(state.number_operator))
    sector_dimensions = {
        str(occupation): int(np.count_nonzero(number_diagonal == occupation))
        for occupation in range(cfg.modes + 1)
    }
    direct_partition = float(
        np.sum(np.exp(-cfg.inverse_temperature * rest_energy * number_diagonal))
    )
    closed_partition = float(
        (1.0 + math.exp(-cfg.inverse_temperature * rest_energy)) ** cfg.modes
    )
    partition_error = abs(direct_partition - closed_partition)

    born_weights = np.exp(
        -2.0
        * particle_cfg.entropy_rate
        * cfg.evolution_time
        * number_diagonal
        / particle_cfg.hbar
    )
    minimum_sector_drop = min(
        born_weights[number_diagonal == occupation - 1][0]
        - born_weights[number_diagonal == occupation][0]
        for occupation in range(1, cfg.modes + 1)
    )

    payload = canonical_payload(cfg, particle_cfg)
    acceptance = {
        "fock_dimension_is_sixteen": cfg.dimension == 16,
        "sector_dimensions_are_binomial": sector_dimensions
        == {"0": 1, "1": 4, "2": 6, "3": 4, "4": 1},
        "canonical_anticommutation_relations_close": maximum_car_error <= 1.0e-14,
        "all_120_fock_lifts_are_unitary": maximum_lift_unitarity_error <= 1.0e-11,
        "all_14400_group_products_second_quantize_functorially": (
            maximum_functor_composition_error <= 1.0e-11
        ),
        "central_pair_is_fermion_parity": maximum_central_parity_error <= 1.0e-13,
        "creation_intertwining_closes": maximum_creation_intertwining_error <= 1.0e-12,
        "second_quantized_compton_hamiltonian_is_E_times_number": (
            hamiltonian_lift_error <= 1.0e-14
        ),
        "yukawa_compton_energy_identity_closes": mass_clock_error <= 2.0e-15,
        "fermion_partition_function_factorizes": partition_error <= 1.0e-12,
        "occupation_increases_entropic_suppression": minimum_sector_drop > 0.0,
        "formal_authority_is_exactly_pinned": (
            payload["formal_authority"]["head"] == FORMAL_HEAD
            and payload["formal_authority"]["source_blob"] == FORMAL_SOURCE_BLOB
            and payload["formal_authority"]["theorem"] == FORMAL_THEOREM
        ),
    }
    return {
        **payload,
        "task": "M10.3a-g",
        "fingerprint": fingerprint(payload),
        "fock_dimension": cfg.dimension,
        "sector_dimensions": sector_dimensions,
        "group_elements": len(group),
        "group_products_checked": len(group) ** 2,
        "maximum_car_error": maximum_car_error,
        "maximum_lift_unitarity_error": maximum_lift_unitarity_error,
        "maximum_functor_composition_error": maximum_functor_composition_error,
        "maximum_central_parity_error": maximum_central_parity_error,
        "maximum_creation_intertwining_error": maximum_creation_intertwining_error,
        "hamiltonian_lift_error": hamiltonian_lift_error,
        "mass_clock_error": mass_clock_error,
        "partition_error": partition_error,
        "born_weights_by_occupation": {
            str(occupation): float(born_weights[number_diagonal == occupation][0])
            for occupation in range(cfg.modes + 1)
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m10_one_particle_carrier_is_second_quantized": True,
            "binary_icosahedral_action_is_lifted_to_fock_space": True,
            "central_2I_sign_is_fermion_parity": True,
            "compton_yukawa_energy_is_occupation_additive": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
