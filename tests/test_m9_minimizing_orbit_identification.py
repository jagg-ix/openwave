from openwave.xperiments.m9_cat_ept.minimizing_orbit_identification import (
    FROZEN_MODE_FINGERPRINT,
    FROZEN_MODE_RATIO,
    external_testability_gate,
    run_minimizing_orbit_identification,
)


def test_external_mode_comparison_is_fail_closed():
    gate = external_testability_gate()
    assert not gate["comparison_admissible"]
    assert not gate["comparison_performed"]
    assert gate["prerequisites"]["no_refit_protocol_frozen"]


def test_m9_71_record_remains_immutable():
    result = run_minimizing_orbit_identification()
    frozen = result["frozen_external_protocol"]
    assert frozen["dimensionless_ratio"] == FROZEN_MODE_RATIO
    assert frozen["fingerprint"] == FROZEN_MODE_FINGERPRINT


def test_m9_80_finite_grid_identification_passes_without_physical_promotion():
    result = run_minimizing_orbit_identification()
    assert result["passed"]
    assert result["decision"][
        "finite_grid_minimizing_orbit_identification_qualified"
    ]
    assert not result["decision"]["analytic_minimizing_orbit_identified_in_lean"]
    assert not result["decision"]["physical_prediction_validated"]
