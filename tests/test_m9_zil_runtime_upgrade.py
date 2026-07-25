from openwave.xperiments.m9_cat_ept.zil_runtime_upgrade import (
    CURRENT_ZIL_HEAD,
    ZIL_RUNTIME_SOURCES,
    expected_graph_blobs,
    expected_runtime_blobs,
)
from openwave.xperiments.m9_cat_ept.zil_runtime_upgrade_current import (
    SELF_GRAPH,
    run_zil_runtime_upgrade,
    runtime_fingerprint,
    validate_zil_runtime_upgrade,
)


def all_graph_blobs():
    return {**expected_graph_blobs(), SELF_GRAPH["path"]: SELF_GRAPH["blob"]}


def test_current_zil_runtime_and_dual_root_contract_pass():
    result = run_zil_runtime_upgrade()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["repository"] == {
        "name": "jagg-ix/zil-lean",
        "branch": "main",
        "head": CURRENT_ZIL_HEAD,
    }
    assert result["root_contract"]["physlib_embedded_formalization"][
        "import"
    ] == "Zil"
    assert result["root_contract"]["openwave_native_graph_tooling"][
        "import"
    ] == "Zil.Native"
    assert len(ZIL_RUNTIME_SOURCES) == 6
    assert len(result["openwave_graphs"]) == 4
    assert result["decision"]["migration_graph_is_current_authority_input"]
    assert not result["decision"]["formal_or_physical_status_changed"]


def test_historical_zil_pins_are_not_treated_as_current():
    result = run_zil_runtime_upgrade()
    historical = {item["head"] for item in result["historical_pins"]}
    assert historical == {
        "f39758f85ee6300b8060e4f8ea1ecf344ed32c96",
        "64462a3c5e2ffb51a7b226675491cc3a9b156a8d",
    }
    assert CURRENT_ZIL_HEAD not in historical
    assert result["decision"]["historical_pins_remain_auditable"]


def test_zil_head_drift_fails_closed():
    result = validate_zil_runtime_upgrade(observed_head="0" * 40)
    assert not result["passed"]
    assert "ZIL runtime head drift detected" in result["errors"]
    assert not result["acceptance"]["current_zil_head_is_exact"]


def test_zil_runtime_source_drift_fails_closed():
    observed = expected_runtime_blobs()
    observed["Zil.lean"] = "0" * 40
    result = validate_zil_runtime_upgrade(observed_runtime_blobs=observed)
    assert not result["passed"]
    assert "ZIL runtime source drift detected: Zil.lean" in result["errors"]
    assert not result["acceptance"]["observed_runtime_blobs_match"]


def test_openwave_zil_graph_drift_fails_closed():
    observed = all_graph_blobs()
    path = SELF_GRAPH["path"]
    observed[path] = "f" * 40
    result = validate_zil_runtime_upgrade(observed_graph_blobs=observed)
    assert not result["passed"]
    assert f"OpenWave ZIL graph drift detected: {path}" in result["errors"]
    assert not result["acceptance"][
        "migration_graph_is_native_and_blob_pinned"
    ]


def test_zil_runtime_fingerprint_is_deterministic():
    result = run_zil_runtime_upgrade()
    assert len(result["fingerprint"]) == 64
    assert runtime_fingerprint() == runtime_fingerprint()
