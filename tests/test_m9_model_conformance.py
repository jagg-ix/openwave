from openwave.xperiments.m9_cat_ept.model_conformance import (
    CRITERIA,
    PROMOTED_KEYS,
    fingerprint,
    run_conformance_study,
    validate_profile,
)


def test_exact_visible_criteria_count():
    assert len(CRITERIA) == 21


def test_domain_partition():
    assert validate_profile()["domain_counts"] == {
        "particles": 12,
        "forces": 5,
        "waves": 3,
        "thermal": 1,
    }


def test_status_counts_after_m9_86():
    assert validate_profile()["status_counts"] == {
        "validated": 3,
        "partial": 17,
        "negative": 1,
        "not_yet": 0,
    }


def test_exactly_audited_three_rows_are_promoted():
    validated = {item.key for item in CRITERIA if item.status == "validated"}
    assert validated == PROMOTED_KEYS == {
        "spin_half_statistics",
        "em_waves",
        "thermal_field",
    }


def test_promoted_rows_keep_stronger_boundaries():
    by_key = {item.key: item for item in CRITERIA}
    assert "not derived" in by_key["spin_half_statistics"].finding
    assert "Photon quantization" in by_key["em_waves"].finding
    assert "Microscopic CAT/EPT thermodynamics" in by_key["thermal_field"].finding


def test_stability_includes_rellich_interaction_and_identity_evidence():
    stability = next(item for item in CRITERIA if item.key == "particle_stability")
    assert all(
        any(name in path for path in stability.evidence)
        for name in (
            "m9_84_method_note.md",
            "m9_85_method_note.md",
            "m9_86_method_note.md",
        )
    )
    assert "local-Rellich" in stability.finding
    assert "analytic minimizing-orbit identity" in stability.finding
    assert stability.status == "partial"


def test_external_mode_comparison_remains_blocked_and_unvalidated():
    clock = next(item for item in CRITERIA if item.key == "de_broglie_clock")
    assert clock.status == "partial"
    assert any("m9_80_method_note.md" in path for path in clock.evidence)
    assert "blocks external comparison" in clock.finding


def test_single_criterion_negative_remains_lepton_hierarchy():
    negatives = [item.key for item in CRITERIA if item.status == "negative"]
    assert negatives == ["lepton_mass_spectrum"]


def test_full_study_passes():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(fingerprint()) == 64
