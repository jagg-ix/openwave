"""M13.8 BCJ weighted bilinear as a finite GKP source-response kernel."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping
import numpy as np
from .wilson_rt_surface_scaling_m137 import run_wilson_rt_scaling_study

MILESTONE="M13.8"
SCHEMA="openwave.m13.bcj-gkp-source-kernel.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean","sha":"110a42b466c7fcf8be68be4326cb1d0c9197043c","theorems":["threeChannelNumerator_in_jacobiKernel_iff","weightedBilinear_comm","cubicDoubleCopy_eq_weightedBilinear","cubicDoubleCopy_shift_left_of_orthogonal"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean","sha":"d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3","theorems":["massDimension_relation","cftTwoPoint_scaling","gkpWitten_regularized_source_response","gkpWitten_affine_source_hessian"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Particles/QCDFundamentalBCJRelations.lean","sha":"5756653f5dbd58ac14fef7307d03223e7bf81304","theorems":["forwardBCJRelation_iff_backwardBCJRelation","qcdPrimitiveBCJ_backward_relation"]},)

def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class BCJGKPSourceKernelConfig:
 kappa:float=2.0
 multiplicity:int=4
 denominators:tuple[float,float,float]=(1.3,1.7,2.2)
 source:tuple[float,float]=(0.7,-0.2)
 variation:tuple[float,float]=(0.3,0.5)
 derivative_step:float=1e-5
 boundary_dimension:float=4.0
 mass_radius_sq:float=0.16
 separation:float=1.4
 dilation:float=1.8
 def validate(self):
  if self.kappa<=0 or self.multiplicity<3 or min(self.denominators)<=0 or self.derivative_step<=0 or self.boundary_dimension<=0 or self.separation<=0 or self.dilation<=0: raise ValueError("valid positive kernel controls required")
def conformal_dimension(d:float,mu:float)->float:
 rad=(d/2.0)**2+mu
 if rad<0: raise ValueError("BF bound violated")
 return d/2.0+math.sqrt(rad)
def canonical_payload(config=None):
 c=BCJGKPSourceKernelConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT BCJ weighted-bilinear GKP source kernel","configuration":asdict(c),"lineage_dependencies":["M13.7"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.bcj_gkp_source_kernel_m138:run_bcj_gkp_source_kernel_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def run_bcj_gkp_source_kernel_study(config=None):
 cfg=BCJGKPSourceKernelConfig() if config is None else config; cfg.validate()
 basis=np.asarray([[1.0,1.0],[-1.0,1.0],[0.0,-2.0]],dtype=float)
 prefactor=(cfg.kappa/2.0)**(cfg.multiplicity-2)
 weights=prefactor/np.asarray(cfg.denominators,dtype=float)
 kernel=basis.T@np.diag(weights)@basis
 source=np.asarray(cfg.source,dtype=float); variation=np.asarray(cfg.variation,dtype=float)
 numerator=basis@source; numerator_tilde=basis@variation
 amplitude=float(numerator@np.diag(weights)@numerator_tilde)
 source_bilinear=float(source@kernel@variation)
 diagonal=float(numerator@np.diag(weights)@numerator)
 def action(t:float)->float:
  current=source+t*variation
  return 0.5*float(current@kernel@current)
 h=cfg.derivative_step
 first=(action(h)-action(-h))/(2*h)
 second=(action(h)-2*action(0.0)+action(-h))/h**2
 expected_second=float(variation@kernel@variation)
 direction=kernel@variation
 gauge_source=np.asarray([direction[1],-direction[0]],dtype=float)
 gauge_shift=basis@gauge_source
 orthogonality=float(gauge_shift@np.diag(weights)@numerator_tilde)
 shifted=float((numerator+gauge_shift)@np.diag(weights)@numerator_tilde)
 eig=np.linalg.eigvalsh(kernel)
 delta=conformal_dimension(cfg.boundary_dimension,cfg.mass_radius_sq)
 two_point=cfg.separation**(-2.0*delta)
 two_point_moved=(cfg.dilation*cfg.separation)**(-2.0*delta)
 diagnostics={
  "basis_jacobi_error":float(np.max(np.abs(np.sum(basis,axis=0)))),"numerator_jacobi_error":abs(float(np.sum(numerator))),"second_copy_jacobi_error":abs(float(np.sum(numerator_tilde))),"gauge_shift_jacobi_error":abs(float(np.sum(gauge_shift))),
  "kernel_symmetry_error":float(np.max(np.abs(kernel-kernel.T))),"kernel_eigenvalues":eig.tolist(),"kernel_min_eigenvalue":float(np.min(eig)),
  "double_copy_source_bilinear_error":abs(amplitude-source_bilinear),"double_copy_exchange_error":abs(amplitude-float(numerator_tilde@np.diag(weights)@numerator)),"diagonal_double_copy":diagonal,
  "source_first_derivative_error":abs(first-source_bilinear),"source_hessian_error":abs(second-expected_second),
  "gauge_orthogonality_error":abs(orthogonality),"gauge_shift_amplitude_error":abs(shifted-amplitude),
  "conformal_dimension":delta,"mass_dimension_error":abs(delta*(delta-cfg.boundary_dimension)-cfg.mass_radius_sq),"two_point_scaling_error":abs(two_point_moved-cfg.dilation**(-2.0*delta)*two_point),
  "surface_dependency_passed":bool(run_wilson_rt_scaling_study()["passed"]),
 }
 acceptance={
  "bcj_sources_obey_jacobi":max(diagnostics[k] for k in ("basis_jacobi_error","numerator_jacobi_error","second_copy_jacobi_error","gauge_shift_jacobi_error"))<5e-14,
  "source_kernel_is_symmetric_positive":diagnostics["kernel_symmetry_error"]<5e-14 and diagnostics["kernel_min_eigenvalue"]>0,
  "double_copy_equals_gkp_bilinear_response":diagnostics["double_copy_source_bilinear_error"]<5e-14 and diagnostics["double_copy_exchange_error"]<5e-14,
  "finite_source_derivatives_close":diagnostics["source_first_derivative_error"]<5e-10 and diagnostics["source_hessian_error"]<5e-5,
  "generalized_gauge_shift_is_invisible":diagnostics["gauge_orthogonality_error"]<5e-14 and diagnostics["gauge_shift_amplitude_error"]<5e-14,
  "diagonal_double_copy_is_positive":diagnostics["diagonal_double_copy"]>=0,
  "gkp_mass_dimension_and_scaling_close":diagnostics["mass_dimension_error"]<5e-13 and diagnostics["two_point_scaling_error"]<5e-13,
  "dependencies_pass":diagnostics["surface_dependency_passed"],
 }
 p=canonical_payload(cfg);return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"bcj_weighted_bilinear_used_as_finite_gkp_kernel":True,"interacting_witten_diagram_not_claimed":True,"ads_double_copy_theorem_not_claimed":True,"continuum_boundary_correlator_not_claimed":True}}
