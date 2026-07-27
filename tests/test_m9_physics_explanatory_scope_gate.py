from openwave.xperiments.m9_cat_ept.physics_explanatory_scope_gate import run_physics_explanatory_scope_gate


def test_broad_modeling_passes_but_fundamental_theory_gate_stays_closed() -> None:
    result = run_physics_explanatory_scope_gate()
    assert result["passed"] and result["represented"] and result["formal_coverage"]
    assert len(result["dynamical_domains"]) >= 5
    assert len(result["continuum_supported_domains"]) >= 6
    assert not result["calibration_ready"]
    assert not result["externally_validated"]
    assert not result["explanatory_compression_ready"]
    assert result["decision"]["broad_internal_physics_modeling_ready"]
    assert not result["decision"]["predictive_fundamental_theory_ready"]


def test_all_explanatory_blockers_are_explicit() -> None:
    result = run_physics_explanatory_scope_gate()
    assert set(result["explanatory_requirements"]) == {"single_universal_action_or_generator", "independent_parameter_fixing", "end_to_end_continuum_dynamics", "cross_domain_heldout_prediction"}
    assert not any(result["explanatory_requirements"].values())
