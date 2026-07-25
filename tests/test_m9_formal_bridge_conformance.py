from openwave.xperiments.m9_cat_ept.model_conformance import (
    CRITERIA,
    PROMOTED_KEYS,
    run_conformance_study,
    validate_profile,
)


def criterion(key: str):
    return next(item for item in CRITERIA if item.key == key)


def test_formal_spin_and_force_evidence_is_registered():
    spin = criterion("magnetic_moment_spin")
    electric = criterion("electric_force")
    magnetic = criterion("magnetic_force")
    gravity = criterion("gravity")
    assert any("canonical_spin_magnetic_bridge.py" in path for path in spin.evidence)
    assert any("canonical_force_formal_bridge.py" in path for path in electric.evidence)
    assert any("canonical_force_formal_bridge.py" in path for path in magnetic.evidence)
    assert all(
        any("formalization_import.py" in path for path in item.evidence)
        for item in (spin, electric, magnetic, gravity)
    )


def test_formal_availability_does_not_promote_physical_rows():
    assert criterion("magnetic_moment_spin").status == "partial"
    assert criterion("electric_force").status == "partial"
    assert criterion("magnetic_force").status == "partial"
    assert criterion("gravity").status == "partial"
    assert {item.key for item in CRITERIA if item.status == "validated"} == PROMOTED_KEYS
    assert validate_profile()["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }


def test_findings_preserve_anomaly_charged_branch_and_calibration_boundaries():
    assert "not derived from the CAT/EPT particle" in criterion(
        "magnetic_moment_spin"
    ).finding
    assert "winding is not embedded" in criterion("electric_force").finding
    assert "not a calibrated dipole force law" in criterion("magnetic_force").finding
    assert "remain open" in criterion("gravity").finding


def test_full_conformance_study_passes_through_m9_95():
    result = run_conformance_study()
    assert result["schema"] == "openwave.m9.models-conformance.v13"
    assert result["passed"] and all(result["acceptance"].values())
