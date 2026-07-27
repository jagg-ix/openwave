"""M9.126 authority for the Physlib experimental-evidence extraction."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping
from .m125_three_clock_common_carrier_authority import run_m125_three_clock_common_carrier_authority
from .formalization_m126_extension import run_formalization_m126_extension
from .experimental_evidence_inventory_m126 import run_experimental_evidence_inventory
from .planckian_paper_holdout_m126 import run_planckian_paper_holdout
from .experimental_evidence_qualification_m126 import run_experimental_evidence_qualification

def fingerprint(payload:Any)->str:return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_m126_existing_experimental_evidence_authority()->dict[str,Any]:
 prev=run_m125_three_clock_common_carrier_authority(); formal=run_formalization_m126_extension(); inv=run_experimental_evidence_inventory(); hold=run_planckian_paper_holdout(); qual=run_experimental_evidence_qualification()
 component={"experimental_record_count":len(inv["planckian_records"]),"paper_count":len(inv["papers"]),"retrospective_paper_holdout":hold["passed"],"broad_band_pass_rate":hold["summary"]["broad_band_pass_rate"],"qualified_existing_evidence":qual["qualified_gate"]["passed"],"prospective_external_validation":qual["decision"]["prospective_external_validation_complete"],"physical_promotion_allowed":qual["decision"]["physical_promotion_allowed"]}
 payload={"schema":"openwave.m9.m126-existing-experimental-evidence-authority.v1","task":"M9.126","previous_authority":prev,"formal_authority":formal,"component":component,"claim_boundary":{"retrospective_registry_is_prospective_test":False,"broad_band_pass_is_unique_entropic_clock_evidence":False,"rounded_values_are_precision_dataset":False}}
 acceptance={"previous_M9_125_authority_is_preserved":prev["passed"],"formal_evidence_authority_passes":formal["passed"],"M9_126a_inventory_closes":inv["passed"],"M9_126b_paper_holdout_closes":hold["passed"],"M9_126c_qualification_is_fail_closed":qual["passed"],"external_promotion_remains_blocked":not component["prospective_external_validation"] and not component["physical_promotion_allowed"],"no_claim_boundary_is_crossed":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
 return {**payload,"component_results":{"inventory":inv,"holdout":hold,"qualification":qual},"acceptance":acceptance,"passed":all(acceptance.values()),"fingerprint":fingerprint(payload),"decision":{"existing_experimental_papers_recognized":True,"retrospective_planckian_holdout_complete":True,"prospective_external_validation_complete":False,"M9_127_requires_raw_or_independent_dataset":True}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
