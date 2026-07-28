from openwave.xperiments.m9_cat_ept.m129_calibration_existing_data_authority import run_m129_calibration_existing_data_authority


def test_m129_authority_keeps_physical_promotion_blocked():
    result = run_m129_calibration_existing_data_authority()
    assert result["passed"]
    assert result["decision"]["internal_methodology_ready"]
    assert not result["decision"]["physical_promotion_allowed"]
