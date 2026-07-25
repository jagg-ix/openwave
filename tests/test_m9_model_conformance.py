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


def test_status_counts_after_m9_92():
    assert validate_profile()["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }


def test_exactly_audited_seven_rows_are_promoted():
    validated = {item.key for item in CRITERIA if item.status == "validated"}
    assert validated == PROMOTED_KEYS == {
        "charge_quantization",
        "particle_stability",
        "spin_half_statistics",
        "em_waves",
        "klein_gordon",
        "orbital_quantization",
        "thermal_field",
    }


def test_promoted_rows_keep_stronger_boundaries():
    by_key = {item.key: item for item in CRITERIA}
    assert "not thereby identified" in by_key["charge_quantization"].finding
    assert "not physical-particle identification" in by_key["particle_stability"].finding
    assert "Physical electron identity" in by_key["spin_half_statistics"].finding
    assert "Photon quantization" in by_key["em_waves"].finding
    assert "Interacting scalar QFT" in by_key["klein_gordon"].finding
    assert "Emergent particles" in by_key["orbital_quantization"].finding
    assert "Microscopic CAT/EPT thermodynamics" in by_key["thermal_field"].finding


def test_new_closures_have_focused_evidence():
    by_key = {item.key: item for item in CRITERIA}
    assert any("m9_90_method_note.md" in path for path in by_key["charge_quantization"].evidence)
    assert any("m9_91_method_note.md" in path for path in by_key["klein_gordon"].evidence)
    assert any("m9_92_method_note.md" in path for path in by_key["orbital_quantization"].evidence)


def test_stability_includes_live_flow_conservation_and_orbit_evidence():
    stability = next(item for item in CRITERIA if item.key == "particle_stability")
    assert all(
        any(name in path for path in stability.evidence)
        for name in (
            "m9_87_method_note.md",
            "m9_88_method_note.md",
            "m9_89_method_note.md",
        )
    )
    assert "genuine free H1 unitary group" in stability.finding
    assert "standing-wave phase orbit" in stability.finding
    assert stability.status == "validated"


def test_external_mode_comparison_remains_blocked_and_unvalidated():
    clock = next(item for item in CRITERIA if item.key == "de_broglie_clock")
    assert clock.status == "partial"
    assert "external evidence remain open" in clock.finding


def test_single_criterion_negative_remains_lepton_hierarchy():
    negatives = [item.key for item in CRITERIA if item.status == "negative"]
    assert negatives == ["lepton_mass_spectrum"]


def test_full_study_passes():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(fingerprint()) == 64
