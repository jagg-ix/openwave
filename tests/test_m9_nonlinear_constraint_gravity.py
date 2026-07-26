import numpy as np

from openwave.xperiments.m9_cat_ept.nonlinear_constraint_gravity import (
    NonlinearMetricConfig,
    constraint_fields,
    project_constraints,
)


def test_zero_metric_and_zero_source_close_constraints():
    cfg = NonlinearMetricConfig(steps=20)
    shape = (cfg.points,) * 3
    u = np.zeros(shape)
    trace_k = np.zeros(shape)
    matter = {"total_gravitational_source": np.zeros(shape)}
    current = tuple(np.zeros(shape) for _ in range(3))
    result = constraint_fields(u, trace_k, matter, current, cfg)
    assert result["hamiltonian_relative"] == 0.0
    assert result["momentum_relative"] == 0.0
    projected_u, projected_k = project_constraints(u, trace_k, result, cfg)
    assert np.allclose(projected_u, 0.0)
    assert np.allclose(projected_k, 0.0)


def test_metric_config_rejects_even_operational_grid():
    try:
        NonlinearMetricConfig(points=16)
    except ValueError:
        return
    raise AssertionError("even metric grid was accepted")
