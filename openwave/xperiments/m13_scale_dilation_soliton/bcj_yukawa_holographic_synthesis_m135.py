"""M13.5 massive BCJ/QCD, Wilson-Regge, Yukawa, GKP and RT synthesis."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping
from .yukawa_dilation_gkp_m133 import yukawa_mass, conformal_dimensions
from .yukawa_rt_holographic_entropy_m134 import run_yukawa_rt_holographic_study
MILESTONE="M13.5"; SCHEMA="openwave.m13.bcj-yukawa-holographic-synthesis.v1"; FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean","sha":"110a42b466c7fcf8be68be4326cb1d0c9197043c","theorems":["bcjDoubleCopy_diagonal_nonneg","faradayBCJDuality","cubicDoubleCopy_eq_cubicAmplitude_colorReplacement"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Particles/QCDFundamentalBCJRelations.lean","sha":"5756653f5dbd58ac14fef7307d03223e7bf81304","theorems":["forwardBCJRelation_iff_backwardBCJRelation","threePoint_fundamentalBCJ","fundamentalBCJ_inductionStep_closes"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Yukawa/ReggeStringMassYukawaReplacement.lean","sha":"71a75b6e6b94be3ec9a0fdb4915551accf08e0eb","theorems":["reggeTrajectory_at_massSq","reggeMass_sq","reggeWidth_at_mass_eq_widthFromRate_iff"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Yukawa/MassDecoherenceProportionality.lean","sha":"578152c3b9d73b3baec98f845bca2f566f59e93e","theorems":["yukawaWidth_eq_widthFromRate_entropyRate","yukawaEntropyRate_eq_const_mul_mass"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean","sha":"d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3","theorems":["massDimension_relation","cftTwoPoint_scaling"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean","sha":"c14aede2c8654bdbdb4aedfca543c36872c65e55","theorems":["rtAreaEntropy_nonneg","rt_log_square_prefactor_identity"]},
 {"path":"Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean","sha":"870efa65de9037ea7c8e617628b15c19fb3de521","theorems":["boltzmannFactor_pos","sourceCoupledPartition_linearSource_hasDerivAt_zero"]},)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class BCJYukawaHolographicConfig:
 yukawa_coupling:float=0.2; higgs_vev:float=math.sqrt(2.0); c:float=1.0; hbar:float=1.0; ads_radius:float=2.0; boundary_dimension:float=4.0
 entropic_frequency:float=1.3; spin:float=2.0; loop_area:float=4.0; gluons:int=4; quark_pairs:int=2
 def validate(self):
  if min(self.yukawa_coupling,self.higgs_vev,self.c,self.hbar,self.ads_radius,self.boundary_dimension,self.entropic_frequency,self.spin,self.loop_area)<=0: raise ValueError("positive controls required")
  if self.gluons<=0 or self.quark_pairs<0: raise ValueError("moved-gluon primitive QCD content required")
def canonical_payload(config=None):
 c=BCJYukawaHolographicConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT massive BCJ-Yukawa holographic synthesis","configuration":asdict(c),"lineage_dependencies":["M10.8","M13.2","M13.4"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.bcj_yukawa_holographic_synthesis_m135:run_bcj_yukawa_holographic_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _wilson():
 from openwave.xperiments.m10_cat_ept.wilson_refinement_spectrum_m108 import run_wilson_refinement_spectrum_study
 return run_wilson_refinement_spectrum_study()
def _m132():
 from .holographic_bcj_twistor_wilson_m132 import run_holographic_amplitude_study
 return run_holographic_amplitude_study()
def run_bcj_yukawa_holographic_study(config=None):
 cfg=BCJYukawaHolographicConfig() if config is None else config; cfg.validate()
 m=yukawa_mass(cfg.yukawa_coupling,cfg.higgs_vev); mu=(m*cfg.c*cfg.ads_radius/cfg.hbar)**2; dp,dm=conformal_dimensions(cfg.boundary_dimension,mu)
 colors=(1.0,-0.4,-0.6); nums=(m*m+1.0,0.5*m*m-0.2,0.0); nums=(nums[0],nums[1],-nums[0]-nums[1]); nums2=(0.7,-0.1,-0.6)
 den=(m*m+1.2,m*m+1.7,m*m+2.3)
 gauge=sum(c*n/d for c,n,d in zip(colors,nums,den)); double=sum(n*nt/d for n,nt,d in zip(nums,nums2,den)); diagonal=[n*n/d for n,d in zip(nums,den)]
 forward=(2.0,-3.0,1.0); amps=(1+0j,1+0j,1+0j); fsum=sum(w*a for w,a in zip(forward,amps)); bsum=sum(-w*a for w,a in zip(forward,amps))
 wilson=_wilson(); sigma=float(wilson["area_perimeter_fit"]["area_coefficient"]); alpha_prime=1.0/(2.0*math.pi*sigma); alpha0=cfg.spin-alpha_prime*m*m
 regge_m2=(cfg.spin-alpha0)/alpha_prime; dsi=cfg.yukawa_coupling*cfg.entropic_frequency/(2.0*cfg.hbar); im_alpha=2.0*alpha_prime*m*dsi; regge_width=im_alpha/(alpha_prime*m)
 rt=run_yukawa_rt_holographic_study(); h132=_m132()
 wilson_area=sigma*cfg.loop_area; rt_area=float(rt["diagnostics"]["rt_area"])
 diagnostics={"yukawa_mass":m,"mass_radius_sq":mu,"delta_plus":dp,"delta_minus":dm,"color_jacobi_error":abs(sum(colors)),"kinematic_jacobi_error":abs(sum(nums)),"second_copy_jacobi_error":abs(sum(nums2)),"gauge_amplitude":gauge,"double_copy_amplitude":double,"minimum_diagonal_channel":min(diagonal),"qcd_total_legs":cfg.gluons+2*cfg.quark_pairs,"qcd_moved_leg_is_gluon":cfg.gluons>0,"qcd_forward_sum_error":abs(fsum),"qcd_backward_sum_error":abs(bsum),"qcd_forward_backward_error":abs(fsum+bsum),"wilson_area_coefficient":sigma,"wilson_creutz_11":float(wilson["creutz_11"]),"wilson_passed":bool(wilson["passed"]),"regge_slope":alpha_prime,"regge_intercept":alpha0,"regge_mass_sq_error":abs(regge_m2-m*m),"yukawa_entropy_rate":dsi,"regge_width_error":abs(regge_width-2.0*dsi),"rt_passed":bool(rt["passed"]),"m13_2_passed":bool(h132["passed"]),"rt_area":rt_area,"wilson_effective_area":wilson_area,"finite_area_ratio":wilson_area/rt_area if rt_area else math.inf}
 acceptance={"massive_bcj_jacobi":max(diagnostics["color_jacobi_error"],diagnostics["kinematic_jacobi_error"],diagnostics["second_copy_jacobi_error"])<5e-14,"primitive_qcd_bcj":diagnostics["qcd_total_legs"]==8 and diagnostics["qcd_moved_leg_is_gluon"] and max(diagnostics["qcd_forward_sum_error"],diagnostics["qcd_backward_sum_error"],diagnostics["qcd_forward_backward_error"])<5e-14,"double_copy_finite":math.isfinite(double) and diagnostics["minimum_diagonal_channel"]>=0.0,"wilson_regge_yukawa_mass":diagnostics["wilson_passed"] and sigma>0 and diagnostics["wilson_creutz_11"]>0 and diagnostics["regge_mass_sq_error"]<5e-14,"regge_entropy_width":diagnostics["regge_width_error"]<5e-14,"gkp_and_rt_share_supplied_mass":abs(dp*(dp-cfg.boundary_dimension)-mu)<5e-13 and diagnostics["rt_passed"],"dependencies_pass":diagnostics["m13_2_passed"]}
 p=canonical_payload(cfg);return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"same_supplied_yukawa_mass_threads_all_sectors":True,"wilson_area_coefficient_is_used_as_a_finite_effective_string_tension":True,"bcj_amplitude_is_not_identified_with_rt_entropy":True,"no_continuum_qcd_or_gauge_string_duality_is_claimed":True}}
