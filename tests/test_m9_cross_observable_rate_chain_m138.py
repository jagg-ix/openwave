import math

from openwave.xperiments.m9_cat_ept.cross_observable_rate_chain_m138 import (
    FORMAL_HEAD,
    FORMAL_SOURCE,
    RateCalibration,
    canonical_payload,
    run_cross_observable_rate_chain,
)
from openwave.xperiments.m9_cat_ept.physlib_capability_correction_m136 import (
    COMPLETED,
    OPEN,
    run_physlib_capability_correction,
)


def test_exact_physlib_cross_observable_source_is_pinned():
    assert FORMAL_HEAD == "deb1eb3ecb4aabbba1555b24253d9dd8f6fba1f2"
    assert FORMAL_SOURCE["blob"] == "d99136a02b3d09fa5338f8187ebf023e47be91f0"
    assert "calibrated_rate_linewidth_relaxation_KL_chain" in FORMAL_SOURCE["declarations"]


def test_one_counted_rate_controls_width_relaxation_and_kl():
    result = run_cross_observable_rate_chain(RateCalibration())
    assert result["passed"] and all(result["acceptance"].values())
    gamma = result["calibration"]["gamma"]
    total = result["calibration"]["total_rate"]
    assert math.isclose(result["spectral"]["hwhm"], gamma)
    assert math.isclose(result["spectral"]["fwhm"], total)
    assert math.isclose(result["relaxation"]["T1"], 1.0 / total)
    assert math.isclose(result["kl"]["derivative_fd"], -result["kl"]["production_rate"], rel_tol=2e-9, abs_tol=2e-9)


def test_empirical_scope_is_not_promoted():
    payload = canonical_payload()
    assert not any(payload["claim_boundary"].values())
    assert run_cross_observable_rate_chain()["decision"]["physical_claims_promoted"] == []


def test_capability_matrix_promotes_only_formal_chain():
    result = run_physlib_capability_correction()
    assert result["passed"]
    assert all(COMPLETED[key] for key in (
        "assembled_rate_kl_linewidth_theorem",
        "hwhm_eq_rate_data_gamma",
        "fwhm_eq_two_rate_data_gamma",
        "t1_eq_inv_two_rate_data_gamma",
    ))
    assert OPEN["experimental_cross_carrier_validation"]
    assert OPEN["pure_dephasing_model_selection"]
