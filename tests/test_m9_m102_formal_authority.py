from openwave.xperiments.m9_cat_ept.formalization_m102_extension import (
    COMMITS_SINCE_M101,
    CURRENT_FORMAL_HEAD,
    CURRENT_PHYSLIB_ROOT_BLOB,
    GOVERNANCE_SOURCES,
    HISTORICAL_FORMAL_HEAD,
    canonical_payload,
    run_formalization_m102_extension,
)


def test_historical_and_current_formal_authorities_are_distinct():
    assert HISTORICAL_FORMAL_HEAD == "acdbe8ce6456e66837bd18604cf3107d3181c4de"
    assert CURRENT_FORMAL_HEAD == "eba0124fcfbc1216d973bb6f504c5a6d324de60c"
    assert HISTORICAL_FORMAL_HEAD != CURRENT_FORMAL_HEAD
    assert COMMITS_SINCE_M101 == 6
    assert len(CURRENT_PHYSLIB_ROOT_BLOB) == 40


def test_three_evidence_governance_sources_are_exact():
    assert len(GOVERNANCE_SOURCES) == 3
    assert {source["path"].split("/")[-1] for source in GOVERNANCE_SOURCES} == {
        "ClaimMaturity.lean",
        "EvidenceIntegrity.lean",
        "TheoremIntentAudit.lean",
    }
    assert all(len(source["blob"]) == 40 for source in GOVERNANCE_SOURCES)
    assert GOVERNANCE_SOURCES[0]["build_mode"] == "default-root"
    assert GOVERNANCE_SOURCES[1]["build_mode"] == "default-root"
    assert GOVERNANCE_SOURCES[2]["build_mode"] == "on-demand"


def test_formal_refresh_preserves_historical_reproduction_boundary():
    payload = canonical_payload()
    assert payload["policy"]["historical_reproduction_pin_is_preserved"]
    assert payload["policy"]["governance_updates_do_not_create_physical_evidence"]
    result = run_formalization_m102_extension()
    assert result["passed"]
    assert not result["decision"]["new_numerical_physics_result_created"]
