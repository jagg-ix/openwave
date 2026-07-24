"""Finite-grid unified CAT/EPT PDE closure control.

Couples three-color matter, a diagonal SU(3) gauge wave, geometry, heat,
reservoir and entropy on one periodic grid. The finite-grid generator follows
bounded-generator and reservoir-sandwich patterns found through ZIL on
`entropic-physlib-linear-full`. Continuum semigroup generation remains open.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexField=NDArray[np.complex128]
RealField=NDArray[np.float64]
T8=np.diag([1.,1.,-2.]).astype(np.complex128)/(2*math.sqrt(3))

@dataclass(frozen=True)
class UnifiedPDEConfig:
    length:float=12.; points:int=64; final_time:float=1.5; dt:float=.0015
    matter_dispersion:float=.45; gauge_speed:float=.9; gauge_mass:float=.7; gauge_coupling:float=.35
    geometry_diffusion:float=.22; geometry_mass:float=.8; geometry_coupling:float=.30
    thermal_diffusion:float=.18; thermal_coupling:float=.12; loss_rate:float=.045; heat_per_loss:float=.60
    def __post_init__(self)->None:
        if self.length<=0 or self.points<32 or self.points%2: raise ValueError("positive length and even grid >=32 required")
        if self.final_time<=0 or self.dt<=0: raise ValueError("positive evolution controls required")
        if any(x<0 for x in (self.matter_dispersion,self.gauge_speed,self.gauge_mass,self.gauge_coupling,self.geometry_diffusion,self.geometry_mass,self.geometry_coupling,self.thermal_diffusion,self.thermal_coupling,self.loss_rate,self.heat_per_loss)): raise ValueError("nonnegative couplings required")

@dataclass
class UnifiedState:
    psi:ComplexField; gauge:RealField; gauge_momentum:RealField; geometry:RealField
    temperature:RealField; reservoir:RealField; entropy:RealField; gauge_work:float
    def copy(self)->"UnifiedState":
        return UnifiedState(self.psi.copy(),self.gauge.copy(),self.gauge_momentum.copy(),self.geometry.copy(),self.temperature.copy(),self.reservoir.copy(),self.entropy.copy(),float(self.gauge_work))

def grid(cfg:UnifiedPDEConfig)->tuple[RealField,float]:
    dx=cfg.length/cfg.points; return (np.arange(cfg.points)-cfg.points/2)*dx,dx

def wave_numbers(cfg:UnifiedPDEConfig)->RealField:
    _,dx=grid(cfg); return 2*math.pi*np.fft.fftfreq(cfg.points,d=dx)

def laplacian(field:NDArray[Any],cfg:UnifiedPDEConfig)->NDArray[Any]:
    k=wave_numbers(cfg); return np.fft.ifft(-(k*k)*np.fft.fft(field,axis=-1),axis=-1)

def derivative(field:RealField,cfg:UnifiedPDEConfig)->RealField:
    k=wave_numbers(cfg); return np.fft.ifft(1j*k*np.fft.fft(field)).real

def initial_state(cfg:UnifiedPDEConfig=UnifiedPDEConfig())->UnifiedState:
    x,dx=grid(cfg); envelope=np.exp(-.5*(x/1.05)**2)
    color=np.asarray([math.sqrt(.52),math.sqrt(.31),math.sqrt(.17)],dtype=np.complex128)*np.exp(1j*np.asarray([0.,.35,-.28]))
    psi=color[:,None]*envelope[None,:]*np.exp(.18j*x)[None,:]; psi/=math.sqrt(float(np.sum(np.abs(psi)**2)*dx))
    temperature=1+.04*np.cos(2*math.pi*x/cfg.length)
    z=np.zeros(cfg.points)
    return UnifiedState(psi,z.copy(),z.copy(),z.copy(),temperature,z.copy(),z.copy(),0.)

def matter_density(psi:ComplexField)->RealField:return np.sum(np.abs(psi)**2,axis=0).real

def color_density(psi:ComplexField)->RealField:return np.sum(np.conjugate(psi)*(T8@psi),axis=0).real

def rhs(state:UnifiedState,cfg:UnifiedPDEConfig)->UnifiedState:
    rho=matter_density(state.psi); rho_source=rho-float(np.mean(rho)); color_source=color_density(state.psi); color_source-=float(np.mean(color_source))
    t_shift=state.temperature-float(np.mean(state.temperature)); scalar=cfg.geometry_coupling*state.geometry+cfg.thermal_coupling*t_shift; color=cfg.gauge_coupling*state.gauge
    dpsi=1j*cfg.matter_dispersion*laplacian(state.psi,cfg)-1j*scalar[None,:]*state.psi-1j*color[None,:]*(T8@state.psi)-cfg.loss_rate*state.psi
    dgauge=state.gauge_momentum
    dgm=cfg.gauge_speed**2*laplacian(state.gauge,cfg).real-cfg.gauge_mass**2*state.gauge+cfg.gauge_coupling*color_source
    dgeometry=cfg.geometry_diffusion*laplacian(state.geometry,cfg).real-cfg.geometry_mass**2*state.geometry+cfg.geometry_coupling*rho_source
    loss=2*cfg.loss_rate*rho; dtemperature=cfg.thermal_diffusion*laplacian(state.temperature,cfg).real+cfg.heat_per_loss*loss
    floor=np.maximum(state.temperature,.25); grad=derivative(state.temperature,cfg)
    dentropy=cfg.heat_per_loss*loss/floor+cfg.thermal_diffusion*(grad/floor)**2
    _,dx=grid(cfg); dwork=float(np.sum(cfg.gauge_coupling*color_source*state.gauge_momentum)*dx)
    return UnifiedState(dpsi,dgauge,dgm,dgeometry,dtemperature,loss,dentropy,dwork)

def combine(state:UnifiedState,inc:UnifiedState,factor:float)->UnifiedState:
    return UnifiedState(state.psi+factor*inc.psi,state.gauge+factor*inc.gauge,state.gauge_momentum+factor*inc.gauge_momentum,state.geometry+factor*inc.geometry,state.temperature+factor*inc.temperature,state.reservoir+factor*inc.reservoir,state.entropy+factor*inc.entropy,state.gauge_work+factor*inc.gauge_work)

def rk4_step(state:UnifiedState,dt:float,cfg:UnifiedPDEConfig)->UnifiedState:
    k1=rhs(state,cfg); k2=rhs(combine(state,k1,.5*dt),cfg); k3=rhs(combine(state,k2,.5*dt),cfg); k4=rhs(combine(state,k3,dt),cfg); out=state.copy()
    for name in ("psi","gauge","gauge_momentum","geometry","temperature","reservoir","entropy"):
        setattr(out,name,getattr(state,name)+dt*(getattr(k1,name)+2*getattr(k2,name)+2*getattr(k3,name)+getattr(k4,name))/6)
    out.gauge_work=state.gauge_work+dt*(k1.gauge_work+2*k2.gauge_work+2*k3.gauge_work+k4.gauge_work)/6
    return out

def observables(state:UnifiedState,cfg:UnifiedPDEConfig)->dict[str,float]:
    _,dx=grid(cfg); rho=matter_density(state.psi); matter=float(np.sum(rho)*dx); reservoir=float(np.sum(state.reservoir)*dx); heat=float(np.sum(state.temperature)*dx); entropy=float(np.sum(state.entropy)*dx)
    gauge_gradient=derivative(state.gauge,cfg); gauge_energy=.5*float(np.sum(state.gauge_momentum**2+cfg.gauge_speed**2*gauge_gradient**2+cfg.gauge_mass**2*state.gauge**2)*dx)
    gres=-cfg.geometry_diffusion*laplacian(state.geometry,cfg).real+cfg.geometry_mass**2*state.geometry-cfg.geometry_coupling*(rho-float(np.mean(rho)))
    cs=color_density(state.psi); cs-=float(np.mean(cs))
    return {"matter_norm":matter,"reservoir":reservoir,"matter_reservoir_balance":matter+reservoir,"heat":heat,"thermal_loss_balance":heat-cfg.heat_per_loss*reservoir,"entropy":entropy,"minimum_temperature":float(np.min(state.temperature)),"gauge_energy":gauge_energy,"gauge_work":float(state.gauge_work),"gauge_work_balance":gauge_energy-state.gauge_work,"geometry_residual_l2":math.sqrt(float(np.sum(gres**2)*dx)),"color_source_l2":math.sqrt(float(np.sum(cs**2)*dx))}

def simulate(cfg:UnifiedPDEConfig=UnifiedPDEConfig())->dict[str,Any]:
    steps=math.ceil(cfg.final_time/cfg.dt); dt=cfg.final_time/steps; state=initial_state(cfg); stride=max(1,steps//120); records=[observables(state,cfg)]
    for step in range(steps):
        state=rk4_step(state,dt,cfg)
        if (step+1)%stride==0 or step+1==steps: records.append(observables(state,cfg))
    return {"config":asdict(cfg),"state":state,"records":records,"dt":dt,"steps":steps}

def zero_coupling_control()->dict[str,float]:
    cfg=UnifiedPDEConfig(gauge_coupling=0.,geometry_coupling=0.,thermal_coupling=0.,loss_rate=0.,heat_per_loss=0.); run=simulate(cfg); records=run["records"]
    return {"matter_norm_drift":max(abs(x["matter_norm"]-records[0]["matter_norm"]) for x in records),"reservoir_max":max(x["reservoir"] for x in records),"gauge_max":float(np.max(np.abs(run["state"].gauge))),"geometry_max":float(np.max(np.abs(run["state"].geometry))),"heat_drift":max(abs(x["heat"]-records[0]["heat"]) for x in records)}

def timestep_refinement()->dict[str,Any]:
    dts=(.003,.0015,.00075); values=[]
    for dt in dts:
        f=simulate(UnifiedPDEConfig(dt=dt))["records"][-1]; values.append((f["matter_norm"],f["gauge_energy"],f["geometry_residual_l2"],f["heat"]))
    differences=[float(np.linalg.norm(np.asarray(values[i])-np.asarray(values[i+1]))) for i in range(2)]
    return {"dts":dts,"values":values,"successive_differences":differences}

@lru_cache(maxsize=1)
def run_unified_pde_study()->dict[str,Any]:
    cfg=UnifiedPDEConfig(); run=simulate(cfg); records=run["records"]; initial=records[0]; final=records[-1]
    mb=max(abs(x["matter_reservoir_balance"]-initial["matter_reservoir_balance"]) for x in records); tb=max(abs(x["thermal_loss_balance"]-initial["thermal_loss_balance"]) for x in records); gb=max(abs(x["gauge_work_balance"]-initial["gauge_work_balance"]) for x in records); ent=np.asarray([x["entropy"] for x in records]); zero=zero_coupling_control(); ref=timestep_refinement()
    acceptance={"all_six_domains_are_active":final["reservoir"]>.02 and final["gauge_energy"]>1e-8 and final["geometry_residual_l2"]>1e-6 and final["heat"]>initial["heat"] and final["entropy"]>initial["entropy"],"matter_reservoir_balance_closes":mb<=2e-8,"thermal_loss_balance_closes":tb<=2e-8,"gauge_work_balance_closes":gb<=2e-7,"entropy_is_monotone":bool(np.all(np.diff(ent)>=-2e-12)),"temperature_remains_positive":min(x["minimum_temperature"] for x in records)>=.9,"zero_coupling_reduces_cleanly":zero["matter_norm_drift"]<=2e-8 and zero["reservoir_max"]<=2e-14 and zero["gauge_max"]<=2e-14 and zero["geometry_max"]<=2e-14 and zero["heat_drift"]<=2e-13,"timestep_refinement_improves":ref["successive_differences"][1]<ref["successive_differences"][0]}
    return {"schema":"openwave.m9.unified-pde-result.v1","task":"M9.47","config":asdict(cfg),"physlib_zil_boundary":{"reused":["HilbertSchmidtOperatorSpace.HSOp","HilbertSchmidtOperatorSpace.leftMulHS_rightMulHS","NormedSpace.exp","finite-particle reservoir sandwich"],"excluded_open_targets":["continuum_lindblad_generator","continuum_semigroup_wellposed","phase_space_fokker_planck_bridge"],"branch":"entropic-physlib-linear-full"},"initial":initial,"final":final,"maximum_balance_errors":{"matter_reservoir":mb,"thermal_loss":tb,"gauge_work":gb},"zero_coupling_control":zero,"refinement":ref,"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["one finite-grid coupled PDE state across matter, color-wave, geometry, thermal, reservoir, and entropy domains","matter/reservoir, thermal/loss, and gauge/work ledgers","positive entropy production and temperature control","clean zero-coupling reduction","time-step refinement"],"does_not_establish":["continuum well-posedness or semigroup generation","a self-bound three-dimensional CAT/EPT particle","QCD, electroweak theory, or general relativity","physical calibration or experimental agreement"]}}

def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
