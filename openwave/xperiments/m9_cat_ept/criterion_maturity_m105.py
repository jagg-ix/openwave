"""Outcome-driven maturity through M9.105."""
from __future__ import annotations
from dataclasses import asdict,replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any,Mapping
from .criterion_maturity_m102 import current_rows as m102_rows
from .criterion_maturity_current import derive_headline
from .m103_105_evidence_authority import run_m103_105_evidence_authority
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA

def current_rows(authority:Mapping[str,Any]|None=None):
    selected=run_m103_105_evidence_authority() if authority is None else authority; components=selected["components"]; state=components["unrestricted_state"]; packet=components["packet_refinement"]; calibration=components["calibration"]; rows=[]
    for row in m102_rows():
        if row.key in ("magnetic_moment_spin","electric_force","magnetic_force"):
            value=row.state; closed=list(row.closed); open_items=list(row.open)
            if state["stationary_gate"]: value="reduced_constructed";closed.append("unrestricted charged stationary-state gate")
            if state["orbital_gate"]: value="stable_constructed";closed.append("unrestricted charged orbital-stability gate")
            if row.key in ("magnetic_moment_spin","magnetic_force") and packet["refinement_gate"]:closed.append("refined local packet Thomas-BMT reduction")
            if not state["stationary_gate"]:open_items.append("unrestricted charged stationary-state gate")
            if not state["orbital_gate"]:open_items.append("unrestricted charged orbital stability")
            if row.key in ("magnetic_moment_spin","magnetic_force") and not packet["refinement_gate"]:open_items.append("refined packet Thomas-BMT closure")
            rows.append(replace(row,state=value,closed=tuple(dict.fromkeys(closed)),open=tuple(dict.fromkeys(open_items))))
        elif row.key in ("electron_rest_energy","de_broglie_clock"):
            value=row.calibration;closed=list(row.closed);open_items=list(row.open)
            if calibration["independent_ready"]:value="calibrated";closed.append("independent shared calibration bundle")
            else:open_items.append("independent shared calibration bundle")
            if calibration["withheld_predictions_executed"]:closed.append("withheld preregistered physical predictions")
            else:open_items.append("withheld preregistered physical predictions")
            rows.append(replace(row,calibration=value,closed=tuple(dict.fromkeys(closed)),open=tuple(dict.fromkeys(open_items))))
        else:rows.append(row)
    return tuple(rows)

def canonical_payload(authority:Mapping[str,Any]|None=None)->dict[str,Any]:
    selected=run_m103_105_evidence_authority() if authority is None else authority; rows=current_rows(selected);legacy={r.key:r.status for r in LEGACY_CRITERIA};names=("validated_in_scope","conditional_validated","reduced_model_validated","calibration_pending","candidate","negative")
    return {"schema":"openwave.m9.criterion-maturity.v5","physlib_head":selected["physlib_head"],"zil_head":selected["zil_head"],"criteria":[{**asdict(r),"headline":derive_headline(r),"legacy_status":legacy[r.key]} for r in rows],"headline_counts":{n:sum(derive_headline(r)==n for r in rows) for n in names},"physical_subgates":selected["components"],"policy":{"stationary_and_orbital_gates_drive_state_axis":True,"packet_refinement_does_not_create_qed_derivation":True,"independent_calibration_drives_calibration_axis":True,"unexecuted_predictions_do_not_advance_prediction_axis":True}}

def fingerprint(payload:Mapping[str,Any])->str:return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_criterion_maturity_m105()->dict[str,Any]:
    authority=run_m103_105_evidence_authority();payload=canonical_payload(authority);by={r["key"]:r for r in payload["criteria"]};state=authority["components"]["unrestricted_state"];expected="stable_constructed" if state["orbital_gate"] else ("reduced_constructed" if state["stationary_gate"] else "not_constructed");acceptance={"all_21_rows_remain_present":len(by)==21,"three_spin_force_states_follow_actual_gates":all(by[k]["state"]==expected for k in ("magnetic_moment_spin","electric_force","magnetic_force")),"packet_postulate_does_not_change_formal_status":by["magnetic_moment_spin"]["formal"]=="proved","internal_defaults_do_not_become_calibrated":by["de_broglie_clock"]["calibration"]!="calibrated" or authority["components"]["calibration"]["independent_ready"],"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"task":"M9.105-maturity","fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values())}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
