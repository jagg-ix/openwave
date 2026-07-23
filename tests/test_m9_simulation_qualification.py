import pytest
from openwave.xperiments.m9_cat_ept.simulation_qualification import (
    ExponentialBalanceAdapter, ReversibleAdapter, finite_difference_sensitivity,
    reference_scenario, run_qualification, run_simulation_qualification_study,
)

def test_scenario_fingerprint_is_stable():
    assert reference_scenario().fingerprint()==reference_scenario().fingerprint()

def test_duplicate_adapter_names_are_rejected():
    a=ReversibleAdapter(name="x")
    with pytest.raises(ValueError): run_qualification((a,a),reference_scenario())

def test_balance_law_passes():
    a=ExponentialBalanceAdapter("x",.12); t=a.simulate(reference_scenario()); assert a.laws(t)["balance"]

def test_reversible_control_is_constant_norm():
    a=ReversibleAdapter(); t=a.simulate(reference_scenario()); assert a.laws(t)["matter_constant"]

def test_parameter_sensitivity_is_nonzero():
    assert finite_difference_sensitivity(.12)>1

def test_pairwise_models_are_distinct():
    r=run_simulation_qualification_study(); assert min(r["pairwise_distances"].values())>1e-3

def test_replay_is_deterministic():
    assert run_simulation_qualification_study()["acceptance"]["deterministic_replay"]

def test_full_study_passes():
    r=run_simulation_qualification_study(); assert r["passed"] and all(r["acceptance"].values())
