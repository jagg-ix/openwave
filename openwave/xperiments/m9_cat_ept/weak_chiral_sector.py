"""Reduced weak/chiral transition simulation control.

A two-flavor, two-chirality state has left-sector flavor mixing and positive
left-selective decay into a reservoir. This is not electroweak theory.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
import json, math
from typing import Any
import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm
ComplexVector=NDArray[np.complex128]

@dataclass(frozen=True)
class WeakConfig:
    flavor_mixing:float=.55; flavor_detuning:float=.18; left_decay_rate:float=.22; chirality_mixing:float=0.; final_time:float=18.; steps:int=900
    def __post_init__(self)->None:
        if self.flavor_mixing<0 or self.left_decay_rate<0: raise ValueError("nonnegative mixing and decay required")
        if self.final_time<=0 or self.steps<2: raise ValueError("positive evolution interval required")

def generator(cfg:WeakConfig)->NDArray[np.complex128]:
    h=np.zeros((4,4),dtype=np.complex128); h[0,0]=cfg.flavor_detuning; h[1,1]=-cfg.flavor_detuning; h[0,1]=h[1,0]=cfg.flavor_mixing; h[2,2]=cfg.flavor_detuning; h[3,3]=-cfg.flavor_detuning; h[0,2]=h[2,0]=cfg.chirality_mixing; h[1,3]=h[3,1]=cfg.chirality_mixing
    gamma=np.diag([cfg.left_decay_rate,cfg.left_decay_rate,0.,0.]).astype(np.complex128)
    return -1j*h-.5*gamma
def basis_state(index:int)->ComplexVector:
    if index not in range(4): raise ValueError("basis index must be 0..3")
    state=np.zeros(4,dtype=np.complex128); state[index]=1.; return state
def evolve(initial:ComplexVector,cfg:WeakConfig=WeakConfig())->dict[str,Any]:
    initial=np.asarray(initial,dtype=np.complex128)
    if initial.shape!=(4,): raise ValueError("four-component state required")
    norm=float(np.vdot(initial,initial).real)
    if norm<=0: raise ValueError("nonzero state required")
    state=initial/math.sqrt(norm); dt=cfg.final_time/cfg.steps; propagator=expm(generator(cfg)*dt); reservoir=0.; records=[]
    for step in range(cfg.steps+1):
        p=np.abs(state)**2; matter=float(np.sum(p)); records.append({"time":step*dt,"e_left":float(p[0]),"mu_left":float(p[1]),"e_right":float(p[2]),"mu_right":float(p[3]),"matter":matter,"reservoir":reservoir,"balance":matter+reservoir})
        if step<cfg.steps:
            before=float(np.vdot(state,state).real); state=propagator@state; after=float(np.vdot(state,state).real); reservoir+=before-after
    return {"state":state,"records":records,"final":records[-1]}
def zero_decay_unitary_control()->dict[str,float]:
    run=evolve(basis_state(0),WeakConfig(left_decay_rate=0.)); return {"balance_error":max(abs(r["balance"]-1) for r in run["records"]),"maximum_mu_left":max(r["mu_left"] for r in run["records"])}
def chiral_selectivity_control()->dict[str,Any]:
    cfg=WeakConfig(flavor_mixing=0.,flavor_detuning=0.); left=evolve(basis_state(0),cfg); right=evolve(basis_state(2),cfg)
    return {"left_final_matter":left["final"]["matter"],"left_final_reservoir":left["final"]["reservoir"],"right_final_matter":right["final"]["matter"],"right_final_reservoir":right["final"]["reservoir"]}
def timestep_refinement()->dict[str,Any]:
    steps=(225,450,900,1800); values=[]
    for count in steps:
        f=evolve(basis_state(0),WeakConfig(steps=count))["final"]; values.append((f["e_left"],f["mu_left"],f["reservoir"]))
    differences=[float(np.linalg.norm(np.asarray(values[i])-np.asarray(values[i+1]))) for i in range(3)]
    return {"steps":steps,"final_values":values,"successive_differences":differences}
@lru_cache(maxsize=1)
def run_weak_chiral_study()->dict[str,Any]:
    cfg=WeakConfig(); run=evolve(basis_state(0),cfg); records=run["records"]; chiral=chiral_selectivity_control(); unitary=zero_decay_unitary_control(); refinement=timestep_refinement(); maximum_mu=max(r["mu_left"] for r in records); balance=max(abs(r["balance"]-1) for r in records); reservoir=np.asarray([r["reservoir"] for r in records]); zero=evolve(basis_state(0),WeakConfig(flavor_mixing=0.,flavor_detuning=0.))
    acceptance={"left_flavor_transition_occurs":maximum_mu>=.15,"decay_reservoir_balance_closes":balance<=2e-13,"reservoir_is_monotone":bool(np.all(np.diff(reservoir)>=-2e-14)),"right_chiral_state_is_inert":abs(chiral["right_final_matter"]-1)<=2e-13 and chiral["right_final_reservoir"]<=2e-13,"left_chiral_state_decays":chiral["left_final_matter"]<.05 and chiral["left_final_reservoir"]>.95,"zero_flavor_mixing_blocks_transition":max(r["mu_left"] for r in zero["records"])<=1e-15,"zero_decay_is_unitary_and_mixes":unitary["balance_error"]<=2e-13 and unitary["maximum_mu_left"]>=.5,"exact_step_refinement_stabilizes":max(refinement["successive_differences"])<=5e-13}
    return {"schema":"openwave.m9.weak-chiral-result.v1","task":"M9.41","config":asdict(cfg),"maximum_mu_left_population":maximum_mu,"final":run["final"],"maximum_balance_error":balance,"chiral_selectivity":chiral,"zero_decay_control":unitary,"refinement":refinement,"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["left-selective flavor-transition control","positive decay-to-reservoir ledger","right-chiral inert control","unitary zero-decay reduction","zero-mixing transition rejection"],"does_not_establish":["electroweak gauge theory","W or Z bosons","physical decay rates or cross sections","parity violation emerging from CAT/EPT fields"]}}
def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
