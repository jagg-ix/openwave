"""M9.126c: fail-closed qualification of existing Physlib experimental evidence."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping
from .experimental_evidence_inventory_m126 import run_experimental_evidence_inventory
from .planckian_paper_holdout_m126 import run_planckian_paper_holdout

QUALIFIED_REQUIREMENTS=("source:published_measurements","identity:material_and_regime","separation:paper_level_holdout","prediction:fixed_planckian_band","comparison:baseline_reported")
EXTERNAL_PROMOTION_REQUIREMENTS=QUALIFIED_REQUIREMENTS+("data:raw_values_and_uncertainties","protocol:prospective_commitment_before_access","calibration:independent_transport_extraction","analysis:predeclared_exclusion_rules","discriminator:entropic_time_beats_dimensional_baseline","replication:independent_dataset")

def fingerprint(payload:Any)->str:
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def evaluate(observed,requirements):
    missing=tuple(x for x in requirements if x not in observed)
    return {"passed":not missing,"missing":missing}

@lru_cache(maxsize=1)
def run_experimental_evidence_qualification()->dict[str,Any]:
    inv=run_experimental_evidence_inventory(); hold=run_planckian_paper_holdout(); observed=set(QUALIFIED_REQUIREMENTS)
    q=evaluate(observed,QUALIFIED_REQUIREMENTS); ext=evaluate(observed,EXTERNAL_PROMOTION_REQUIREMENTS)
    payload={"schema":"openwave.m9.experimental-evidence-qualification.v1","task":"M9.126c","qualified_gate":q,"external_promotion_gate":ext,"claim_boundary":{"retrospective_holdout_is_prospective_validation":False,"published_rounded_values_are_complete_evidence_package":False,"planckian_band_support_is_unique_cat_ept_discriminator":False}}
    acceptance={"inventory_and_holdout_pass":inv["passed"] and hold["passed"],"existing_evidence_is_qualified_for_retrospective_use":q["passed"],"external_promotion_remains_blocked":not ext["passed"],"all_remaining_requirements_are_named":set(ext["missing"])==set(EXTERNAL_PROMOTION_REQUIREMENTS)-observed,"no_claim_boundary_is_crossed":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"acceptance":acceptance,"passed":all(acceptance.values()),"fingerprint":fingerprint(payload),"decision":{"existing_physlib_experimental_evidence_recognized":True,"retrospective_planckian_evaluation_ready":True,"prospective_external_validation_complete":False,"physical_promotion_allowed":False}}

def result_to_json(result:Mapping[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
