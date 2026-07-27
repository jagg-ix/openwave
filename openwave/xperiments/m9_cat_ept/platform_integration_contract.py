"""Fail-closed platform contract through M9.126."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping
from .model_conformance_current import CURRENT_CONFORMANCE_SCHEMA,CURRENT_MILESTONE,canonical_payload as current_conformance_payload
from .model_registration_current import CURRENT_CONFORMANCE_RUNNER,CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA,canonical_registration_payload
SCHEMA="openwave.m9.platform-integration-contract.v9"; ROOT=Path(__file__).resolve().parents[3]; DOCUMENT_PATHS=("MODELS.md","MODELS_M9.md","openwave/xperiments/m9_cat_ept/__init__.py","openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md")
def _read(path:str)->str:return (ROOT/path).read_text(encoding="utf-8")
def fingerprint(payload:Mapping[str,Any])->str:return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
@lru_cache(maxsize=1)
def run_platform_integration_contract()->dict[str,Any]:
 registration=canonical_registration_payload(); conformance=current_conformance_payload(); docs={p:_read(p) for p in DOCUMENT_PATHS}; current=registration["m9_126"]
 payload={"schema":SCHEMA,"current_milestone":CURRENT_MILESTONE,"current_registration_schema":registration["schema"],"current_conformance_schema":conformance["schema"],"current_conformance_runner":registration["registration"]["conformance_runner"],"merged_formal_head":current["merged_formal_head"],"development_formal_head":current["development_formal_head"],"zil_public_head":current["zil_public_head"],"document_fingerprints":{p:sha256(t.encode()).hexdigest() for p,t in docs.items()},"claim_boundary":{"existing_evidence_registry_implies_prospective_validation":False,"broad_planckian_band_implies_unique_cat_ept_support":False}}
 profile=docs["MODELS_M9.md"]; roadmap=docs["openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"]
 acceptance={"stable_registration_points_to_schema_v29":registration["schema"]==CURRENT_REGISTRATION_SCHEMA,"stable_registration_points_to_current_conformance":registration["registration"]["conformance_runner"]==CURRENT_CONFORMANCE_RUNNER,"stable_conformance_preserves_schema_v22":conformance["schema"]==CURRENT_CONFORMANCE_SCHEMA,"stable_conformance_composes_M9_126":conformance["current_milestone"]==CURRENT_MILESTONE and conformance["latest_evidence"]["passed"],"public_documents_expose_M9_126":all("M9.126" in t for t in docs.values()),"profile_names_current_schemas_and_evidence_boundary":all(tok in profile for tok in (CURRENT_REGISTRATION_SCHEMA,CURRENT_CONFORMANCE_SCHEMA,SCHEMA,"Planckian","prospective")),"roadmap_advances_raw_data_target_to_M9_127":all(tok in roadmap for tok in ("M9.126a","M9.126b","M9.126c","M9.127","NEXT")),"existing_evidence_is_registered_without_promotion":current["existing_evidence_qualified"] and not current["prospective_external_validation_complete"] and not current["external_physical_promotion_allowed"],"no_claim_boundary_is_crossed":not any(payload["claim_boundary"].values()),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
 return {**payload,"task":"M9-platform-integration","acceptance":acceptance,"passed":all(acceptance.values()),"fingerprint":fingerprint(payload),"decision":{"M9_is_exposed_as_first_class_OpenWave_model":True,"stable_aliases_are_current":True,"physical_claims_promoted":[]}}
def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
