import math
import pytest
from openwave.xperiments.m9_cat_ept.two_body_forces import InteractionParameters, electric_energy, run_two_body_force_study

def test_invalid_softening_is_rejected():
    with pytest.raises(ValueError): InteractionParameters(electric_softening=0)
def test_electric_energy_is_finite_at_origin(): assert math.isfinite(electric_energy(0,1,1,InteractionParameters()))
def test_energy_derivatives_match_forces():
    r=run_two_body_force_study(); assert r["acceptance"]["electric_derivative_matches_energy"] and r["acceptance"]["magnetic_derivative_matches_energy"]
def test_asymptotic_slopes():
    r=run_two_body_force_study(); assert abs(r["electric"]["asymptotic_log_slope"]+2)<2e-2 and abs(r["magnetic"]["asymptotic_log_slope"]+4)<3e-2
def test_electric_signs():
    r=run_two_body_force_study(); assert r["electric"]["like_force"]>0 and r["electric"]["opposite_force"]<0
def test_magnetic_orientation_signs():
    r=run_two_body_force_study(); assert r["magnetic"]["parallel_axial_force"]<0 and r["magnetic"]["antiparallel_axial_force"]>0
def test_action_reaction_and_superposition():
    r=run_two_body_force_study(); assert r["combined_action_reaction_error"]<2e-14 and r["acceptance"]["finite_size_regularization_and_superposition"]
def test_full_force_study_passes_without_emergent_particle_claim():
    r=run_two_body_force_study(); assert r["passed"] and not r["emergent_particle_interaction_established"]
