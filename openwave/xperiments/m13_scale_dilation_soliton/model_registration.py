"""M13 model registration: CAT/EPT scale geometry over M11/M12 carriers."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from hashlib import sha256
import json
from typing import Any,Mapping
from .scale_geometry_m131 import run_scale_geometry
from .soliton_tensor_bridge_m131 import run_soliton_tensor_bridge
MILESTONE="M13.1"; SCHEMA="openwave.m13.scale-dilation-soliton-tensor.v1"; FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ScaleDilationLogMetric.lean","sha":"0c8262bac90d2dff03a04cc8e15efb21ee87ff0e","theorems":["scaleLagrangian_dilation_invariant","noether_dilation_charge","dilationFlow_log_derivative","entropicEnergyDecay_eq_dilationFlow","dilation_isometry","scaleDistance_eq_dist_log","blockspin_ladder","sqrtTwo_half_blockspin","blockspin_geodesic","gauss_iff_dilation_invariant","chargedSector_scaleDistance"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/ComptonClock/EntropicProperDistance.lean","sha":"6ea714cbb98e94aa9b42602f800c9d6f81295c94","theorems":["entropicProperDistance_eq_entropicAction","expEntropicDistance_eq_schmidtNumber"]},
 {"path":"Physlib/QuantumMechanics/ComplexAction/EntropicTime/ComplexNoetherChargeEntropicHorizon.lean","sha":"79c6994ca14c661cccdf81a4844ad37943ed3e62","theorems":["entropicEnergyDecay_hasDerivAt","complexNoetherChargePath_hasDerivAt_zero"]},
 {"path":"Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean","sha":"9d2c905c940480f1ed570cf0be965d5a9b6c4831","theorems":["kernelMode_infinite","kernelOccupationBasis_particleNumber","continuumKernelNormSq_nonneg"]},)
@dataclass(frozen=True)
class ScaleDilationSolitonConfig:
 generator:float=.75; initial_scale:float=1.3; multiplier:float=2.7; times:tuple[float,...]=(-1.,-.5,0.,.5,1.); lattice_steps:int=6; lattice_a0:float=.125
 rungs:tuple[float,...]=(0.,.5,1.,1.5); grid_points:int=1025; half_length:float=12.; inverse_width:float=1.; tensor_modes:int=96
 schmidt_number:float=3.; compton_scale:float=1.; horizon_energy:float=2.5; charge:float=3.; charge_time:float=.4
 def validate(self):
  if min(self.initial_scale,self.multiplier,self.lattice_a0,self.half_length,self.inverse_width,self.compton_scale)<=0 or self.schmidt_number<=1 or self.grid_points<129 or self.grid_points%2==0 or self.tensor_modes<8: raise ValueError("invalid M13 configuration")
def canonical_payload(config=None):
 c=ScaleDilationSolitonConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT scale-dilation pointwise/infinite-mode soliton tensor","configuration":asdict(c),"lineage_dependencies":["M11.1","M11.2","M12.3"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.model_registration:run_scale_dilation_soliton_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None): return sha256(json.dumps(canonical_payload() if payload is None else payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def run_scale_dilation_soliton_study(config=None):
 c=ScaleDilationSolitonConfig() if config is None else config; c.validate()
 g=run_scale_geometry(c.generator,c.initial_scale,c.multiplier,c.times,c.lattice_steps,c.lattice_a0,c.rungs,c.schmidt_number,c.compton_scale,c.horizon_energy,c.charge,c.charge_time)
 b,campaign=run_soliton_tensor_bridge(c.rungs,c.grid_points,c.half_length,c.inverse_width,c.tensor_modes); d={**g,**b}
 a={"dilation_noether":max(d[k] for k in ("group_error","inverse_error","lagrangian_error","euler_lagrange_error","noether_charge_error"))<5e-14,
 "invariant_log_metric":max(d[k] for k in ("metric_isometry_error","metric_log_error"))<5e-14,
 "lattice_ladder_halfstep":max(d[k] for k in ("ladder_step_error","ladder_total_error","sqrt_two_half_step_error","geodesic_error"))<5e-14,
 "entropic_orbits":max(d[k] for k in ("horizon_orbit_error","schmidt_recovery_error","charged_sector_error"))<5e-14 and d["gauss_fixed"],
 "pointwise_scale_transport":d["soliton_norm_error"]<5e-13 and d["soliton_residual"]<5e-12 and d["soliton_width_error"]<2e-5 and d["soliton_metric_error"]<5e-14,
 "infinite_mode_tensor_transport":d["tensor_trace_error"]<5e-13 and d["tensor_purity_error"]<5e-13 and d["tensor_min_eigenvalue"]>-5e-13 and d["tensor_min_retained"]>.999,
 "particle_compton_metric":d["particle_metric_error"]<5e-14 and d["particle_additivity_error"]<5e-14 and d["particle_masses_ordered"],"dependencies_pass":all(d["prior_layers"].values())}
 p=canonical_payload(c); return {**p,"task":MILESTONE,"diagnostics":d,"scale_campaign":campaign,"acceptance":a,"fingerprint":fingerprint(p),"passed":all(a.values()),"decision":{"registered_as_new_model":True,"m11_pointwise_and_infinite_mode_carriers_reused":True,"particle_masses_are_supplied_inputs":True,"finite_cutoff_is_not_infinite_particle_fock_space":True,"no_new_lattice_data_or_holographic_dictionary_claimed":True}}
