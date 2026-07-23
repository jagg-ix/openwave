import numpy as np, pytest
from openwave.xperiments.m9_cat_ept.entropic_integrator import (
    LinearEntropicKernel, SplitConfig, evolve, initial_state, reference_kernel,
    refinement, run_entropic_integrator_study,
)

def test_config_rejects_unknown_method():
    with pytest.raises(ValueError): SplitConfig(method="bad")

def test_kernel_rejects_negative_loss():
    h=np.eye(2,dtype=complex); g=np.diag([0.1,-0.1]).astype(complex)
    with pytest.raises(ValueError): LinearEntropicKernel(h,g)

def test_strang_is_second_order():
    assert min(refinement()["orders"]) >= 1.8

def test_balance_closes():
    result=run_entropic_integrator_study(); assert result["maximum_balance_error"] <= 2e-12

def test_entropic_clock_is_monotone():
    result=run_entropic_integrator_study(); assert result["acceptance"]["entropic_clock_monotone"]

def test_zero_loss_is_unitary():
    assert run_entropic_integrator_study()["zero_loss_norm_drift"] <= 2e-12

def test_lie_and_strang_are_distinct():
    k=reference_kernel(); x=initial_state()
    a=evolve(k,x,SplitConfig(dt=.2,method="lie")); b=evolve(k,x,SplitConfig(dt=.2,method="strang"))
    assert np.linalg.norm(a.state-b.state)>1e-6

def test_full_study_passes():
    r=run_entropic_integrator_study(); assert r["passed"] and all(r["acceptance"].values())
