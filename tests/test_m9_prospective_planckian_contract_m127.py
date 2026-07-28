from openwave.xperiments.m9_cat_ept.prospective_planckian_contract_m127 import evaluate_package, run_prospective_planckian_contract


def test_prospective_contract_fails_closed_without_raw_data():
    result = run_prospective_planckian_contract()
    assert result["passed"]
    assert not result["decision"]["qualified_live_dataset_present"]
    assert not evaluate_package({})["qualified"]
    assert not result["decision"]["physical_promotion_allowed"]
