from openwave.xperiments.m9_cat_ept.published_summary_ingestion_m131 import (
    published_summary_rows,
    run_published_summary_ingestion,
)


def test_published_summary_rows_are_ingested_without_raw_data_overclaim():
    result = run_published_summary_ingestion()
    assert result["passed"]
    assert len(result["rows"]) == 9
    assert not result["raw_observation_rows_ingested"]
    assert {row["source_id"] for row in published_summary_rows()} == {
        "moreva-2017-multitime",
        "gustavsson-2016-qubit",
        "lu-2003-dot",
    }
