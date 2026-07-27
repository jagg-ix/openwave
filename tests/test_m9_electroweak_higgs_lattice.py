import numpy as np

from openwave.xperiments.m9_cat_ept.electroweak_higgs_lattice import (
    ElectroweakHiggsConfig,
    evolution_step,
    gauge_transform,
    initialize_electroweak_state,
    kinetic_action,
    local_electroweak_gauge,
    potential_density,
    run_electroweak_higgs_lattice,
    su2_wilson_action,
    u1_wilson_action,
)


def test_local_su2_u1_higgs_observables_are_gauge_invariant() -> None:
    cfg = ElectroweakHiggsConfig(covariance_steps=2, relaxation_steps=4)
    higgs, su2_links, u1_links = initialize_electroweak_state(cfg)
    su2_gauge, u1_gauge = local_electroweak_gauge(cfg)
    transformed = gauge_transform(
        higgs,
        su2_links,
        u1_links,
        su2_gauge,
        u1_gauge,
        cfg.hypercharge_power,
    )

    assert np.isclose(
        kinetic_action(higgs, su2_links, u1_links, cfg.hypercharge_power),
        kinetic_action(transformed[0], transformed[1], transformed[2], cfg.hypercharge_power),
        rtol=2.0e-12,
        atol=2.0e-12,
    )
    assert np.isclose(
        np.sum(potential_density(higgs, cfg)),
        np.sum(potential_density(transformed[0], cfg)),
        rtol=2.0e-12,
        atol=2.0e-12,
    )
    assert np.isclose(
        su2_wilson_action(su2_links),
        su2_wilson_action(transformed[1]),
        rtol=2.0e-12,
        atol=2.0e-12,
    )
    assert np.isclose(
        u1_wilson_action(u1_links),
        u1_wilson_action(transformed[2]),
        rtol=2.0e-12,
        atol=2.0e-12,
    )


def test_higgs_and_links_step_commutes_with_local_gauge_transform() -> None:
    cfg = ElectroweakHiggsConfig(covariance_steps=2, relaxation_steps=4)
    higgs, su2_links, u1_links = initialize_electroweak_state(cfg)
    su2_gauge, u1_gauge = local_electroweak_gauge(cfg)
    transformed = gauge_transform(
        higgs,
        su2_links,
        u1_links,
        su2_gauge,
        u1_gauge,
        cfg.hypercharge_power,
    )

    next_state = evolution_step(higgs, su2_links, u1_links, cfg)
    transformed_next = evolution_step(transformed[0], transformed[1], transformed[2], cfg)
    expected = gauge_transform(
        next_state[0],
        next_state[1],
        next_state[2],
        su2_gauge,
        u1_gauge,
        cfg.hypercharge_power,
    )

    assert np.linalg.norm(transformed_next[0] - expected[0]) <= 2.0e-11
    assert np.linalg.norm(transformed_next[1] - expected[1]) <= 2.0e-11
    assert np.linalg.norm(transformed_next[2] - expected[2]) <= 2.0e-11


def test_electroweak_higgs_campaign_passes_without_standard_model_promotion() -> None:
    result = run_electroweak_higgs_lattice()

    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["local_SU2xU1_link_carrier_constructed"]
    assert result["decision"]["quartic_Higgs_vacuum_orbit_constructed"]
    assert not result["decision"]["complete_electroweak_theory_constructed"]
    assert not any(result["claim_boundary"].values())
