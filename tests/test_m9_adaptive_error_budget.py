import math
import pytest
from openwave.xperiments.m9_cat_ept.adaptive_error_budget import BudgetConfig, adaptive_plan, coupling_reference, heun_decay, run_adaptive_error_budget_study, trapezoid_sine

def test_invalid_allocations_rejected():
    with pytest.raises(ValueError): BudgetConfig(temporal_fraction=.4,spatial_fraction=.2,domain_fraction=.2,coupling_fraction=.1)

def test_heun_converges(): assert abs(heun_decay(64)-math.exp(-1))<abs(heun_decay(32)-math.exp(-1))
def test_trapezoid_converges(): assert abs(trapezoid_sine(128)-2)<abs(trapezoid_sine(64)-2)
def test_coupling_reference_is_fixed_point():
    x=coupling_reference(); assert abs(x-(.2+.5*math.cos(x)))<1e-14

def test_every_component_meets_budget():
    p=adaptive_plan(); assert all(c["estimated_error"]<=c["allocated_tolerance"] for c in p["components_full"].values())
def test_propagated_bound_contains_actual_error():
    p=adaptive_plan(); assert p["actual_benchmark_error"]<=p["propagated_bound"]
def test_plan_is_deterministic(): assert adaptive_plan()["fingerprint"]==adaptive_plan()["fingerprint"]
def test_full_study_passes():
    r=run_adaptive_error_budget_study(); assert r["passed"] and all(r["acceptance"].values())
