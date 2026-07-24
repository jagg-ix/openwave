"""Long-horizon three-dimensional perturbation and stability campaign.

Reuses the M9.37 trapped Gross--Pitaevskii minimizer and evolves the normalized
field with a symmetric split-step Fourier integrator. Deterministic phase-noise,
compression, displacement and combined perturbations are compared against a
trap-free self-binding control. PhysLib/ZIL weak-limit APIs provide provenance;
no continuum stability theorem is claimed.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray
from .minimizer_3d import MinimizerConfig, energy, lattice, minimize, normalize, observables

ComplexField=NDArray[np.complex128]

@dataclass(frozen=True)
class StabilityConfig:
    points:int=16; half_width:float=6.; coupling:float=1.; trap_frequency:float=1.
    final_time:float=24.; dt:float=.01; sample_stride:int=40; seed:int=20260723
    def __post_init__(self)->None:
        if self.points<12 or self.points%2: raise ValueError("even cubic grid with at least 12 points required")
        if self.half_width<=0 or self.final_time<=0 or self.dt<=0: raise ValueError("positive spatial and evolution controls required")
        if self.coupling<0 or self.trap_frequency<0: raise ValueError("nonnegative coupling and trap required")
        if self.sample_stride<1: raise ValueError("positive sample stride required")

def minimizer_config(cfg:StabilityConfig)->MinimizerConfig:
    return MinimizerConfig(points=cfg.points,half_width=cfg.half_width,trap_frequency=cfg.trap_frequency,coupling=cfg.coupling,max_iterations=1400,gradient_tolerance=4e-7,initial_step=.08)

def ground_state(cfg:StabilityConfig)->ComplexField:return minimize(minimizer_config(cfg))["field"]

def k_squared(cfg:StabilityConfig)->NDArray[np.float64]:
    _,_,_,dx=lattice(minimizer_config(cfg)); wave=2*math.pi*np.fft.fftfreq(cfg.points,d=dx); kx,ky,kz=np.meshgrid(wave,wave,wave,indexing="ij"); return kx*kx+ky*ky+kz*kz

def potential(cfg:StabilityConfig)->NDArray[np.float64]:
    x,y,z,_=lattice(minimizer_config(cfg)); return .5*cfg.trap_frequency**2*(x*x+y*y+z*z)

def split_step(field:ComplexField,dt:float,cfg:StabilityConfig)->ComplexField:
    external=potential(cfg); phase=np.exp(-.5j*dt*(external+cfg.coupling*np.abs(field)**2)); field=phase*field; fh=np.fft.fftn(field); fh*=np.exp(-.5j*dt*k_squared(cfg)); field=np.fft.ifftn(fh); return np.exp(-.5j*dt*(external+cfg.coupling*np.abs(field)**2))*field

def phase_noise(field:ComplexField,amplitude:float,cfg:StabilityConfig)->ComplexField:
    return field*np.exp(1j*amplitude*np.random.default_rng(cfg.seed).normal(size=field.shape))

def radial_compression(field:ComplexField,amplitude:float,cfg:StabilityConfig)->ComplexField:
    x,y,z,dx=lattice(minimizer_config(cfg)); return normalize(field*np.exp(-amplitude*(x*x+y*y+z*z)),dx)

def displacement(field:ComplexField,cells:int=1)->ComplexField:return np.roll(field,shift=(cells,0,0),axis=(0,1,2))

def scenario_field(ground:ComplexField,name:str,cfg:StabilityConfig)->ComplexField:
    _,_,_,dx=lattice(minimizer_config(cfg))
    if name=="baseline": return ground.copy()
    if name=="phase_noise": return normalize(phase_noise(ground,.10,cfg),dx)
    if name=="compression": return radial_compression(ground,.035,cfg)
    if name=="displacement": return normalize(displacement(ground),dx)
    if name=="combined": return normalize(displacement(radial_compression(phase_noise(ground,.08,cfg),.025,cfg)),dx)
    raise ValueError(name)

def evolve_scenario(initial:ComplexField,cfg:StabilityConfig)->dict[str,Any]:
    mcfg=minimizer_config(cfg); _,_,_,dx=lattice(mcfg); state=normalize(initial.copy(),dx); steps=math.ceil(cfg.final_time/cfg.dt); dt=cfg.final_time/steps; records=[]; e0=energy(state,mcfg)
    for step in range(steps+1):
        if step%cfg.sample_stride==0 or step==steps:
            obs=observables(state,mcfg); records.append({"time":step*dt,**obs,"energy_drift":obs["energy"]-e0})
        if step<steps: state=split_step(state,dt,cfg)
    return {"state":state,"records":records,"dt":dt,"steps":steps}

def summarize_scenario(name:str,run:dict[str,Any],cfg:StabilityConfig)->dict[str,Any]:
    records=run["records"]; norms=np.asarray([x["norm"] for x in records]); radii=np.asarray([x["rms_radius"] for x in records]); boundaries=np.asarray([x["boundary_fraction"] for x in records]); drifts=np.asarray([x["energy_drift"] for x in records]); com=np.asarray([x["center_of_mass_norm"] for x in records])
    return {"name":name,"maximum_norm_error":float(np.max(np.abs(norms-1))),"minimum_rms_radius":float(np.min(radii)),"maximum_rms_radius":float(np.max(radii)),"radius_ratio":float(np.max(radii)/np.min(radii)),"maximum_boundary_fraction":float(np.max(boundaries)),"maximum_energy_drift":float(np.max(np.abs(drifts))),"maximum_center_of_mass_norm":float(np.max(com)),"bounded_in_trap":bool(np.max(radii)<.42*cfg.half_width and np.max(boundaries)<1e-3)}

def trapped_campaign(cfg:StabilityConfig=StabilityConfig())->dict[str,Any]:
    ground=ground_state(cfg); rows=[summarize_scenario(name,evolve_scenario(scenario_field(ground,name,cfg),cfg),cfg) for name in ("baseline","phase_noise","compression","displacement","combined")]; return {"scenarios":rows,"all_bounded":all(x["bounded_in_trap"] for x in rows)}

def untrapped_control(cfg:StabilityConfig=StabilityConfig())->dict[str,Any]:
    ground=ground_state(cfg); free=StabilityConfig(points=cfg.points,half_width=cfg.half_width,coupling=cfg.coupling,trap_frequency=0.,final_time=cfg.final_time,dt=cfg.dt,sample_stride=cfg.sample_stride,seed=cfg.seed); run=evolve_scenario(ground,free); summary=summarize_scenario("untrapped",run,free); summary["final_rms_radius"]=run["records"][-1]["rms_radius"]; summary["final_boundary_fraction"]=run["records"][-1]["boundary_fraction"]; return summary

def timestep_refinement()->dict[str,Any]:
    configs=(StabilityConfig(final_time=8.,dt=.02,sample_stride=20),StabilityConfig(final_time=8.,dt=.01,sample_stride=40),StabilityConfig(final_time=8.,dt=.005,sample_stride=80)); values=[]
    for cfg in configs:
        ground=ground_state(cfg); final=evolve_scenario(scenario_field(ground,"combined",cfg),cfg)["records"][-1]; values.append((final["rms_radius"],final["energy"],final["boundary_fraction"]))
    differences=[float(np.linalg.norm(np.asarray(values[i])-np.asarray(values[i+1]))) for i in range(2)]; return {"dts":[x.dt for x in configs],"values":values,"successive_differences":differences}

def perturbation_continuity()->dict[str,Any]:
    cfg=StabilityConfig(final_time=6.,dt=.01,sample_stride=30); ground=ground_state(cfg); base=evolve_scenario(ground,cfg)["records"][-1]["rms_radius"]; amplitudes=(.02,.04,.08); deviations=[abs(evolve_scenario(phase_noise(ground,a,cfg),cfg)["records"][-1]["rms_radius"]-base) for a in amplitudes]; return {"amplitudes":amplitudes,"radius_deviations":deviations,"ordered":all(deviations[i+1]>=deviations[i]-5e-5 for i in range(2))}

@lru_cache(maxsize=1)
def run_long_horizon_stability_study()->dict[str,Any]:
    cfg=StabilityConfig(); campaign=trapped_campaign(cfg); free=untrapped_control(cfg); refinement=timestep_refinement(); continuity=perturbation_continuity(); rows=campaign["scenarios"]; ne=max(x["maximum_norm_error"] for x in rows); ed=max(x["maximum_energy_drift"] for x in rows); boundary=max(x["maximum_boundary_fraction"] for x in rows); ratio=max(x["radius_ratio"] for x in rows)
    acceptance={"all_trapped_perturbations_remain_bounded":campaign["all_bounded"],"norm_is_preserved":ne<=2e-12,"split_step_energy_drift_is_controlled":ed<=2e-3,"boundary_leakage_remains_small":boundary<=1e-3,"radius_excursions_remain_bounded":ratio<=1.35,"untrapped_control_spreads":free["final_rms_radius"]>2 and free["final_boundary_fraction"]>2e-2,"timestep_refinement_improves":refinement["successive_differences"][1]<refinement["successive_differences"][0],"perturbation_response_is_continuous":continuity["ordered"]}
    return {"schema":"openwave.m9.long-horizon-stability-result.v1","task":"M9.48","config":asdict(cfg),"physlib_zil_reuse":{"branch":"entropic-physlib-linear-full","weak_limit_components":["MeasureTheory.TendstoInDistribution","MeasureTheory.tendstoInDistribution_of_ae_tendsto","ProbabilityMeasure"],"finite_evolution_component":"NormedSpace.exp","excluded_open_targets":["continuum_semigroup_wellposed","continuum_lindblad_generator"]},"trapped_campaign":campaign,"untrapped_control":free,"refinement":refinement,"perturbation_continuity":continuity,"summary":{"maximum_norm_error":ne,"maximum_energy_drift":ed,"maximum_boundary_fraction":boundary,"maximum_radius_ratio":ratio},"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["long-horizon deterministic 3D split-step campaign","bounded trapped response to four perturbation classes","norm, energy, radius, center, and boundary diagnostics","time-step refinement and perturbation-continuity controls","explicit trap-free spreading control"],"does_not_establish":["self-bound particle stability","continuum orbital stability theorem","full unified M9.47 dynamics in three dimensions","experimental particle lifetime"]}}

def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
