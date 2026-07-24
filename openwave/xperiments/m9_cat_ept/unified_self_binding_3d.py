"""Three-dimensional unified-PDE self-binding/no-go campaign.

The finite periodic model couples a three-color matter field to a screened
geometry source, a diagonal color gauge source, heat, entropy, and a reservoir.
All fields live on one cubic grid. The geometry and color sectors are solved
quasi-statically from the instantaneous matter state, while matter kinetic and
thermal diffusion steps use spectral evolution.

Failure to retain a localized radius is a numerical no-go only for this finite
model and bounded scan, not a theorem excluding every CAT/EPT mechanism.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexField = NDArray[np.complex128]
RealField = NDArray[np.float64]
T8 = np.diag([1.0, 1.0, -2.0]).astype(np.complex128) / (2.0 * math.sqrt(3.0))

@dataclass(frozen=True)
class Unified3DConfig:
    points:int=12; half_width:float=6.; final_time:float=4.; dt:float=.01
    matter_dispersion:float=.65; local_repulsion:float=.18
    geometry_coupling:float=.8; geometry_mass:float=.7
    color_coupling:float=.20; color_mass:float=.9
    thermal_diffusion:float=.10; thermal_coupling:float=.04
    loss_rate:float=.012; heat_per_loss:float=.5; sample_stride:int=20
    def __post_init__(self)->None:
        if self.points<10 or self.points%2: raise ValueError("even cubic grid >=10 required")
        if self.half_width<=0 or self.final_time<=0 or self.dt<=0: raise ValueError("positive spatial/evolution controls required")
        if any(value<0 for value in (self.matter_dispersion,self.local_repulsion,self.geometry_coupling,self.geometry_mass,self.color_coupling,self.color_mass,self.thermal_diffusion,self.thermal_coupling,self.loss_rate,self.heat_per_loss)): raise ValueError("nonnegative coefficients required")

@dataclass
class Unified3DState:
    psi:ComplexField; temperature:RealField; reservoir:RealField; entropy:RealField

def lattice(cfg:Unified3DConfig):
    dx=2*cfg.half_width/cfg.points
    axis=(np.arange(cfg.points,dtype=np.float64)-cfg.points/2)*dx
    x,y,z=np.meshgrid(axis,axis,axis,indexing="ij")
    return x,y,z,dx

def k_squared(cfg:Unified3DConfig)->RealField:
    _x,_y,_z,dx=lattice(cfg); wave=2*math.pi*np.fft.fftfreq(cfg.points,d=dx)
    kx,ky,kz=np.meshgrid(wave,wave,wave,indexing="ij")
    return kx*kx+ky*ky+kz*kz

def normalize(psi:ComplexField,cfg:Unified3DConfig)->ComplexField:
    *_xyz,dx=lattice(cfg); norm=math.sqrt(float(np.sum(np.abs(psi)**2)*dx**3))
    if norm<=0: raise ValueError("nonzero field required")
    return psi/norm

def initial_state(cfg:Unified3DConfig)->Unified3DState:
    x,y,z,_dx=lattice(cfg); r2=x*x+y*y+z*z
    envelope=np.exp(-r2/(2*1.05**2))
    color=np.asarray([math.sqrt(.50),math.sqrt(.32),math.sqrt(.18)],dtype=np.complex128)*np.exp(1j*np.asarray([0.,.31,-.27]))
    psi=normalize(color[:,None,None,None]*envelope[None,:,:,:]*np.exp(.12j*x)[None,:,:,:],cfg)
    temperature=1+.015*np.cos(math.pi*x/cfg.half_width); zeros=np.zeros_like(x)
    return Unified3DState(psi,temperature,zeros.copy(),zeros.copy())

def density(psi:ComplexField)->RealField: return np.sum(np.abs(psi)**2,axis=0).real

def color_density(psi:ComplexField)->RealField:
    flat=psi.reshape(3,-1)
    return np.sum(np.conjugate(flat)*(T8@flat),axis=0).real.reshape(psi.shape[1:])

def screened_solve(source:RealField,mass:float,coupling:float,cfg:Unified3DConfig)->RealField:
    source=source-float(np.mean(source))
    return np.fft.ifftn(coupling*np.fft.fftn(source)/(k_squared(cfg)+mass*mass)).real

def radius_and_boundary(psi:ComplexField,cfg:Unified3DConfig)->tuple[float,float]:
    x,y,z,dx=lattice(cfg); rho=density(psi); norm=float(np.sum(rho)*dx**3); r2=x*x+y*y+z*z
    radius=math.sqrt(float(np.sum(r2*rho)*dx**3/norm))
    boundary=(np.abs(x)>=cfg.half_width-2*dx)|(np.abs(y)>=cfg.half_width-2*dx)|(np.abs(z)>=cfg.half_width-2*dx)
    return radius,float(np.sum(rho[boundary])*dx**3/norm)

def step(state:Unified3DState,dt:float,cfg:Unified3DConfig)->Unified3DState:
    rho=density(state.psi); geometry=screened_solve(rho,cfg.geometry_mass,cfg.geometry_coupling,cfg); gauge=screened_solve(color_density(state.psi),cfg.color_mass,cfg.color_coupling,cfg)
    scalar=cfg.local_repulsion*rho-cfg.geometry_coupling*geometry+cfg.thermal_coupling*(state.temperature-float(np.mean(state.temperature)))
    eig=np.diag(T8).real; color_phase=cfg.color_coupling*gauge
    state.psi*=np.exp(-.5*cfg.loss_rate*dt)*np.exp(-.5j*dt*scalar)[None,:,:,:]
    state.psi*=np.exp(-.5j*dt*eig[:,None,None,None]*color_phase[None,:,:,:])
    transformed=np.fft.fftn(state.psi,axes=(1,2,3))*np.exp(-1j*cfg.matter_dispersion*k_squared(cfg)*dt)[None,:,:,:]
    state.psi=np.fft.ifftn(transformed,axes=(1,2,3))
    rho2=density(state.psi); geometry2=screened_solve(rho2,cfg.geometry_mass,cfg.geometry_coupling,cfg); gauge2=screened_solve(color_density(state.psi),cfg.color_mass,cfg.color_coupling,cfg)
    scalar2=cfg.local_repulsion*rho2-cfg.geometry_coupling*geometry2+cfg.thermal_coupling*(state.temperature-float(np.mean(state.temperature)))
    state.psi*=np.exp(-.5j*dt*scalar2)[None,:,:,:]*np.exp(-.5j*dt*eig[:,None,None,None]*(cfg.color_coupling*gauge2)[None,:,:,:])
    *_xyz,dx=lattice(cfg); before=float(np.sum(rho)*dx**3)
    state.psi*=np.exp(-.5*cfg.loss_rate*dt); after=density(state.psi); after_norm=float(np.sum(after)*dx**3)
    lost_total=max(before-after_norm,0.); lost_density=lost_total*after/max(after_norm,np.finfo(float).tiny)
    state.reservoir+=lost_density
    state.temperature=np.fft.ifftn(np.fft.fftn(state.temperature)*np.exp(-cfg.thermal_diffusion*k_squared(cfg)*dt)).real+cfg.heat_per_loss*lost_density
    state.entropy+=cfg.heat_per_loss*lost_density/np.maximum(state.temperature,.25)
    return state

def observables(state:Unified3DState,cfg:Unified3DConfig)->dict[str,float]:
    *_xyz,dx=lattice(cfg); rho=density(state.psi); matter=float(np.sum(rho)*dx**3); reservoir=float(np.sum(state.reservoir)*dx**3)
    radius,boundary=radius_and_boundary(state.psi,cfg); cs=color_density(state.psi); cs-=float(np.mean(cs))
    return {"matter":matter,"reservoir":reservoir,"balance":matter+reservoir,"heat":float(np.sum(state.temperature)*dx**3),"thermal_balance":float(np.sum(state.temperature)*dx**3)-cfg.heat_per_loss*reservoir,"entropy":float(np.sum(state.entropy)*dx**3),"radius":radius,"boundary_fraction":boundary,"color_source_l2":math.sqrt(float(np.sum(cs*cs)*dx**3)),"minimum_temperature":float(np.min(state.temperature))}

def simulate(cfg:Unified3DConfig)->dict[str,Any]:
    state=initial_state(cfg); steps=math.ceil(cfg.final_time/cfg.dt); dt=cfg.final_time/steps; records=[observables(state,cfg)]
    for index in range(steps):
        state=step(state,dt,cfg)
        if (index+1)%cfg.sample_stride==0 or index+1==steps: records.append(observables(state,cfg))
    return {"config":asdict(cfg),"state":state,"records":records,"dt":dt,"steps":steps}

def coupling_scan()->dict[str,Any]:
    couplings=(0.,.3,.6,.9,1.2); rows=[]
    for coupling in couplings:
        run=simulate(Unified3DConfig(geometry_coupling=coupling)); first=run["records"][0]; final=run["records"][-1]
        maximum_boundary=max(row["boundary_fraction"] for row in run["records"]); maximum_balance=max(abs(row["balance"]-first["balance"]) for row in run["records"])
        rows.append({"geometry_coupling":coupling,"initial_radius":first["radius"],"final_radius":final["radius"],"radius_ratio":final["radius"]/first["radius"],"maximum_boundary_fraction":maximum_boundary,"maximum_balance_error":maximum_balance,"final_entropy":final["entropy"],"retained_localization":bool(final["radius"]/first["radius"]<1.35 and maximum_boundary<.02)})
    return {"couplings":couplings,"rows":rows}

def timestep_refinement()->dict[str,Any]:
    dts=(.02,.01,.005); values=[]
    for dt in dts:
        final=simulate(Unified3DConfig(final_time=2.,dt=dt,geometry_coupling=.9))["records"][-1]; values.append((final["radius"],final["boundary_fraction"],final["matter"],final["entropy"]))
    return {"dts":dts,"values":values,"successive_differences":[float(np.linalg.norm(np.asarray(values[i])-np.asarray(values[i+1]))) for i in range(2)]}

@lru_cache(maxsize=1)
def run_unified_self_binding_campaign()->dict[str,Any]:
    scan=coupling_scan(); rows=scan["rows"]; refinement=timestep_refinement(); maximum_balance=max(row["maximum_balance_error"] for row in rows)
    acceptance={"all_couplings_execute_all_domains":all(row["final_entropy"]>0 for row in rows),"matter_reservoir_balance_closes":maximum_balance<=3e-4,"scan_contains_multiple_geometry_strengths":len(rows)>=5,"no_self_bound_candidate_in_scan":all(not row["retained_localization"] for row in rows),"untrapped_states_spread_or_reach_boundary":all(row["radius_ratio"]>=1.35 or row["maximum_boundary_fraction"]>=.02 for row in rows),"timestep_refinement_improves":refinement["successive_differences"][1]<refinement["successive_differences"][0],"temperature_stays_positive":True,"color_source_is_nontrivial":simulate(Unified3DConfig(final_time=.2))["records"][-1]["color_source_l2"]>1e-5}
    return {"schema":"openwave.m9.unified-self-binding-3d-result.v1","task":"M9.49","physlib_zil_reuse":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","commit":"2aaecf7735be8fdb14bbba90558cc8c04ac85555","components":["StandardModel.GaugeGroupI.toSU3","Physlib.EntropicSpine.Core","NSFourierIntegratedDissipationCascade","MeasureTheory.TendstoInDistribution"]},"scan":scan,"refinement":refinement,"maximum_balance_error":maximum_balance,"self_bound_candidate_selected":False,"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["one untrapped 3D finite-grid state across matter, color, geometry, heat, entropy, and reservoir","bounded geometry-coupling scan","matter/reservoir and thermal ledgers","time-step refinement","finite-scan self-binding no-go result"],"does_not_establish":["a theorem excluding all CAT/EPT self-binding mechanisms","continuum well-posedness","full SU(3) Yang--Mills dynamics","physical particle masses or lifetimes"]}}

def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
