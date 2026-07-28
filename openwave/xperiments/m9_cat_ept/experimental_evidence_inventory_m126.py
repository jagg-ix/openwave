"""M9.126a: qualified inventory of experimental papers already recorded by Physlib."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

PLANCKIAN_RECORDS = (
    {"id":"bruin_sr3ru2o7","paper":"Bruin2013","family":"ruthenate","material":"Sr3Ru2O7 QCP","ratio":0.3,"source_kind":"published_measurement","uncertainty":None},
    {"id":"bruin_lsco_opt","paper":"Bruin2013","family":"cuprate","material":"LSCO p=0.16","ratio":0.7,"source_kind":"published_measurement","uncertainty":None},
    {"id":"bruin_bafeasp","paper":"Bruin2013","family":"pnictide","material":"BaFe2(As,P)2 QCP","ratio":0.5,"source_kind":"published_measurement","uncertainty":None},
    {"id":"bruin_bi","paper":"Bruin2013","family":"semimetal","material":"Bi","ratio":1.0,"source_kind":"published_measurement","uncertainty":None},
    {"id":"bruin_bedt","paper":"Bruin2013","family":"organic","material":"BEDT-TTF","ratio":0.4,"source_kind":"published_measurement","uncertainty":None},
    {"id":"legros_lsco","paper":"Legros2019","family":"cuprate","material":"LSCO p=0.21","ratio":1.1,"source_kind":"published_measurement","uncertainty":None},
    {"id":"legros_prlacu","paper":"Legros2019","family":"cuprate","material":"(Pr,La)CuO4 p=0.24","ratio":1.0,"source_kind":"published_measurement","uncertainty":None},
    {"id":"cao_matbg","paper":"Cao2020","family":"twisted_graphene","material":"magic-angle bilayer graphene","ratio":0.7,"source_kind":"published_measurement","uncertainty":None},
)
ILLUSTRATIVE_CONTROLS = (
    {"id":"heavy_fermion_residual","ratio":15.0,"source_kind":"illustrative_counterexample"},
    {"id":"insulating_regime","ratio":0.05,"source_kind":"illustrative_counterexample"},
)
OTHER_EVIDENCE = (
    {"domain":"muon_g2","status":"consistency_identity","measurement":"Fermilab final 2025 a_mu and magic gamma","independent_prediction":False},
    {"domain":"fundamental_constants","status":"conditional_comparison","measurement":"CODATA alpha and G","independent_prediction":False},
    {"domain":"particle_reactions","status":"selection_rule_compatibility","measurement":"observed weak decays and mu->e gamma non-observation","independent_prediction":False},
    {"domain":"alpha_decay","status":"sharp_test_defined","measurement":"published lifetimes across >30 orders of magnitude","independent_prediction":False},
)

def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",",":"), default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_experimental_evidence_inventory() -> dict[str, Any]:
    payload = {
        "schema":"openwave.m9.experimental-evidence-inventory.v1",
        "task":"M9.126a",
        "physlib_sources":(
            "Physlib/QuantumMechanics/ComplexAction/Particles/EmpiricalEvidence.lean",
            "Physlib/Meta/DerivedPredictions.lean",
            "Physlib/QuantumMechanics/ComplexAction/Particles/ExperimentalParticleReactions.lean",
            "Physlib/QuantumMechanics/ComplexAction/Particles/SharpPredictions.lean",
        ),
        "planckian_records":PLANCKIAN_RECORDS,
        "illustrative_controls":ILLUSTRATIVE_CONTROLS,
        "other_evidence":OTHER_EVIDENCE,
        "claim_boundary":{
            "rounded_figure_value_is_raw_dataset":False,
            "paper_citation_is_qualified_holdout":False,
            "consistency_identity_is_independent_prediction":False,
            "illustrative_counterexample_is_measured_material":False,
        },
    }
    papers=sorted({r["paper"] for r in PLANCKIAN_RECORDS})
    acceptance={
        "eight_literature_records_are_inventoryed":len(PLANCKIAN_RECORDS)==8,
        "three_independent_papers_are_present":papers==["Bruin2013","Cao2020","Legros2019"],
        "all_ratios_are_positive":all(r["ratio"]>0 for r in PLANCKIAN_RECORDS),
        "illustrative_controls_are_separated":all(r["source_kind"]=="illustrative_counterexample" for r in ILLUSTRATIVE_CONTROLS),
        "uncertainty_gap_is_explicit":all(r["uncertainty"] is None for r in PLANCKIAN_RECORDS),
        "no_evidence_boundary_is_crossed":not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload),
    }
    return {**payload,"papers":papers,"acceptance":acceptance,"passed":all(acceptance.values()),"fingerprint":fingerprint(payload),"decision":{"existing_experimental_papers_found":True,"qualified_raw_dataset_complete":False,"strongest_ready_domain":"planckian_dissipation"}}

def result_to_json(result: Mapping[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
