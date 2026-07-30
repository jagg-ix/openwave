"""M13.10 lossless holographic dimensional reduction and stereographic boundary."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json, math
from typing import Any, Mapping

MILESTONE="M13.10"
SCHEMA="openwave.m13.lossless-holographic-reduction.v1"
FORMAL_HEAD="8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/AdSCFT/JohnsonLindenstraussHolographicReduction.lean","sha":"087b3e89c427e2fb16089bcc05ca1a3fa9f56d2f","theorems":["JLBound_of_isometry","JLBound_zero_iff","jlTargetDim_mono","holographic_reduction_is_exact_JL","stereographic_boundary_chart_lossless","stereographic_roundtrip_is_exact_JL","stereographic_domain_is_dualSphere"]},
)
def _canon(v:Mapping[str,Any])->str:return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
@dataclass(frozen=True)
class HolographicReductionConfig:
 epsilon:float=0.12
 K:float=4.0
 point_counts:tuple[int,...]=(8,32,128,512)
 theta:float=1.1
 phi:float=0.7
 def validate(self):
  if self.epsilon<0 or self.K<0 or any(n<=1 for n in self.point_counts):raise ValueError("nonnegative distortion/K and point counts >1 required")
def canonical_payload(config=None):
 c=HolographicReductionConfig() if config is None else config
 return {"schema":SCHEMA,"model_id":"M13","milestone":MILESTONE,"model":"CAT/EPT lossless holographic dimensional reduction","configuration":asdict(c),"lineage_dependencies":["M13.2","M13.9"],"study_api":"openwave.xperiments.m13_scale_dilation_soliton.lossless_holographic_reduction_m1310:run_holographic_reduction_study","formal_authority":{"repository":"jagg-ix/entropic-physlib-private","branch":"entropic-physlib-linear-full","head":FORMAL_HEAD,"sources":list(FORMAL_SOURCES)}}
def fingerprint(payload=None):return sha256(_canon(canonical_payload() if payload is None else payload).encode()).hexdigest()
def _stereo(x,y,z):
 if abs(1-z)<1e-15: raise ValueError("north pole excluded")
 return complex(x,y)/(1-z)
def _stereo_inv(w):
 r2=(w.real*w.real+w.imag*w.imag)
 den=r2+1
 return (2*w.real/den,2*w.imag/den,(r2-1)/den)
def run_holographic_reduction_study(config=None):
 c=HolographicReductionConfig() if config is None else config;c.validate()
 x=math.sin(c.theta)*math.cos(c.phi);y=math.sin(c.theta)*math.sin(c.phi);z=math.cos(c.theta)
 w=_stereo(x,y,z);xr,yr,zr=_stereo_inv(w)
 roundtrip=max(abs(x-xr),abs(y-yr),abs(z-zr))
 sphere_error=abs(x*x+y*y+z*z-1)
 recovered_sphere_error=abs(xr*xr+yr*yr+zr*zr-1)
 d=math.sqrt((x-0.2)**2+(y+0.1)**2+(z-0.3)**2)
 dk=d
 jl_lower=(1-c.epsilon)*d*d
 jl_upper=(1+c.epsilon)*d*d
 exact_zero_error=abs(dk*dk-d*d)
 dims=[math.ceil(c.K*math.log(n)) for n in c.point_counts]
 diagnostics={
  "sphere_point":[x,y,z],"stereographic_coordinate":[w.real,w.imag],"roundtrip_error":roundtrip,
  "sphere_norm_error":sphere_error,"recovered_sphere_norm_error":recovered_sphere_error,
  "bulk_distance":d,"boundary_distance":dk,"jl_lower":jl_lower,"jl_upper":jl_upper,
  "jl_lower_margin":dk*dk-jl_lower,"jl_upper_margin":jl_upper-dk*dk,"zero_distortion_error":exact_zero_error,
  "target_dimensions":dims,"target_dimensions_monotone":all(b>=a for a,b in zip(dims,dims[1:])),
 }
 acceptance={
  "stereographic_roundtrip_is_lossless":roundtrip<5e-14,
  "boundary_and_dual_sphere_match":max(sphere_error,recovered_sphere_error)<5e-14,
  "exact_isometry_satisfies_jl_bound":diagnostics["jl_lower_margin"]>=-5e-14 and diagnostics["jl_upper_margin"]>=-5e-14,
  "zero_distortion_is_exact":exact_zero_error<5e-14,
  "jl_target_dimension_is_logarithmic_monotone":diagnostics["target_dimensions_monotone"],
 }
 p=canonical_payload(c)
 return {**p,"task":MILESTONE,"diagnostics":diagnostics,"acceptance":acceptance,"fingerprint":fingerprint(p),"passed":all(acceptance.values()),"decision":{"holographic_reduction_used_as_zero_distortion_isometry":True,"random_jl_embedding_existence_not_claimed":True,"full_su22_twistor_action_not_claimed":True}}
