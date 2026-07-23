import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.topological_charge import (
    VortexGrid,
    additivity_study,
    contour_study,
    perturbation_study,
    run_topological_charge_study,
    sector_resolution_study,
    vortex_field,
    winding_number,
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError):
        VortexGrid(points=128)

def test_integer_sectors_recovered():
    assert sector_resolution_study()["maximum_quantization_error"]<=2e-12

def test_global_phase_invariance():
    g=VortexGrid(); f=vortex_field(g,((0,0,1),))
    a=winding_number(g,f)["raw_winding"]
    b=winding_number(g,f*np.exp(1.234j))["raw_winding"]
    assert abs(a-b)<=2e-12

def test_contour_independence():
    assert len(set(contour_study()["integer_windings"]))==1

def test_smooth_perturbation_preserves_sector():
    assert perturbation_study()["integer_preserved"]

def test_multi_vortex_additivity():
    assert additivity_study()["integer_additivity_error"]==0

def test_zero_on_contour_is_rejected():
    g=VortexGrid(contour_radius=4.0)
    with pytest.raises(ValueError):
        winding_number(g,np.zeros((g.points,g.points),dtype=np.complex128))

def test_full_study_passes_without_electric_charge_promotion():
    r=run_topological_charge_study()
    assert r["passed"] and r["field_derived_integer_charge"]
    assert r["identified_with_electric_charge"] is False
    assert r["spontaneous_sector_selection"] is False
