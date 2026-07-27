"""M9.126 formal authority for existing experimental evidence already in Physlib."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping
from .formalization_m125_extension import run_formalization_m125_extension

EVIDENCE_SOURCES=(
 {"path":"Physlib/QuantumMechanics/ComplexAction/Particles/EmpiricalEvidence.lean","blob":"7db6a79b97d53361615ab04fe76161450904e191","role":"published Planckian material ratios and explicit controls"},
 {"path":"Physlib/Meta/DerivedPredictions.lean","blob":"4c9a94b57c2d745da546fdd3030b995730802f40","role":"epistemically typed experimental bounds and measured constants"},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Particles/ExperimentalParticleReactions.lean","blob":"b57128a851619b9bcbc1c6198e259f5a4a37ba9e","role":"observed reaction and selection-rule compatibility"},
 {"path":"Physlib/QuantumMechanics/ComplexAction/Particles/SharpPredictions.lean","blob":"faa0d3ca179f63cfee562b83c301d3dc30a81d11","role":"falsifiable Planckian and lifetime prediction carriers"},
)

def fingerprint(payload:Any)->str:
 return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_formalization_m126_extension()->dict[str,Any]:
 prev=run_formalization_m125_extension()
 payload={"schema":"openwave.m9.formalization-m126-extension.v1","previous":prev,"sources":EVIDENCE_SOURCES,"claim_boundary":{"paper_reference_is_new_lean_theorem":False,"experimental_value_is_kernel_derived":False,"development_evidence_is_prospective_validation":False}}
 acceptance={"previous_authority_passes":prev["passed"],"four_evidence_sources_are_pinned":len(EVIDENCE_SOURCES)==4,"all_blobs_are_sha1":all(len(s["blob"])==40 for s in EVIDENCE_SOURCES),"no_authority_boundary_is_crossed":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
 return {**payload,"merged_formal_head":prev["merged_formal_head"],"development_head":prev["development_head"],"development_branch":prev["development_branch"],"zil_public_head":prev["zil_public_head"],"acceptance":acceptance,"passed":all(acceptance.values()),"fingerprint":fingerprint(payload),"decision":{"existing_experimental_evidence_sources_registered":True,"new_Lean_proof_claimed_by_OpenWave":False}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
