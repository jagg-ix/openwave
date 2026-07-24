from openwave.xperiments.m9_cat_ept.model_conformance import (
    CRITERIA,
    fingerprint,
    run_conformance_study,
    validate_profile,
)


def test_exact_visible_criteria_count():
    assert len(CRITERIA) == 21


def test_domain_partition():
    assert validate_profile()["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1}


def test_status_counts_after_m9_68():
    assert validate_profile()["status_counts"] == {"validated": 0, "partial": 20, "negative": 1, "not_yet": 0}


def test_stability_includes_m9_66_67():
    stability = next(item for item in CRITERIA if item.key == "particle_stability")
    assert all(any(name in path for path in stability.evidence) for name in ("m9_66_method_note.md", "m9_67_method_note.md"))


def test_falsified_subprediction_is_referenced_but_not_criterion_negative():
    clock = next(item for item in CRITERIA if item.key == "de_broglie_clock")
    assert clock.status == "partial"
    assert any("m9_68_method_note.md" in path for path in clock.evidence)
    assert "fails" in clock.finding


def test_single_criterion_negative_remains_lepton_hierarchy():
    negatives = [item.key for item in CRITERIA if item.status == "negative"]
    assert negatives == ["lepton_mass_spectrum"]


def test_full_study_passes():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(fingerprint()) == 64
