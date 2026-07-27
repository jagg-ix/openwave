from openwave.xperiments.m9_cat_ept.physics_scope_profile import DOMAINS, run_physics_scope_profile


def test_nonparticle_scope_profile_has_eight_honest_domains() -> None:
    result = run_physics_scope_profile()
    assert result["passed"]
    assert len(DOMAINS) == 8
    assert len(result["domains"]) == 8
    assert sum(result["headline_counts"].values()) == 8
    assert not result["policy"]["particle_spectroscopy_is_primary_scorecard"]
    assert all(row["formal_sources"] for row in result["domains"])
    assert all(row["closed"] and row["open"] for row in result["domains"])
    assert not result["decision"]["external_physical_validation_complete"]


def test_scope_profile_keeps_physical_promotion_axes_open() -> None:
    result = run_physics_scope_profile()
    assert all(row["prediction"] != "external_validated" for row in result["domains"])
    assert any(row["calibration"] == "open" for row in result["domains"])
