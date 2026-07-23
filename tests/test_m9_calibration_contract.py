import math

import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.calibration_contract import (
    CalibrationAnchors,
    calibrated_signature,
    default_contract,
    identifiability_audit,
    missing_anchor_rejections,
    physical_rate_per_second,
    recover_rate_from_pair,
    run_calibration_contract_study,
    synthetic_roundtrip,
)


def test_anchor_validation_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        CalibrationAnchors(0.0, 0.9, 0.9, 0.9)
    with pytest.raises(ValueError):
        CalibrationAnchors(1.0, 1.1, 0.9, 0.9)


def test_dimensionless_rate_converts_with_time_anchor() -> None:
    contract = default_contract()
    rate = physical_rate_per_second(0.17, contract.anchors)
    assert math.isclose(rate, 68000.0, rel_tol=1e-15)


def test_three_signatures_are_operationally_distinct() -> None:
    contract = default_contract()
    time = 5e-6
    amplitude = calibrated_signature("imaginary_action", time, 0.17, contract)
    lindblad = calibrated_signature("lindblad_dephasing", time, 0.23, contract)
    reservoir = calibrated_signature("explicit_reservoir", time, 0.12, contract)
    assert amplitude["accessible_trace"] < lindblad["accessible_trace"]
    assert lindblad["normalized_purity"] < amplitude["normalized_purity"]
    assert reservoir["reservoir_transfer"] > 0.0


def test_pair_recovery_closes_for_all_mechanisms() -> None:
    contract = default_contract()
    rates = {
        "imaginary_action": 0.17,
        "lindblad_dephasing": 0.23,
        "explicit_reservoir": 0.12,
    }
    for mechanism, rate in rates.items():
        first = calibrated_signature(mechanism, 1e-6, rate, contract)
        second = calibrated_signature(mechanism, 7.5e-6, rate, contract)
        recovered = recover_rate_from_pair(mechanism, first, second, contract)
        assert math.isclose(recovered, rate, abs_tol=2e-14)


def test_unanchored_rate_scale_is_rank_deficient() -> None:
    audit = identifiability_audit(default_contract())
    assert audit["rank_without_time_anchor"] == 1
    assert audit["unanchored_null_vector_residual"] <= 1e-12


def test_time_anchor_restores_rank() -> None:
    audit = identifiability_audit(default_contract())
    assert audit["rank_with_time_anchor"] == 2
    assert np.isfinite(audit["condition_number_with_anchor"])


def test_missing_anchor_cases_are_rejected() -> None:
    assert all(missing_anchor_rejections().values())


def test_synthetic_roundtrip_is_not_physical_calibration() -> None:
    result = synthetic_roundtrip(default_contract())
    assert result["maximum_absolute_error"] <= 2e-14
    assert result["synthetic_only"] is True


def test_full_contract_study_passes_with_negative_physical_claim() -> None:
    result = run_calibration_contract_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["physical_calibration_completed"] is False
    assert result["classification"]["does_not_establish"]
