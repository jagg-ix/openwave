import json
from dataclasses import replace
from pathlib import Path
import numpy as np
from openwave.xperiments.m9_cat_ept.independent_breathing_comparison import IndependentComparisonConfig,comparison_fingerprint,fit_dominant_frequency,relax_stationary_state

def test_frequency_fit_recovers_synthetic_mode():
 cfg=replace(IndependentComparisonConfig(),fit_start=1.,fit_end=9.,omega_min=1.,omega_max=3.,omega_samples=1200);times=np.linspace(0,10,2001);values=1.2+.01*times+.05*np.cos(2.15*times+.4);r=fit_dominant_frequency(times,values,cfg);assert abs(r['omega_dimensionless']-2.15)<.01

def test_small_relaxation_is_nonincreasing():
 cfg=replace(IndependentComparisonConfig(),grids=(12,),relaxation_steps=600,relaxation_check_stride=100,relaxation_energy_tolerance=0.,final_time=2.,fit_start=.2,fit_end=1.8);assert relax_stationary_state(12,cfg)['energy_nonincreasing']

def test_fingerprint_is_deterministic():assert comparison_fingerprint()==comparison_fingerprint()

def test_stored_comparison_falsifies_frozen_prediction():
 path=Path(__file__).parents[1]/'openwave/xperiments/m9_cat_ept/research/data/m9_68_independent_breathing_comparison_result.json';r=json.loads(path.read_text());assert r['passed'] and r['decision']['prediction_falsified_by_higher_fidelity_openwave_test'] and r['summary']['minimum_relative_error']>.40
