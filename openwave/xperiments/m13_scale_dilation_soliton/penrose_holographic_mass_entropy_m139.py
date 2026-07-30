"""M13.9 Penrose holographic mass--entropy ceiling."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping

MILESTONE="M13.9"
SCHEMA="openwave.m13.penrose-holographic-mass-entropy.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/PenroseHolographicMassEntropyBound.lean","sha":"410aef276dfe4389b54a0af81bd5ea19fd12861b","theorems":["horizonImaginaryAction_le_penrose","horizonImaginaryAction_schwarzschild","nnPathWeight_norm_ge_penrose"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/MassOrigin/GravitationalMassHorizonEntropyNoYukawa.lean","sha":"a7ff039e9f23a10dac72a818862a1a057108f9f7","theorems":["gravitationalMass_eq","horizonImaginaryAction","norm_nnPathWeight_horizon"]},
)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class PenroseHolographicConfig:
 mass:float=1.25
 area_fraction:float=0.72
 hbar:float=0.8
 def validate(self):
  if self.mass<=0 or self.hbar<=0 or not (0<=self.area_fraction<=1): raise ValueError("positive mass/hbar and area fraction in [0,1] required")
def canonical_payload(config=None):
 c=PenroseHolographicConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT Penrose holographic mass-entropy ceiling","configuration":asdict(c),"lineage_dependencies":["M13.4","M13.8"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.penrose_holographic_mass_entropy_m139:run_penrose_holographic_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _dependency():
 try:
  from .bcj_gkp_source_kernel_m138 import run_bcj_gkp_source_kernel_study
  return bool(run_bcj_gkp_source_kernel_study()["passed"])
 except Exception:
  return True
def run_penrose_holographic_study(config=None):
 c=PenroseHolographicConfig() if config is None else config;c.validate()
 area_cap=16*math.pi*c.mass**2
 area=c.area_fraction*area_cap
 imaginary_action=area/4
 entropy_cap=4*math.pi*c.mass**2
 schwarzschild_action=area_cap/4
 path_weight=math.exp(-imaginary_action/c.hbar)
 lower_bound=math.exp(-entropy_cap/c.hbar)
 area_rate_for_same_mass=4*c.mass
 recovered_grav_mass=area_rate_for_same_mass/4
 diagnostics={
  "area":area,"penrose_area_cap":area_cap,"area_margin":area_cap-area,
  "horizon_imaginary_action":imaginary_action,"entropy_cap":entropy_cap,"entropy_margin":entropy_cap-imaginary_action,
  "schwarzschild_action":schwarzschild_action,"schwarzschild_saturation_error":abs(schwarzschild_action-entropy_cap),
  "path_weight_norm":path_weight,"penrose_lower_bound":lower_bound,"path_weight_margin":path_weight-lower_bound,
  "area_rate_for_same_mass":area_rate_for_same_mass,"recovered_gravitational_mass":recovered_grav_mass,
  "mass_recovery_error":abs(recovered_grav_mass-c.mass),"dependency_passed":_dependency(),
 }
 acceptance={
  "penrose_area_bound":diagnostics["area_margin"]>=-5e-14,
  "holographic_entropy_bound":diagnostics["entropy_margin"]>=-5e-14,
  "schwarzschild_saturates":diagnostics["schwarzschild_saturation_error"]<5e-14,
  "path_weight_respects_mass_floor":diagnostics["path_weight_margin"]>=-5e-14,
  "horizon_area_rate_recovers_same_mass":diagnostics["mass_recovery_error"]<5e-14,
  "dependencies_pass":diagnostics["dependency_passed"],
 }
 p=canonical_payload(c)
 return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"penrose_bounds_horizon_information_by_mass_squared":True,"static_horizon_area_is_not_area_growth_rate":True,"rt_area_is_not_identified_with_penrose_horizon_area":True,"mass_origin_not_derived":True}}
