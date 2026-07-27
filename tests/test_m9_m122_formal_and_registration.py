from openwave.xperiments.m9_cat_ept.formalization_m122_extension import (
    FORMAL_SOURCES,
    run_formalization_m122_extension,
    validate_formal_snapshot,
)
from openwave.xperiments.m9_cat_ept.m122_external_evidence_readiness_authority import (
    run_m122_external_evidence_readiness_authority,
)
from openwave.xperiments.m9_cat_ept.model_registration_m122 import (
    run_model_registration_study,
)


def test_formal_snapshot_registers_trace_and_zero_width_authorities() -> None:
    result = run_formalization_m122_extension()
    paths = {source["path"] for source in result["sources"]}
    assert result["passed"]
    assert result["current_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
    assert any(path.endswith("TracePreservation.lean") for path in paths)
    assert any(path.endswith("CauchyWeakLimit.lean") for path in paths)


def test_formal_snapshot_fails_closed_on_head_root_and_source_drift() -> None:
    expected = {
        f"{source.get('repository', 'jagg-ix/entropic-physlib-private')}:{source['path']}": source["blob"]
        for source in FORMAL_SOURCES
    }
    changed = dict(expected)
    changed[next(iter(changed))] = "0" * 40
    assert not validate_formal_snapshot(head="0" * 40)["passed"]
    assert not validate_formal_snapshot(root_blob="0" * 40)["passed"]
    assert not validate_formal_snapshot(source_blobs=changed)["passed"]


def test_m122_authority_and_registration_pass_without_physical_promotion() -> None:
    authority = run_m122_external_evidence_readiness_authority()
    registration = run_model_registration_study()
    current = registration["m9_122"]

    assert authority["passed"]
    assert registration["passed"]
    assert registration["schema"] == "openwave.model-registration.v25"
    assert current["external_evidence_package_schema"]
    assert current["blinded_external_evaluator"]
    assert current["independent_identity_bridge_contract"]
    assert not current["real_external_evidence_ingested"]
    assert not current["external_validation_complete"]
    assert current["physical_claims_promoted"] == []
