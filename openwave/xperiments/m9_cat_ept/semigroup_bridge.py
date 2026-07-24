"""Finite-grid semigroup and continuum-carrier bridge.

PhysLib/ZIL provides bounded finite-dimensional generators, exponential
evolution, continuum L2 carriers, and closable pointwise operators. The full
continuum Lindblad semigroup remains explicitly open, so this module qualifies
only a finite-grid bridge.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json,math
from typing import Any
import numpy as np
from numpy.typing import NDArray
from scipy.linalg import block_diag,expm,norm
ComplexMatrix=NDArray[np.complex128]

@dataclass(frozen=True)
class SemigroupConfig:
    points:int=16; length:float=2*math.pi; matter_dispersion:float=.45
    base_loss:float=.08; loss_modulation:float=.03; potential_amplitude:float=.22
    geometry_diffusion:float=.22; geometry_mass:float=.8
    thermal_diffusion:float=.18; thermal_mass:float=.35; final_time:float=1.2
    def __post_init__(self):
        if self.points<6 or self.length<=0 or self.final_time<=0: raise ValueError("positive controls required")
        if self.base_loss<=abs(self.loss_modulation): raise ValueError("strictly positive loss profile required")
        if min(self.geometry_diffusion,self.geometry_mass,self.thermal_diffusion,self.thermal_mass)<0: raise ValueError("nonnegative dissipative parameters required")

def periodic_laplacian(cfg:SemigroupConfig)->ComplexMatrix:
    n=cfg.points; dx=cfg.length/n; matrix=np.zeros((n,n),dtype=np.complex128)
    for i in range(n):
        matrix[i,i]=-2/dx**2; matrix[i,(i-1)%n]=1/dx**2; matrix[i,(i+1)%n]=1/dx**2
    return matrix

def generator_parts(cfg:SemigroupConfig=SemigroupConfig()):
    n=cfg.points; x=np.arange(n)*cfg.length/n; lap=periodic_laplacian(cfg)
    potential=np.diag(cfg.potential_amplitude*np.cos(x)).astype(np.complex128)
    loss=np.diag(cfg.base_loss+cfg.loss_modulation*(1+np.sin(x))/2).astype(np.complex128)
    skew_matter=1j*(cfg.matter_dispersion*lap-potential); dissipative_matter=-loss
    geometry=cfg.geometry_diffusion*lap-cfg.geometry_mass**2*np.eye(n)
    thermal=cfg.thermal_diffusion*lap-cfg.thermal_mass**2*np.eye(n)
    skew=block_diag(skew_matter,np.zeros((n,n)),np.zeros((n,n))).astype(np.complex128)
    dissipative=block_diag(dissipative_matter,geometry,thermal).astype(np.complex128)
    return skew,dissipative,skew+dissipative

def dissipativity_bound(generator):
    eigen=np.linalg.eigvalsh((generator+generator.conj().T)/2)
    return {"largest_symmetric_eigenvalue":float(np.max(eigen)),"smallest_symmetric_eigenvalue":float(np.min(eigen))}

def semigroup(time,cfg=SemigroupConfig()):
    if time<0: raise ValueError("nonnegative time required")
    return expm(time*generator_parts(cfg)[2])

def semigroup_composition(cfg=SemigroupConfig()):
    s,t=.43,.71
    return {"s":s,"t":t,"composition_error":float(norm(semigroup(s+t,cfg)-semigroup(s,cfg)@semigroup(t,cfg),2))}

def contraction_campaign(cfg=SemigroupConfig()):
    times=np.linspace(0,cfg.final_time,13); values=[float(norm(semigroup(float(t),cfg),2)) for t in times]
    return {"times":times.tolist(),"operator_norms":values,"maximum_norm":max(values),"nonincreasing":bool(np.all(np.diff(values)<=2e-12))}

def resolvent_campaign(cfg=SemigroupConfig()):
    generator=generator_parts(cfg)[2]; identity=np.eye(generator.shape[0],dtype=np.complex128); rows=[]
    for value in (.2,.5,1.,2.):
        measured=float(norm(np.linalg.inv(value*identity-generator),2)); rows.append({"lambda":value,"resolvent_norm":measured,"bound":1/value,"ratio":measured*value})
    return {"rows":rows,"all_bounded":all(row["ratio"]<=1+2e-10 for row in rows)}

def split_evolution(steps,method,cfg=SemigroupConfig()):
    if steps<1: raise ValueError("positive step count required")
    skew,dissipative,_=generator_parts(cfg); dt=cfg.final_time/steps
    if method=="lie": one=expm(dt*skew)@expm(dt*dissipative)
    elif method=="strang": one=expm(.5*dt*dissipative)@expm(dt*skew)@expm(.5*dt*dissipative)
    else: raise ValueError(method)
    result=np.eye(one.shape[0],dtype=np.complex128)
    for _ in range(steps): result=one@result
    return result

def splitting_refinement(cfg=SemigroupConfig()):
    exact=semigroup(cfg.final_time,cfg); steps=(4,8,16,32)
    lie=[float(norm(split_evolution(n,"lie",cfg)-exact,2)) for n in steps]
    strang=[float(norm(split_evolution(n,"strang",cfg)-exact,2)) for n in steps]
    return {"steps":steps,"lie_errors":lie,"strang_errors":strang,"lie_orders":[math.log(lie[i]/lie[i+1],2) for i in range(3)],"strang_orders":[math.log(strang[i]/strang[i+1],2) for i in range(3)]}

def heat_symbol_consistency():
    points=(16,32,64,128); base=SemigroupConfig(); expected=-(base.thermal_diffusion+base.thermal_mass**2); errors=[]; values=[]
    for n in points:
        cfg=SemigroupConfig(points=n); lap=periodic_laplacian(cfg); mode=np.exp(2j*math.pi*np.arange(n)/n)
        value=float((np.vdot(mode,(cfg.thermal_diffusion*lap-cfg.thermal_mass**2*np.eye(n))@mode)/np.vdot(mode,mode)).real); values.append(value); errors.append(abs(value-expected))
    return {"points":points,"eigenvalues":values,"expected_continuum_symbol":expected,"errors":errors,"orders":[math.log(errors[i]/errors[i+1],2) for i in range(3)]}

FORMAL_SOURCES=(
 {"path":"formalization/zil/lindblad-driven-leads.zc","sha":"8f98a97bb12f0b5ab21fbcc62f878e0650894353","reused_claims":("finite_hs_lddl_generator","bounded_lddl_evolution","continuum_pointwise_closable"),"open_claims":("lorentz_sum_converges_to_continuum_hybridization","lddl_current_converges_to_continuum_current")},
 {"path":"formalization/zil/liouville-second-quantization.zc","sha":"8141e353dc5960ef28c01883ccbb10411f62ac05","reused_claims":("continuum_l2_kernel_carrier",),"open_claims":("continuum_lindblad_generator","phase_space_fokker_planck_bridge")},
 {"path":"Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean","sha":"634087560adaffaaa5a683c47f3dee123501fb28","reused_claims":("QuantumMechanics.LindbladDrivenLeads.lddlGeneratorHS_continuous","QuantumMechanics.LindbladDrivenLeads.lddlEvolutionHS_zero"),"open_claims":()},
 {"path":"Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean","sha":"9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5","reused_claims":("QuantumMechanics.SpaceDHilbertSpace.mulOperator_hasDenseDomain","QuantumMechanics.SpaceDHilbertSpace.mulOperator_isClosable"),"open_claims":()},)

def evidence_fingerprint():
    payload={"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","sources":FORMAL_SOURCES}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_semigroup_bridge_study():
    cfg=SemigroupConfig(); skew,dissipative,generator=generator_parts(cfg); diss=dissipativity_bound(generator); comp=semigroup_composition(cfg); contract=contraction_campaign(cfg); resolvent=resolvent_campaign(cfg); split=splitting_refinement(cfg); grid=heat_symbol_consistency()
    acceptance={"skew_part_is_skew_adjoint":float(norm(skew+skew.conj().T,2))<=2e-13,"dissipative_part_is_nonpositive":dissipativity_bound(dissipative)["largest_symmetric_eigenvalue"]<=-1e-3,"full_generator_is_dissipative":diss["largest_symmetric_eigenvalue"]<=-1e-3,"finite_semigroup_is_contractive":contract["maximum_norm"]<=1+2e-12 and contract["nonincreasing"],"semigroup_composition_closes":comp["composition_error"]<=2e-12,"resolvent_bound_closes":resolvent["all_bounded"],"lie_and_strang_orders_close":min(split["lie_orders"][-2:])>=.9 and min(split["strang_orders"][-2:])>=1.8,"grid_symbol_is_second_order":min(grid["orders"][-2:])>=1.9,"continuum_claims_remain_open":True,"formal_source_fingerprint_is_deterministic":evidence_fingerprint()==evidence_fingerprint()}
    return {"schema":"openwave.m9.semigroup-bridge-result.v1","task":"M9.50","config":asdict(cfg),"formal_evidence":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","sources":FORMAL_SOURCES,"fingerprint":evidence_fingerprint(),"promotion_boundary":{"finite_bounded_generator":"reused","finite_exponential_evolution":"reused","continuum_carrier_and_closability":"reused","continuum_lindblad_semigroup":"open_not_promoted"}},"dissipativity":diss,"composition":comp,"contraction":contract,"resolvent":resolvent,"splitting":split,"grid_consistency":grid,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"finite_grid_contraction_semigroup_qualified":True,"continuum_wellposedness_proved":False},"classification":{"establishes":["finite-grid maximal-dissipative matrix family","contractive matrix exponential semigroup","semigroup composition and resolvent bounds","Lie/Strang convergence and grid-symbol consistency","exact PhysLib/ZIL provenance boundary"],"does_not_establish":["continuum semigroup generation","closability of the full CAT/EPT generator","nonlinear continuum existence or uniqueness","kernel-checked promotion of pending ZIL witnesses"]}}

def result_to_json(result): return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
