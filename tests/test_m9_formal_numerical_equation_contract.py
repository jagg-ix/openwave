from openwave.xperiments.m9_cat_ept.formal_numerical_equation_contract import (
    FORMAL_BRANCH,
    FORMAL_SOURCES,
    equation_relations,
)
from openwave.xperiments.m9_cat_ept.formal_numerical_equation_contract_current import (
    ALL_OPENWAVE_SOURCES,
    current_contract_fingerprint,
    expected_formal_blobs,
    expected_openwave_blobs,
    run_formal_numerical_equation_contract,
    validate_formal_numerical_equation_contract,
)


def test_current_formal_branch_and_sources_are_exact():
    assert FORMAL_BRANCH == "entropic-physlib-linear-full"
    assert len(FORMAL_SOURCES) == 9
    assert len(ALL_OPENWAVE_SOURCES) == 8
    assert all(len(item["blob"]) == 40 for item in FORMAL_SOURCES)
    assert all(len(item["blob"]) == 40 for item in ALL_OPENWAVE_SOURCES)


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
        "legacy_results_are_direct_tests_of_current_formal_equations"
    ]
    assert result["decision"]["criterion_rows_promoted"] == []


def test_formal_source_drift_fails_closed():
    observed = expected_formal_blobs()
    path = next(iter(observed))
    observed[path] = "0" * 40
    result = validate_formal_numerical_equation_contract(
        observed_formal_blobs=observed
    )
    assert not result["passed"]
    assert f"formal source drift detected: {path}" in result["errors"]


def test_openwave_source_drift_fails_closed():
    observed = expected_openwave_blobs()
    path = next(iter(observed))
    observed[path] = "f" * 40
    result = validate_formal_numerical_equation_contract(
        observed_openwave_blobs=observed
    )
    assert not result["passed"]
    assert f"OpenWave source drift detected: {path}" in result["errors"]


def test_contract_fingerprint_is_deterministic():
    assert len(current_contract_fingerprint()) == 64
    assert current_contract_fingerprint() == current_contract_fingerprint()
