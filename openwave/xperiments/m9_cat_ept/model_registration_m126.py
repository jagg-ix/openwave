"""M9.126 registration for existing experimental evidence in Physlib."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping
from .m126_existing_experimental_evidence_authority import run_m126_existing_experimental_evidence_authority
from .model_registration_m125 import canonical_registration_payload as previous_payload

def fingerprint(payload:Any)->str:return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def canonical_registration_payload()->dict[str,Any]:
 previous=previous_payload(); evidence=run_m126_existing_experimental_evidence_authority(); c=evidence["component"]; f=evidence["formal_authority"]
 return {**previous,"schema":"openwave.model-registration.v29","m9_126":{"existing_experimental_evidence_registered":evidence["passed"],"formal_authority_fingerprint":f["fingerprint"],"formal_source_count":len(f["sources"]),"merged_formal_head":f["merged_formal_head"],"development_formal_head":f["development_head"],"development_formal_branch":f["development_branch"],"zil_public_head":f["zil_public_head"],"planckian_record_count":c["experimental_record_count"],"independent_paper_count":c["paper_count"],"retrospective_paper_holdout_complete":c["retrospective_paper_holdout"],"broad_band_pass_rate":c["broad_band_pass_rate"],"existing_evidence_qualified":c["qualified_existing_evidence"],"prospective_external_validation_complete":c["prospective_external_validation"],"external_physical_promotion_allowed":False,"physical_claims_promoted":[]},"claim_boundary":{**previous["claim_boundary"],"existing_papers_are_new_external_input":False,"retrospective_holdout_is_prospective_validation":False,"planckian_consistency_uniquely_validates_cat_ept":False}}

@lru_cache(maxsize=1)
def run_model_registration_study()->dict[str,Any]:
 evidence=run_m126_existing_experimental_evidence_authority(); payload=canonical_registration_payload(); c=payload["m9_126"]
 acceptance={"M9_126_authority_passes":evidence["passed"],"schema_v29_is_current":payload["schema"]=="openwave.model-registration.v29","four_evidence_sources_are_registered":c["formal_source_count"]==4 and len(c["formal_authority_fingerprint"])==64,"eight_records_and_three_papers_are_registered":c["planckian_record_count"]==8 and c["independent_paper_count"]==3,"retrospective_holdout_is_registered":c["retrospective_paper_holdout_complete"] and c["broad_band_pass_rate"]==1.0,"qualification_does_not_promote_prospective_validation":c["existing_evidence_qualified"] and not c["prospective_external_validation_complete"],"promotion_remains_blocked":not c["external_physical_promotion_allowed"] and c["physical_claims_promoted"]==[],"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
 return {**payload,"task":"M9.126-registration","registration_fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"existing_experimental_registry_is_current":True,"retrospective_evidence_use_ready":True,"prospective_external_validation_complete":False}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
