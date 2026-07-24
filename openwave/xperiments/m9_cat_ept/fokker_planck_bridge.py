"""Phase-space Fokker--Planck bridge for the entropic dissipative sector.

The bridge evolves a positive density on periodic x and bounded velocity v using
Strang splitting:
  * conservative semi-Lagrangian free streaming in x;
  * a reversible birth-death Markov approximation of Ornstein--Uhlenbeck
    friction/diffusion in v.

The velocity generator satisfies detailed balance with a discrete Gaussian,
its exponential is stochastic, and the phase-space evolution preserves mass and
positivity while decreasing relative entropy to equilibrium.

This is a finite phase-space bridge, not a continuum theorem.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
import json,math
from typing import Any
import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm

Array=NDArray[np.float64]

@dataclass(frozen=True)
class FPConfig:
    nx:int=32
    nv:int=41
    length:float=2*math.pi
    vmax:float=5.
    friction:float=.7
    diffusion:float=.55
    dt:float=.025
    final_time:float=2.
    def __post_init__(self)->None:
        if self.nx<8 or self.nv<9 or self.nv%2==0: raise ValueError("valid grids required")
        if min(self.length,self.vmax,self.friction,self.diffusion,self.dt,self.final_time)<=0:
            raise ValueError("positive controls required")

def grids(cfg:FPConfig)->tuple[Array,Array,float,float]:
    dx=cfg.length/cfg.nx
    x=np.arange(cfg.nx)*dx
    v=np.linspace(-cfg.vmax,cfg.vmax,cfg.nv)
    return x,v,dx,float(v[1]-v[0])

def equilibrium_velocity(cfg:FPConfig)->Array:
    _,v,_,dv=grids(cfg)
    variance=cfg.diffusion/cfg.friction
    weight=np.exp(-.5*v*v/variance)
    return weight/(np.sum(weight)*dv)

def velocity_generator(cfg:FPConfig)->Array:
    _,v,_,dv=grids(cfg)
    U=cfg.friction*v*v/(2*cfg.diffusion)
    Q=np.zeros((cfg.nv,cfg.nv))
    base=cfg.diffusion/(dv*dv)
    for i in range(cfg.nv-1):
        forward=base*math.exp(-.5*(U[i+1]-U[i]))
        backward=base*math.exp(-.5*(U[i]-U[i+1]))
        Q[i+1,i]+=forward; Q[i,i]-=forward
        Q[i,i+1]+=backward; Q[i+1,i+1]-=backward
    return Q

def velocity_propagator(time:float,cfg:FPConfig)->Array:
    if time<0: raise ValueError("nonnegative time required")
    return expm(time*velocity_generator(cfg))

def initial_density(cfg:FPConfig)->Array:
    x,v,dx,dv=grids(cfg)
    px=1+.35*np.cos(x-.4)
    pv=np.exp(-.5*((v-1.3)/.8)**2)
    f=px[:,None]*pv[None,:]
    return f/(np.sum(f)*dx*dv)

def stream_x(density:Array,time:float,cfg:FPConfig)->Array:
    _,v,dx,_=grids(cfg); out=np.empty_like(density)
    for j,velocity in enumerate(v):
        shift=velocity*time/dx
        lower=math.floor(shift); frac=shift-lower
        out[:,j]=(1-frac)*np.roll(density[:,j],lower)+frac*np.roll(density[:,j],lower+1)
    return out

def ou_step(density:Array,time:float,cfg:FPConfig)->Array:
    P=velocity_propagator(time,cfg)
    return (P@density.T).T

def strang_step(density:Array,dt:float,cfg:FPConfig)->Array:
    return stream_x(ou_step(stream_x(density,.5*dt,cfg),dt,cfg),.5*dt,cfg)

def observables(density:Array,cfg:FPConfig)->dict[str,float]:
    x,v,dx,dv=grids(cfg)
    mass=float(np.sum(density)*dx*dv)
    mean_v=float(np.sum(density*v[None,:])*dx*dv/mass)
    variance=float(np.sum(density*(v[None,:]-mean_v)**2)*dx*dv/mass)
    eq=equilibrium_velocity(cfg)
    equilibrium=np.ones((cfg.nx,1))/cfg.length*eq[None,:]
    safe=np.maximum(density,1e-300)
    relative_entropy=float(np.sum(safe*np.log(safe/equilibrium))*dx*dv)
    return {"mass":mass,"minimum":float(np.min(density)),"mean_velocity":mean_v,
            "velocity_variance":variance,"relative_entropy":relative_entropy}

def simulate(cfg:FPConfig=FPConfig())->dict[str,Any]:
    steps=math.ceil(cfg.final_time/cfg.dt); dt=cfg.final_time/steps
    density=initial_density(cfg); records=[observables(density,cfg)]
    stride=max(1,steps//80)
    for i in range(steps):
        density=strang_step(density,dt,cfg)
        if (i+1)%stride==0 or i+1==steps: records.append(observables(density,cfg))
    return {"density":density,"records":records,"dt":dt,"steps":steps}

def ou_semigroup_error(cfg:FPConfig)->float:
    return float(np.max(np.abs(
      velocity_propagator(.6,cfg)@velocity_propagator(.9,cfg)-
      velocity_propagator(1.5,cfg))))

def detailed_balance_error(cfg:FPConfig)->float:
    Q=velocity_generator(cfg); eq=equilibrium_velocity(cfg); _,_,_,dv=grids(cfg)
    pi=eq*dv; errors=[]
    for i in range(cfg.nv):
        for j in range(cfg.nv):
            errors.append(abs(Q[i,j]*pi[j]-Q[j,i]*pi[i]))
    return float(max(errors))

def analytic_moments(time:float,cfg:FPConfig)->dict[str,float]:
    _,v,dx,dv=grids(cfg); f=initial_density(cfg)
    m0=float(np.sum(f*v[None,:])*dx*dv)
    var0=float(np.sum(f*(v[None,:]-m0)**2)*dx*dv)
    eqvar=cfg.diffusion/cfg.friction
    return {"mean":m0*math.exp(-cfg.friction*time),
      "variance":eqvar+(var0-eqvar)*math.exp(-2*cfg.friction*time)}

def refinement()->dict[str,Any]:
    dts=(.1,.05,.025,.0125); values=[]
    for dt in dts:
        cfg=FPConfig(dt=dt)
        f=simulate(cfg)["records"][-1]
        values.append((f["mean_velocity"],f["velocity_variance"],f["relative_entropy"]))
    differences=[float(np.linalg.norm(np.asarray(values[i])-np.asarray(values[i+1])))
                 for i in range(len(values)-1)]
    return {"dts":dts,"values":values,"successive_differences":differences}

@lru_cache(maxsize=1)
def run_fokker_planck_study()->dict[str,Any]:
    cfg=FPConfig(); run=simulate(cfg); records=run["records"]; final=records[-1]
    masses=np.asarray([r["mass"] for r in records])
    mins=np.asarray([r["minimum"] for r in records])
    entropy=np.asarray([r["relative_entropy"] for r in records])
    analytic=analytic_moments(cfg.final_time,cfg)
    semi=ou_semigroup_error(cfg); balance=detailed_balance_error(cfg); ref=refinement()
    P=velocity_propagator(cfg.dt,cfg)
    acceptance={
      "velocity_generator_conserves_mass":float(np.max(np.abs(np.sum(velocity_generator(cfg),axis=0))))<=2e-13,
      "ou_semigroup_law_closes":semi<=3e-14,
      "ou_propagator_is_positive":float(np.min(P))>=-2e-14,
      "detailed_balance_closes":balance<=3e-14,
      "phase_space_mass_closes":float(np.max(np.abs(masses-1)))<=3e-13,
      "phase_space_positivity_preserved":float(np.min(mins))>=-2e-15,
      "relative_entropy_is_nonincreasing":bool(np.all(np.diff(entropy)<=2e-11)),
      "moments_track_ou_limit":abs(final["mean_velocity"]-analytic["mean"])<=.04 and abs(final["velocity_variance"]-analytic["variance"])<=.08,
      "timestep_refinement_improves":ref["successive_differences"][-1]<ref["successive_differences"][0],
    }
    return {
      "schema":"openwave.m9.fokker-planck-bridge.v1","task":"M9.53",
      "config":asdict(cfg),"initial":records[0],"final":final,
      "analytic_final_moments":analytic,"ou_semigroup_error":semi,
      "detailed_balance_error":balance,"refinement":ref,
      "physlib_zil_evidence":{
        "branch":"entropic-physlib-linear-full",
        "anchors":["OpenSystemLindblad.lindblad_trace_preserving",
                   "DampedHeatSemigroup.RealC0ContractionSemigroup"],
        "closes_open_target":"phase_space_fokker_planck_bridge",
        "boundary":"finite Markov/Strang bridge; continuum kinetic theorem remains open",
      },
      "acceptance":acceptance,"passed":all(acceptance.values()),
      "classification":{"establishes":[
        "positive conservative phase-space evolution","OU detailed balance and semigroup controls",
        "relative-entropy decay","finite phase-space bridge from dissipative dynamics"],
        "does_not_establish":["continuum hypoelliptic well-posedness",
        "derivation from the full CAT/EPT density matrix","physical transport coefficients"]},
    }

def result_to_json(result:dict[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"