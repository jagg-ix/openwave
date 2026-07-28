from openwave.xperiments.m9_cat_ept.physlib_four_clock_authority_m128 import run_physlib_four_clock_authority


def test_physlib_authority_separates_merged_and_candidate():
    result = run_physlib_four_clock_authority()
    assert result["passed"]
    assert result["merged_authority"]["pr"] == 37
    assert result["candidate_authority"]["pr"] == 38
    assert result["candidate_authority"]["state"] != "merged"
