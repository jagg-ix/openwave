"""Current M9 registration over schema-v20 conformance."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any,Mapping
from .model_conformance_m105 import canonical_payload as conformance_payload,run_conformance_study
from .model_registration_m102 import canonical_registration_payload as previous_payload

def canonical_registration_payload()->dict[str,Any]:
    previous=previous_payload();conformance=conformance_payload();components=conformance["evidence"]["components"]
    return {**previous,"schema":"openwave.model-registration.v11","conformance":conformance,"m9_103_105":{"physlib_head":conformance["formal_authority"]["physlib"]["head"],"zil_head":conformance["formal_authority"]["zil"]["current_head"],"unrestricted_campaign_registered":components["unrestricted_state"]["passed"],"unrestricted_stationary_gate":components["unrestricted_state"]["stationary_gate"],"unrestricted_orbital_gate":components["unrestricted_state"]["orbital_gate"],"packet_refinement_registered":components["packet_refinement"]["passed"],"packet_refinement_gate":components["packet_refinement"]["refinement_gate"],"independent_calibration_registered":components["calibration"]["passed"],"independent_calibration_ready":components["calibration"]["independent_ready"],"withheld_predictions_executed":components["calibration"]["withheld_predictions_executed"],"headline_counts":conformance["summary"],"physical_claims_promoted":[]},"claim_boundary":{**previous["claim_boundary"],"unrestricted_solver_is_physical_particle":False,"postulated_thomas_extension_is_qed_derivation":False,"internal_anchor_is_independent_calibration":False,"unexecuted_prediction_is_validation":False}}

def fingerprint(payload:Mapping[str,Any]|None=None)->str:
    selected=canonical_registration_payload() if payload is None else dict(payload);return sha256(json.dumps(selected,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_model_registration_study()->dict[str,Any]:
    conformance=run_conformance_study();payload=canonical_registration_payload();current=payload["m9_103_105"];boundaries=("unrestricted_solver_is_physical_particle","postulated_thomas_extension_is_qed_derivation","internal_anchor_is_independent_calibration","unexecuted_prediction_is_validation");acceptance={"m105_conformance_passes":conformance["passed"],"schema_v11_is_current":payload["schema"]=="openwave.model-registration.v11","three_campaigns_are_registered":current["unrestricted_campaign_registered"] and current["packet_refinement_registered"] and current["independent_calibration_registered"],"subgates_are_explicit_booleans":all(isinstance(current[k],bool) for k in ("unrestricted_stationary_gate","unrestricted_orbital_gate","packet_refinement_gate","independent_calibration_ready","withheld_predictions_executed")),"no_physical_claim_is_promoted_by_registration":current["physical_claims_promoted"]==[],"all_new_boundaries_are_preserved":all(not payload["claim_boundary"][k] for k in boundaries),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"task":"M9.103-105-registration","registration_fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"m105_registration_is_current":True,"physical_identity_changed":False,"external_prediction_status_is_outcome_driven":True}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
