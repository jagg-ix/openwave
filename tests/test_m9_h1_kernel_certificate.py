import numpy as np

from openwave.xperiments.m9_cat_ept.h1_kernel_certificate import (
    density_slack,
    run_h1_kernel_certificate,
)


def test_density_factorization_specialization_closes():
    density = np.linspace(0.0, 1.0, 257)
    lhs, rhs = density_slack(3.0, 5.0, density)
    assert float(np.max(np.abs(lhs - rhs))) < 1e-13
    assert float(np.min(lhs)) >= -1e-13


def test_h1_kernel_certificate_keeps_analytic_scope_explicit():
    result = run_h1_kernel_certificate()
    assert result["passed"] and all(result["acceptance"].values())
    decision = result["decision"]
    assert decision["density_coercivity_kernel_proved"]
    assert decision["conditional_h1_orbital_stability_kernel_proved"]
    assert not decision["spatial_cubic_quintic_h1_flow_constructed_in_kernel"]
    assert not decision["m9_70_end_to_end_analytic_target_closed"]
