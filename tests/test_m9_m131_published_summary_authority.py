from openwave.xperiments.m9_cat_ept.m131_published_summary_authority import (
    run_m131_published_summary_authority,
)


def test_m131_authority_passes_internally_and_fails_closed_physically():
    result = run_m131_published_summary_authority()
    assert result["passed"]
    assert result["internal_ready"]
    assert not result["physical_ready"]
    assert result["requirements"]["published_summary_rows_ingested"]
    assert not result["requirements"]["raw_source_file_digests_verified"]
    assert not result["requirements"]["raw_observation_rows_ingested"]
    assert not result["requirements"]["real_raw_leave_one_carrier_out_result"]
