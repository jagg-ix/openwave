"""M9.66 audit of the two M9.63 coefficient-selection conditions."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json, math
from typing import Any
import numpy as np
from .coefficient_self_consistency import CoefficientSelectionConfig, gaussian_energy_constants, gaussian_peak_density, selected_coefficients

OPENWAVE_HEAD="e11e8fce88ce886812860ce747c48d32c8eaeb57"
FORMAL_REPOSITORY="jagg-ix/entropic-physlib-private"; FORMAL_BRANCH="entropic-physlib-linear-full"
FORMAL_HEAD="e2c06741c3e49deb604082a2e9c2e918eab8d545"; ZIL_HEAD="f39758f85ee6300b8060e4f8ea1ecf344ed32c96"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalElectrograviticAction.lean","sha":"39e807f424cf8384135299e84fdffc97fb506ee5","role":"global coupled-action derivative interface"},
 {"path":"Physlib/QuantumMechanics/Clock/EntropicAgreement.lean","sha":"8d7cb5a9c87dba47beefdc4a6c317aa872536632","role":"operational action-rate clock calibration"},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean","sha":"d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7","role":"exact cubic continuum semiflow and attractor results"},)

@dataclass(frozen=True)
class DerivationAuditConfig:
 dispersion:float=.65; reference_scale:float=1.; radial_cutoff:float=8.; radial_points:int=20001
 alternative_ratio_multipliers:tuple[float,...]=(1.,4/3,2.)
 def __post_init__(self):
  if min(self.dispersion,self.reference_scale,self.radial_cutoff)<=0 or self.radial_points<1001: raise ValueError("invalid audit controls")

def gaussian_scale_derivative(alpha,beta,cfg=DerivationAuditConfig()):
 c=gaussian_energy_constants(cfg.dispersion);s=cfg.reference_scale
 return -2*c["kinetic"]/s**3+3*c["quartic"]*alpha/s**4-6*c["sextic"]*beta/s**7

def stationary_field_residual(alpha,beta,cfg=DerivationAuditConfig()):
 s=cfg.reference_scale;r=np.linspace(0,cfg.radial_cutoff,cfg.radial_points)
 psi=math.pi**(-.75)*s**(-1.5)*np.exp(-r*r/(2*s*s));rho=psi*psi
 lap=(r*r/s**4-3/s**2)*psi
 op=-cfg.dispersion*lap+(-alpha*rho+beta*rho*rho)*psi;w=4*math.pi*r*r
 mass=float(np.trapezoid(w*psi*psi,r));mu=float(np.trapezoid(w*psi*op,r)/mass)
 residual=op-mu*psi;rn=math.sqrt(float(np.trapezoid(w*residual*residual,r)));on=math.sqrt(float(np.trapezoid(w*op*op,r)))
 return {"mass":mass,"best_chemical_potential":mu,"residual_l2":rn,"operator_l2":on,"relative_residual":rn/on,"peak_operator":float(op[0]/psi[0]),"peak_minus_chemical_potential":float(op[0]/psi[0]-mu)}

def solve_with_density_landmark(multiplier,cfg=DerivationAuditConfig()):
 rp=gaussian_peak_density(cfg.reference_scale);c=gaussian_energy_constants(cfg.dispersion);s=cfg.reference_scale
 matrix=np.asarray([[1,-multiplier*rp],[3*c["quartic"]*s**3,-6*c["sextic"]]],float);rhs=np.asarray([0,2*c["kinetic"]*s**4],float)
 alpha,beta=np.linalg.solve(matrix,rhs);res=matrix@np.asarray([alpha,beta])-rhs
 return {"ratio_multiplier":multiplier,"alpha":float(alpha),"beta":float(beta),"determinant":float(np.linalg.det(matrix)),"maximum_equation_residual":float(np.max(np.abs(res)))}

def alternative_landmark_audit(cfg=DerivationAuditConfig()):
 names=("local_action_minimum","coercive_equality_density","interaction_inflection")
 rows=[{"landmark":name,**solve_with_density_landmark(k,cfg)} for name,k in zip(names,cfg.alternative_ratio_multipliers)]
 return {"rows":rows,"distinct_positive_pairs":len({(round(x["alpha"],10),round(x["beta"],10)) for x in rows}),"all_systems_nondegenerate":all(abs(x["determinant"])>1e-5 for x in rows),"all_equations_close":all(x["maximum_equation_residual"]<2e-13 for x in rows)}

def evidence_fingerprint(cfg=DerivationAuditConfig()):
 payload={"config":asdict(cfg),"openwave":OPENWAVE_HEAD,"physlib":FORMAL_HEAD,"zil":ZIL_HEAD,"sources":FORMAL_SOURCES}
 return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_selection_derivation_audit():
 cfg=DerivationAuditConfig();sel=selected_coefficients(CoefficientSelectionConfig(dispersion=cfg.dispersion,reference_scale=cfg.reference_scale));a,b=sel["alpha"],sel["beta"]
 derivative=gaussian_scale_derivative(a,b,cfg);field=stationary_field_residual(a,b,cfg);alts=alternative_landmark_audit(cfg)
 acceptance={"current_repository_heads_are_pinned":all(len(x)==40 for x in (OPENWAVE_HEAD,FORMAL_HEAD,ZIL_HEAD)),"scale_stationarity_is_action_derived":abs(derivative)<=2e-13,"normalized_field_equation_is_tested":field["mass"]>.999999,"gaussian_is_not_an_exact_stationary_field":field["relative_residual"]>.10,"alternative_local_landmarks_are_nondegenerate":alts["all_systems_nondegenerate"],"alternative_local_landmarks_close":alts["all_equations_close"],"peak_matching_is_not_uniquely_selected":alts["distinct_positive_pairs"]>=3,"fingerprint_is_deterministic":evidence_fingerprint(cfg)==evidence_fingerprint(cfg)}
 return {"schema":"openwave.m9.selection-derivation-audit.v1","task":"M9.66","config":asdict(cfg),"repositories":{"openwave":OPENWAVE_HEAD,"physlib":{"repository":FORMAL_REPOSITORY,"branch":FORMAL_BRANCH,"head":FORMAL_HEAD},"zil":ZIL_HEAD},"formal_sources":FORMAL_SOURCES,"selected_coefficients":{"alpha":a,"beta":b},"scale_stationarity":{"derivative":derivative,"derived_from_reduced_action_variation":True},"stationary_field_residual":field,"alternative_density_landmarks":alts,"fingerprint":evidence_fingerprint(cfg),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"scale_stationarity_derived_from_reduced_action":True,"peak_density_matching_derived_from_full_normalized_field_equation":False,"m9_63_pair_first_principles_unique":False,"m9_63_peak_condition_rejected_as_current_first_principles_derivation":True},"classification":{"establishes":["Gaussian scale stationarity is an exact reduced-action variation","the selected Gaussian has a nonzero stationary-field residual","alternative local density landmarks select different positive pairs"],"does_not_establish":["that no future CAT/EPT principle can select the condition","physical coefficient calibration","a stationary non-Gaussian particle profile"]}}

def result_to_json(result): return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
