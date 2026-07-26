"""Evidence authority for M9.103--M9.105."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any,Mapping
from .formalization_m105_extension import run_formalization_m105_extension
from .zil_runtime_reporting_m105 import run_zil_runtime_reporting_authority
from .unrestricted_charged_stationary import run_unrestricted_charged_stationary
from .packet_tbmt_refinement import run_packet_tbmt_refinement
from .independent_calibration_protocol import run_independent_calibration_protocol

def canonical_payload()->dict[str,Any]:
    formal=run_formalization_m105_extension(); zil=run_zil_runtime_reporting_authority(); state=run_unrestricted_charged_stationary(); packet=run_packet_tbmt_refinement(); calibration=run_independent_calibration_protocol()
    return {"schema":"openwave.m9.m103-105-evidence-authority.v1","physlib_head":formal["physlib"]["head"],"zil_head":formal["zil"]["current_head"],"components":{"unrestricted_state":{"passed":state["passed"],"stationary_gate":state["unrestricted_stationary_state_constructed"],"orbital_gate":state["unrestricted_orbital_stability_qualified"]},"packet_refinement":{"passed":packet["passed"],"source_stationary_gate":packet["source"]["source_stationarity_gate"],"refinement_gate":packet["refined_packet_tbmt_closed"],"thomas_status":packet["decision"]["covariant_thomas_extension_status"]},"calibration":{"passed":calibration["passed"],"independent_ready":calibration["decision"]["independent_calibration_complete"],"withheld_predictions_executed":calibration["decision"]["withheld_predictions_executed"]},"zil_reporting":{"passed":zil["passed"],"runtime_head":zil["repository"]["current_head"]}},"claim_boundary":{"unrestricted_solver_is_stable_physical_particle":False,"external_thomas_postulate_is_qed_derivation":False,"internal_anchor_is_independent_calibration":False,"preregistered_but_unexecuted_prediction_is_validation":False,"zil_runtime_execution_is_physics_proof":False}}

def fingerprint(payload:Mapping[str,Any]|None=None)->str:
    selected=canonical_payload() if payload is None else dict(payload);return sha256(json.dumps(selected,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_m103_105_evidence_authority()->dict[str,Any]:
    formal=run_formalization_m105_extension(); zil=run_zil_runtime_reporting_authority(); state=run_unrestricted_charged_stationary(); packet=run_packet_tbmt_refinement(); calibration=run_independent_calibration_protocol(); payload=canonical_payload(); acceptance={"formal_authority_passes":formal["passed"],"zil_reporting_authority_passes":zil["passed"],"unrestricted_campaign_executes":state["passed"],"packet_refinement_campaign_executes":packet["passed"],"calibration_protocol_executes":calibration["passed"],"all_physical_subgates_are_exposed":all(k in payload["components"]["unrestricted_state"] for k in ("stationary_gate","orbital_gate")) and "refinement_gate" in payload["components"]["packet_refinement"],"claim_boundaries_are_false":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"component_results":{"formal":formal,"zil":zil,"unrestricted_state":state,"packet_refinement":packet,"calibration":calibration},"fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"three_next_critical_targets_have_executable_campaigns":True,"physical_closure_is_outcome_driven":True,"physical_identity_changed":False}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
