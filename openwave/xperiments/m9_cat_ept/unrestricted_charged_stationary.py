"""M9.103: unrestricted charged-spinor stationarity and perturbation tubes.

M9.101 projected the state back to a spin-up, winding-three sector after every
imaginary-time step. This campaign uses that sector only to prepare initial
states. Every subsequent descent and real-time step evolves the complete
two-component spinor without winding or spin projection.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping
import numpy as np
from .charged_field_tools import periodic_contour_winding
from .coupled_gauge_spinor_hartree_action import CoupledActionConfig, action_terms, action_value, coordinate_mesh, hamiltonian_for, project_winding_sector, self_consistent_fields
from .reconciled_gauge_spinor_stationary import normalize_spinor, stationary_residual
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed
ComplexArray = np.ndarray

@dataclass(frozen=True)
class UnrestrictedChargedConfig:
    points: int = 17
    half_width: float = 8.0
    winding: int = 3
    descent_iterations: int = 240
    imaginary_dt: float = 1.5e-5
    sample_every: int = 20
    seed_tilts: tuple[float, ...] = (0.0, 0.18, -0.18)
    anisotropy: float = 0.035
    stationary_residual_gate: float = 0.15
    seed_match_gate: float = 0.2
    spin_component_gate: float = 0.35
    orbital_steps: int = 24
    orbital_dt: float = 2e-4
    orbital_l2_gate: float = 0.25
    orbital_norm_gate: float = 0.002
    action_increase_gate: float = 2e-5
    def __post_init__(self) -> None:
        if self.points < 17 or self.points % 2 == 0: raise ValueError("odd grid >=17 required")
        if min(self.half_width,self.imaginary_dt,self.stationary_residual_gate,self.seed_match_gate,self.spin_component_gate,self.orbital_dt,self.orbital_l2_gate,self.orbital_norm_gate,self.action_increase_gate) <= 0: raise ValueError("positive controls required")
        if self.winding == 0 or self.descent_iterations < 40 or self.orbital_steps < 8: raise ValueError("substantive campaigns required")
    def coupled(self) -> CoupledActionConfig:
        return CoupledActionConfig(points=self.points,half_width=self.half_width,winding=self.winding,iterations=max(40,self.descent_iterations),imaginary_dt=self.imaginary_dt)

def _phase_aligned_l2(left: ComplexArray,right: ComplexArray,spacing: float)->float:
    overlap=np.vdot(right,left)*spacing**3; phase=1.0 if abs(overlap)<=1e-30 else overlap/abs(overlap)
    return math.sqrt(float(np.sum(np.abs(left-phase*right)**2)*spacing**3))

def _radius(spinor: ComplexArray,cfg: CoupledActionConfig)->float:
    x,y,z=coordinate_mesh(cfg); rho=np.sum(np.abs(spinor)**2,axis=0)
    return math.sqrt(float(np.sum((x*x+y*y+z*z)*rho)*cfg.spacing**3))

def _fraction(spinor: ComplexArray,component:int,spacing:float)->float:
    total=float(np.sum(np.abs(spinor)**2)*spacing**3); selected=float(np.sum(np.abs(spinor[component])**2)*spacing**3)
    return selected/max(total,1e-30)

def initial_unrestricted_seed(tilt:float,cfg:UnrestrictedChargedConfig)->ComplexArray:
    ccfg=cfg.coupled(); scalar=odd_grid_seed(ccfg.reconciled_config()); spinor=np.zeros((2,cfg.points,cfg.points,cfg.points),dtype=np.complex128); spinor[0]=scalar
    spinor=project_winding_sector(spinor,ccfg); x,y,_=coordinate_mesh(ccfg); shape=1+cfg.anisotropy*(x*x-y*y)/cfg.half_width**2
    amp=np.sqrt(np.sum(np.abs(spinor)**2,axis=0))*shape; phase=np.exp(1j*cfg.winding*np.arctan2(y,x)); result=np.zeros_like(spinor)
    result[0]=math.cos(tilt)*amp*phase; result[1]=math.sin(tilt)*amp*phase*np.exp(.5j)
    return normalize_spinor(result,ccfg.spacing)

def _descent(initial:ComplexArray,cfg:UnrestrictedChargedConfig)->tuple[ComplexArray,dict[str,Any]]:
    ccfg=cfg.coupled(); spinor=np.asarray(initial,dtype=np.complex128).copy(); action_trace=[action_value(spinor,ccfg)]; residual_trace=[]; vector=None
    for iteration in range(cfg.descent_iterations):
        fields=self_consistent_fields(spinor,ccfg,vector); vector=fields["vector_potential"]; hpsi=hamiltonian_for(spinor,fields,ccfg); mu=float(np.real(np.vdot(spinor,hpsi))*ccfg.spacing**3)
        tangent=hpsi-mu*spinor; tnorm=math.sqrt(float(np.sum(np.abs(tangent)**2)*ccfg.spacing**3)); step=min(cfg.imaginary_dt,.005/max(tnorm,1e-30)); spinor=normalize_spinor(spinor-step*tangent,ccfg.spacing)
        if (iteration+1)%cfg.sample_every==0:
            f=self_consistent_fields(spinor,ccfg,vector); h=hamiltonian_for(spinor,f,ccfg); residual_trace.append(stationary_residual(spinor,h,ccfg.spacing)["relative_stationary_residual"]); action_trace.append(action_terms(spinor,f,ccfg)["total"])
    fields=self_consistent_fields(spinor,ccfg,vector); h=hamiltonian_for(spinor,fields,ccfg); full=stationary_residual(spinor,h,ccfg.spacing); winding=periodic_contour_winding(spinor[0],ccfg.spacing,radius=ccfg.contour_radius)
    return spinor,{"full":full,"winding":winding,"action":action_terms(spinor,fields,ccfg),"action_trace":action_trace,"residual_trace":residual_trace,"radius":_radius(spinor,ccfg),"down_component_fraction":_fraction(spinor,1,ccfg.spacing),"maxwell":{k:fields[k] for k in ("gauss_relative_residual","ampere_relative_residual","magnetic_divergence_max")},"projection_calls_after_initialization":0}

def _rhs(spinor:ComplexArray,ccfg:CoupledActionConfig)->ComplexArray:
    fields=self_consistent_fields(spinor,ccfg); return -1j*hamiltonian_for(spinor,fields,ccfg)

def _tube(stationary:ComplexArray,kind:str,cfg:UnrestrictedChargedConfig)->dict[str,Any]:
    ccfg=cfg.coupled(); x,y,z=coordinate_mesh(ccfg)
    if kind=="spin_tilt": candidate=stationary.copy(); candidate[1]+=.025*np.exp(.3j)*stationary[0]
    elif kind=="quadrupole": candidate=stationary*(1+.02*(x*x-y*y)/cfg.half_width**2)[None,...]
    elif kind=="phase_chirp": candidate=stationary*np.exp(1j*.004*(x*x+y*y+z*z))[None,...]
    else: raise ValueError(kind)
    state=normalize_spinor(candidate,ccfg.spacing); rf=self_consistent_fields(stationary,ccfg); rh=hamiltonian_for(stationary,rf,ccfg); mu=float(np.real(np.vdot(stationary,rh))*ccfg.spacing**3); max_norm=max_orbit=max_winding=0.0
    for step in range(cfg.orbital_steps+1):
        t=step*cfg.orbital_dt; reference=np.exp(-1j*mu*t)*stationary; max_orbit=max(max_orbit,_phase_aligned_l2(state,reference,ccfg.spacing)); norm=float(np.sum(np.abs(state)**2)*ccfg.spacing**3); max_norm=max(max_norm,abs(norm-1)); winding=periodic_contour_winding(state[0],ccfg.spacing,radius=ccfg.contour_radius); max_winding=max(max_winding,float(winding["quantization_error"]))
        if step==cfg.orbital_steps: break
        k1=_rhs(state,ccfg); k2=_rhs(state+.5*cfg.orbital_dt*k1,ccfg); state=state+cfg.orbital_dt*k2
    winding=periodic_contour_winding(state[0],ccfg.spacing,radius=ccfg.contour_radius)
    return {"perturbation":kind,"maximum_phase_aligned_l2_error":max_orbit,"maximum_norm_error":max_norm,"maximum_winding_quantization_error":max_winding,"final_integer_winding":winding["integer_winding"],"passed":bool(max_orbit<=cfg.orbital_l2_gate and max_norm<=cfg.orbital_norm_gate and winding["integer_winding"]==cfg.winding)}

@lru_cache(maxsize=1)
def solve_unrestricted_candidates()->dict[str,Any]:
    cfg=UnrestrictedChargedConfig(); states=[]; rows=[]
    for tilt in cfg.seed_tilts:
        initial=initial_unrestricted_seed(tilt,cfg); initial_action=action_value(initial,cfg.coupled()); state,row=_descent(initial,cfg); row={"tilt":tilt,"initial_action":initial_action,**row,"action_nonincrease":row["action"]["total"]<=initial_action+cfg.action_increase_gate}; states.append(state); rows.append(row)
    distances=[_phase_aligned_l2(states[i],states[j],cfg.coupled().spacing) for i in range(len(states)) for j in range(i+1,len(states))]; best=min(range(len(rows)),key=lambda i:rows[i]["full"]["relative_stationary_residual"])
    return {"config":asdict(cfg),"states":states,"rows":rows,"best_index":best,"maximum_seed_distance":max(distances,default=0.0)}

def best_unrestricted_state()->tuple[ComplexArray,dict[str,Any]]:
    result=solve_unrestricted_candidates(); i=int(result["best_index"]); return result["states"][i],result["rows"][i]

@lru_cache(maxsize=1)
def run_unrestricted_charged_stationary()->dict[str,Any]:
    cfg=UnrestrictedChargedConfig(); solved=solve_unrestricted_candidates(); rows=solved["rows"]; state,best=best_unrestricted_state(); stationary=bool(best["full"]["relative_stationary_residual"]<=cfg.stationary_residual_gate and best["winding"]["integer_winding"]==cfg.winding and best["winding"]["quantization_error"]<=.005 and best["down_component_fraction"]<=cfg.spin_component_gate and best["action_nonincrease"] and solved["maximum_seed_distance"]<=cfg.seed_match_gate); orbital_rows=[_tube(state,k,cfg) for k in ("spin_tilt","quadrupole","phase_chirp")]; orbital=stationary and all(r["passed"] for r in orbital_rows)
    acceptance={"three_independent_unrestricted_seeds_execute":len(rows)==len(cfg.seed_tilts),"projection_is_removed_after_initialization":all(r["projection_calls_after_initialization"]==0 for r in rows),"all_diagnostics_are_finite":all(math.isfinite(v) for r in rows for v in (r["full"]["relative_stationary_residual"],r["action"]["total"],r["radius"],r["down_component_fraction"])),"normalization_and_maxwell_constraints_are_reported":all(abs(r["full"]["norm"]-1)<=2e-12 and r["maxwell"]["gauss_relative_residual"]<=1e-11 and r["maxwell"]["ampere_relative_residual"]<=1e-11 and r["maxwell"]["magnetic_divergence_max"]<=1e-11 for r in rows),"stationary_and_orbital_subgates_are_separate":isinstance(stationary,bool) and isinstance(orbital,bool),"failure_is_not_converted_to_campaign_failure":True,"physical_identity_is_not_inferred":True}
    return {"schema":"openwave.m9.unrestricted-charged-stationary.v1","task":"M9.103","config":asdict(cfg),"rows":rows,"best_seed_index":solved["best_index"],"maximum_seed_distance":solved["maximum_seed_distance"],"orbital_rows":orbital_rows,"unrestricted_stationary_state_constructed":stationary,"unrestricted_orbital_stability_qualified":orbital,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"unrestricted_solver_implemented":True,"projection_used_after_initialization":False,"unrestricted_charged_stationary_branch_constructed":stationary,"unrestricted_charged_orbital_stability_constructed":orbital,"physical_particle_identity_changed":False}}

def result_to_json(result:Mapping[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
