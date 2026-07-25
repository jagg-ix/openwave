from openwave.xperiments.m9_cat_ept.formal_numerical_equation_contract import (
    FORMAL_BRANCH,
    FORMAL_SOURCES,
    OPENWAVE_SOURCES,
    contract_fingerprint,
    equation_relations,
    run_formal_numerical_equation_contract,
)


def test_current_formal_branch_and_sources_are_exact():
    assert FORMAL_BRANCH == "entropic-physlib-linear-full"
    assert len(FORMAL_SOURCES) == 9
    assert len(OPENWAVE_SOURCES) == 5
    assert all(len(item["blob"]) == 40 for item in FORMAL_SOURCES)
    assert all(len(item["blob"]) == 40 for item in OPENWAVE_SOURCES)


def test_major_equation_mismatches_are_machine_visible():
    rows = {row.identifier: row for row in equation_relations()}
    assert rows["binding_interaction"].relation == "formal_term_missing_numerically"
    assert rows["schrodinger_mass_map"].relation == "parameter_mismatch"
    assert rows["discrete_differential_complex"].relation == "discrete_operator_mismatch"
    assert rows["dirac_velocity"].relation == "observable_domain_mismatch"
    assert rows["spin_precession"].relation == "observable_domain_mismatch"
    assert rows["dirac_clifford_algebra"].relation == "exact_structure"


def test_contract_passes_without_promotion():
    result = run_formal_numerical_equation_contract()
    assert result["passed"] and all(result["acceptance"].values())
    assert not result["decision"][
        "openwave_legacy_results_are_direct_numerical_tests_of_current_formal_equations"
    ]
    assert result["decision"]["criterion_rows_promoted"] == []


def test_contract_fingerprint_is_deterministic():
    assert len(contract_fingerprint()) == 64
    assert contract_fingerprint() == contract_fingerprint()
