from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.color_matter_gauss_m107 import (
    ColorMatterGaussConfig,
    color_density,
    covariant_hamiltonian_matrix,
    deterministic_matter_field,
    gauge_transform_matter,
    run_color_matter_gauss_study,
    solve_sourced_gauss,
)
from openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106 import (
    deterministic_gauges,
    deterministic_lattice_links,
    gauge_transform_links,
)


def test_covariant_hopping_matrix_is_hermitian() -> None:
    cfg = ColorMatterGaussConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    matrix = covariant_hamiltonian_matrix(links, cfg.mass, cfg.hopping)
    assert np.max(np.abs(matrix - matrix.conj().T)) <= 2.0e-13


def test_sourced_gauss_solution_is_locally_covariant() -> None:
    cfg = ColorMatterGaussConfig()
    links = deterministic_lattice_links(cfg.size, cfg.link_scale)
    gauges = deterministic_gauges(cfg.size, cfg.gauge_scale)
    matter = deterministic_matter_field(cfg.size)
    transformed_links = gauge_transform_links(links, gauges)
    transformed_matter = gauge_transform_matter(matter, gauges)
    electric, residual, _ = solve_sourced_gauss(
        links, color_density(matter), cfg.color_charge
    )
    transformed_electric, transformed_residual, _ = solve_sourced_gauss(
        transformed_links, color_density(transformed_matter), cfg.color_charge
    )
    expected = np.asarray(
        np.einsum(
            "xyab,xymbc,xycd->xymad",
            gauges,
            electric,
            gauges.conj().transpose(0, 1, 3, 2),
        )
    )
    assert residual <= 2.0e-12
    assert transformed_residual <= 2.0e-12
    assert np.max(np.abs(transformed_electric - expected)) <= 2.0e-12


def test_complete_m10_7_color_matter_study_passes() -> None:
    result = run_color_matter_gauss_study()
    assert result["passed"]
    assert result["hamiltonian_hermitian_error"] <= 2.0e-13
    assert result["hamiltonian_covariance_error"] <= 2.0e-12
    assert result["evolution_covariance_error"] <= 2.0e-12
    assert result["initial_scalar_continuity_error"] <= 2.0e-12
    assert result["initial_color_continuity_error"] <= 2.0e-12
    assert result["final_sourced_gauss_residual"] <= 2.0e-12
    assert result["electric_covariance_error"] <= 2.0e-12
    assert result["matter_response"] >= 1.0e-2
    assert result["decision"]["fundamental_color_matter_is_dynamical"]
    assert result["decision"]["sourced_gauss_constraint_is_solved_covariantly"]
