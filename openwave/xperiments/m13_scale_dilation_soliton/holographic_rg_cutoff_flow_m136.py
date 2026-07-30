"""M13.6 finite free-scalar Hamiltonian RG and RT cutoff flow."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from hashlib import sha256
import json,math
from typing import Any,Mapping
import numpy as np
MILESTONE="M13.6";SCHEMA="openwave.m13.holographic-rg-cutoff-flow.v1";FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QFT/HamiltonianRenormalisation/FreeScalarCovarianceFlow.lean","sha":"7d878d9658f0c7f191fdd9a02ec682757b1c9767","theorems":["covariance_flow_step","fixedPoint_covariance_flow"]},
 {"path":"Physlib/QFT/HamiltonianRenormalisation/DirectHamiltonianFlow.lean","sha":"b75e77e371938663ac744b52efff2018f31d0925","theorems":["gaussianWeyl_flow","covariance_fixedPoint_automatic","couplingFunction_tendsto_one","couplingFunction_tendsto_zero"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ScaleDilationLogMetric.lean","sha":"0c8262bac90d2dff03a04cc8e15efb21ee87ff0e","theorems":["blockspin_ladder","scaleDistance_eq_dist_log"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean","sha":"c14aede2c8654bdbdb4aedfca543c36872c65e55","theorems":["brownHenneaux_third","cftEntropyVacuumLine_strongSubadditivity"]},)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class HolographicRGConfig:
 levels:int=7;epsilon0:float=1.;q:float=1.4;t0:float=1.1;image_modes:tuple[int,...]=(1,2,3);ads_radius:float=2.;newton_constant:float=.25;interval:float=12.;cutoff0:float=1.
 def validate(self):
  if self.levels<4 or min(self.epsilon0,self.q,self.t0,self.ads_radius,self.newton_constant,self.interval,self.cutoff0)<=0 or self.interval<=self.cutoff0 or any(n==0 for n in self.image_modes):raise ValueError("invalid M13.6 controls")
def _abc(q):return math.cosh(q),q*math.cosh(q)-math.sinh(q),math.sinh(q)-q
def _cov(e,q,t):
 a,b,c=_abc(q);return e*e/q**3*(b+c*math.cos(t))/(a-math.cos(t))
def _flow_cov(e,q,t):
 a,b,c=_abc(q/2);ct=math.cos(t/2);p=(e/2)**2/(q/2)**3
 return .5*p*((b+c*ct)/(a-ct)*(1+ct)+(b-c*ct)/(a+ct)*(1-ct))
def canonical_payload(config=None):
 c=HolographicRGConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT free-scalar Hamiltonian RG and RT cutoff flow","configuration":asdict(c),"lineage_dependencies":["M13.5"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.holographic_rg_cutoff_flow_m136:run_holographic_rg_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _dependency():
 from .bcj_yukawa_holographic_synthesis_m135 import run_bcj_yukawa_holographic_study
 return bool(run_bcj_yukawa_holographic_study()["passed"])
def run_holographic_rg_study(config=None):
 c=HolographicRGConfig() if config is None else config;c.validate();a,b,d=_abc(c.q);A,B,C=_abc(c.q/2)
 rec=max(abs(a-(2*A*A-1)),abs(b-2*(2*A*B+B+C+A*C)),abs(d-2*(B+C+A*C)));cov=abs(_cov(c.epsilon0,c.q,c.t0)-_flow_cov(c.epsilon0,c.q,c.t0))
 M=np.array([[1.4,.2,.1],[.2,1.1,-.05],[.1,-.05,.9]]);I=np.array([[1.,0.],[.5,.5],[0.,1.]]);f=np.array([.7,-.4]);gauss=abs(math.exp(-.25*(I@f)@M@(I@f))-math.exp(-.25*f@(I.T@M@I)@f))
 ts=np.array([c.t0/2**k for k in range(c.levels)]);principal=2*(1-np.cos(ts))/ts**2;pe=np.abs(principal-1);images={str(n):2*(1-np.cos(ts))/(ts+2*math.pi*n)**2 for n in c.image_modes}
 charge=3*c.ads_radius/(2*c.newton_constant);cuts=np.array([c.cutoff0/2**k for k in range(c.levels)]);S=charge/3*np.log(c.interval/cuts)
 diag={"fixed_point_recursion_error":rec,"fixed_point_covariance_error":cov,"gaussian_pullback_error":gauss,"principal_values":principal.tolist(),"principal_last_error":float(pe[-1]),"principal_errors_decrease":bool(np.all(np.diff(pe)<0)),"image_values":{k:v.tolist() for k,v in images.items()},"image_last_max":float(max(abs(v[-1]) for v in images.values())),"image_errors_decrease":bool(all(np.all(np.diff(np.abs(v))<0) for v in images.values())),"cutoffs":cuts.tolist(),"entropies":S.tolist(),"scale_step_error":float(np.max(np.abs(np.log(cuts[:-1]/cuts[1:])-math.log(2)))),"entropy_step_error":float(np.max(np.abs(np.diff(S)-charge/3*math.log(2)))),"dependency_passed":_dependency()}
 acc={"free_scalar_covariance_fixed_point":max(rec,cov)<5e-13,"gaussian_measure_pullback":gauss<5e-14,"principal_mode_survives":diag["principal_errors_decrease"] and diag["principal_last_error"]<2e-4,"image_modes_freeze":diag["image_errors_decrease"] and diag["image_last_max"]<2e-5,"cutoff_steps_match_scale_metric":diag["scale_step_error"]<5e-14,"rt_cutoff_response_is_linear_in_log_scale":diag["entropy_step_error"]<5e-13,"dependencies_pass":diag["dependency_passed"]}
 p=canonical_payload(c);return {**p,"task":MILESTONE,"diagnostics":diag,"acceptance":acc,"fingerprint":fingerprint(p),"passed":all(acc.values()),"decision":{"finite_free_scalar_rg_only":True,"rt_cutoff_flow_is_an_adapter":True,"interacting_rg_fixed_point_not_claimed":True,"holographic_c_theorem_not_claimed":True}}
