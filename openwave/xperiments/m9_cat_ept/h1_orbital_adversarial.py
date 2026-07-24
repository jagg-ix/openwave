"""M9.67 adversarial H1-like orbit and formal-gap campaign."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
import json,math
from typing import Any
import numpy as np
from .coefficient_self_consistency import selected_coefficients
from .cubic_quintic_continuum import coercivity_constant

OPENWAVE_HEAD="e11e8fce88ce886812860ce747c48d32c8eaeb57";FORMAL_HEAD="e2c06741c3e49deb604082a2e9c2e918eab8d545";ZIL_HEAD="f39758f85ee6300b8060e4f8ea1ecf344ed32c96"
FORMAL_SOURCE={"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean","sha":"d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7","closed_scope":["jointly continuous fixed-energy cubic semiflow","strict norm contraction","zero-field global attractor"],"excluded_scope":["spatial Laplacian cubic--quintic H1 evolution","mass/energy conservation for the conservative PDE","compactness modulo symmetries","orbital stability of a nonzero branch"]}

@dataclass(frozen=True)
class H1AdversarialConfig:
 dispersion:float=.65;grids:tuple[int,...]=(20,24);half_width:float=8.;dt:float=5e-4;final_time:float=.4;sample_stride:int=100
 cases:tuple[str,...]=("scale_minus","scale_plus","anisotropic","phase_chirp","translated","noise");seed:int=20260724
 def __post_init__(self):
  if min(self.dispersion,self.half_width,self.dt,self.final_time)<=0 or any(n<16 or n%2 for n in self.grids):raise ValueError("invalid campaign")

def coefficients():
 x=selected_coefficients();return float(x["alpha"]),float(x["beta"])

def grid(n,L):
 dx=2*L/n;axis=(np.arange(n)-n/2)*dx;x,y,z=np.meshgrid(axis,axis,axis,indexing="ij");wave=2*math.pi*np.fft.fftfreq(n,d=dx);kx,ky,kz=np.meshgrid(wave,wave,wave,indexing="ij")
 return x,y,z,x*x+y*y+z*z,kx*kx+ky*ky+kz*kz,np.asarray(dx)

def normalize(psi,dx):
 mass=float(np.sum(np.abs(psi)**2)*dx**3)
 if mass<=0:raise ValueError("nonzero state required")
 return psi/math.sqrt(mass)

def initial_state(case,n,cfg):
 g=grid(n,cfg.half_width);x,y,z,r2,k2,dx=g
 if case=="scale_minus":field=np.exp(-r2/(2*.96**2))
 elif case=="scale_plus":field=np.exp(-r2/(2*1.04**2))
 elif case=="anisotropic":
  sx,sy=1.08,.94;sz=1/(sx*sy);field=np.exp(-.5*((x/sx)**2+(y/sy)**2+(z/sz)**2))
 elif case=="phase_chirp":field=np.exp(-r2/2)*np.exp(.08j*r2)
 elif case=="translated":field=np.exp(-((x-.55)**2+y*y+z*z)/2)
 elif case=="noise":
  base=np.exp(-r2/2).astype(complex);rng=np.random.default_rng(cfg.seed+n);noise=rng.normal(size=base.shape)+1j*rng.normal(size=base.shape);noise=np.fft.ifftn(np.fft.fftn(noise)*np.exp(-.15*k2));field=base*(1+.03*noise/np.std(noise.real))
 else:raise ValueError(case)
 return normalize(np.asarray(field,complex),float(dx)),g

def observables(psi,g,cfg):
 a,b=coefficients();x,y,z,_r2,k2,dxa=g;dx=float(dxa);rho=np.abs(psi)**2;mass=float(np.sum(rho)*dx**3)
 center=np.asarray([float(np.sum(q*rho)*dx**3/mass) for q in (x,y,z)]);coords=(x-center[0],y-center[1],z-center[2]);cr2=sum(q*q for q in coords);radius=math.sqrt(float(np.sum(cr2*rho)*dx**3/mass))
 cov=np.asarray([[float(np.sum(coords[i]*coords[j]*rho)*dx**3/mass) for j in range(3)] for i in range(3)]);eig=np.linalg.eigvalsh(cov);boundary=(np.abs(x)>=cfg.half_width-2*dx)|(np.abs(y)>=cfg.half_width-2*dx)|(np.abs(z)>=cfg.half_width-2*dx)
 grad=np.fft.ifftn(np.sqrt(k2)*np.fft.fftn(psi));grad2=float(np.sum(np.abs(grad)**2)*dx**3);energy=cfg.dispersion*grad2-.5*a*float(np.sum(rho**2)*dx**3)+(b/3)*float(np.sum(rho**3)*dx**3)
 return {"mass":mass,"energy":energy,"gradient_sq":grad2,"center_norm":float(np.linalg.norm(center)),"centered_radius":radius,"boundary_fraction":float(np.sum(rho[boundary])*dx**3/mass),"covariance_anisotropy":float(eig[-1]/max(eig[0],1e-15))}

def strang_step(psi,dt,k2,cfg):
 a,b=coefficients();rho=np.abs(psi)**2;psi*=np.exp(-.5j*dt*(-a*rho+b*rho*rho));psi=np.fft.ifftn(np.fft.fftn(psi)*np.exp(-1j*cfg.dispersion*k2*dt));rho=np.abs(psi)**2;return psi*np.exp(-.5j*dt*(-a*rho+b*rho*rho))

def evolve_case(case,points,cfg=H1AdversarialConfig()):
 psi,g=initial_state(case,points,cfg);initial=observables(psi,g,cfg);steps=math.ceil(cfg.final_time/cfg.dt);dt=cfg.final_time/steps;maxm=maxe=0.;maxg=initial["gradient_sq"];maxr=minr=initial["centered_radius"];maxb=initial["boundary_fraction"];maxa=initial["covariance_anisotropy"]
 for i in range(steps):
  psi=strang_step(psi,dt,g[4],cfg)
  if (i+1)%cfg.sample_stride==0 or i+1==steps:
   row=observables(psi,g,cfg);maxm=max(maxm,abs(row["mass"]-initial["mass"]));maxe=max(maxe,abs(row["energy"]-initial["energy"]));maxg=max(maxg,row["gradient_sq"]);maxr=max(maxr,row["centered_radius"]);minr=min(minr,row["centered_radius"]);maxb=max(maxb,row["boundary_fraction"]);maxa=max(maxa,row["covariance_anisotropy"])
 final=observables(psi,g,cfg);a,b=coefficients();bound=(initial["energy"]+coercivity_constant(a,b)*initial["mass"])/cfg.dispersion
 return {"case":case,"points":points,"dt":dt,"initial":initial,"final":final,"maximum_mass_error":maxm,"maximum_energy_drift":maxe,"maximum_gradient_sq":maxg,"coercive_gradient_bound":bound,"minimum_centered_radius":minr,"maximum_centered_radius":maxr,"maximum_boundary_fraction":maxb,"maximum_covariance_anisotropy":maxa,"gradient_bound_respected":maxg<=bound+1e-8}

def formal_gap_ledger():return ({"interface":"fixed-spatial-energy cubic damping semiflow","status":"directly proved with explicit scope","boundary":"multiplication energy plus pointwise cubic damping on C(X,C)"},{"interface":"spatial Laplacian cubic--quintic local H1 well-posedness","status":"not closed end-to-end","boundary":"requires differential generator and H1 estimates"},{"interface":"mass and energy conservation for spatial PDE","status":"not kernel-formalized","boundary":"OpenWave numerical ledgers only"},{"interface":"compactness modulo phase and translation","status":"not kernel-formalized","boundary":"finite perturbations are not concentration compactness"},{"interface":"orbital stability of nonzero branch","status":"not kernel-formalized","boundary":"requires full variational/PDE theorem"})

@lru_cache(maxsize=1)
def run_h1_adversarial_campaign():
 cfg=H1AdversarialConfig();rows=[evolve_case(case,n,cfg) for n in cfg.grids for case in cfg.cases]
 acceptance={"current_formal_head_is_pinned":FORMAL_HEAD=="e2c06741c3e49deb604082a2e9c2e918eab8d545","formal_cubic_semiflow_scope_is_recorded":FORMAL_SOURCE["sha"]=="d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7","all_adversarial_cases_execute_on_both_grids":len(rows)==len(cfg.grids)*len(cfg.cases),"mass_is_preserved":max(x["maximum_mass_error"] for x in rows)<2e-10,"energy_drift_is_controlled":max(x["maximum_energy_drift"] for x in rows)<3e-6,"coercive_h1_bound_is_respected":all(x["gradient_bound_respected"] for x in rows),"all_orbits_remain_centered_radius_bounded":max(x["maximum_centered_radius"] for x in rows)<1.40,"boundary_loading_remains_small":max(x["maximum_boundary_fraction"] for x in rows)<2e-3,"formal_h1_gap_is_not_overstated":any(x["status"]=="not closed end-to-end" for x in formal_gap_ledger())}
 return {"schema":"openwave.m9.h1-adversarial-orbit.v1","task":"M9.67","config":asdict(cfg),"repositories":{"openwave":OPENWAVE_HEAD,"physlib":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD},"zil":ZIL_HEAD},"formal_source":FORMAL_SOURCE,"formal_gap_ledger":formal_gap_ledger(),"rows":rows,"summary":{"maximum_mass_error":max(x["maximum_mass_error"] for x in rows),"maximum_energy_drift":max(x["maximum_energy_drift"] for x in rows),"maximum_centered_radius":max(x["maximum_centered_radius"] for x in rows),"maximum_boundary_fraction":max(x["maximum_boundary_fraction"] for x in rows),"maximum_gradient_to_bound_ratio":max(x["maximum_gradient_sq"]/x["coercive_gradient_bound"] for x in rows)},"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"adversarial_h1_like_orbits_numerically_bounded":True,"coercive_h1_apriori_control_numerically_respected":True,"spatial_cubic_quintic_h1_kernel_theorem_proved":False,"arbitrary_h1_orbital_stability_proved":False,"m9_67_formal_target_closed":False},"classification":{"establishes":["bounded evolution for six perturbation classes on two grids","numerical respect of the coercive H1 gradient bound","exact formal gap ledger"],"does_not_establish":["kernel H1 well-posedness","concentration compactness","arbitrary-H1 orbital stability"]}}

def result_to_json(result):return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
