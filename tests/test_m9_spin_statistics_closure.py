import numpy as np

from openwave.xperiments.m9_cat_ept.spin_statistics_closure import (
    antisymmetrized_amplitude,
    exchange,
    run_spin_statistics_closure,
    two_state_exchange_audit,
)


def test_antisymmetric_exchange_and_pauli_exclusion():
    up = np.asarray([1.0, 0.0], dtype=np.complex128)
    down = np.asarray([0.0, 1.0], dtype=np.complex128)
    amplitude = antisymmetrized_amplitude(up, down)
    assert np.allclose(exchange(amplitude), -amplitude)
    assert np.allclose(antisymmetrized_amplitude(up, up), 0.0)


def test_exchange_audit_closes():
    result = two_state_exchange_audit()
    assert result["swap_to_minus_state_error"] == 0.0
    assert result["double_swap_return_error"] == 0.0
    assert result["identical_state_exclusion_norm"] == 0.0


def test_spin_statistics_closure_passes_without_particle_overclaim():
    result = run_spin_statistics_closure()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["spin_half_statistics_validated_in_platform"]
    assert not result["decision"][
        "fermionic_assignment_of_specific_cat_ept_particle_derived"
    ]
