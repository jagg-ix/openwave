from openwave.xperiments.m9_cat_ept.formalization_m121_extension import (
    CURRENT_FORMAL_HEAD,
    FORMAL_SOURCES,
    PHYSLIB_ROOT_BLOB,
    ZIL_PUBLIC_HEAD,
    run_formalization_m121_extension,
    validate_formal_snapshot,
)
from openwave.xperiments.m9_cat_ept.m121_open_system_evidence_authority import (
    run_m121_open_system_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.model_registration_m121 import (
    run_model_registration_study,
)


def test_m121_formal_snapshot_passes() -> None:
    result = run_formalization_m121_extension()
    assert result["passed"]
    assert result["current_formal_head"] == CURRENT_FORMAL_HEAD
    assert result["physlib_root_blob"] == PHYSLIB_ROOT_BLOB
    assert result["zil_public_head"] == ZIL_PUBLIC_HEAD
    assert len(result["sources"]) == 5


def test_m121_formal_snapshot_fails_closed_on_drift() -> None:
    expected = {source["path"]: source["blob"] for source in FORMAL_SOURCES}
    changed = dict(expected)
    changed[next(iter(changed))] = "0" * 40
    assert not validate_formal_snapshot(head="0" * 40)["passed"]
    assert not validate_formal_snapshot(root_blob="0" * 40)["passed"]
    assert not validate_formal_snapshot(zil_head="0" * 40)["passed"]
    assert not validate_formal_snapshot(source_blobs=changed)["passed"]


def test_m121_authority_and_registration_pass_without_external_promotion() -> None:
    authority = run_m121_open_system_evidence_authority()
    registration = run_model_registration_study()
    current = registration["m9_121"]
    assert authority["passed"]
    assert registration["passed"]
    assert registration["schema"] == "openwave.model-registration.v24"
    assert current["cptp_open_system_decay"]
    assert current["intrinsic_model_unit_lifetime"]
    assert current["blind_prediction_commitment"]
    assert current["physical_promotion_gate"]
    assert not current["independent_physical_anchor_ready"]
    assert not current["heldout_validation_complete"]
    assert not current["external_physical_promotion_allowed"]
    assert current["physical_claims_promoted"] == []
