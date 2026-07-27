from openwave.xperiments.m9_cat_ept.newton_g_theorem_and_evidence_scope import (
    run_newton_G_theorem_evidence_scope,
    universal_G_equal_masses,
)


def test_species_audit_does_not_falsify_lean_theorems():
    result = run_newton_G_theorem_evidence_scope()
    assert result["passed"]
    assert result["decision"]["Lean_theorems_contradicted"] is False
    assert all(not row["contradicted_by_species_audit"] for row in result["theorems"])


def test_universal_effective_G_for_positive_masses_forces_equal_mass_numerically():
    equal = universal_G_equal_masses(2.0, 2.0)
    unequal = universal_G_equal_masses(2.0, 3.0)
    assert equal["universal_G_for_both_is_consistent"]
    assert not unequal["universal_G_for_both_is_consistent"]
    assert unequal["effective_G1_over_G2"] == 2.25


def test_papers_are_scoped_to_subclaims_not_full_G_chain():
    result = run_newton_G_theorem_evidence_scope()
    assert result["decision"]["papers_validate_full_CAT_EPT_G_chain"] is False
    assert result["decision"]["paper_evidence_requires_narrower_edges"] is True
    assert "Delta S_I = m*c^2*Delta tau_phys for the relevant physical clock" in result[
        "load_bearing_untested_premises"
    ]
