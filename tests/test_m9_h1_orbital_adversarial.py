from dataclasses import replace
from openwave.xperiments.m9_cat_ept.h1_orbital_adversarial import H1AdversarialConfig,evolve_case,formal_gap_ledger,run_h1_adversarial_campaign

def test_formal_gap_is_explicit():
 rows=formal_gap_ledger();assert any(x['status']=='not closed end-to-end' for x in rows) and any('orbital stability' in x['interface'] for x in rows)

def test_small_adversarial_run_preserves_ledgers():
 cfg=replace(H1AdversarialConfig(),grids=(16,),cases=('anisotropic',),final_time=.05,sample_stride=25);row=evolve_case('anisotropic',16,cfg);assert row['maximum_mass_error']<1e-10 and row['maximum_energy_drift']<3e-6 and row['gradient_bound_respected']

def test_full_adversarial_campaign_passes():
 r=run_h1_adversarial_campaign();assert r['passed'] and not r['decision']['spatial_cubic_quintic_h1_kernel_theorem_proved']
