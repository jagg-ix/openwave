from openwave.xperiments.m9_cat_ept.existing_experiment_four_clock_protocol_m129 import run_existing_experiment_protocol


def test_existing_experiment_protocol_is_fail_closed():
    result = run_existing_experiment_protocol()
    assert result["passed"]
    assert result["decision"]["existing_experiments_can_be_reused"]
    assert not result["decision"]["qualified_live_package_present"]
