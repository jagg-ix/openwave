
import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.wave_reductions import (
    WaveConfig, gaussian_pulse, kg_evolve, maxwell_evolve,
    maxwell_massless_kg_bridge, resolution_study,
    run_wave_reduction_study, single_mode_dispersion, translation_speed
)

def test_invalid_grid_rejected():
    with pytest.raises(ValueError): WaveConfig(points=63)

def test_maxwell_energy_conserved():
    cfg=WaveConfig(); pulse=gaussian_pulse(cfg)
    r=maxwell_evolve(pulse,pulse/cfg.wave_speed,cfg)
    e=np.asarray([x["energy"] for x in r["records"]])
    assert np.max(np.abs(e-e[0]))<=2e-13

def test_kg_energy_conserved():
    cfg=WaveConfig(); pulse=gaussian_pulse(cfg)
    r=kg_evolve(pulse,np.zeros_like(pulse),cfg)
    e=np.asarray([x["energy"] for x in r["records"]])
    assert np.max(np.abs(e-e[0]))<=2e-12

def test_massless_bridge():
    assert maxwell_massless_kg_bridge()["maximum_field_error"]<=3e-13

def test_translation_speed():
    assert translation_speed()["maximum_translation_error"]<=2e-13

def test_dispersion_relation():
    assert single_mode_dispersion()["relative_error"]<=2e-3

def test_resolution_bridge_stable():
    assert resolution_study()["maximum_error"]<=4e-13

def test_full_study_passes():
    r=run_wave_reduction_study()
    assert r["passed"] and all(r["acceptance"].values())
