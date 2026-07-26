"""M9.105: independent calibration and preregistered prediction protocol."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any,Literal,Mapping,Sequence
from .clock_action_rate_calibration import run_clock_action_rate_calibration
from .formalization_m105_extension import CURRENT_ZIL_HEAD
from .formalization_m102_extension import CURRENT_FORMAL_HEAD
EvidenceClass=Literal["definition","external","internal","derived","absent"]

@dataclass(frozen=True)
class CalibrationAnchor:
    name:str; value:float|None; unit:str; evidence_class:EvidenceClass; source:str; depends_on:tuple[str,...]=(); target_dependencies:tuple[str,...]=()
    @property
    def independent(self)->bool:
        return self.value is not None and self.evidence_class in ("definition","external") and not self.target_dependencies

REQUIRED_INDEPENDENT=("sigma0","clock_frequency","mass","charge_unit","force_unit")

def default_anchors()->tuple[CalibrationAnchor,...]:
    clock=run_clock_action_rate_calibration(); omega=float(clock["measured_internal_frequency"]); mass=float(clock["compton_clock_mass"]); yukawa=float(clock["isolated_yukawa"])
    return (
        CalibrationAnchor("hbar",1.0,"natural-action","definition","OpenWave natural-unit convention"),
        CalibrationAnchor("c",1.0,"natural-speed","definition","OpenWave natural-unit convention"),
        CalibrationAnchor("higgs_scale",1.0,"natural-energy","internal","M9.101 default"),
        CalibrationAnchor("sigma0",1.0,"lattice-length","internal","M9.101 inference width"),
        CalibrationAnchor("clock_frequency",omega,"inverse-time","internal","M9.71 radial mode",target_dependencies=("de_broglie_clock",)),
        CalibrationAnchor("mass",mass,"energy/c^2","derived","m=hbar*omega/c^2",depends_on=("hbar","clock_frequency","c"),target_dependencies=("de_broglie_clock","electron_rest_energy")),
        CalibrationAnchor("yukawa",yukawa,"dimensionless","derived","y=sqrt(2)*hbar*omega/(c^2*v)",depends_on=("hbar","clock_frequency","c","higgs_scale"),target_dependencies=("de_broglie_clock",)),
        CalibrationAnchor("charge_unit",1.0,"winding-third","internal","q=n/3",target_dependencies=("charge_quantization","electric_force")),
        CalibrationAnchor("force_unit",None,"physical-force","absent","no independent conversion registered",depends_on=("mass","charge_unit"),target_dependencies=("electric_force","magnetic_force")),
    )

def anchor_map(anchors:Sequence[CalibrationAnchor])->dict[str,CalibrationAnchor]:
    result={a.name:a for a in anchors}
    if len(result)!=len(anchors): raise ValueError("duplicate calibration anchor")
    return result

def dependency_cycles(anchors:Sequence[CalibrationAnchor])->list[list[str]]:
    table=anchor_map(anchors); visiting=set(); visited=set(); cycles=[]
    def visit(name:str,path:list[str])->None:
        if name in visiting:
            start=path.index(name) if name in path else 0; cycles.append(path[start:]+[name]); return
        if name in visited or name not in table:return
        visiting.add(name)
        for dep in table[name].depends_on:visit(dep,path+[name])
        visiting.remove(name); visited.add(name)
    for name in table:visit(name,[])
    return cycles

def calibration_audit(anchors:Sequence[CalibrationAnchor])->dict[str,Any]:
    table=anchor_map(anchors); cycles=dependency_cycles(anchors); missing=sorted({d for a in anchors for d in a.depends_on if d not in table}); required={name:{"present":name in table,"independent":bool(name in table and table[name].independent),"evidence_class":table[name].evidence_class if name in table else "absent","target_dependencies":list(table[name].target_dependencies) if name in table else []} for name in REQUIRED_INDEPENDENT}; ready=not cycles and not missing and all(r["independent"] for r in required.values())
    return {"anchors":[asdict(a) for a in anchors],"required_independent":required,"dependency_cycles":cycles,"missing_dependencies":missing,"independent_calibration_ready":ready,"self_fitted_targets":sorted({t for a in anchors for t in a.target_dependencies})}

PREDICTIONS=(
    {"id":"CAT-EPT-M9.105-G-FROM-SIGMA0","observable":"Newton coupling from independently measured sigma0","required_anchors":("sigma0","hbar","c"),"failure_rule":"reject if frozen sigma0 misses withheld G gate"},
    {"id":"CAT-EPT-M9.105-CLOCK-MASS","observable":"clock frequency and mass on a withheld state","required_anchors":("clock_frequency","mass","hbar","c"),"failure_rule":"reject if independent mass and clock disagree"},
    {"id":"CAT-EPT-M9.105-FORCE-SCALE","observable":"force across withheld separations","required_anchors":("mass","charge_unit","force_unit"),"failure_rule":"reject if frozen units fail multi-distance gate"},
)

def prediction_readiness(audit:Mapping[str,Any])->list[dict[str,Any]]:
    required=audit["required_independent"]; rows=[]
    for p in PREDICTIONS:
        missing=[n for n in p["required_anchors"] if n in required and not required[n]["independent"]]; rows.append({**p,"missing_independent_anchors":missing,"ready":not missing and audit["independent_calibration_ready"],"executed":False})
    return rows

def validate_external_anchor_bundle(payload:Mapping[str,Any])->dict[str,Any]:
    raw=payload.get("anchors"); errors=[]
    if not isinstance(raw,list):return {"passed":False,"errors":["anchors must be a list"]}
    anchors=[]
    for i,row in enumerate(raw):
        try: anchors.append(CalibrationAnchor(str(row["name"]),None if row.get("value") is None else float(row["value"]),str(row["unit"]),str(row["evidence_class"]),str(row["source"]),tuple(map(str,row.get("depends_on",[]))),tuple(map(str,row.get("target_dependencies",[])))))
        except Exception as exc: errors.append(f"anchor {i}: {exc}")
    if errors:return {"passed":False,"errors":errors}
    audit=calibration_audit(anchors)
    if not audit["independent_calibration_ready"]:errors.append("independent calibration prerequisites do not close")
    return {"passed":not errors,"errors":errors,"audit":audit}

def fingerprint(payload:Mapping[str,Any])->str:return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_independent_calibration_protocol()->dict[str,Any]:
    audit=calibration_audit(default_anchors()); predictions=prediction_readiness(audit); payload={"schema":"openwave.m9.independent-calibration-protocol.v1","task":"M9.105","physlib_head":CURRENT_FORMAL_HEAD,"zil_head":CURRENT_ZIL_HEAD,"audit":audit,"preregistered_predictions":predictions,"policy":{"internal_anchor_is_not_independent_calibration":True,"derived_identity_is_not_external_measurement":True,"target_used_to_fit_anchor_blocks_prediction":True,"predictions_require_frozen_independent_anchors":True}}
    acceptance={"dependency_graph_is_well_formed":not audit["dependency_cycles"] and not audit["missing_dependencies"],"five_required_anchor_classes_are_audited":set(audit["required_independent"])==set(REQUIRED_INDEPENDENT),"current_internal_defaults_are_not_overpromoted":not audit["independent_calibration_ready"],"self_fitted_targets_are_explicit":bool(audit["self_fitted_targets"]),"three_predictions_have_failure_rules":len(predictions)==3 and all(r["failure_rule"] for r in predictions),"unready_predictions_are_not_executed":all(not r["executed"] for r in predictions if not r["ready"]),"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"independent_calibration_complete":audit["independent_calibration_ready"],"withheld_predictions_executed":any(r["executed"] for r in predictions),"physical_units_calibrated":False,"current_model_promoted":False}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
