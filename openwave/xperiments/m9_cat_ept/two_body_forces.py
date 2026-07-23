"""M9.30: regularized two-body electric and magnetic interaction kernels."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

RealVector=NDArray[np.float64]

@dataclass(frozen=True)
class InteractionParameters:
    electric_coupling: float=1.0
    magnetic_coupling: float=1.0
    electric_softening: float=.30
    magnetic_softening: float=.40
    derivative_step: float=1e-4
    def __post_init__(self)->None:
        if self.electric_coupling<=0 or self.magnetic_coupling<=0: raise ValueError("positive couplings required")
        if self.electric_softening<=0 or self.magnetic_softening<=0: raise ValueError("positive softening lengths required")
        if self.derivative_step<=0: raise ValueError("positive derivative step required")

def electric_energy(r:float,q1:float,q2:float,p:InteractionParameters)->float:
    return p.electric_coupling*q1*q2/math.sqrt(r*r+p.electric_softening**2)

def electric_force_exact(r:float,q1:float,q2:float,p:InteractionParameters)->float:
    return p.electric_coupling*q1*q2*r/(r*r+p.electric_softening**2)**1.5

def magnetic_orientation_factor(m1:RealVector,m2:RealVector,direction:RealVector)->float:
    unit=direction/np.linalg.norm(direction)
    return float(np.dot(m1,m2)-3*np.dot(m1,unit)*np.dot(m2,unit))

def magnetic_energy(r:float,m1:RealVector,m2:RealVector,direction:RealVector,p:InteractionParameters)->float:
    return p.magnetic_coupling*magnetic_orientation_factor(m1,m2,direction)/(r*r+p.magnetic_softening**2)**1.5

def magnetic_force_exact(r:float,m1:RealVector,m2:RealVector,direction:RealVector,p:InteractionParameters)->float:
    return 3*p.magnetic_coupling*magnetic_orientation_factor(m1,m2,direction)*r/(r*r+p.magnetic_softening**2)**2.5

def numerical_force(energy_function,separation:float,step:float)->float:
    return -float((energy_function(separation+step)-energy_function(separation-step))/(2*step))

def asymptotic_slope(separations:NDArray[np.float64],forces:NDArray[np.float64])->float:
    return float(np.polyfit(np.log(separations),np.log(np.abs(forces)),1)[0])

def force_pair(radial_force:float,direction:RealVector)->tuple[RealVector,RealVector]:
    first=radial_force*direction/np.linalg.norm(direction); return first,-first

def combined_force(r:float,q1:float,q2:float,m1:RealVector,m2:RealVector,direction:RealVector,p:InteractionParameters)->float:
    return electric_force_exact(r,q1,q2,p)+magnetic_force_exact(r,m1,m2,direction,p)

@lru_cache(maxsize=1)
def run_two_body_force_study()->dict[str,Any]:
    p=InteractionParameters(); direction=np.array([0.,0.,1.]); parallel=np.array([0.,0.,.5]); antiparallel=-parallel; probe=3.0
    electric_numeric=numerical_force(lambda r:electric_energy(r,1,1,p),probe,p.derivative_step)
    electric_exact=electric_force_exact(probe,1,1,p)
    magnetic_numeric=numerical_force(lambda r:magnetic_energy(r,parallel,parallel,direction,p),probe,p.derivative_step)
    magnetic_exact=magnetic_force_exact(probe,parallel,parallel,direction,p)
    separations=np.geomspace(5,30,40)
    electric_slope=asymptotic_slope(separations,np.array([electric_force_exact(r,1,1,p) for r in separations]))
    magnetic_slope=asymptotic_slope(separations,np.array([magnetic_force_exact(r,parallel,parallel,direction,p) for r in separations]))
    like=electric_force_exact(probe,1,1,p); opposite=electric_force_exact(probe,1,-1,p)
    aligned=magnetic_force_exact(probe,parallel,parallel,direction,p); anti=magnetic_force_exact(probe,parallel,antiparallel,direction,p)
    first,second=force_pair(combined_force(probe,1,-1,parallel,parallel,direction,p),direction)
    acceptance={
      "electric_derivative_matches_energy":abs(electric_numeric-electric_exact)<=2e-9,
      "magnetic_derivative_matches_energy":abs(magnetic_numeric-magnetic_exact)<=2e-9,
      "coulomb_force_asymptote":abs(electric_slope+2)<=2e-2,
      "dipole_force_asymptote":abs(magnetic_slope+4)<=3e-2,
      "electric_signs":like>0 and opposite<0,
      "magnetic_orientation_signs":aligned<0 and anti>0,
      "action_reaction_closes":float(np.linalg.norm(first+second))<=2e-14,
      "finite_size_regularization_and_superposition":math.isfinite(electric_energy(0,1,1,p)) and math.isfinite(magnetic_energy(1e-12,parallel,parallel,direction,p)) and abs(combined_force(probe,1,-1,parallel,parallel,direction,p)-(opposite+aligned))<=2e-14,
    }
    return {"schema":"openwave.m9.two-body-force-result.v1","task":"M9.30","parameters":asdict(p),"probe_separation":probe,
            "electric":{"like_force":like,"opposite_force":opposite,"numeric_derivative_force":electric_numeric,"exact_force":electric_exact,"asymptotic_log_slope":electric_slope},
            "magnetic":{"parallel_axial_force":aligned,"antiparallel_axial_force":anti,"numeric_derivative_force":magnetic_numeric,"exact_force":magnetic_exact,"asymptotic_log_slope":magnetic_slope},
            "combined_action_reaction_error":float(np.linalg.norm(first+second)),"acceptance":acceptance,"passed":all(acceptance.values()),
            "field_observable_kernel":True,"emergent_particle_interaction_established":False,
            "classification":{"establishes":["regularized electric and dipole kernels","Coulomb and dipole asymptotes","sign and action-reaction controls"],
                              "does_not_establish":["emergence from full CAT/EPT PDE","force between stable CAT/EPT particles","physical couplings"]}}

def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
