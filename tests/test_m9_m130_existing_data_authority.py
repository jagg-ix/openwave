from openwave.xperiments.m9_cat_ept.m130_existing_data_authority import run_m130_existing_data_authority


def test_m130_existing_data_authority_fails_closed():
    result = run_m130_existing_data_authority()
    assert result["passed"]
    assert result["internal_ready"]
    assert not result["physical_ready"]
