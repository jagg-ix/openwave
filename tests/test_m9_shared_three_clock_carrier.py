import numpy as np
from openwave.xperiments.m9_cat_ept.shared_three_clock_carrier import SharedThreeClockCarrier, run_shared_three_clock_carrier

def test_shared_carrier_passes_and_closes_reduced_identifications():
    result = run_shared_three_clock_carrier()
    assert result['passed']
    assert all(result['acceptance'].values())
    assert result['decision']['shared_finite_clock_carrier_constructed']
    assert result['decision']['conditioned_generator_modular_identification_reduced']
    assert not result['decision']['full_constraint_to_conditioning_theorem_complete']

def test_shared_carrier_semigroup_and_conditioning():
    carrier = SharedThreeClockCarrier()
    times, history = carrier.history_state()
    assert abs(np.trace(history).real - 1.0) < 1e-13
    for index in (0, 5, 17):
        assert np.linalg.norm(carrier.condition_history(history, index) - carrier.state(float(times[index]))) < 1e-13
    assert np.linalg.norm(carrier.evolve(carrier.state(1.2), 0.7) - carrier.state(1.9)) < 1e-13
