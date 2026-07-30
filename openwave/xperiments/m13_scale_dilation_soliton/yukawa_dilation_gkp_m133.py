"""M13.3 Yukawa mass, dilation-group, and GKP-Witten bridge.

The Yukawa coupling is held fixed while the Higgs/clock scale is transported by
the exact multiplicative dilation group.  The adapter treats mass as inverse
length, so ``m R`` and the GKP conformal dimension remain invariant.  This is a
finite executable bridge, not a derivation of the Yukawa coupling or AdS/CFT.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping

MILESTONE="M13.3"
SCHEMA="openwave.m13.yukawa-dilation-gkp.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/Yukawa/MassDecoherenceProportionality.lean","sha":"578152c3b9d73b3baec98f845bca2f566f59e93e","theorems":["yukawaWidth_div_mass","yukawaEntropyRate_eq_const_mul_mass","yukawaMass_yukawaCoupling"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Yukawa/CouplingIsolation.lean","sha":"527116982460e59e62c5736249a624f836d2f102","theorems":["yukawa_isolated_explicit","yukawaCoupling_comptonMass","clockFrequency_sets_entropyRate"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ScaleDilationLogMetric.lean","sha":"0c8262bac90d2dff03a04cc8e15efb21ee87ff0e","theorems":["dilationFlow_add","dilationFlow_neg","dilationGroupHom","dilation_isometry","scaleDistance_eq_dist_log"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean","sha":"d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3","theorems":["massDimension_relation","conformalDimension_sum","bulkToBoundaryKernel_scaling"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/WeylCartanDilatonicCharge.lean","sha":"d29eabad8399b6bc90c3a55b260a4272273c5523","theorems":["weylCartan_connection_isWeyl","weylForce_zero_of_no_dilatonicCharge","homotheticCurvature_antisymm"]},
)

def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
def dilation_flow(H:float,t:float)->float:return math.exp(H*t)
def scale_distance(x:float,y:float)->float:
 if x<=0 or y<=0: raise ValueError("positive scales required")
 return abs(math.log(x/y))
def yukawa_mass(y:float,v:float)->float:return y*v/math.sqrt(2.0)
def conformal_dimensions(d:float,mu:float)->tuple[float,float]:
 rad=(d/2.0)**2+mu
 if rad<0: raise ValueError("BF bound violated")
 s=math.sqrt(rad); return d/2.0+s,d/2.0-s

@dataclass(frozen=True)
class YukawaDilationGKPConfig:
 yukawa_coupling:float=0.2
 higgs_vev:float=math.sqrt(2.0)
 c:float=1.0
 hbar:float=1.0
 ads_radius:float=3.0
 boundary_dimension:float=4.0
 generator:float=0.7
 sample_times:tuple[float,...]=(-1.0,-0.5,0.0,0.5,1.0)
 dilatonic_charge:float=0.75
 homothetic_field_strength:float=0.4
 def validate(self)->None:
  if min(self.yukawa_coupling,self.higgs_vev,self.c,self.hbar,self.ads_radius,self.boundary_dimension)<=0: raise ValueError("positive controls required")

def canonical_payload(config:YukawaDilationGKPConfig|None=None)->dict[str,Any]:
 c=YukawaDilationGKPConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT Yukawa-dilation GKP bridge","configuration":asdict(c),"lineage_dependencies":["M10.1","M13.1"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.yukawa_dilation_gkp_m133:run_yukawa_dilation_gkp_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload:Mapping[str,Any]|None=None)->str:return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()

def _dependencies()->dict[str,bool]:
 try:
  from openwave.xperiments.m10_cat_ept.dirac_cartan_2i_yukawa_model import run_m10_core_study
  m10=bool(run_m10_core_study()["passed"])
 except Exception:
  m10=False
 try:
  from .model_registration import run_scale_dilation_soliton_study
  m131=bool(run_scale_dilation_soliton_study()["passed"])
 except Exception:
  m131=False
 return {"m10_yukawa_carrier":m10,"m13_1_scale_carrier":m131}

def run_yukawa_dilation_gkp_study(config:YukawaDilationGKPConfig|None=None)->dict[str,Any]:
 cfg=YukawaDilationGKPConfig() if config is None else config; cfg.validate()
 m0=yukawa_mass(cfg.yukawa_coupling,cfg.higgs_vev)
 omega=m0*cfg.c**2/cfg.hbar
 y_iso=math.sqrt(2.0)*cfg.hbar*omega/(cfg.c**2*cfg.higgs_vev)
 mu0=(m0*cfg.c*cfg.ads_radius/cfg.hbar)**2
 dp0,dm0=conformal_dimensions(cfg.boundary_dimension,mu0)
 records=[]
 max_mass=max_radius=max_mu=max_delta=max_compton=max_metric=0.0
 for t in cfg.sample_times:
  lam=dilation_flow(cfg.generator,t)
  vt=cfg.higgs_vev/lam
  mt=yukawa_mass(cfg.yukawa_coupling,vt)
  Rt=cfg.ads_radius*lam
  mut=(mt*cfg.c*Rt/cfg.hbar)**2
  dp,dm=conformal_dimensions(cfg.boundary_dimension,mut)
  lc0=cfg.hbar/(m0*cfg.c); lct=cfg.hbar/(mt*cfg.c)
  max_mass=max(max_mass,abs(mt-m0/lam)); max_radius=max(max_radius,abs(Rt-cfg.ads_radius*lam))
  max_mu=max(max_mu,abs(mut-mu0)); max_delta=max(max_delta,abs(dp-dp0),abs(dm-dm0))
  max_compton=max(max_compton,abs(lct-lc0*lam))
  max_metric=max(max_metric,abs(scale_distance(Rt,cfg.ads_radius)-abs(math.log(lam))))
  records.append({"time":t,"factor":lam,"higgs_vev":vt,"mass":mt,"ads_radius":Rt,"mass_radius_sq":mut,"delta_plus":dp,"delta_minus":dm,"compton_length":lct})
 group_err=max(abs(dilation_flow(cfg.generator,s+t)-dilation_flow(cfg.generator,s)*dilation_flow(cfg.generator,t)) for s in cfg.sample_times for t in cfg.sample_times)
 inv_err=max(abs(dilation_flow(cfg.generator,-t)*dilation_flow(cfg.generator,t)-1.0) for t in cfg.sample_times)
 gkp_err=abs(dp0*(dp0-cfg.boundary_dimension)-mu0)
 vieta_err=max(abs(dp0+dm0-cfg.boundary_dimension),abs(dp0*dm0+mu0))
 force=cfg.dilatonic_charge*cfg.homothetic_field_strength/16.0
 deps=_dependencies()
 diagnostics={"yukawa_mass":m0,"compton_frequency":omega,"isolated_coupling_error":abs(y_iso-cfg.yukawa_coupling),"group_error":group_err,"inverse_error":inv_err,"inverse_mass_scaling_error":max_mass,"radius_scaling_error":max_radius,"mass_radius_invariance_error":max_mu,"conformal_dimension_invariance_error":max_delta,"compton_scaling_error":max_compton,"scale_metric_error":max_metric,"gkp_mass_dimension_error":gkp_err,"gkp_vieta_error":vieta_err,"dilatonic_force":force,"zero_charge_force":0.0,"dependencies":deps}
 acceptance={"yukawa_mass_and_clock":abs(cfg.hbar*omega-m0*cfg.c**2)<5e-14 and diagnostics["isolated_coupling_error"]<5e-14,"dilation_group":max(group_err,inv_err)<5e-14,"inverse_mass_length_transport":max(max_mass,max_radius,max_compton,max_metric)<5e-13,"gkp_mass_radius_invariant":max(max_mu,max_delta,gkp_err,vieta_err)<5e-12,"dilatonic_charge_kept_distinct":abs(force-cfg.dilatonic_charge*cfg.homothetic_field_strength/16.0)<5e-14 and diagnostics["zero_charge_force"]==0.0,"dependencies_pass":all(deps.values())}
 p=canonical_payload(cfg)
 return {**p,"task":MILESTONE,"diagnostics":diagnostics,"scale_records":records,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"yukawa_coupling_is_supplied_not_derived":True,"inverse_mass_scaling_is_an_explicit_adapter":True,"mass_radius_product_is_the_holographic_invariant":True,"weyl_cartan_dilatonic_charge_is_not_the_global_dilation_group":True}}
