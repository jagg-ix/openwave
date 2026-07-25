from openwave.xperiments.m9_cat_ept.conservative_flow_composition import (
    run_conservative_flow_composition,
)


def test_conservative_flow_composition_passes():
    result = run_conservative_flow_composition()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["global_spectral_conservative_flow_qualified"]
    assert result["decision"]["particle_escape_under_declared_perturbations_observed"] is False


def test_energy_refines_for_every_perturbation():
    result = run_conservative_flow_composition()
    for values in result["energy_refinement"].values():
        assert values[2] < values[1] < values[0]
        assert 0.18 < values[1] / values[0] < 0.32
        assert 0.18 < values[2] / values[1] < 0.32
