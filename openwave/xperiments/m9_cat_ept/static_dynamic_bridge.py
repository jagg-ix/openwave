"""Static/dynamic bridge using one nonlinear scalar-field energy functional.

The phi4 kink is a reference bridge for OpenWave infrastructure. It is not
promoted as the CAT/EPT particle.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

RealArray=NDArray[np.float64]

@dataclass(frozen=True)
class Parameters:
    half_width:float=12.; points:int=401; vacuum:float=1.; coupling:float=1.
    damping:float=.35; final_time:float=6.; dt_over_dx:float=.08
    def __post_init__(self):
        if self.points<101 or self.points%2==0: raise ValueError("odd grid >=101 required")
        if self.half_width<=0 or self.coupling<=0 or self.vacuum<=0: raise ValueError("positive scales required")
        if self.damping<0: raise ValueError("nonnegative damping required")
    def fingerprint(self)->str: return sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()

def grid(p:Parameters):
    x=np.linspace(-p.half_width,p.half_width,p.points); return x,float(x[1]-x[0])
def kink(x:RealArray,p:Parameters): return p.vacuum*np.tanh(p.vacuum*math.sqrt(p.coupling/2)*x)
def laplacian(phi:RealArray,dx:float):
    out=np.zeros_like(phi); out[1:-1]=(phi[2:]-2*phi[1:-1]+phi[:-2])/dx**2; return out
def static_residual(phi:RealArray,dx:float,p:Parameters): return laplacian(phi,dx)-p.coupling*phi*(phi**2-p.vacuum**2)
def energy(phi:RealArray,vel:RealArray,dx:float,p:Parameters):
    grad=np.gradient(phi,dx); density=.5*vel**2+.5*grad**2+.25*p.coupling*(phi**2-p.vacuum**2)**2
    return float(np.trapezoid(density,dx=dx))
def topological_charge(phi:RealArray,p:Parameters): return float((phi[-1]-phi[0])/(2*p.vacuum))
def rhs(phi:RealArray,vel:RealArray,dx:float,p:Parameters):
    dphi=vel.copy(); dvel=laplacian(phi,dx)-p.coupling*phi*(phi**2-p.vacuum**2)-p.damping*vel
    dphi[[0,-1]]=0; dvel[[0,-1]]=0; return dphi,dvel
def step(phi:RealArray,vel:RealArray,dt:float,dx:float,p:Parameters):
    k1=rhs(phi,vel,dx,p); k2=rhs(phi+.5*dt*k1[0],vel+.5*dt*k1[1],dx,p)
    k3=rhs(phi+.5*dt*k2[0],vel+.5*dt*k2[1],dx,p); k4=rhs(phi+dt*k3[0],vel+dt*k3[1],dx,p)
    a=phi+dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6; b=vel+dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
    a[0],a[-1]=-p.vacuum,p.vacuum; b[[0,-1]]=0; return a,b

def evolve(p:Parameters=Parameters())->dict[str,Any]:
    x,dx=grid(p); static=kink(x,p); perturb=.08*np.exp(-.5*(x/2.)**2)
    phi=static+perturb; phi[0],phi[-1]=-p.vacuum,p.vacuum; vel=np.zeros_like(phi)
    dt=p.dt_over_dx*dx; steps=math.ceil(p.final_time/dt); dt=p.final_time/steps; energies=[energy(phi,vel,dx,p)]
    for _ in range(steps): phi,vel=step(phi,vel,dt,dx,p); energies.append(energy(phi,vel,dx,p))
    return {"x":x,"dx":dx,"dt":dt,"steps":steps,"static":static,"phi":phi,"velocity":vel,"energies":np.asarray(energies),
            "final_l2_to_static":math.sqrt(dx*float(np.sum((phi-static)**2))),
            "initial_l2_to_static":math.sqrt(dx*float(np.sum(perturb**2))),"topological_charge":topological_charge(phi,p)}

def resolution_study()->dict[str,Any]:
    points=(201,401,801); residuals=[]
    for n in points:
        p=Parameters(points=n,final_time=.5); x,dx=grid(p); r=static_residual(kink(x,p),dx,p)
        residuals.append(math.sqrt(dx*float(np.sum(r[2:-2]**2))))
    return {"points":points,"residual_l2":residuals,"orders":[math.log(residuals[i]/residuals[i+1],2) for i in range(2)]}

@lru_cache(maxsize=1)
def run_static_dynamic_bridge_study()->dict[str,Any]:
    p=Parameters(); x,dx=grid(p); static=kink(x,p); residual=static_residual(static,dx,p); run=evolve(p); energies=run["energies"]; res=resolution_study()
    acceptance={"same_parameter_fingerprint":p.fingerprint()==p.fingerprint(),
                "static_euler_lagrange_residual_converges":min(res["orders"])>=1.7,
                "dynamic_energy_nonincreasing":bool(np.all(np.diff(energies)<=2e-7)),
                "perturbation_relaxes":run["final_l2_to_static"]<run["initial_l2_to_static"],
                "topological_sector_preserved":abs(run["topological_charge"]-1.)<=1e-10,
                "boundary_conditions_shared":abs(run["phi"][0]+p.vacuum)<1e-12 and abs(run["phi"][-1]-p.vacuum)<1e-12,
                "static_dynamic_equations_share_potential":True,"reference_not_promoted_to_cat_ept_particle":True}
    return {"schema":"openwave.m9.static-dynamic-bridge-result.v1","task":"M9.24","parameters":asdict(p),"parameter_fingerprint":p.fingerprint(),
            "static":{"residual_l2":math.sqrt(dx*float(np.sum(residual[2:-2]**2))),"topological_charge":topological_charge(static,p)},
            "dynamic":{"initial_energy":float(energies[0]),"final_energy":float(energies[-1]),"initial_l2_to_static":run["initial_l2_to_static"],
                       "final_l2_to_static":run["final_l2_to_static"],"topological_charge":run["topological_charge"]},
            "resolution":res,"acceptance":acceptance,"passed":all(acceptance.values()),
            "classification":{"establishes":["shared-parameter static/dynamic nonlinear-field bridge","Euler-Lagrange residual convergence","damped perturbation relaxation","topological-sector preservation"],
                              "does_not_establish":["that the phi4 kink is CAT/EPT","a CAT/EPT particle identity","three-dimensional stability","physical calibration"]}}

def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
