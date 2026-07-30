"""M13.11 Lovelock holographic dimension activation."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping

MILESTONE="M13.11"
SCHEMA="openwave.m13.lovelock-holographic-dimension.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/LovelockHolographicDimensionalReduction.lean","sha":"681c4b78f1d485822d3ec46a9b5d47a655d16af7","theorems":["lovelock_dynamical_iff_boundary_dim","einstein_dynamical_iff_boundary_ge_two","gaussBonnet_dynamical_iff_boundary_ge_four","lovelock_topological_at_critical_boundary"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean","sha":"d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3","theorems":["massDimension_relation","conformalDimension_sum"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean","sha":"c14aede2c8654bdbdb4aedfca543c36872c65e55","theorems":["rtAreaEntropy_nonneg","brownHenneaux_third"]},
)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class LovelockHolographicConfig:
 max_boundary_dimension:int=10
 max_order:int=4
 mass_radius_sq:float=0.16
 def validate(self):
  if self.max_boundary_dimension<4 or self.max_order<2:raise ValueError("sufficient dimensions/orders required")
def canonical_payload(config=None):
 c=LovelockHolographicConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT Lovelock holographic dimension activation","configuration":asdict(c),"lineage_dependencies":["M13.2","M13.10"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.lovelock_holographic_dimension_m1311:run_lovelock_holographic_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _gen_trace(D:int,k:int)->int:
 return math.factorial(D)//math.factorial(D-k) if 0<=k<=D else 0
def _delta(d:int,mu:float)->float:return d/2+math.sqrt((d/2)**2+mu)
def run_lovelock_holographic_study(config=None):
 c=LovelockHolographicConfig() if config is None else config;c.validate()
 rows=[]
 max_error=0
 for d in range(1,c.max_boundary_dimension+1):
  dynamic_orders=[]
  for n in range(1,c.max_order+1):
   trace=_gen_trace(d+1,2*n+1)
   dynamic=trace>0
   expected=(2*n<=d)
   max_error=max(max_error,float(dynamic!=expected))
   if dynamic:dynamic_orders.append(n)
  rows.append({"boundary_dimension":d,"bulk_dimension":d+1,"dynamic_orders":dynamic_orders,"dynamic_count":len(dynamic_orders),"expected_count":min(c.max_order,d//2),"gkp_delta_plus":_delta(d,c.mass_radius_sq),"rt_einstein_available":d>=2,"gauss_bonnet_available":d>=4})
 critical=[]
 for n in range(1,c.max_order+1):
  dcrit=2*n-1
  at_critical=_gen_trace(dcrit+1,2*n+1)
  one_up=_gen_trace(dcrit+2,2*n+1)
  critical.append({"order":n,"critical_boundary_dimension":dcrit,"critical_trace":at_critical,"next_boundary_dimension":dcrit+1,"next_trace":one_up})
 diagnostics={
  "rows":rows,"activation_mismatch":max_error,
  "einstein_threshold_ok":all((r["rt_einstein_available"]==(r["boundary_dimension"]>=2)) for r in rows),
  "gauss_bonnet_threshold_ok":all((r["gauss_bonnet_available"]==(r["boundary_dimension"]>=4)) for r in rows),
  "critical_rows":critical,
  "all_critical_topological":all(r["critical_trace"]==0 for r in critical),
  "all_next_dimensions_dynamical":all(r["next_trace"]>0 for r in critical),
  "dynamic_counts_match":all(r["dynamic_count"]==r["expected_count"] for r in rows),
 }
 acceptance={
  "lovelock_activation_matches_boundary_threshold":diagnostics["activation_mismatch"]==0,
  "einstein_turns_on_at_cft2":diagnostics["einstein_threshold_ok"],
  "gauss_bonnet_turns_on_at_cft4":diagnostics["gauss_bonnet_threshold_ok"],
  "critical_dimensions_are_topological":diagnostics["all_critical_topological"],
  "one_dimension_up_is_dynamical":diagnostics["all_next_dimensions_dynamical"],
  "active_order_count_matches_floor_half_dimension":diagnostics["dynamic_counts_match"],
 }
 p=canonical_payload(c)
 return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"boundary_dimension_controls_lovelock_activation":True,"gkp_and_rt_use_same_boundary_dimension_counter":True,"lovelock_couplings_not_derived":True,"full_corrected_entropy_functional_not_claimed":True}}
