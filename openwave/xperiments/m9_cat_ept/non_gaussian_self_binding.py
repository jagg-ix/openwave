"""Non-Gaussian and topological 3D self-binding search.

Reuses the merged M9.49 untrapped unified finite-grid equations with Gaussian,
exponential, super-Gaussian, hollow-shell and unit-winding toroidal profiles.
A negative result is restricted to these finite-grid families.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
import json,math
from typing import Any
import numpy as np
from .unified_self_binding_3d import Unified3DConfig,Unified3DState,lattice,normalize,observables,step

@dataclass(frozen=True)
class ProfileCampaignConfig:
    points:int=10; half_width:float=5.; final_time:float=3.; dt:float=.02
    sample_stride:int=10; seed:int=20260724
    def __post_init__(self):
        if self.points<10 or self.points%2: raise ValueError("even cubic grid >=10 required")
        if self.half_width<=0 or self.final_time<=0 or self.dt<=0: raise ValueError("positive campaign controls required")

def unified_config(campaign,geometry_coupling):
    return Unified3DConfig(points=campaign.points,half_width=campaign.half_width,final_time=campaign.final_time,dt=campaign.dt,geometry_coupling=geometry_coupling,sample_stride=campaign.sample_stride)

def color_vector():
    return np.asarray([math.sqrt(.50),math.sqrt(.32),math.sqrt(.18)],dtype=np.complex128)*np.exp(1j*np.asarray([0.,.31,-.27]))

def envelope(name,cfg):
    x,y,z,_=lattice(cfg); r=np.sqrt(x*x+y*y+z*z)
    if name=="gaussian": return np.exp(-r*r/(2*1.05**2))
    if name=="exponential": return np.exp(-r/.82)
    if name=="super_gaussian": return np.exp(-.5*(r/1.18)**4)
    if name=="shell": return np.exp(-.5*((r-1.55)/.48)**2)
    if name=="vortex_torus":
        cylindrical=np.sqrt(x*x+y*y)
        return np.exp(-.5*(((cylindrical-1.45)/.45)**2+(z/.55)**2))
    raise ValueError(name)

def profile_state(name,cfg):
    x,y,z,_=lattice(cfg); env=envelope(name,cfg)
    phase=np.exp(1j*np.arctan2(y,x)) if name=="vortex_torus" else np.exp(.12j*x)
    psi=normalize(color_vector()[:,None,None,None]*env[None,...]*phase[None,...],cfg)
    temperature=1+.015*np.cos(math.pi*x/cfg.half_width); zero=np.zeros_like(x)
    return Unified3DState(psi,temperature,zero.copy(),zero.copy())

def square_loop_winding(psi,cfg,component=0):
    center=cfg.points//2; radius=max(2,cfg.points//4); indices=[]
    for i in range(center-radius,center+radius): indices.append((i,center-radius,center))
    for j in range(center-radius,center+radius): indices.append((center+radius,j,center))
    for i in range(center+radius,center-radius,-1): indices.append((i,center+radius,center))
    for j in range(center+radius,center-radius,-1): indices.append((center-radius,j,center))
    values=np.asarray([psi[component,i%cfg.points,j%cfg.points,k] for i,j,k in indices])
    return float(np.sum(np.angle(np.roll(values,-1)*np.conjugate(values)))/(2*math.pi))

def evolve_profile(name,geometry_coupling,campaign=ProfileCampaignConfig()):
    cfg=unified_config(campaign,geometry_coupling); state=profile_state(name,cfg); initial_winding=square_loop_winding(state.psi,cfg)
    steps=math.ceil(cfg.final_time/cfg.dt); dt=cfg.final_time/steps; records=[observables(state,cfg)]
    for index in range(steps):
        state=step(state,dt,cfg)
        if (index+1)%cfg.sample_stride==0 or index+1==steps: records.append(observables(state,cfg))
    first,final=records[0],records[-1]; maximum_boundary=max(row["boundary_fraction"] for row in records); maximum_balance=max(abs(row["balance"]-first["balance"]) for row in records)
    final_winding=square_loop_winding(state.psi,cfg); retained=final["radius"]/first["radius"]<1.35 and maximum_boundary<.02
    return {"profile":name,"geometry_coupling":geometry_coupling,"initial_radius":first["radius"],"final_radius":final["radius"],"radius_ratio":final["radius"]/first["radius"],"maximum_boundary_fraction":maximum_boundary,"maximum_balance_error":maximum_balance,"final_entropy":final["entropy"],"initial_winding":initial_winding,"final_winding":final_winding,"retained_localization":bool(retained)}

def profile_campaign(campaign=ProfileCampaignConfig()):
    profiles=("gaussian","exponential","super_gaussian","shell","vortex_torus"); couplings=(.6,.9,1.2)
    rows=[evolve_profile(profile,coupling,campaign) for profile in profiles for coupling in couplings]
    return {"profiles":profiles,"couplings":couplings,"rows":rows,"candidate_count":sum(row["retained_localization"] for row in rows)}

def domain_control():
    configs=(ProfileCampaignConfig(points=10,half_width=5.,final_time=2.,dt=.02),ProfileCampaignConfig(points=12,half_width=6.,final_time=2.,dt=.02))
    rows=[evolve_profile("vortex_torus",1.2,campaign) for campaign in configs]
    return {"rows":rows,"larger_domain_has_larger_final_radius":rows[1]["final_radius"]>rows[0]["final_radius"]+.15}

def topology_control():
    row=evolve_profile("vortex_torus",.9,ProfileCampaignConfig(final_time=.4,dt=.01,sample_stride=5))
    return {**row,"initial_winding_is_unit":abs(row["initial_winding"]-1)<=.15,"short_time_winding_is_retained":abs(row["final_winding"]-1)<=.25}

@lru_cache(maxsize=1)
def run_profile_self_binding_search():
    campaign=profile_campaign(); domain=domain_control(); topology=topology_control(); rows=campaign["rows"]
    acceptance={"five_profile_families_are_scanned":len(campaign["profiles"])==5,"three_geometry_couplings_are_scanned":len(campaign["couplings"])==3,"all_runs_close_matter_reservoir_balance":max(row["maximum_balance_error"] for row in rows)<=4e-4,"all_runs_activate_entropy":min(row["final_entropy"] for row in rows)>0,"no_profile_selects_self_binding":campaign["candidate_count"]==0,"every_profile_spreads_or_reaches_boundary":all(row["radius_ratio"]>=1.35 or row["maximum_boundary_fraction"]>=.02 for row in rows),"vortex_winding_is_resolved_short_time":topology["initial_winding_is_unit"] and topology["short_time_winding_is_retained"],"vortex_radius_tracks_larger_domain":domain["larger_domain_has_larger_final_radius"]}
    return {"schema":"openwave.m9.non-gaussian-self-binding-result.v1","task":"M9.52","config":asdict(ProfileCampaignConfig()),"campaign":campaign,"domain_control":domain,"topology_control":topology,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"self_bound_candidate_selected":False,"profile_family_no_go":True,"universal_cat_ept_no_go":False},"classification":{"establishes":["five-family non-Gaussian three-dimensional search","shell and unit-winding toroidal controls","bounded geometry-coupling scan","matter/reservoir and entropy diagnostics","profile-family negative self-binding result"],"does_not_establish":["a universal no-go theorem","all topological sectors or nonlinear actions","continuum compactness or orbital stability","physical particle nonexistence"]}}

def result_to_json(result):return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
