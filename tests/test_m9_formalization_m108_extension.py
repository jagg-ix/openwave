from openwave.xperiments.m9_cat_ept.formalization_m108_extension import (
    CURRENT_FORMAL_HEAD,
    CURRENT_ZIL_HEAD,
    PROGRAM_HEALTH_BASELINE,
    validate_program_health,
)


def test_current_heads_and_health_baseline_are_pinned():
    assert CURRENT_FORMAL_HEAD == "128974a501d3d0a43108a3ab9a1bd9d4fea5d7db"
    assert CURRENT_ZIL_HEAD == "e09723a44185a1e70031ad2661c8009dc98bef74"
    assert PROGRAM_HEALTH_BASELINE["untested_numerical"] == 0
    assert validate_program_health()["passed"]


def test_program_health_regression_fails_closed():
    observed = dict(PROGRAM_HEALTH_BASELINE)
    observed["hidden_debt"] += 1
    result = validate_program_health(observed)
    assert not result["passed"]
    assert "hidden_debt regressed" in result["errors"]
