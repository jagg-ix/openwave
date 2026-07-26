import numpy as np

from openwave.xperiments.m9_cat_ept.composite_candidate_states import (
    CandidateStateConfig,
    phase_aligned_distance,
    run_candidate_state_construction,
)


def test_four_candidate_states_close_declared_reduced_gates():
    result = run_candidate_state_construction()
    assert result["passed"]
    assert result["candidate_gates"] == {
        "dark_matter": True,
        "quarks": True,
        "baryons": True,
        "mesons": True,
    }
    assert not result["decision"]["cosmological_or_hadronic_identity_established"]


def test_phase_aligned_distance_is_zero_on_same_state():
    cfg = CandidateStateConfig(relaxation_steps=100, perturbation_steps=20)
    state = np.ones(cfg.points, dtype=np.complex128)
    assert phase_aligned_distance(state, state, cfg) == 0.0
