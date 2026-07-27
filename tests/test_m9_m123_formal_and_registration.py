from openwave.xperiments.m9_cat_ept.formalization_m123_extension import CURRENT_FORMAL_HEAD, FORMAL_SOURCES, PHYSLIB_ROOT_BLOB, run_formalization_m123_extension, validate_formal_snapshot
from openwave.xperiments.m9_cat_ept.m123_nonparticle_physics_authority import run_m123_nonparticle_physics_authority
from openwave.xperiments.m9_cat_ept.model_registration_m123 import run_model_registration_study


def test_m123_formal_authority_pins_cross_domain_sources() -> None:
    result = run_formalization_m123_extension()
    assert result["passed"] and len(FORMAL_SOURCES) == 11
    assert result["current_formal_head"] == CURRENT_FORMAL_HEAD
    assert result["physlib_root_blob"] == PHYSLIB_ROOT_BLOB
    assert all(source["declarations"] for source in FORMAL_SOURCES)


def test_formal_snapshot_rejects_head_root_and_source_drift() -> None:
    assert not validate_formal_snapshot(head="0" * 40)["passed"]
    assert not validate_formal_snapshot(root_blob="0" * 40)["passed"]
    expected = {f"{source.get('repository', 'jagg-ix/entropic-physlib-private')}:{source['path']}": source["blob"] for source in FORMAL_SOURCES}
    first = next(iter(expected))
    expected[first] = "0" * 40
    assert not validate_formal_snapshot(source_blobs=expected)["passed"]


def test_m123_authority_and_schema_v26_registration_pass() -> None:
    authority, registration = run_m123_nonparticle_physics_authority(), run_model_registration_study()
    current = registration["m9_123"]
    assert authority["passed"] and registration["passed"]
    assert registration["schema"] == "openwave.model-registration.v26"
    assert current["formal_source_count"] == 11
    assert current["nonparticle_domain_count"] == 8
    assert current["nonparticle_control_count"] == 6
    assert current["broad_internal_physics_modeling"]
    assert not current["particle_spectroscopy_primary"]
    assert not current["predictive_fundamental_theory_ready"]
    assert not current["external_validation_complete"]
    assert current["physical_claims_promoted"] == []
