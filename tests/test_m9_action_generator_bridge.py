import pytest
from openwave.xperiments.m9_cat_ept.formal_action_generator_bridge import ActionConfig,derivative_control,flow_control,evidence_fingerprint,run_action_generator_study

def test_invalid_grid_rejected():
 with pytest.raises(ValueError): ActionConfig(points=31)
def test_action_derivative_closes(): assert derivative_control()['absolute_error']<=2e-8
def test_flow_split():
 r=flow_control(); assert r['dissipative_action_rate']<0 and abs(r['hamiltonian_action_rate'])<=1e-12
def test_full_study():
 r=run_action_generator_study(); assert r['passed'] and all(r['acceptance'].values()) and len(evidence_fingerprint())==64
