from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106 import (
    PeriodicSU3HamiltonianConfig,
    deterministic_gauges,
    deterministic_lattice_links,
    gauge_transform_links,
    magnetic_action,
    plaquette_matrix,
    rectangular_wilson_loop,
    run_periodic_su3_hamiltonian_study,
)


def test_periodic_plaquette_transforms_by_local_conjugation() -> None:
    cfg = PeriodicSU3HamiltonianConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    gauges = deterministic_gauges(cfg.size, cfg.gauge_scale)
    transformed = gauge_transform_links(links, gauges)
    for x in range(cfg.size):
        for y in range(cfg.size):
            expected = gauges[x, y] @ plaquette_matrix(links, x, y) @ gauges[x, y].conj().T
            assert np.max(np.abs(plaquette_matrix(transformed, x, y) - expected)) <= 2.0e-12
    assert abs(magnetic_action(transformed, cfg.inverse_coupling) - magnetic_action(links, cfg.inverse_coupling)) <= 2.0e-12


def test_periodic_wilson_loops_are_defined() -> None:
    cfg = PeriodicSU3HamiltonianConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    for width, height in ((1, 1), (2, 1), (1, 2), (2, 2)):
        value = rectangular_wilson_loop(links, 0, 0, width, height)
        assert np.isfinite(value.real)
        assert np.isfinite(value.imag)


def test_complete_m10_6_hamiltonian_study_passes() -> None:
    result = run_periodic_su3_hamiltonian_study()
    assert result["passed"]
    assert result["relative_hamiltonian_drift"] <= 2.0e-6
    assert result["final_gauss_residual"] <= 5.0e-9
    assert result["maximum_unitarity_error"] <= 2.0e-12
    assert result["maximum_determinant_error"] <= 2.0e-12
    assert result["reversibility_link_error"] <= 2.0e-9
    assert result["reversibility_electric_error"] <= 2.0e-8
    assert result["decision"]["periodic_hamiltonian_su3_lattice_is_constructed"]
    assert result["decision"]["source_free_gauss_law_is_evolved"]
