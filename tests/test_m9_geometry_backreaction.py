import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.geometry_backreaction import GeometryConfig, constraint_residual, density_contrast, metric_observables, periodic_density, proper_time, relax_metric, resolution_study, run_geometry_backreaction_study, source_to_metric

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): GeometryConfig(points=127)

def test_density_contrast_has_zero_mean():
    cfg=GeometryConfig(); assert abs(np.mean(density_contrast(periodic_density(cfg))))<1e-15

def test_constraint_solution_closes():
    cfg=GeometryConfig(); source=density_contrast(periodic_density(cfg)); h=source_to_metric(source,cfg)
    assert np.linalg.norm(constraint_residual(h,source,cfg))/np.sqrt(cfg.points)<2e-13

def test_zero_coupling_is_flat():
    cfg=GeometryConfig(coupling=0); source=density_contrast(periodic_density(cfg))
    assert np.max(np.abs(source_to_metric(source,cfg)))<1e-15

def test_relaxation_lowers_functional():
    cfg=GeometryConfig(); run=relax_metric(density_contrast(periodic_density(cfg)),cfg)
    values=np.asarray([row["functional"] for row in run["records"]])
    assert np.all(np.diff(values)<=2e-13)

def test_proper_time_probe_positive():
    cfg=GeometryConfig(); source=density_contrast(periodic_density(cfg)); h=source_to_metric(source,cfg)
    lapse=metric_observables(h,cfg)["lapse"]
    assert proper_time(lapse,10,cfg.points//2)>0

def test_resolution_stabilizes():
    r=resolution_study()
    assert max(r["successive_differences"])<=2e-13 or r["successive_differences"][-1]<r["successive_differences"][0]

def test_full_study_passes():
    r=run_geometry_backreaction_study()
    assert r["passed"] and all(r["acceptance"].values())
