from openwave.xperiments.m9_cat_ept.existing_data_adapters_m131 import run_dataset_adapters

def test_dataset_adapters():
    result = run_dataset_adapters()
    assert result["passed"]
    assert not result["decision"]["real_rows_imported"]
