from openwave.xperiments.m9_cat_ept.formalization_m105_extension import CURRENT_ZIL_HEAD,HISTORICAL_ZIL_HEAD,PHYSICS_SOURCES,ZIL_SOURCES,canonical_payload


def test_current_physlib_and_zil_sources_are_pinned():
    payload=canonical_payload()
    assert payload["physlib"]["head"]=="eba0124fcfbc1216d973bb6f504c5a6d324de60c"
    assert CURRENT_ZIL_HEAD=="e09723a44185a1e70031ad2661c8009dc98bef74"
    assert CURRENT_ZIL_HEAD!=HISTORICAL_ZIL_HEAD
    assert len(PHYSICS_SOURCES)==8
    assert len(ZIL_SOURCES)==5
    assert all(len(row["blob"])==40 for row in (*PHYSICS_SOURCES,*ZIL_SOURCES))
    assert payload["policy"]["reporting_runtime_updates_promote_no_physics"]
