from openwave.xperiments.m9_cat_ept.m131_existing_data_import_authority import run_m131_existing_data_import_authority

def test_m131_authority_fails_closed():
    result = run_m131_existing_data_import_authority()
    assert result["passed"]
    assert result["internal_ready"]
    assert not result["physical_ready"]
