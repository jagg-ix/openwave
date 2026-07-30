from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.second_quantized_fock_m103 import (
    SecondQuantizedFockConfig,
    annihilation_matrix,
    construct_fock_state,
    creation_matrix,
    run_second_quantized_fock_study,
)


def test_four_mode_jordan_wigner_car_is_exact() -> None:
    cfg = SecondQuantizedFockConfig()
    identity = np.eye(cfg.dimension, dtype=np.complex128)
    annihilators = tuple(annihilation_matrix(cfg.modes, index) for index in range(cfg.modes))
    creators = tuple(creation_matrix(cfg.modes, index) for index in range(cfg.modes))
    for left in range(cfg.modes):
        for right in range(cfg.modes):
            delta = identity if left == right else 0.0
            assert np.max(
                np.abs(
                    annihilators[left] @ creators[right]
                    + creators[right] @ annihilators[left]
                    - delta
                )
            ) == 0.0
            assert np.max(
                np.abs(
                    creators[left] @ creators[right]
                    + creators[right] @ creators[left]
                )
            ) == 0.0


def test_fock_state_has_binomial_number_sectors() -> None:
    state = construct_fock_state()
    numbers = np.real(np.diag(state.number_operator))
    assert state.vacuum.shape == (16,)
    assert np.count_nonzero(numbers == 0) == 1
    assert np.count_nonzero(numbers == 1) == 4
    assert np.count_nonzero(numbers == 2) == 6
    assert np.count_nonzero(numbers == 3) == 4
    assert np.count_nonzero(numbers == 4) == 1


def test_complete_m10_3_study_passes() -> None:
    result = run_second_quantized_fock_study()
    assert result["passed"]
    assert result["fock_dimension"] == 16
    assert result["group_elements"] == 120
    assert result["group_products_checked"] == 14_400
    assert result["maximum_car_error"] <= 1.0e-14
    assert result["maximum_lift_unitarity_error"] <= 1.0e-11
    assert result["maximum_functor_composition_error"] <= 1.0e-11
    assert result["maximum_central_parity_error"] <= 1.0e-13
    assert result["maximum_creation_intertwining_error"] <= 1.0e-12
    assert result["decision"]["m10_one_particle_carrier_is_second_quantized"]
    assert result["decision"]["central_2I_sign_is_fermion_parity"]


def test_occupation_increases_entropic_suppression() -> None:
    weights = run_second_quantized_fock_study()["born_weights_by_occupation"]
    assert weights["0"] > weights["1"] > weights["2"] > weights["3"] > weights["4"]
