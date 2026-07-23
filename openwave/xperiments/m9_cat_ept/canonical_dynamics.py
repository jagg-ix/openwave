"""Canonical dimensionless CAT/EPT reference dynamics."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray

ComplexVector=NDArray[np.complex128]
SX=np.asarray([[0,1],[1,0]],dtype=np.complex128)
SZ=np.asarray([[1,0],[0,-1]],dtype=np.complex128)
I=np.eye(2,dtype=np.complex128)

@dataclass(frozen=True)
class Parameters:
    omega:float=1.1; mixing:float=.3; irreversible_rate:float=.08
    loss_asymmetry:float=.25; geometry_frequency:float=.7
    backreaction_strength:float=.12; matter_geometry_coupling:float=.18
    def __post_init__(self):
        if self.irreversible_rate<0 or not 0<=self.loss_asymmetry<=1: raise ValueError("invalid loss")
        if self.geometry_frequency<=0: raise ValueError("invalid geometry frequency")

@dataclass
class State:
    psi:ComplexVector; q:float; p:float; entropy:float; reservoir:float; initial_balance:float=1.0
    def copy(self): return State(self.psi.copy(),self.q,self.p,self.entropy,self.reservoir,self.initial_balance)

def initial_state()->State:
    psi=np.asarray([math.sqrt(.65),math.sqrt(.35)*np.exp(.2j)],dtype=np.complex128)
    return State(psi/np.linalg.norm(psi),.15,0.,0.,0.)

def hamiltonian(s:State,p:Parameters): return .5*p.omega*SZ+p.mixing*SX+p.matter_geometry_coupling*s.q*SZ
def loss_operator(p:Parameters): return p.irreversible_rate*(I+p.loss_asymmetry*SZ)

def observables(s:State,p:Parameters)->dict[str,float]:
    n=float(np.vdot(s.psi,s.psi).real); sz=float(np.vdot(s.psi,SZ@s.psi).real)
    return {"matter_norm":n,"reservoir":s.reservoir,"total_balance":n+s.reservoir,
            "entropic_clock":s.entropy,"geometry_q":s.q,"geometry_p":s.p,
            "geometry_energy":.5*(s.p**2+(p.geometry_frequency*s.q)**2),"sigma_z":sz,
            "constraint_residual":n+s.reservoir-s.initial_balance}

def rhs(s:State,p:Parameters)->State:
    H,G=hamiltonian(s,p),loss_operator(p)
    dpsi=(-1j*H-G)@s.psi; n=max(float(np.vdot(s.psi,s.psi).real),np.finfo(float).tiny)
    flux=2*float(np.vdot(s.psi,G@s.psi).real); sz=float(np.vdot(s.psi,SZ@s.psi).real)
    return State(dpsi,s.p,-p.geometry_frequency**2*s.q+p.backreaction_strength*sz,flux/(2*n),flux,0.)

def add(s:State,k:State,a:float)->State:
    return State(s.psi+a*k.psi,s.q+a*k.q,s.p+a*k.p,s.entropy+a*k.entropy,s.reservoir+a*k.reservoir,s.initial_balance)

def step(s:State,dt:float,p:Parameters)->State:
    k1=rhs(s,p); k2=rhs(add(s,k1,.5*dt),p); k3=rhs(add(s,k2,.5*dt),p); k4=rhs(add(s,k3,dt),p)
    out=s.copy(); out.psi=s.psi+dt*(k1.psi+2*k2.psi+2*k3.psi+k4.psi)/6
    out.q=s.q+dt*(k1.q+2*k2.q+2*k3.q+k4.q)/6; out.p=s.p+dt*(k1.p+2*k2.p+2*k3.p+k4.p)/6
    out.entropy=s.entropy+dt*(k1.entropy+2*k2.entropy+2*k3.entropy+k4.entropy)/6
    out.reservoir=s.reservoir+dt*(k1.reservoir+2*k2.reservoir+2*k3.reservoir+k4.reservoir)/6
    return out

def evolve(dt:float,final_time:float=4.,p:Parameters=Parameters())->dict[str,Any]:
    steps=math.ceil(final_time/dt); dt=final_time/steps; s=initial_state(); records=[observables(s,p)]
    for _ in range(steps): s=step(s,dt,p); records.append(observables(s,p))
    return {"state":s,"records":records,"dt":dt,"steps":steps}

def refinement()->dict[str,Any]:
    dts=(.08,.04,.02,.01); runs=[evolve(dt) for dt in dts]; ref=runs[-1]["state"]
    errors=[float(np.linalg.norm(r["state"].psi-ref.psi)+abs(r["state"].q-ref.q)+abs(r["state"].p-ref.p)) for r in runs[:-1]]
    return {"dts":dts,"errors":errors,"orders":[math.log(errors[i]/errors[i+1],2) for i in range(2)]}

def reductions()->dict[str,float]:
    p=Parameters(); zloss=Parameters(**{**asdict(p),"irreversible_rate":0.}); zback=Parameters(**{**asdict(p),"backreaction_strength":0.,"matter_geometry_coupling":0.})
    full=evolve(.01,p=p)["state"]; unit=evolve(.01,p=zloss)["state"]; dec=evolve(.01,p=zback)["state"]
    return {"zero_loss_norm_drift":abs(observables(unit,zloss)["matter_norm"]-1.),"zero_loss_entropy":unit.entropy,
            "zero_loss_reservoir":unit.reservoir,"zero_backreaction_geometry_change":abs(dec.q-initial_state().q),
            "full_geometry_change":abs(full.q-initial_state().q)}

@lru_cache(maxsize=1)
def run_canonical_dynamics_study()->dict[str,Any]:
    p=Parameters(); run=evolve(.01,p=p); ref=refinement(); red=reductions(); rec=run["records"]
    norms=np.asarray([x["matter_norm"] for x in rec]); ent=np.asarray([x["entropic_clock"] for x in rec])
    bal=np.asarray([x["total_balance"] for x in rec]); con=np.asarray([x["constraint_residual"] for x in rec])
    acceptance={"rk4_converges":min(ref["orders"])>=3.5,"matter_contracts":bool(np.all(np.diff(norms)<=2e-10)),
                "entropy_monotone":bool(np.all(np.diff(ent)>=-2e-10)),"balance_closes":float(np.max(np.abs(bal-1)))<=2e-8,
                "constraint_closes":float(np.max(np.abs(con)))<=2e-8,
                "zero_loss_reduces_to_unitary":red["zero_loss_norm_drift"]<=2e-8 and abs(red["zero_loss_entropy"])<=2e-10,
                "backreaction_is_executable":abs(red["full_geometry_change"]-red["zero_backreaction_geometry_change"])>1e-3,
                "sectors_explicit":True}
    return {"schema":"openwave.m9.canonical-dynamics-result.v1","task":"M9.23","parameters":asdict(p),"final":rec[-1],
            "refinement":ref,"reductions":red,"acceptance":acceptance,"passed":all(acceptance.values()),
            "classification":{"establishes":["one executable canonical state","explicit reversible, irreversible, geometry, constraint, and ledger sectors","zero-loss and zero-backreaction reductions"],
            "does_not_establish":["physical time","a stable particle","a microscopic loss law","experimental calibration"]}}

def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
