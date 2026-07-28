from openwave.xperiments.m9_cat_ept.existing_data_normalization_m130 import run_existing_data_normalization


def test_existing_data_normalization():
    result = run_existing_data_normalization()
    assert result["passed"]
    assert len(result["rows"]) == 2
