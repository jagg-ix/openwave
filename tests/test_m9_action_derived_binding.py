import pytest
from openwave.xperiments.m9_cat_ept.action_derived_binding import BindingCampaignConfig,derivative_control,parameter_scan,resolution_campaign,run_binding_discrimination

def test_invalid_grid_rejected():
 with pytest.raises(ValueError): BindingCampaignConfig(points=(11,14,16))
def test_binding_derivative_closes(): assert derivative_control()['absolute_error']<=2e-7
def test_candidate_beats_baseline():
 rows=parameter_scan(); assert rows[-1]['radius_ratio']<.4*rows[0]['radius_ratio']
def test_resolution_campaign_retains_localization(): assert all(x['retained_localization'] for x in resolution_campaign())
def test_full_study():
 r=run_binding_discrimination(); assert r['passed'] and all(r['acceptance'].values()) and not r['decision']['stable_physical_particle_established']
