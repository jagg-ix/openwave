import pytest
from openwave.xperiments.m9_cat_ept.three_clock_calibration_contract import ClockCalibrationConfig, ThreeClockCalibration, run_three_clock_calibration_contract

def test_calibration_contract_passes_without_physical_claim():
    result = run_three_clock_calibration_contract()
    assert result['passed']
    assert all(result['acceptance'].values())
    assert result['decision']['page_wootters_to_modular_internal_calibration_constructed']
    assert not result['decision']['independent_physical_clock_calibration_complete']

def test_invalid_calibrations_fail_closed():
    with pytest.raises(ValueError):
        ThreeClockCalibration(ClockCalibrationConfig(relational_to_model_time=-1.0))
    with pytest.raises(ValueError):
        ThreeClockCalibration(ClockCalibrationConfig(nominal_lapse=0.0))
