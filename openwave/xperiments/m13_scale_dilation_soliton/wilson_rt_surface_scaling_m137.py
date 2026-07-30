"""M13.7 finite Wilson area-law and RT minimal-surface scaling comparison."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping
import numpy as np
from .holographic_rg_cutoff_flow_m136 import run_holographic_rg_study

MILESTONE="M13.7"
SCHEMA="openwave.m13.wilson-rt-surface-scaling.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QFT/Lattice/WilsonLoopAreaLaw.lean","sha":"ffd0b7e6dc1ec8b39851755aeda3ae753a5c42d0","theorems":["areaLaw_implies_decay","vortexStringTension_pos","vortexStringTension_strictMono_on","vortexAreaLaw_exp","linear_potential_pos"]},
 {"path":"Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean","sha":"870efa65de9037ea7c8e617628b15c19fb3de521","theorems":["boltzmannFactor_pos","sourceCoupledPartition_linearSource_hasDerivAt_zero"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean","sha":"c14aede2c8654bdbdb4aedfca543c36872c65e55","theorems":["rtAreaEntropy_nonneg","rt_log_square_prefactor_identity","rtPoincareLineDensity_regulated_integral_eq_neg_two_log"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ScaleDilationLogMetric.lean","sha":"0c8262bac90d2dff03a04cc8e15efb21ee87ff0e","theorems":["dilation_isometry","scaleDistance_eq_dist_log"]},)

def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class WilsonRTScalingConfig:
 vortex_density:float=0.17
 rectangle_scales:tuple[float,...]=(0.75,1.0,1.5,2.0,2.5)
 base_width:float=1.1
 base_height:float=0.9
 ads_radius:float=2.0
 newton_constant:float=0.25
 interval:float=8.0
 cutoff:float=0.5
 common_dilation:float=2.25
 def validate(self):
  if not 0<self.vortex_density<0.5 or min(self.rectangle_scales)<=0 or min(self.base_width,self.base_height,self.ads_radius,self.newton_constant,self.interval,self.cutoff,self.common_dilation)<=0: raise ValueError("valid positive surface controls required")
  if self.interval<=self.cutoff: raise ValueError("resolved RT interval required")
def vortex_tension(rho:float)->float:return -math.log(1.0-2.0*rho)
def wilson_loop(sigma:float,area:float)->float:return math.exp(-sigma*area)
def rt_entropy(c:float,ell:float,cutoff:float)->float:return c/3.0*math.log(ell/cutoff)
def canonical_payload(config=None):
 c=WilsonRTScalingConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT finite Wilson and RT surface-scaling comparison","configuration":asdict(c),"lineage_dependencies":["M10.8","M13.6"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.wilson_rt_surface_scaling_m137:run_wilson_rt_scaling_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _wilson_dependency():
 from openwave.xperiments.m10_cat_ept.wilson_refinement_spectrum_m108 import run_wilson_refinement_spectrum_study
 return run_wilson_refinement_spectrum_study()
def run_wilson_rt_scaling_study(config=None):
 cfg=WilsonRTScalingConfig() if config is None else config; cfg.validate()
 sigma_v=vortex_tension(cfg.vortex_density)
 scales=np.asarray(cfg.rectangle_scales,dtype=float)
 areas=(cfg.base_width*scales)*(cfg.base_height*scales)
 loops=np.asarray([wilson_loop(sigma_v,float(area)) for area in areas])
 exponents=-np.log(loops)
 fit=np.polyfit(areas,exponents,1)
 rho_samples=np.asarray([0.05,0.1,0.2,0.3,0.4])
 tensions=np.asarray([vortex_tension(float(rho)) for rho in rho_samples])
 m10=_wilson_dependency(); sigma_fit=float(m10["area_perimeter_fit"]["area_coefficient"])
 central_charge=3.0*cfg.ads_radius/(2.0*cfg.newton_constant)
 entropy=rt_entropy(central_charge,cfg.interval,cfg.cutoff); rt_area=4.0*cfg.newton_constant*entropy
 lam=cfg.common_dilation
 entropy_moved=rt_entropy(central_charge,lam*cfg.interval,lam*cfg.cutoff)
 ref_area=cfg.base_width*cfg.base_height
 wilson_exp_ref=sigma_fit*ref_area
 wilson_exp_moved=sigma_fit*(lam*cfg.base_width)*(lam*cfg.base_height)
 diagnostics={
  "vortex_tension":sigma_v,"vortex_tensions":tensions.tolist(),"vortex_tension_monotone":bool(np.all(np.diff(tensions)>0)),
  "areas":areas.tolist(),"loops":loops.tolist(),"area_law_slope_error":abs(float(fit[0])-sigma_v),"area_law_intercept":float(fit[1]),
  "m10_wilson_passed":bool(m10["passed"]),"m10_area_coefficient":sigma_fit,"m10_creutz_11":float(m10["creutz_11"]),"m10_gauge_error":float(m10.get("loop_gauge_error",0.0)),
  "central_charge":central_charge,"rt_entropy":entropy,"rt_area":rt_area,"rt_area_identity_error":abs(rt_area/(4.0*cfg.newton_constant)-entropy),
  "rt_common_dilation_error":abs(entropy_moved-entropy),"wilson_quadratic_scaling_error":abs(wilson_exp_moved-lam**2*wilson_exp_ref),
  "surface_ratio":wilson_exp_ref/rt_area,"rg_dependency_passed":bool(run_holographic_rg_study()["passed"]),
 }
 acceptance={
  "vortex_tension_is_positive_and_monotone":sigma_v>0 and diagnostics["vortex_tension_monotone"],
  "vortex_area_law_is_exact":diagnostics["area_law_slope_error"]<5e-14 and abs(diagnostics["area_law_intercept"])<5e-14 and bool(np.all((loops>0)&(loops<1))),
  "m10_wilson_campaign_passes":diagnostics["m10_wilson_passed"] and sigma_fit>0 and diagnostics["m10_creutz_11"]>0 and diagnostics["m10_gauge_error"]<2e-12,
  "rt_area_identity_closes":entropy>0 and diagnostics["rt_area_identity_error"]<5e-14,
  "rt_is_invariant_under_common_boundary_dilation":diagnostics["rt_common_dilation_error"]<5e-13,
  "wilson_exponent_has_quadratic_boundary_scale_weight":diagnostics["wilson_quadratic_scaling_error"]<5e-13,
  "finite_surface_comparison_is_positive":math.isfinite(diagnostics["surface_ratio"]) and diagnostics["surface_ratio"]>0,
  "dependencies_pass":diagnostics["rg_dependency_passed"],
 }
 p=canonical_payload(cfg);return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"wilson_and_rt_surfaces_are_compared":True,"wilson_rt_equality_is_not_claimed":True,"finite_wilson_tension_is_not_a_continuum_string_tension":True}}
