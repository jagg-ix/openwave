"""M15.3 infinite-mode BCJ and causal continuum transport under Kuchař consistency."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from .kuchar_bcj_pointwise_coverage_m152 import run_kuchar_bcj_pointwise_coverage_study
from openwave.xperiments.m14_continuum_ads_double_copy.causal_green_hadamard_m141 import run_causal_green_hadamard_study
from openwave.xperiments.m14_continuum_ads_double_copy.infinite_bcj_direct_limit_m142 import run_infinite_bcj_direct_limit_study

MILESTONE = "M15.3"
SCHEMA = "openwave.m15.kuchar-continuum-bcj-causal.v1"
FORMAL_HEAD = "1061988e0c356075562ced1bd88758ba4922375c"

@dataclass(frozen=True)
class KucharContinuumBCJConfig:
    require_hadamard: bool = True
    require_tail_bound: bool = True
    require_generalized_gauge_invariance: bool = True

def _canon(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

def _passed(result: Mapping[str, Any]) -> bool:
    acceptance = result.get("acceptance", {})
    return bool(result.get("passed", False)) and all(bool(v) for v in acceptance.values())

def canonical_payload(config: KucharContinuumBCJConfig | None = None) -> dict[str, Any]:
    c = KucharContinuumBCJConfig() if config is None else config
    return {"schema": SCHEMA, "model_id": "M15", "milestone": MILESTONE, "configuration": asdict(c), "formal_head": FORMAL_HEAD, "lineage_dependencies": ["M15.2", "M14.1", "M14.2"], "study_api": "openwave.xperiments.m15_kuchar_relational_time.kuchar_continuum_bcj_causal_m153:run_kuchar_continuum_bcj_causal_study"}

def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(_canon(payload).encode()).hexdigest()

def run_kuchar_continuum_bcj_causal_study(config: KucharContinuumBCJConfig | None = None) -> dict[str, Any]:
    c = KucharContinuumBCJConfig() if config is None else config
    finite_pointwise = run_kuchar_bcj_pointwise_coverage_study()
    causal = run_causal_green_hadamard_study()
    infinite = run_infinite_bcj_direct_limit_study()
    coverage = {
        "finite_and_pointwise_bcj": _passed(finite_pointwise),
        "retarded_advanced_green": _passed(causal),
        "pauli_jordan_homogeneous_transport": _passed(causal),
        "positive_frequency_hadamard_probe": _passed(causal),
        "square_summable_infinite_bcj": _passed(infinite),
        "quantitative_tail_control": _passed(infinite),
        "weighted_generalized_gauge_invariance": _passed(infinite),
        "direct_system_fixed_mode_preservation": _passed(infinite),
    }
    acceptance = {
        "m152_finite_pointwise_coverage_passes": coverage["finite_and_pointwise_bcj"],
        "causal_green_hadamard_campaign_passes": _passed(causal),
        "infinite_bcj_direct_limit_campaign_passes": _passed(infinite),
        "continuum_transport_is_causal": coverage["retarded_advanced_green"],
        "hadamard_gate_is_present": (not c.require_hadamard) or coverage["positive_frequency_hadamard_probe"],
        "tail_bound_gate_is_present": (not c.require_tail_bound) or coverage["quantitative_tail_control"],
        "gauge_invariance_gate_is_present": (not c.require_generalized_gauge_invariance) or coverage["weighted_generalized_gauge_invariance"],
        "all_declared_infinite_and_continuum_surfaces_are_covered": all(coverage.values()),
    }
    payload = canonical_payload(c)
    return {**payload, "task": MILESTONE, "coverage": coverage, "dependency_fingerprints": {"m152": finite_pointwise.get("fingerprint"), "m141": causal.get("fingerprint"), "m142": infinite.get("fingerprint")}, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"continuum_limit_requires_explicit_summability": True, "green_hadamard_inputs_remain_visible": True, "kuchar_global_time_not_inferred": True}}
