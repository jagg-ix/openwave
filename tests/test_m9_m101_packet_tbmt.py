import numpy as np

from openwave.xperiments.m9_cat_ept.covariant_packet_tbmt import (
    local_tbmt_omega,
    local_velocity,
)


def zeros(shape=(3, 3, 3)):
    return tuple(np.zeros(shape, dtype=np.float64) for _ in range(3))


def test_lab_frame_bmt_has_correct_dirac_rest_limit():
    shape = (3, 3, 3)
    beta = zeros(shape)
    gamma = np.ones(shape, dtype=np.float64)
    electric = zeros(shape)
    magnetic = (
        np.zeros(shape, dtype=np.float64),
        np.zeros(shape, dtype=np.float64),
        np.ones(shape, dtype=np.float64),
    )
    omega = local_tbmt_omega(
        beta,
        gamma,
        electric,
        magnetic,
        charge=1.0,
        mass=1.0,
        g_factor=2.0,
    )
    assert np.max(np.abs(omega[0])) == 0.0
    assert np.max(np.abs(omega[1])) == 0.0
    assert np.max(np.abs(omega[2] + 1.0)) < 1e-15


def test_packet_velocity_fails_closed_to_subluminal_values():
    state = np.zeros((4, 2, 2, 2), dtype=np.complex128)
    state[0] = 1.0
    beta, gamma, audit = local_velocity(state)
    magnitude = np.sqrt(sum(component * component for component in beta))
    assert float(np.max(magnitude)) < 1.0
    assert float(np.min(gamma)) >= 1.0
    assert audit["maximum_used_beta"] < 1.0


def test_electric_term_changes_lab_frame_omega():
    shape = (2, 2, 2)
    beta = (
        np.full(shape, 0.2),
        np.zeros(shape),
        np.zeros(shape),
    )
    gamma = np.full(shape, 1.0 / np.sqrt(1.0 - 0.2**2))
    magnetic = (
        np.zeros(shape),
        np.zeros(shape),
        np.ones(shape),
    )
    no_e = local_tbmt_omega(
        beta, gamma, zeros(shape), magnetic,
        charge=1.0, mass=1.0, g_factor=2.0,
    )
    electric = (
        np.zeros(shape),
        np.ones(shape),
        np.zeros(shape),
    )
    with_e = local_tbmt_omega(
        beta, gamma, electric, magnetic,
        charge=1.0, mass=1.0, g_factor=2.0,
    )
    assert np.linalg.norm(with_e[2] - no_e[2]) > 0.0
