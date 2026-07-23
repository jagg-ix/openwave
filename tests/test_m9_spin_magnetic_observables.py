import pytest
from openwave.xperiments.m9_cat_ept.spin_magnetic_observables import SpinParameters, field_observables, localized_spinor, run_spin_magnetic_study

def test_invalid_grid_is_rejected():
    with pytest.raises(ValueError): SpinParameters(points=200)
def test_normalization_and_spin_half():
    p=SpinParameters(); o=field_observables(localized_spinor(p),p); assert abs(o["norm"]-1)<2e-12 and abs(o["spin_z"]-.5)<2e-12
def test_magnetic_moment_is_from_pauli_current():
    o=run_spin_magnetic_study()["observables"]; assert abs(o["magnetic_moment_z"]-o["expected_pauli_moment"])<5e-4
def test_orbital_control_is_zero(): assert abs(run_spin_magnetic_study()["observables"]["orbital_z"])<2e-12
def test_spin_flip_reverses_spin_and_moment():
    r=run_spin_magnetic_study(); assert abs(r["spin_down_observables"]["spin_z"]+r["observables"]["spin_z"])<2e-12 and abs(r["spin_down_observables"]["magnetic_moment_z"]+r["observables"]["magnetic_moment_z"])<5e-4
def test_double_cover():
    r=run_spin_magnetic_study(); assert r["double_cover"]["two_pi_to_minus_state_error"]<2e-12 and r["double_cover"]["four_pi_return_error"]<2e-12
def test_bilinears_and_global_phase_are_invariant():
    r=run_spin_magnetic_study(); assert r["acceptance"]["bilinears_return_after_two_pi"] and r["acceptance"]["global_phase_and_resolution_robust"]
def test_full_spin_study_passes_without_exchange_claim():
    r=run_spin_magnetic_study(); assert r["passed"] and not r["fermionic_exchange_statistics_established"]
