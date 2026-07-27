from openwave.xperiments.m9_cat_ept.formalization_m124_extension import (
    DEVELOPMENT_HEAD,
    FORMAL_REPOSITORY,
    FORMAL_SOURCES,
    run_formalization_m124_extension,
    validate_formal_snapshot,
)
from openwave.xperiments.m9_cat_ept.model_registration_m124 import run_model_registration_study


def test_three_clock_formal_authority_is_pinned() -> None:
    result = run_formalization_m124_extension()
    assert result["passed"]
    assert len(result["sources"]) == 4
    assert result["development_head"] == "af78ea63ee0b39456d8dab023761482196b8c172"
    assert result["development_branch"] == "entropic-physlib-linear-full"
    assert not result["decision"]["single_unified_clock_theorem_present"]


def test_formal_snapshot_rejects_head_and_blob_drift() -> None:
    assert not validate_formal_snapshot(development_head="0" * 40)["passed"]
    expected = {f"{source.get('repository', FORMAL_REPOSITORY)}:{source['path']}": source["blob"] for source in FORMAL_SOURCES}
    first = next(iter(expected))
    expected[first] = "0" * 40
    assert not validate_formal_snapshot(development_head=DEVELOPMENT_HEAD, source_blobs=expected)["passed"]


def test_schema_v27_registration_passes_without_unified_clock_promotion() -> None:
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_124"]
    assert result["schema"] == "openwave.model-registration.v27"
    assert current["clock_role_count"] == 3
    assert current["pairwise_bridge_count"] == 3
    assert current["three_aspect_time_framework"]
    assert not current["single_unified_physical_clock_established"]
    assert current["physical_claims_promoted"] == []
