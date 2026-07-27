from openwave.xperiments.m9_cat_ept.three_clock_time_profile import run_three_clock_time_profile


def test_three_clock_roles_and_bridges_are_distinct() -> None:
    result = run_three_clock_time_profile()
    assert result["passed"]
    assert len(result["roles"]) == 3
    assert {row["key"] for row in result["roles"]} == {"page_wootters_relational", "modular_thermal", "entropic_irreversible"}
    assert len(result["pairwise_bridges"]) == 3
    assert not result["decision"]["single_unified_physical_clock_established"]
