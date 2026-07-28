from openwave.xperiments.m9_cat_ept.four_clock_calibration_family_m129 import run_calibration_family


def test_nonaffine_calibration_closes():
    result = run_calibration_family()
    assert result["passed"]
    assert result["maximum_roundtrip_error"] < 1e-12
    assert result["acceptance"]["non_affine_map_is_exercised"]
