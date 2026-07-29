from openwave.xperiments.m9_cat_ept.model_conformance import CRITERIA as BASE_CRITERIA
from openwave.xperiments.m9_cat_ept.model_conformance_m96 import (
    CRITERIA,
    ROW_REPLACEMENTS,
    run_conformance_study,
)


def test_m96_overlay_changes_exactly_three_rows():
    base = {item.key: item for item in BASE_CRITERIA}
    current = {item.key: item for item in CRITERIA}
    assert list(current) == list(base)
    changed = {
        key
        for key in current
        if current[key].evidence != base[key].evidence
        or current[key].finding != base[key].finding
    }
    assert changed == set(ROW_REPLACEMENTS)
    assert all(current[key].status == base[key].status == "partial" for key in changed)


def test_m96_profile_preserves_status_and_validated_sets():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.models-conformance.v14"
    assert result["audit"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    assert result["decision"]["m9_96_evidence_overlay_applied"]
    assert result["decision"]["criterion_rows_promoted"] == []


def test_m96_findings_name_new_closures_and_shared_blocker():
    rows = {item.key: item for item in CRITERIA}
    assert "response moments agree" in rows["magnetic_moment_spin"].finding
    assert "no passing stable charged stationary branch" in rows["magnetic_moment_spin"].finding
    assert "Maxwell-stress flux" in rows["electric_force"].finding
    assert "center acceleration" in rows["electric_force"].finding
    assert "static Ampere closure" in rows["magnetic_force"].finding
    assert "Torque/precession" in rows["magnetic_force"].finding
