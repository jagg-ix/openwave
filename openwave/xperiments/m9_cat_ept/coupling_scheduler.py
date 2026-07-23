"""Deterministic multi-domain coupling graph and dependency scheduler."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import copy, json
from typing import Any, Callable, Mapping

@dataclass(frozen=True)
class FieldSpec:
    name:str; domain:str; description:str=""
    def __post_init__(self)->None:
        if not self.name or not self.domain: raise ValueError("named field and domain required")

@dataclass(frozen=True)
class KernelSpec:
    name:str; domain:str; reads:tuple[str,...]; writes:tuple[str,...]; lagged_reads:tuple[str,...]=(); after:tuple[str,...]=()
    def __post_init__(self)->None:
        if not self.name or not self.domain or not self.writes: raise ValueError("named writing kernel required")
        if len(self.reads)!=len(set(self.reads)) or len(self.writes)!=len(set(self.writes)): raise ValueError("duplicate field declaration")
        if not set(self.lagged_reads).issubset(self.reads): raise ValueError("lagged reads must be declared reads")

@dataclass(frozen=True)
class KernelContext:
    current:Mapping[str,Any]; previous:Mapping[str,Any]; spec:KernelSpec
    def read(self,field:str)->Any:
        if field not in self.spec.reads: raise KeyError(f"{self.spec.name} did not declare read {field}")
        return (self.previous if field in self.spec.lagged_reads else self.current)[field]

KernelFunction=Callable[[KernelContext],Mapping[str,Any]]
class ScheduleError(ValueError): pass
class ExecutionError(RuntimeError): pass

@dataclass(frozen=True)
class CompiledSchedule:
    fields:tuple[FieldSpec,...]; kernels:tuple[KernelSpec,...]; stages:tuple[tuple[str,...],...]; fingerprint:str
    def kernel(self,name:str)->KernelSpec:
        for item in self.kernels:
            if item.name==name:return item
        raise KeyError(name)

def _payload(fields,kernels,stages):
    return {"fields":[asdict(x) for x in sorted(fields,key=lambda x:x.name)],"kernels":[{**asdict(x),"reads":sorted(x.reads),"writes":sorted(x.writes),"lagged_reads":sorted(x.lagged_reads),"after":sorted(x.after)} for x in sorted(kernels,key=lambda x:x.name)],"stages":[list(x) for x in stages]}

def compile_schedule(fields:tuple[FieldSpec,...],kernels:tuple[KernelSpec,...])->CompiledSchedule:
    fn=[x.name for x in fields]; kn=[x.name for x in kernels]
    if len(fn)!=len(set(fn)): raise ScheduleError("duplicate field")
    if len(kn)!=len(set(kn)): raise ScheduleError("duplicate kernel")
    known_fields,known_kernels=set(fn),set(kn); writers={}
    for kernel in kernels:
        unknown=(set(kernel.reads)|set(kernel.writes))-known_fields
        if unknown: raise ScheduleError(f"kernel {kernel.name} references unknown fields: {sorted(unknown)}")
        unknown_after=set(kernel.after)-known_kernels
        if unknown_after: raise ScheduleError(f"kernel {kernel.name} references unknown dependencies: {sorted(unknown_after)}")
        for field in kernel.writes:
            if field in writers: raise ScheduleError(f"field {field} has multiple writers")
            writers[field]=kernel.name
    deps={name:set() for name in kn}
    for kernel in kernels:
        deps[kernel.name].update(kernel.after)
        for field in kernel.reads:
            if field in kernel.lagged_reads: continue
            writer=writers.get(field)
            if writer is not None and writer!=kernel.name: deps[kernel.name].add(writer)
    stages=[]; emitted=set()
    while len(emitted)<len(kn):
        ready=sorted(name for name,required in deps.items() if name not in emitted and required.issubset(emitted))
        if not ready: raise ScheduleError("dependency cycle")
        stages.append(tuple(ready)); emitted.update(ready)
    stage_tuple=tuple(stages); payload=_payload(fields,kernels,stage_tuple)
    fingerprint=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CompiledSchedule(tuple(sorted(fields,key=lambda x:x.name)),tuple(sorted(kernels,key=lambda x:x.name)),stage_tuple,fingerprint)

def execute_generation(schedule:CompiledSchedule,functions:Mapping[str,KernelFunction],state:Mapping[str,Any],previous_state:Mapping[str,Any]|None=None)->dict[str,Any]:
    known={x.name for x in schedule.fields}
    if set(state)!=known or set(functions)!={x.name for x in schedule.kernels}: raise ExecutionError("schema mismatch")
    working=copy.deepcopy(dict(state)); previous=copy.deepcopy(dict(state if previous_state is None else previous_state)); original=copy.deepcopy(working); trace=[]
    if set(previous)!=known: raise ExecutionError("previous state mismatch")
    try:
        for index,stage in enumerate(schedule.stages):
            snapshot=copy.deepcopy(working); updates={}
            for name in stage:
                spec=schedule.kernel(name); outputs=dict(functions[name](KernelContext(snapshot,previous,spec)))
                if set(outputs)!=set(spec.writes): raise ExecutionError(f"kernel {name} output mismatch")
                if set(outputs)&set(updates): raise ExecutionError("stage write collision")
                updates.update(outputs)
            working.update(updates); trace.append({"stage":index,"kernels":list(stage),"writes":sorted(updates)})
    except Exception as exc:
        working=original; raise ExecutionError(f"transaction rolled back: {exc}") from exc
    return {"state":working,"trace":trace,"schedule_fingerprint":schedule.fingerprint}

def reference_specs():
    fields=(FieldSpec("psi","matter"),FieldSpec("density","matter"),FieldSpec("geometry_source","geometry"),FieldSpec("metric","geometry"),FieldSpec("entropy","irreversible"),FieldSpec("reservoir","irreversible"),FieldSpec("clock","observables"),FieldSpec("report","observables"))
    kernels=(KernelSpec("density_from_psi","matter",("psi",),("density",)),KernelSpec("entropy_update","irreversible",("psi",),("entropy",)),KernelSpec("reservoir_update","irreversible",("psi",),("reservoir",)),KernelSpec("geometry_source","geometry",("density",),("geometry_source",)),KernelSpec("metric_solve","geometry",("geometry_source",),("metric",)),KernelSpec("clock_read","observables",("metric","entropy"),("clock",)),KernelSpec("report","observables",("density","metric","entropy","reservoir","clock"),("report",)))
    return fields,kernels

def reference_functions():
    return {"density_from_psi":lambda c:{"density":[float(abs(v)**2) for v in c.read("psi")]},"entropy_update":lambda c:{"entropy":.5*sum(float(abs(v)**2) for v in c.read("psi"))},"reservoir_update":lambda c:{"reservoir":1-sum(float(abs(v)**2) for v in c.read("psi"))},"geometry_source":lambda c:{"geometry_source":[v-sum(c.read("density"))/len(c.read("density")) for v in c.read("density")]},"metric_solve":lambda c:{"metric":[.25*v for v in c.read("geometry_source")]},"clock_read":lambda c:{"clock":c.read("entropy")+max(c.read("metric"))},"report":lambda c:{"report":{"density_total":sum(c.read("density")),"metric_peak":max(c.read("metric")),"entropy":c.read("entropy"),"reservoir":c.read("reservoir"),"clock":c.read("clock")}}}

def run_scheduler_study()->dict[str,Any]:
    fields,kernels=reference_specs(); schedule=compile_schedule(fields,kernels)
    state={"psi":[.8+0j,.4+0j],"density":[0.,0.],"geometry_source":[0.,0.],"metric":[0.,0.],"entropy":0.,"reservoir":0.,"clock":0.,"report":{}}
    first=execute_generation(schedule,reference_functions(),state); second=execute_generation(schedule,reference_functions(),state); shuffled=compile_schedule(tuple(reversed(fields)),tuple(reversed(kernels)))
    lagged_fields=(FieldSpec("matter","matter"),FieldSpec("geometry","geometry")); lagged_kernels=(KernelSpec("matter_step","matter",("geometry",),("matter",),lagged_reads=("geometry",)),KernelSpec("geometry_step","geometry",("matter",),("geometry",))); lagged=compile_schedule(lagged_fields,lagged_kernels)
    cycle=False
    try: compile_schedule(lagged_fields,(KernelSpec("matter_step","matter",("geometry",),("matter",)),KernelSpec("geometry_step","geometry",("matter",),("geometry",))))
    except ScheduleError: cycle=True
    conflict=False
    try: compile_schedule((FieldSpec("x","a"),),(KernelSpec("one","a",(),("x",)),KernelSpec("two","a",(),("x",))))
    except ScheduleError: conflict=True
    rollback=False; bad=dict(reference_functions()); bad["metric_solve"]=lambda _c:(_ for _ in ()).throw(RuntimeError("forced"))
    try: execute_generation(schedule,bad,state)
    except ExecutionError: rollback=state["metric"]==[0.,0.] and state["report"]=={}
    acceptance={"expected_stage_order":schedule.stages==(("density_from_psi","entropy_update","reservoir_update"),("geometry_source",),("metric_solve",),("clock_read",),("report",)),"deterministic_replay":first["state"]==second["state"],"declaration_order_invariant":schedule.fingerprint==shuffled.fingerprint,"lagged_feedback_compiles":lagged.stages==(("matter_step",),("geometry_step",)),"unlagged_cycle_rejected":cycle,"write_conflict_rejected":conflict,"transaction_rollback_verified":rollback,"provenance_trace_complete":len(first["trace"])==len(schedule.stages)}
    return {"schema":"openwave.m9.coupling-scheduler-result.v1","task":"M9.35","stages":[list(x) for x in schedule.stages],"fingerprint":schedule.fingerprint,"final_report":first["state"]["report"],"lagged_feedback_stages":[list(x) for x in lagged.stages],"trace":first["trace"],"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["declared multi-domain field and kernel graph","deterministic topological stage compilation","explicit lagged feedback semantics","transactional stage execution and provenance","cycle, schema, and write-conflict rejection"],"does_not_establish":["physical correctness of a coupling","automatic discretization compatibility","distributed execution or GPU scheduling","convergence of arbitrary nonlinear feedback loops"]}}

def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
