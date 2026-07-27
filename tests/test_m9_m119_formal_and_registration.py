from openwave.xperiments.m9_cat_ept.formalization_m119_extension import (
    CURRENT_FORMAL_HEAD,
    PHYSLIB_ROOT_BLOB,
    expected_source_blobs,
    run_formalization_m119_extension,
    validate_formalization_m119,
)
from openwave.xperiments.m9_cat_ept.m119_gauge_covariant_evidence_authority import (
    run_m119_gauge_covariant_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.model_registration_m119 import (
    run_model_registration_study,
)


def test_m119_formal_authority_is_exact_and_fails_closed_on_drift() -> None:
    result = run_formalization_m119_extension()

    assert result["passed"]
    assert result["formal_repository"]["current_head"] == CURRENT_FORMAL_HEAD
    assert result["formal_repository"]["physlib_root_blob"] == PHYSLIB_ROOT_BLOB
    assert len(result["sources"]) == 6

    assert not validate_formalization_m119(observed_head="0" * 40)["passed"]
    assert not validate_formalization_m119(observed_root_blob="1" * 40)["passed"]

    drifted = expected_source_blobs()
    path = next(iter(drifted))
    drifted[path] = "2" * 40
    validation = validate_formalization_m119(observed_source_blobs=drifted)
    assert not validation["passed"]
    assert any(path in error for error in validation["errors"])


def test_m119_evidence_authority_composes_both_gauge_sectors() -> None:
    result = run_m119_gauge_covariant_evidence_authority()
    component = result["component"]

    assert result["passed"]
    assert component["local_SU3_links"]
    assert component["gauge_covariant_color_dynamics"]
    assert component["Wilson_observables"]
    assert component["local_SU2xU1_links"]
    assert component["gauge_covariant_Higgs_dynamics"]
    assert component["quartic_Higgs_vacuum_orbit"]
    assert not component["QCD_confinement_established"]
    assert not component["complete_electroweak_theory"]
    assert not any(result["claim_boundary"].values())


def test_schema_v22_registration_keeps_physical_boundaries_open() -> None:
    result = run_model_registration_study()
    current = result["m9_119"]

    assert result["passed"]
    assert result["schema"] == "openwave.model-registration.v22"
    assert current["formal_source_count"] == 6
    assert current["local_SU3_link_carrier"]
    assert current["local_SU2xU1_link_carrier"]
    assert not current["QCD_confinement_established"]
    assert not current["complete_electroweak_theory"]
    assert current["physical_claims_promoted"] == []
