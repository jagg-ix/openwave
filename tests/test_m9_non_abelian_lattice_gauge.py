import numpy as np

from openwave.xperiments.m9_cat_ept.non_abelian_lattice_gauge import (
    NonAbelianGaugeConfig,
    evolution_step,
    gauge_transform,
    initialize_links,
    initialize_matter,
    link_determinant_error,
    link_unitarity_error,
    local_gauge_transformation,
    matter_kinetic_action,
    run_non_abelian_lattice_gauge,
    wilson_action,
)


def test_local_su3_observables_are_gauge_invariant() -> None:
    cfg = NonAbelianGaugeConfig(steps=2)
    matter = initialize_matter(cfg)
    links = initialize_links(cfg)
    gauge = local_gauge_transformation(cfg)
    transformed_matter, transformed_links = gauge_transform(matter, links, gauge)

    assert np.isclose(
        matter_kinetic_action(matter, links),
        matter_kinetic_action(transformed_matter, transformed_links),
        rtol=2.0e-12,
        atol=2.0e-12,
    )
    assert np.isclose(
        wilson_action(links, cfg.inverse_coupling)[0],
        wilson_action(transformed_links, cfg.inverse_coupling)[0],
        rtol=2.0e-12,
        atol=2.0e-12,
    )


def test_matter_and_link_step_commutes_with_local_su3_transform() -> None:
    cfg = NonAbelianGaugeConfig(steps=2)
    matter = initialize_matter(cfg)
    links = initialize_links(cfg)
    gauge = local_gauge_transformation(cfg)
    transformed = gauge_transform(matter, links, gauge)

    next_matter, next_links = evolution_step(matter, links, cfg)
    transformed_next = evolution_step(transformed[0], transformed[1], cfg)
    expected = gauge_transform(next_matter, next_links, gauge)

    assert np.linalg.norm(transformed_next[0] - expected[0]) <= 2.0e-11
    assert np.linalg.norm(transformed_next[1] - expected[1]) <= 2.0e-11
    assert link_unitarity_error(next_links) <= 2.0e-11
    assert link_determinant_error(next_links) <= 2.0e-11


def test_non_abelian_campaign_passes_without_qcd_promotion() -> None:
    result = run_non_abelian_lattice_gauge()

    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["local_SU3_link_carrier_constructed"]
    assert result["decision"]["gauge_covariant_color_matter_evolution_constructed"]
    assert not result["decision"]["QCD_confinement_established"]
    assert not any(result["claim_boundary"].values())
