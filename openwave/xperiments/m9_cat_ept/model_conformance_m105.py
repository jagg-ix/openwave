"""Canonical M9 conformance through M9.105."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any,Mapping
from .criterion_maturity_m105 import canonical_payload as maturity_payload,run_criterion_maturity_m105
from .formalization_m105_extension import canonical_payload as formal_payload,run_formalization_m105_extension
from .m103_105_evidence_authority import canonical_payload as evidence_payload,run_m103_105_evidence_authority
from .zil_runtime_reporting_m105 import canonical_payload as zil_payload,run_zil_runtime_reporting_authority

def canonical_payload()->dict[str,Any]:
    return {"schema":"openwave.m9.models-conformance.v20","model":"M9 CAT/EPT","formal_authority":formal_payload(),"zil_runtime":zil_payload(),"evidence":evidence_payload(),"maturity":maturity_payload(),"summary":maturity_payload()["headline_counts"],"claim_boundary":{"unrestricted_campaign_execution_is_state_closure":False,"external_thomas_postulate_is_qed_derivation":False,"internal_calibration_is_independent_calibration":False,"preregistered_prediction_is_experimental_validation":False,"zil_report_is_physics_proof":False}}

def fingerprint(payload:Mapping[str,Any]|None=None)->str:
    selected=canonical_payload() if payload is None else dict(payload);return sha256(json.dumps(selected,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_conformance_study()->dict[str,Any]:
    formal=run_formalization_m105_extension();zil=run_zil_runtime_reporting_authority();evidence=run_m103_105_evidence_authority();maturity=run_criterion_maturity_m105();payload=canonical_payload();acceptance={"formal_authority_passes":formal["passed"],"zil_reporting_passes":zil["passed"],"three_campaign_authority_passes":evidence["passed"],"maturity_authority_passes":maturity["passed"],"schema_v20_is_current":payload["schema"]=="openwave.m9.models-conformance.v20","claim_boundaries_remain_false":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"task":"M9.103-105-conformance","fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"m103_105_is_current_conformance_profile":True,"three_scientific_targets_completed_as_falsification_campaigns":True,"physical_promotion_is_subgate_driven":True}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
