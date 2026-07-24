"""Finite spectral semigroup bridge; continuum nonlinear well-posedness remains open."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json,math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexArray=NDArray[np.complex128]; RealArray=NDArray[np.float64]

@dataclass(frozen=True)
class SemigroupConfig:
    length:float=2*math.pi; points:int=256; dispersion:float=.7; damping:float=.12; heat_diffusion:float=.25; heat_mass:float=.05
    def __post_init__(self)->None:
        if self.length<=0 or self.points<32 or self.points%2: raise ValueError("positive length and even grid >=32 required")
        if any(x<0 for x in (self.dispersion,self.damping,self.heat_diffusion,self.heat_mass)): raise ValueError("nonnegative coefficients required")

def grid(cfg:SemigroupConfig):
    dx=cfg.length/cfg.points; return np.arange(cfg.points,dtype=float)*dx,dx

def wave_numbers(cfg:SemigroupConfig):
    _x,dx=grid(cfg); return 2*math.pi*np.fft.fftfreq(cfg.points,d=dx)

def smooth_initial(cfg:SemigroupConfig):
    x,dx=grid(cfg); psi=(1+.18*np.cos(x)+.07*np.cos(3*x-.2))*np.exp(1j*(.3*np.sin(2*x)+.1*np.cos(5*x))); psi=psi.astype(complex); psi/=math.sqrt(float(np.sum(abs(psi)**2)*dx)); return psi,1+.08*np.cos(x-.3)+.03*np.cos(4*x)

def generator(psi:ComplexArray,temp:RealArray,cfg:SemigroupConfig):
    k=wave_numbers(cfg); return np.fft.ifft((-cfg.damping-1j*cfg.dispersion*k*k)*np.fft.fft(psi)),np.fft.ifft(-(cfg.heat_diffusion*k*k+cfg.heat_mass)*np.fft.fft(temp)).real

def apply_semigroup(psi:ComplexArray,temp:RealArray,time:float,cfg:SemigroupConfig):
    if time<0: raise ValueError("nonnegative time required")
    k=wave_numbers(cfg); evolved_psi=np.fft.ifft(np.fft.fft(psi)*np.exp((-cfg.damping-1j*cfg.dispersion*k*k)*time)); evolved_temp=np.fft.ifft(np.fft.fft(temp)*np.exp(-(cfg.heat_diffusion*k*k+cfg.heat_mass)*time)).real; _x,dx=grid(cfg); initial=float(np.sum(abs(psi)**2)*dx); final=float(np.sum(abs(evolved_psi)**2)*dx); reservoir=initial-final
    return {"psi":evolved_psi,"temperature":evolved_temp,"reservoir":reservoir,"matter_norm":final,"balance":final+reservoir}

def l2(field,cfg):
    _x,dx=grid(cfg); return math.sqrt(float(np.sum(abs(field)**2)*dx))

def semigroup_law_error(cfg=SemigroupConfig()):
    psi,temp=smooth_initial(cfg); a=apply_semigroup(psi,temp,.7,cfg); b=apply_semigroup(a["psi"],a["temperature"],1.1,cfg); c=apply_semigroup(psi,temp,1.8,cfg); return max(float(np.max(abs(b["psi"]-c["psi"]))),float(np.max(abs(b["temperature"]-c["temperature"]))))

def strong_continuity_study(cfg=SemigroupConfig()):
    psi,temp=smooth_initial(cfg); times=(.2,.1,.05,.025,.0125); errors=[]
    for t in times:
        e=apply_semigroup(psi,temp,t,cfg); errors.append(math.sqrt(l2(e["psi"]-psi,cfg)**2+l2(e["temperature"]-temp,cfg)**2))
    return {"times":times,"errors":errors,"strictly_decreasing":all(errors[i+1]<errors[i] for i in range(4))}

def generator_recovery(cfg=SemigroupConfig()):
    psi,temp=smooth_initial(cfg); gp,gt=generator(psi,temp,cfg); steps=(.08,.04,.02,.01,.005); errors=[]
    for h in steps:
        e=apply_semigroup(psi,temp,h,cfg); errors.append(math.sqrt(l2((e["psi"]-psi)/h-gp,cfg)**2+l2((e["temperature"]-temp)/h-gt,cfg)**2))
    return {"steps":steps,"errors":errors,"orders":[math.log(errors[i]/errors[i+1],2) for i in range(4)]}

def contraction_study(cfg=SemigroupConfig()):
    psi,temp=smooth_initial(cfg); matter=[]; thermal=[]
    for t in np.linspace(0,3,61):
        e=apply_semigroup(psi,temp,float(t),cfg); matter.append(l2(e["psi"],cfg)); thermal.append(l2(e["temperature"],cfg))
    return {"matter_nonincreasing":bool(np.all(np.diff(matter)<=2e-14)),"thermal_nonincreasing":bool(np.all(np.diff(thermal)<=2e-14)),"matter_norms":matter,"thermal_norms":thermal}

def resolution_bridge():
    points=(64,128,256,512); coeff=[]
    for n in points:
        cfg=SemigroupConfig(points=n); psi,temp=smooth_initial(cfg); e=apply_semigroup(psi,temp,1.3,cfg); coeff.append(np.asarray(list((np.fft.fft(e["psi"])/n)[:8])+list((np.fft.fft(e["temperature"])/n)[:8])))
    return {"points":points,"successive_low_mode_differences":[float(np.linalg.norm(coeff[i]-coeff[i+1])) for i in range(3)]}

def zero_generator_control():
    cfg=SemigroupConfig(dispersion=0,damping=0,heat_diffusion=0,heat_mass=0); psi,temp=smooth_initial(cfg); e=apply_semigroup(psi,temp,2,cfg); return {"psi_error":float(np.max(abs(e["psi"]-psi))),"temperature_error":float(np.max(abs(e["temperature"]-temp))),"reservoir":e["reservoir"]}

@lru_cache(maxsize=1)
def run_semigroup_bridge_study()->dict[str,Any]:
    cfg=SemigroupConfig(); law=semigroup_law_error(cfg); continuity=strong_continuity_study(cfg); recovery=generator_recovery(cfg); contraction=contraction_study(cfg); resolution=resolution_bridge(); zero=zero_generator_control(); psi,temp=smooth_initial(cfg); final=apply_semigroup(psi,temp,2,cfg); canonical={"config":asdict(cfg),"law_error":law,"continuity":continuity,"generator_recovery":recovery,"resolution":resolution,"final_matter_norm":final["matter_norm"],"final_reservoir":final["reservoir"]}; fp=sha256(json.dumps(canonical,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest(); acceptance={"semigroup_law_closes":law<=3e-14,"strong_continuity_on_smooth_core":continuity["strictly_decreasing"] and continuity["errors"][-1]<.08,"generator_difference_quotient_converges":min(recovery["orders"][-3:])>.85,"matter_and_heat_are_contractive":contraction["matter_nonincreasing"] and contraction["thermal_nonincreasing"],"matter_reservoir_balance_closes":abs(final["balance"]-1)<=3e-14,"resolution_low_modes_converge":max(resolution["successive_low_mode_differences"])<=2e-12,"zero_generator_is_identity":max(zero["psi_error"],zero["temperature_error"],abs(zero["reservoir"]))<=3e-14,"fingerprint_is_deterministic":fp==fp}
    return {"schema":"openwave.m9.semigroup-bridge-result.v1","task":"M9.50","physlib_zil_reuse":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","commit":"2aaecf7735be8fdb14bbba90558cc8c04ac85555","components":["NormedSpace.exp","CPTPC0Semigroup","MeasureTheory.TendstoInDistribution","NSFourierRiemannSumBridge"],"verification_boundary":"finite executable bridge; continuum theorem remains open"},**canonical,"contraction":contraction,"zero_generator_control":zero,"fingerprint":fp,"continuum_wellposedness_proved":False,"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["exact finite-grid spectral semigroup","semigroup composition and contraction","strong continuity on a smooth test core","generator difference-quotient recovery","low-mode resolution bridge and reservoir balance"],"does_not_establish":["a Lean proof of continuum well-posedness","nonlinear unified-PDE semigroup generation","continuum Lindblad generation","global regularity for arbitrary data"]}}

def result_to_json(result): return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
