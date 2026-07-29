from openwave.xperiments.m9_cat_ept.physlib_capability_correction_m136 import (
    COMPLETED,
    OPEN,
    SOURCES,
    ZIL_METRICS,
    run_physlib_capability_correction,
)


def test_corrected_capability_matrix_passes():
    result = run_physlib_capability_correction()
    assert result["passed"]
    assert all(result["acceptance"].values())


def test_gravity_maxwell_and_clock_coverage_is_not_understated():
    assert COMPLETED["weak_adm_constraint_propagation_local"]
    assert COMPLETED["all_real_time_lipschitz_flow"]
    assert COMPLETED["maximal_cauchy_zorn_existence"]
    assert COMPLETED["caticha_kg_intrinsic_maxwell_equality"]
    assert COMPLETED["page_wootters_pure_dissipative_limit"]


def test_assembled_rate_linewidth_theorem_remains_open():
    assert OPEN["assembled_rate_kl_linewidth_theorem"]
    assert OPEN["hwhm_eq_rate_data_gamma"]
    assert OPEN["fwhm_eq_two_rate_data_gamma"]
    assert OPEN["t1_eq_inv_two_rate_data_gamma"]


def test_zil_metrics_and_source_pins_are_exact():
    assert ZIL_METRICS["edges_total"] == 4589
    assert ZIL_METRICS["fully_documented_predictions"] == 21
    assert ZIL_METRICS["circular_requires_chains"] == 0
    assert ZIL_METRICS["adaptive_conformance_failures"] == 0
    assert ZIL_METRICS["primitive_premises"] == 143
    assert ZIL_METRICS["buried_weakest_link_conditionals"] == 9
    assert all(len(item["blob"]) == 40 for item in SOURCES.values())
