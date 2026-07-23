import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.intrinsic_clock_reduction import ClockParameters, generate_clock_trace, run_intrinsic_clock_study, zero_channel_controls

def test_invalid_velocity_is_rejected():
    with pytest.raises(ValueError): ClockParameters(velocity_amplitude=1.0)
def test_phase_frequency_is_recovered(): assert abs(run_intrinsic_clock_study()["recovered_internal_frequency"]-1.7)<2e-12
def test_entropy_and_geometry_are_monotone():
    r=run_intrinsic_clock_study(); assert r["acceptance"]["entropy_monotone"] and r["acceptance"]["geometry_clock_monotone_and_subluminal"]
def test_channels_are_not_affinely_identical():
    r=run_intrinsic_clock_study(); assert r["entropy_vs_phase_affine_residual"]>1e-2 and r["geometry_vs_phase_affine_residual"]>1e-3
def test_zero_loss_keeps_phase():
    c=zero_channel_controls(); assert c["zero_loss_entropy_span"]<2e-12 and c["zero_loss_phase_span"]>10
def test_zero_frequency_keeps_entropy():
    c=zero_channel_controls(); assert c["zero_frequency_phase_span"]<2e-12 and c["zero_frequency_entropy_span"]>.5
def test_global_amplitude_scaling_does_not_change_clocks():
    a=generate_clock_trace(); b=generate_clock_trace(amplitude_scale=4); assert np.max(np.abs(a["phase"]-b["phase"]))<2e-12 and np.max(np.abs(a["entropic_clock"]-b["entropic_clock"]))<2e-12
def test_full_clock_study_passes_without_physical_time_promotion():
    r=run_intrinsic_clock_study(); assert r["passed"] and not r["physical_time_identified"]
