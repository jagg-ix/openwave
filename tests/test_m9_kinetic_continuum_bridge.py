import numpy as np,pytest
from openwave.xperiments.m9_cat_ept.kinetic_continuum_bridge import KineticConfig,convergence_campaign,hoermander_control,run_kinetic_continuum_study

def test_invalid_levels_rejected():
 with pytest.raises(ValueError): KineticConfig(levels=((16,25,.05),(12,33,.04),(32,41,.03),(48,57,.02)))
def test_hoermander_rank(): assert hoermander_control()['rank']==2
def test_nested_errors_decrease(): assert np.all(np.diff(convergence_campaign()['aggregate_errors_to_finest'])<0)
def test_full_study():
 r=run_kinetic_continuum_study(); assert r['passed'] and all(r['acceptance'].values()) and not r['decision']['continuum_hypoelliptic_wellposedness_proved']
