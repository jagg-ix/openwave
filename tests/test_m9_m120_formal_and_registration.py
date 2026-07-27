from openwave.xperiments.m9_cat_ept.formalization_m120_extension import (
    CURRENT_FORMAL_HEAD,
    FORMAL_SOURCES,
    PENDING_FORMAL_CANDIDATES,
    PHYSLIB_ROOT_BLOB,
    run_formalization_m120_extension,
    validate_formal_snapshot,
)
from openwave.xperiments.m9_cat_ept.m120_spectral_phenomenology_evidence_authority import (
    run_m120_spectral_phenomenology_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.model_registration_m120 import (
    run_model_registration_study,
)


def test_m120_formal_snapshot_passes_and_records_drafts_as_unmerged() -> None:
    result = run_formalization_m120_extension()

    assert result["passed"]
    assert result["current_formal_head"] == CURRENT_FORMAL_HEAD
    assert result["physlib_root_blob"] == PHYSLIB_ROOT_BLOB
    assert len(result["sources"]) == 5
    assert len(PENDING_FORMAL_CANDIDATES) == 2
    assert all(candidate["state"] == "draft-open-unmerged" for candidate in PENDING_FORMAL_CANDIDATES)


def test_m120_formal_snapshot_fails_closed_on_head_root_and_source_drift() -> None:
    expected = {source["path"]: source["blob"] for source in FORMAL_SOURCES}
    changed = dict(expected)
    first = next(iter(changed))
    changed[first] = "0" * 40

    assert not validate_formal_snapshot(head="0" * 40)["passed"]
    assert not validate_formal_snapshot(root_blob="0" * 40)["passed"]
    assert not validate_formal_snapshot(source_blobs=changed)["passed"]


def test_m120_authority_and_registration_pass_without_physical_promotion() -> None:
    authority = run_m120_spectral_phenomenology_evidence_authority()
    registration = run_model_registration_study()
    current = registration["m9_120"]

    assert authority["passed"]
    assert registration["passed"]
    assert registration["schema"] == "openwave.model-registration.v23"
    assert current["gauge_invariant_finite_spectra"]
    assert current["gauge_invariant_transition_response"]
    assert current["finite_spectral_refinement"]
    assert not current["physical_particle_spectrum_predicted"]
    assert not current["intrinsic_decay_channel_constructed"]
    assert not current["continuum_spectrum_theorem_complete"]
    assert not current["physical_prediction_complete"]
    assert current["physical_claims_promoted"] == []
