"""Weak-field gravity and equivalence-principle simulation suite.

Test bodies evolve in Phi(z)=g z + 1/2 Gamma z^2 with acceleration
z''=-(m_g/m_i)dPhi/dz. This is not general relativity.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np

@dataclass(frozen=True)
class GravityConfig:
    acceleration:float=.08; tidal_gradient:float=.012; final_time:float=12.; steps:int=2400
    def __post_init__(self)->None:
        if self.final_time<=0 or self.steps<2: raise ValueError("positive integration interval required")
def potential(z:float,cfg:GravityConfig=GravityConfig())->float:return cfg.acceleration*z+.5*cfg.tidal_gradient*z*z
def potential_gradient(z:float,cfg:GravityConfig=GravityConfig())->float:return cfg.acceleration+cfg.tidal_gradient*z
def acceleration(z:float,inertial_mass:float,gravitational_mass:float,cfg:GravityConfig=GravityConfig())->float:
    if inertial_mass<=0 or gravitational_mass<0: raise ValueError("positive inertial and nonnegative gravitational mass required")
    return -(gravitational_mass/inertial_mass)*potential_gradient(z,cfg)
def velocity_verlet(z0:float,v0:float,inertial_mass:float,gravitational_mass:float,cfg:GravityConfig=GravityConfig())->dict[str,Any]:
    dt=cfg.final_time/cfg.steps; z=float(z0); v=float(v0); positions=[z]; velocities=[v]; energies=[.5*inertial_mass*v*v+gravitational_mass*potential(z,cfg)]
    for _ in range(cfg.steps):
        a0=acceleration(z,inertial_mass,gravitational_mass,cfg); zn=z+dt*v+.5*dt*dt*a0; a1=acceleration(zn,inertial_mass,gravitational_mass,cfg); vn=v+.5*dt*(a0+a1); z,v=zn,vn; positions.append(z); velocities.append(v); energies.append(.5*inertial_mass*v*v+gravitational_mass*potential(z,cfg))
    return {"times":np.linspace(0,cfg.final_time,cfg.steps+1),"positions":np.asarray(positions),"velocities":np.asarray(velocities),"energies":np.asarray(energies)}
def eotvos_parameter(mi_a:float,mg_a:float,mi_b:float,mg_b:float,z:float=0.,cfg:GravityConfig=GravityConfig())->float:
    a=abs(acceleration(z,mi_a,mg_a,cfg)); b=abs(acceleration(z,mi_b,mg_b,cfg)); return 0. if a+b==0 else 2*abs(a-b)/(a+b)
def lapse_from_potential(phi:float)->float:return math.exp(phi)
def clock_redshift(z_low:float,z_high:float,coordinate_time:float,cfg:GravityConfig=GravityConfig())->dict[str,float]:
    if coordinate_time<0: raise ValueError("nonnegative coordinate time required")
    low=potential(z_low,cfg); high=potential(z_high,cfg); tau_low=coordinate_time*lapse_from_potential(low); tau_high=coordinate_time*lapse_from_potential(high); exact=tau_high/tau_low-1.; weak=high-low
    return {"tau_low":tau_low,"tau_high":tau_high,"exact_fraction":exact,"weak_fraction":weak,"weak_error":abs(exact-weak)}
def uniform_field_equivalence(z0:float,v0:float,cfg:GravityConfig=GravityConfig(tidal_gradient=0.))->dict[str,float]:
    if abs(cfg.tidal_gradient)>1e-15: raise ValueError("uniform field required")
    run=velocity_verlet(z0,v0,1.,1.,cfg); times=run["times"]; accelerated=run["positions"]+.5*cfg.acceleration*times*times; inertial=z0+v0*times
    return {"maximum_position_error":float(np.max(np.abs(accelerated-inertial)))}
def tidal_control(cfg:GravityConfig=GravityConfig())->dict[str,float]:
    z1,z2=-.7,.9; observed=acceleration(z2,1,1,cfg)-acceleration(z1,1,1,cfg); expected=-cfg.tidal_gradient*(z2-z1)
    return {"observed_relative_acceleration":observed,"expected_relative_acceleration":expected,"error":abs(observed-expected)}
def timestep_refinement()->dict[str,Any]:
    steps=(300,600,1200,2400); positions=[]
    for count in steps: positions.append(float(velocity_verlet(1.1,-.02,1.,1.,GravityConfig(steps=count))["positions"][-1]))
    differences=[abs(positions[i]-positions[i+1]) for i in range(3)]; orders=[math.log(differences[i]/differences[i+1],2) for i in range(2)]
    return {"steps":steps,"final_positions":positions,"successive_differences":differences,"orders":orders}
@lru_cache(maxsize=1)
def run_equivalence_principle_study()->dict[str,Any]:
    cfg=GravityConfig(); light=velocity_verlet(1,0,1,1,cfg); heavy=velocity_verlet(1,0,7.5,7.5,cfg); mismatch=velocity_verlet(1,0,7.5,7.65,cfg); universal=float(np.max(np.abs(light["positions"]-heavy["positions"]))); violation=float(np.max(np.abs(light["positions"]-mismatch["positions"]))); eu=eotvos_parameter(1,1,7.5,7.5,cfg=cfg); ev=eotvos_parameter(1,1,7.5,7.65,cfg=cfg); drift=float(np.max(np.abs(light["energies"]-light["energies"][0]))); redshift=clock_redshift(0,.25,10,cfg); uniform=uniform_field_equivalence(.4,-.03); tidal=tidal_control(cfg); refinement=timestep_refinement(); zero=velocity_verlet(.3,.2,1,1,GravityConfig(acceleration=0,tidal_gradient=0)); inertial=.3+.2*zero["times"]; zero_error=float(np.max(np.abs(zero["positions"]-inertial)))
    acceptance={"universal_free_fall_for_equal_ratios":universal<=2e-13,"eotvos_parameter_vanishes":eu<=2e-15,"ratio_mismatch_is_detected":violation>=1e-2 and ev>=1e-2,"mechanical_energy_is_conserved":drift<=3e-8,"weak_field_clock_redshift_closes":redshift["weak_error"]<=3e-4,"uniform_field_matches_accelerated_frame":uniform["maximum_position_error"]<=2e-12,"tidal_relative_acceleration_closes":tidal["error"]<=2e-15,"zero_field_reduces_to_inertial_motion":zero_error<=2e-13,"verlet_refinement_is_second_order":min(refinement["orders"])>=1.9}
    return {"schema":"openwave.m9.equivalence-principle-result.v1","task":"M9.42","config":asdict(cfg),"universal_trajectory_difference":universal,"violation_trajectory_difference":violation,"eotvos_universal":eu,"eotvos_violation_control":ev,"maximum_energy_drift":drift,"clock_redshift":redshift,"uniform_field_equivalence":uniform,"tidal_control":tidal,"zero_field_error":zero_error,"refinement":refinement,"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["weak-field universality-of-free-fall control","Eotvos violation diagnostic","uniform gravity/accelerated-frame equivalence control","tidal relative-acceleration ledger","weak-field clock-redshift control"],"does_not_establish":["general relativity","Einstein field equations or tensor geometry","strong-field equivalence principle","physical gravitational coupling or experimental bounds"]}}
def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
