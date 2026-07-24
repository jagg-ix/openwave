from openwave.xperiments.m9_cat_ept.model_conformance import CRITERIA, fingerprint, run_conformance_study, validate_profile

def test_exact_visible_criteria_count():
    assert len(CRITERIA) == 21

def test_domain_partition():
    assert validate_profile()["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1}

def test_status_counts_after_m9_62():
    assert validate_profile()["status_counts"] == {"validated": 0, "partial": 20, "negative": 1, "not_yet": 0}

def test_stability_includes_m9_60_61():
    stability = next(c for c in CRITERIA if c.key == "particle_stability")
    assert all(any(name in path for path in stability.evidence) for name in ("m9_60_method_note.md", "m9_61_method_note.md"))

def test_clock_remains_partial_with_formal_scope():
    clock = next(c for c in CRITERIA if c.key == "de_broglie_clock")
    assert clock.status == "partial"
    assert any("formal_status_matrix.md" in path for path in clock.evidence)

def test_falsification_ledger_is_referenced():
    assert any("physical_calibration_ledger.py" in path for criterion in CRITERIA for path in criterion.evidence)

def test_full_study_passes():
    result = run_conformance_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(fingerprint()) == 64
