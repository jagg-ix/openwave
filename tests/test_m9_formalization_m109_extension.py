from openwave.xperiments.m9_cat_ept.formalization_m109_extension import (
    CURRENT_FORMAL_HEAD,
    PHYSLIB_ROOT_BLOB,
    expected_source_blobs,
    run_formalization_m109_extension,
    validate_formalization_m109,
)


def test_current_G_authority_is_exact_and_scoped():
    result = run_formalization_m109_extension()
    assert result["passed"]
    assert result["formal_repository"]["current_head"] == CURRENT_FORMAL_HEAD
    assert result["formal_repository"]["physlib_root_blob"] == PHYSLIB_ROOT_BLOB
    assert len(result["g_authority_sources"]) == 4
    assert result["scope"]["newton_G_is_canonical_derived_quantity"]
    assert not result["scope"]["particle_mass_value_is_derived"]
    assert not result["scope"]["formal_theorem_proves_species_independent_G"]


def test_G_authority_fails_closed_on_source_drift():
    observed = expected_source_blobs()
    path = next(iter(observed))
    observed[path] = "0" * 40
    result = validate_formalization_m109(observed_source_blobs=observed)
    assert not result["passed"]
    assert path in result["errors"][0]
