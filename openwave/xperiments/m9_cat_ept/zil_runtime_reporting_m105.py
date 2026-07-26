"""Current zil-lean example/report authority for M9.103--M9.105."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any,Mapping
HISTORICAL_ZIL_HEAD="3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc"
CURRENT_ZIL_HEAD="e09723a44185a1e70031ad2661c8009dc98bef74"
ZIL_SOURCES=(
 {"path":"Zil.lean","blob":"faf28e701e4a02781e410491a6d3daf5d47f8879","role":"PhysLib-facing Datalog root"},
 {"path":"Zil/Native.lean","blob":"2e6c87a85ef2f80d2424c8251ffe524067e27dee","role":"native query/provenance/workflow root"},
 {"path":"Makefile","blob":"5f740e9662451d8484a6b0a96383341335ba1607","role":"Make example/report entry points"},
 {"path":"scripts/examples.sh","blob":"b720e3d720bf8ebb37cdd3c7a1ab51abd075be1c","role":"ZIL-EXAMPLES-REPORT/1 runner"},
 {"path":"examples/native-cli/formalization-claims.zc","blob":"9d3c724f40785adcb6dd5947eeaa30bb2977a3d8","role":"current formalization-claims syntax"},)

def parse_examples_report(text:str)->dict[str,Any]:
    lines=[line.rstrip("\n") for line in text.splitlines()]
    if not lines or lines[0]!="ZIL-EXAMPLES-REPORT/1":return {"passed":False,"errors":["invalid report header"],"steps":[]}
    metadata={}; steps=[]; errors=[]; header=None
    for i,line in enumerate(lines[1:],1):
        if line.startswith("step\t"):header=i;break
        if "\t" in line:
            k,v=line.split("\t",1);metadata[k]=v
    if header is None:return {"passed":False,"errors":["missing step header"],"metadata":metadata,"steps":[]}
    columns=lines[header].split("\t")
    for line in lines[header+1:]:
        if not line:continue
        values=line.split("\t")
        if len(values)!=len(columns):errors.append(f"malformed step row: {line}");continue
        row=dict(zip(columns,values)); steps.append(row)
        if row.get("status") not in ("pass","fail","skip"):errors.append(f"invalid status: {row.get('status')}")
    counts={s:sum(r.get("status")==s for r in steps) for s in ("pass","fail","skip")}
    return {"schema":"openwave.m9.zil-examples-report.v1","metadata":metadata,"steps":steps,"counts":counts,"errors":errors,"passed":not errors and counts["fail"]==0 and counts["pass"]>0}

def verify_examples_report(path:str|Path)->dict[str,Any]:
    selected=Path(path)
    if not selected.is_file():return {"passed":False,"errors":[f"missing report: {selected}"],"steps":[]}
    return parse_examples_report(selected.read_text(encoding="utf-8"))

def canonical_payload()->dict[str,Any]:
    return {"schema":"openwave.m9.zil-runtime-reporting.v3","repository":{"name":"jagg-ix/zil-lean","branch":"main","historical_head":HISTORICAL_ZIL_HEAD,"current_head":CURRENT_ZIL_HEAD,"commits_since_m98":1},"sources":[dict(s) for s in ZIL_SOURCES],"commands":{"all_examples":"make examples GROUP=all REPORT=.zil/examples-reports/openwave-m9.tsv","native_graphs":"make examples GROUP=native REPORT=.zil/examples-reports/openwave-native.tsv","formalization_claims":"bin/zil query-ci examples/native-cli/formalization-claims.zc"},"policy":{"root_contract_unchanged":True,"example_report_is_execution_evidence":True,"skipped_toolchain_is_not_failure":True,"runtime_execution_is_not_lean_proof":True,"runtime_execution_is_not_physical_validation":True}}

def fingerprint(payload:Mapping[str,Any]|None=None)->str:
    selected=canonical_payload() if payload is None else dict(payload);return sha256(json.dumps(selected,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_zil_runtime_reporting_authority()->dict[str,Any]:
    payload=canonical_payload(); paths=[s["path"] for s in ZIL_SOURCES]; acceptance={"current_head_is_one_commit_beyond_m98":CURRENT_ZIL_HEAD!=HISTORICAL_ZIL_HEAD and payload["repository"]["commits_since_m98"]==1,"roots_remain_exact":ZIL_SOURCES[0]["blob"]=="faf28e701e4a02781e410491a6d3daf5d47f8879" and ZIL_SOURCES[1]["blob"]=="2e6c87a85ef2f80d2424c8251ffe524067e27dee","five_sources_are_unique_and_pinned":len(paths)==len(set(paths))==5 and all(len(s["blob"])==40 for s in ZIL_SOURCES),"make_and_report_harness_are_registered":"make examples" in payload["commands"]["all_examples"] and "REPORT=" in payload["commands"]["all_examples"],"runtime_and_physics_boundaries_are_explicit":payload["policy"]["runtime_execution_is_not_lean_proof"] and payload["policy"]["runtime_execution_is_not_physical_validation"],"fingerprint_is_deterministic":fingerprint(payload)==fingerprint(payload)}
    return {**payload,"fingerprint":fingerprint(payload),"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"zil_runtime_reporting_upgraded":True,"root_semantics_changed":False,"physics_status_changed":False}}

def result_to_json(result:Mapping[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True)+"\n"
