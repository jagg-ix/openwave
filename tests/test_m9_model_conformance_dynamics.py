from openwave.xperiments.m9_cat_ept.model_conformance_current import (
    CRITERIA as M9_96_CRITERIA,
)
from openwave.xperiments.m9_cat_ept.model_conformance_dynamics import (
    CRITERIA,
    ROW_REPLACEMENTS,
    run_conformance_study,
)


def test_m9_97_overlay_changes_exactly_three_findings():
    before = {item.key: item for item in M9_96_CRITERIA}
    after = {item.key: item for item in CRITERIA}
    changed = {
        key
        for key in before
        if before[key].evidence != after[key].evidence
        or before[key].finding != after[key].finding
        or before[key].status != after[key].status
    }
    assert changed == set(ROW_REPLACEMENTS) == {
        "magnetic_moment_spin",
        "electric_force",
        "magnetic_force",
    }
    assert all(before[key].status == after[key].status == "partial" for key in changed)


def test_m9_97_profile_preserves_21_rows_and_status_counts():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["schema"] == "openwave.m9.models-conformance.v15"
    assert result["audit"]["criterion_count"] == 21
    assert result["audit"]["domain_counts"] == {
        "particles": 12,
        "forces": 5,
        "waves": 3,
        "thermal": 1,
    }
    assert result["audit"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    assert result["decision"]["momentum_and_generator_subreductions_closed"]
    assert result["decision"]["stationary_center_and_bmt_reductions_open"]
    assert result["decision"]["criterion_rows_promoted"] == []
