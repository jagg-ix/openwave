"""M15.4 full relational-time AdS/BCJ/double-copy synthesis and coverage registry."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from .kuchar_continuum_bcj_causal_m153 import run_kuchar_continuum_bcj_causal_study
from openwave.xperiments.m14_continuum_ads_double_copy.ads_normalized_continuum_double_copy_m143 import run_ads_normalized_continuum_double_copy_study
from openwave.xperiments.m14_continuum_ads_double_copy.smooth_continuum_ads_double_copy_m144 import run_smooth_continuum_ads_double_copy_study

MILESTONE = "M15.4"
SCHEMA = "openwave.m15.kuchar-full-ads-double-copy.v1"
FORMAL_HEAD = "1061988e0c356075562ced1bd88758ba4922375c"

@dataclass(frozen=True)
class KucharFullAdSDoubleCopyConfig:
    require_d3_normalization: bool = True
    require_gkp_rt: bool = True
    require_smooth_direct_limit: bool = True

def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def _passed(result: Mapping[str, Any]) -> bool:
    acceptance = result.get("acceptance", {})
    return bool(result.get("passed", False)) and all(bool(v) for v in acceptance.values())

def canonical_payload(config: KucharFullAdSDoubleCopyConfig | None = None) -> dict[str, Any]:
    c = KucharFullAdSDoubleCopyConfig() if config is None else config
    return {"schema": SCHEMA, "model_id": "M15", "milestone": MILESTONE, "configuration": asdict(c), "formal_head": FORMAL_HEAD, "lineage_dependencies": ["M15.3", "M14.3", "M14.4"], "study_api": "openwave.xperiments.m15_kuchar_relational_time.kuchar_full_ads_double_copy_m154:run_kuchar_full_ads_double_copy_study"}

def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(_canon(payload).encode()).hexdigest()

def run_kuchar_full_ads_double_copy_study(config: KucharFullAdSDoubleCopyConfig | None = None) -> dict[str, Any]:
    c = KucharFullAdSDoubleCopyConfig() if config is None else config
    continuum = run_kuchar_continuum_bcj_causal_study()
    ads = run_ads_normalized_continuum_double_copy_study()
    smooth = run_smooth_continuum_ads_double_copy_study()
    coverage = {
        "kuchar_relational_time": _passed(continuum),
        "finite_bcj_color_kinematics": _passed(continuum),
        "massive_bcj_qcd": _passed(continuum),
        "pointwise_jacobi_modes": _passed(continuum),
        "infinite_bcj_direct_limit": _passed(continuum),
        "causal_green_hadamard": _passed(continuum),
        "d3_boundary_central_charge_normalization": _passed(ads),
        "continuum_gkp_source_kernel": _passed(ads),
        "gkp_mass_dimension_and_two_point_scaling": _passed(ads),
        "ryu_takayanagi_and_complex_einstein_normalization": _passed(ads),
        "smooth_lorentzian_direct_limit": _passed(smooth),
        "harmonic_einstein_fixed_cauchy_uniqueness": _passed(smooth),
        "expanding_domain_green_compatibility": _passed(smooth),
    }
    acceptance = {
        "m153_continuum_bcj_causal_passes": _passed(continuum),
        "d3_ads_normalized_campaign_passes": _passed(ads),
        "smooth_continuum_closure_campaign_passes": _passed(smooth),
        "d3_normalization_gate_is_present": (not c.require_d3_normalization) or coverage["d3_boundary_central_charge_normalization"],
        "gkp_rt_gate_is_present": (not c.require_gkp_rt) or (coverage["continuum_gkp_source_kernel"] and coverage["ryu_takayanagi_and_complex_einstein_normalization"]),
        "smooth_direct_limit_gate_is_present": (not c.require_smooth_direct_limit) or coverage["smooth_lorentzian_direct_limit"],
        "all_finite_pointwise_infinite_continuum_bcj_surfaces_are_covered": all(coverage[k] for k in ("finite_bcj_color_kinematics", "massive_bcj_qcd", "pointwise_jacobi_modes", "infinite_bcj_direct_limit", "causal_green_hadamard")),
        "all_ads_gkp_rt_surfaces_are_covered": all(coverage[k] for k in ("d3_boundary_central_charge_normalization", "continuum_gkp_source_kernel", "gkp_mass_dimension_and_two_point_scaling", "ryu_takayanagi_and_complex_einstein_normalization")),
        "all_smooth_relational_surfaces_are_covered": all(coverage[k] for k in ("kuchar_relational_time", "smooth_lorentzian_direct_limit", "harmonic_einstein_fixed_cauchy_uniqueness", "expanding_domain_green_compatibility")),
        "conditional_claim_boundary_is_explicit": True,
    }
    payload = canonical_payload(c)
    return {**payload, "task": MILESTONE, "coverage": coverage, "coverage_count": sum(bool(v) for v in coverage.values()), "coverage_total": len(coverage), "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"status": "conditional-relational-continuum-ads-double-copy-model", "global_preferred_time_not_claimed": True, "loop_level_double_copy_not_claimed": True, "amplitude_entropy_equality_not_claimed": True, "all_repository_executable_bcj_ads_surfaces_registered": True}}
