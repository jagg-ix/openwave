import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.lepton_hierarchy_audit import (
    SpectrumBenchmark, fit_log_geometric, fit_log_quadratic,
    leave_one_out_geometric, m927_effective_parameters,
    perturbation_audit, run_lepton_hierarchy_audit
)

def test_benchmark_normalizes():
    assert np.allclose(SpectrumBenchmark().normalized()[0],1)

def test_geometric_fit_is_inadequate():
    assert fit_log_geometric(SpectrumBenchmark())["maximum_multiplicative_error"]>=2

def test_leave_one_out_is_poor():
    assert leave_one_out_geometric(SpectrumBenchmark())["maximum_factor"]>=10

def test_quadratic_exactly_interpolates():
    r=fit_log_quadratic(SpectrumBenchmark())
    assert r["maximum_relative_error"]<=2e-14 and r["residual_dof"]==0

def test_quadratic_turns_over():
    r=fit_log_quadratic(SpectrumBenchmark())
    assert r["turnover_generation"]<3 and not r["monotone_beyond_observed"]

def test_m927_requires_per_generation_knobs():
    r=m927_effective_parameters(SpectrumBenchmark())
    assert r["independent_parameter_count"]==3
    assert r["shared_geometric_q"]["maximum_multiplicative_error"]>=1.5

def test_perturbation_is_amplified():
    r=perturbation_audit(SpectrumBenchmark())
    assert r["relative_prediction_span"]>=5*r["relative_input_perturbation"]

def test_full_audit_passes_as_negative():
    r=run_lepton_hierarchy_audit()
    assert r["passed"] and all(r["acceptance"].values())
    assert not r["decision"]["predictive_lepton_hierarchy_selected"]
