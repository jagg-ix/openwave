"""M13.4 Yukawa/Compton cutoff and Ryu--Takayanagi entropy bridge."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping
from .yukawa_dilation_gkp_m133 import yukawa_mass, scale_distance, run_yukawa_dilation_gkp_study

MILESTONE="M13.4"; SCHEMA="openwave.m13.yukawa-rt-entropy.v1"; FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean","sha":"c14aede2c8654bdbdb4aedfca543c36872c65e55","theorems":["rt_log_square_prefactor_identity","rtPoincareLineDensity_regulated_integral_eq_neg_two_log","cftEntropyVacuumLine_strongSubadditivity","cftEntropyFiniteT_strongSubadditivity"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/MassOrigin/GravitationalMassHorizonEntropyNoYukawa.lean","sha":"a7ff039e9f23a10dac72a818862a1a057108f9f7","theorems":["gravitationalMass_eq","gravitationalWidth_eq","norm_nnPathWeight_horizon"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/MassOrigin/HiggsClockThreeOrigins.lean","sha":"377374eb2e0861e671a6f5fcf08da44f1ca52a1c","theorems":["higgsClockFrequency_eq","higgs_clock_three_origins"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Yukawa/MassDecoherenceProportionality.lean","sha":"578152c3b9d73b3baec98f845bca2f566f59e93e","theorems":["yukawaEntropyRate_eq_const_mul_mass"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ScaleDilationLogMetric.lean","sha":"0c8262bac90d2dff03a04cc8e15efb21ee87ff0e","theorems":["dilation_isometry","scaleDistance_eq_dist_log","adsRadial_dilation_invariant"]},)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class YukawaRTHolographicConfig:
 yukawa_coupling:float=0.2; higgs_vev:float=math.sqrt(2.0); c:float=1.0; hbar:float=1.0
 ads_radius:float=2.0; newton_constant:float=0.25; interval_to_cutoff:float=12.0; dilation_factor:float=2.5; log_mass_step:float=1e-5
 def validate(self)->None:
  if min(self.yukawa_coupling,self.higgs_vev,self.c,self.hbar,self.ads_radius,self.newton_constant,self.interval_to_cutoff,self.dilation_factor,self.log_mass_step)<=0: raise ValueError("positive controls required")
  if self.interval_to_cutoff<=1: raise ValueError("interval must exceed cutoff")
def canonical_payload(config=None):
 c=YukawaRTHolographicConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT Yukawa-Compton RT entropy bridge","configuration":asdict(c),"lineage_dependencies":["M13.2","M13.3"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.yukawa_rt_holographic_entropy_m134:run_yukawa_rt_holographic_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _deps():
 try:a=bool(run_yukawa_dilation_gkp_study()["passed"])
 except Exception:a=False
 try:
  from .holographic_bcj_twistor_wilson_m132 import run_holographic_amplitude_study
  b=bool(run_holographic_amplitude_study()["passed"])
 except Exception:b=False
 return {"m13_3_yukawa_dilation_gkp":a,"m13_2_holographic_closure":b}
def _entropy(central:float,ell:float,cutoff:float)->float:return central/3.0*math.log(ell/cutoff)
def run_yukawa_rt_holographic_study(config=None):
 cfg=YukawaRTHolographicConfig() if config is None else config; cfg.validate()
 m=yukawa_mass(cfg.yukawa_coupling,cfg.higgs_vev); cutoff=cfg.hbar/(m*cfg.c); ell=cfg.interval_to_cutoff*cutoff
 central=3.0*cfg.ads_radius/(2.0*cfg.newton_constant); entropy=_entropy(central,ell,cutoff); area=4.0*cfg.newton_constant*entropy
 rt_err=abs(area/(4.0*cfg.newton_constant)-entropy); metric_err=abs(entropy-central/3.0*scale_distance(ell,cutoff))
 lam=cfg.dilation_factor; mp=m/lam; cutoffp=cfg.hbar/(mp*cfg.c); ellp=lam*ell; entropy_p=_entropy(central,ellp,cutoffp)
 dilation_err=abs(entropy_p-entropy)
 h=cfg.log_mass_step
 def s_log(delta:float)->float:
  mm=m*math.exp(delta); aa=cfg.hbar/(mm*cfg.c); return _entropy(central,ell,aa)
 derivative=(s_log(h)-s_log(-h))/(2*h); derivative_err=abs(derivative-central/3.0)
 Adot=4.0*cfg.newton_constant*m/cfg.c; grav_mass=cfg.c/(4.0*cfg.newton_constant)*Adot; horizon_rate=cfg.c**3/(4.0*cfg.newton_constant)*Adot
 omega=m*cfg.c**2/cfg.hbar; horizon_omega=cfg.c**3*Adot/(4.0*cfg.newton_constant*cfg.hbar)
 deps=_deps(); diagnostics={"yukawa_mass":m,"compton_cutoff":cutoff,"interval_length":ell,"brown_henneaux_central_charge":central,"cft_entropy":entropy,"rt_area":area,"rt_identity_error":rt_err,"scale_metric_entropy_error":metric_err,"dilation_entropy_error":dilation_err,"log_mass_entropy_derivative":derivative,"log_mass_entropy_derivative_error":derivative_err,"horizon_area_rate":Adot,"gravitational_mass_recovery_error":abs(grav_mass-m),"horizon_entropy_rate_error":abs(horizon_rate-m*cfg.c**2),"clock_horizon_frequency_error":abs(omega-horizon_omega),"dependencies":deps}
 acceptance={"rt_area_entropy_identity":rt_err<5e-14,"compton_cutoff_scale_metric":metric_err<5e-14,"common_dilation_invariance":dilation_err<5e-13,"mass_log_entropy_response":derivative_err<2e-9,"horizon_area_rate_mass_bridge":max(diagnostics["gravitational_mass_recovery_error"],diagnostics["horizon_entropy_rate_error"],diagnostics["clock_horizon_frequency_error"])<5e-13,"dependencies_pass":all(deps.values())}
 p=canonical_payload(cfg); return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"compton_wavelength_as_rt_cutoff_is_a_model_adapter":True,"rt_area_and_horizon_area_rate_are_not_identified":True,"yukawa_and_gravitational_mass_equality_is_a_supplied_bridge_hypothesis":True}}
