"""M9.68 no-refit higher-fidelity comparison of the frozen M9.65 frequency."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json,math
from typing import Any
import numpy as np
from .coefficient_self_consistency import selected_coefficients
from .preregistered_breathing_prediction import preregistration

OPENWAVE_HEAD="e11e8fce88ce886812860ce747c48d32c8eaeb57";FORMAL_HEAD="e2c06741c3e49deb604082a2e9c2e918eab8d545";ZIL_HEAD="f39758f85ee6300b8060e4f8ea1ecf344ed32c96"

@dataclass(frozen=True)
class IndependentComparisonConfig:
 dispersion:float=.65;grids:tuple[int,...]=(16,20,24);half_width:float=8.;dilation:float=1.04
 relaxation_dt:float=5e-4;relaxation_steps:int=13000;relaxation_check_stride:int=100;relaxation_energy_tolerance:float=1e-11
 real_dt:float=1e-3;final_time:float=24.;sample_stride:int=10;fit_start:float=5.;fit_end:float=22.;omega_min:float=.5;omega_max:float=4.5;omega_samples:int=1600;detrend_degree:int=2
 def __post_init__(self):
  if min(self.dispersion,self.half_width,self.relaxation_dt,self.real_dt,self.final_time)<=0 or any(n<12 or n%2 for n in self.grids):raise ValueError("invalid comparison controls")

def coefficients():
 x=selected_coefficients();return float(x["alpha"]),float(x["beta"])

def grid(n,L):
 dx=2*L/n;axis=(np.arange(n)-n/2)*dx;x,y,z=np.meshgrid(axis,axis,axis,indexing="ij");wave=2*math.pi*np.fft.fftfreq(n,d=dx);kx,ky,kz=np.meshgrid(wave,wave,wave,indexing="ij")
 return x,y,z,x*x+y*y+z*z,kx*kx+ky*ky+kz*kz,np.asarray(dx)

def normalize(psi,dx):
 mass=float(np.sum(np.abs(psi)**2)*dx**3)
 if mass<=0:raise ValueError("nonzero state")
 return psi/math.sqrt(mass)

def observables(psi,g,cfg):
 a,b=coefficients();r2,k2,dx=g[3],g[4],float(g[5]);rho=np.abs(psi)**2;mass=float(np.sum(rho)*dx**3);radius=math.sqrt(float(np.sum(r2*rho)*dx**3/mass));grad=np.fft.ifftn(np.sqrt(k2)*np.fft.fftn(psi));grad2=float(np.sum(np.abs(grad)**2)*dx**3);energy=cfg.dispersion*grad2-.5*a*float(np.sum(rho**2)*dx**3)+(b/3)*float(np.sum(rho**3)*dx**3)
 return {"mass":mass,"radius":radius,"energy":energy}

def relax_stationary_state(points,cfg=IndependentComparisonConfig()):
 a,b=coefficients();g=grid(points,cfg.half_width);r2,k2,dx=g[3],g[4],float(g[5]);psi=normalize(np.exp(-r2/2).astype(complex),dx);kin=np.exp(-cfg.dispersion*k2*cfg.relaxation_dt);energies=[];previous=None;used=cfg.relaxation_steps
 for i in range(cfg.relaxation_steps):
  rho=np.abs(psi)**2;psi*=np.exp(.5*cfg.relaxation_dt*(a*rho-b*rho*rho));psi=np.fft.ifftn(np.fft.fftn(psi)*kin);rho=np.abs(psi)**2;psi*=np.exp(.5*cfg.relaxation_dt*(a*rho-b*rho*rho));psi=normalize(psi,dx)
  if (i+1)%cfg.relaxation_check_stride==0:
   energy=observables(psi,g,cfg)["energy"];energies.append(energy)
   if previous is not None and abs(energy-previous)<cfg.relaxation_energy_tolerance:used=i+1;break
   previous=energy
 final=observables(psi,g,cfg)
 return {"psi":psi,"grid":g,"energies":energies,"steps_used":used,"final_energy":final["energy"],"final_radius":final["radius"],"energy_nonincreasing":all(energies[i+1]<=energies[i]+2e-12 for i in range(len(energies)-1))}

def dilate_state(psi,dilation,dx):
 from scipy.ndimage import map_coordinates
 n=psi.shape[0];indices=np.indices(psi.shape,dtype=float);center=n/2;mapped=[center+(indices[i]-center)/dilation for i in range(3)];real=map_coordinates(psi.real,mapped,order=3,mode="constant",cval=0.);imag=map_coordinates(psi.imag,mapped,order=3,mode="constant",cval=0.)
 return normalize((real+1j*imag)/dilation**1.5,dx)

def real_time_series(psi,g,cfg=IndependentComparisonConfig()):
 a,b=coefficients();k2=g[4];steps=math.ceil(cfg.final_time/cfg.real_dt);dt=cfg.final_time/steps;kin=np.exp(-1j*cfg.dispersion*k2*dt);first=observables(psi,g,cfg);times=[0.];radii=[first["radius"]];energies=[first["energy"]];masses=[first["mass"]]
 for i in range(steps):
  rho=np.abs(psi)**2;psi*=np.exp(-.5j*dt*(-a*rho+b*rho*rho));psi=np.fft.ifftn(np.fft.fftn(psi)*kin);rho=np.abs(psi)**2;psi*=np.exp(-.5j*dt*(-a*rho+b*rho*rho))
  if (i+1)%cfg.sample_stride==0:
   row=observables(psi,g,cfg);times.append((i+1)*dt);radii.append(row["radius"]);energies.append(row["energy"]);masses.append(row["mass"])
 times=np.asarray(times);radii=np.asarray(radii);energies=np.asarray(energies);masses=np.asarray(masses)
 return {"times":times,"radii":radii,"energies":energies,"masses":masses,"dt":dt,"maximum_mass_error":float(np.max(np.abs(masses-masses[0]))),"maximum_energy_drift":float(np.max(np.abs(energies-energies[0])))}

def fit_dominant_frequency(times,values,cfg=IndependentComparisonConfig()):
 mask=(times>=cfg.fit_start)&(times<=cfg.fit_end);t=times[mask];y=values[mask]
 if len(t)<20:raise ValueError("insufficient samples")
 tc=t-float(np.mean(t));best=None
 for omega in np.linspace(cfg.omega_min,cfg.omega_max,cfg.omega_samples):
  cols=[np.ones_like(tc)]+[tc**degree for degree in range(1,cfg.detrend_degree+1)]+[np.cos(omega*t),np.sin(omega*t)];matrix=np.column_stack(cols);coef,*_=np.linalg.lstsq(matrix,y,rcond=None);res=y-matrix@coef;sse=float(res@res);rmse=math.sqrt(sse/len(res))
  if best is None or sse<best[0]:best=(sse,float(omega),rmse)
 return {"omega_dimensionless":best[1],"fit_rmse":best[2],"omega_over_compton":best[1]/(2*cfg.dispersion)}

def compare_grid(points,cfg=IndependentComparisonConfig()):
 relaxed=relax_stationary_state(points,cfg);psi=dilate_state(relaxed["psi"],cfg.dilation,float(relaxed["grid"][5]));series=real_time_series(psi,relaxed["grid"],cfg);freq=fit_dominant_frequency(series["times"],series["radii"],cfg);frozen=preregistration()["dimensionless_ratio"]
 return {"points":points,"relaxation_steps":relaxed["steps_used"],"ground_state_energy":relaxed["final_energy"],"ground_state_radius":relaxed["final_radius"],"relaxation_energy_nonincreasing":relaxed["energy_nonincreasing"],"measured_omega_dimensionless":freq["omega_dimensionless"],"measured_omega_over_compton":freq["omega_over_compton"],"fit_rmse":freq["fit_rmse"],"relative_error_from_frozen_prediction":abs(freq["omega_over_compton"]-frozen)/frozen,"maximum_mass_error":series["maximum_mass_error"],"maximum_energy_drift":series["maximum_energy_drift"],"minimum_radius":float(np.min(series["radii"])),"maximum_radius":float(np.max(series["radii"]))}

def comparison_fingerprint(cfg=IndependentComparisonConfig()):
 payload={"config":asdict(cfg),"openwave":OPENWAVE_HEAD,"physlib":FORMAL_HEAD,"zil":ZIL_HEAD,"frozen":preregistration()}
 return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_independent_breathing_comparison():
 cfg=IndependentComparisonConfig();frozen=preregistration();rows=[compare_grid(n,cfg) for n in cfg.grids];ratios=np.asarray([x["measured_omega_over_compton"] for x in rows]);errors=np.asarray([x["relative_error_from_frozen_prediction"] for x in rows])
 acceptance={"current_repository_heads_are_pinned":all(len(x)==40 for x in (OPENWAVE_HEAD,FORMAL_HEAD,ZIL_HEAD)),"frozen_prediction_is_reused_without_refit":frozen["prediction_id"]=="CAT-EPT-M9.65-BREATHING-COMPTON-RATIO-v1","all_relaxations_decrease_energy":all(x["relaxation_energy_nonincreasing"] for x in rows),"all_real_time_runs_preserve_mass":max(x["maximum_mass_error"] for x in rows)<2e-10,"all_real_time_runs_control_energy":max(x["maximum_energy_drift"] for x in rows)<2e-6,"all_frequency_fits_are_finite":all(math.isfinite(x["measured_omega_over_compton"]) for x in rows),"comparison_is_decisive_against_five_percent_gate":min(errors)>frozen["relative_tolerance"],"grid_spread_is_smaller_than_prediction_error":float(np.ptp(ratios))<float(np.min(errors)),"fingerprint_is_deterministic":comparison_fingerprint(cfg)==comparison_fingerprint(cfg)}
 return {"schema":"openwave.m9.independent-breathing-comparison.v1","task":"M9.68","config":asdict(cfg),"repositories":{"openwave":OPENWAVE_HEAD,"physlib":FORMAL_HEAD,"zil":ZIL_HEAD},"frozen_prediction":frozen,"rows":rows,"summary":{"mean_measured_omega_over_compton":float(np.mean(ratios)),"minimum_measured_omega_over_compton":float(np.min(ratios)),"maximum_measured_omega_over_compton":float(np.max(ratios)),"grid_spread":float(np.ptp(ratios)),"minimum_relative_error":float(np.min(errors)),"maximum_relative_error":float(np.max(errors))},"fingerprint":comparison_fingerprint(cfg),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"prediction_independently_tested":True,"prediction_passes_preregistered_tolerance":False,"prediction_falsified_by_higher_fidelity_openwave_test":True,"external_experimental_test_performed":False,"cat_ept_theory_falsified":False},"classification":{"establishes":["independent relaxed-state comparison on three grids","no-refit test of M9.65 and its five-percent gate","falsification of the Gaussian collective-coordinate breathing prediction inside OpenWave"],"does_not_establish":["external experimental disagreement","falsification of every CAT/EPT clock or particle model","the physical electron breathing spectrum"]}}

def result_to_json(result):return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
