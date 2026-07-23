import pytest
from openwave.xperiments.m9_cat_ept.coupling_scheduler import ExecutionError, FieldSpec, KernelSpec, ScheduleError, compile_schedule, execute_generation, reference_functions, reference_specs, run_scheduler_study

def test_expected_reference_schedule():
    f,k=reference_specs(); s=compile_schedule(f,k); assert s.stages[0]==("density_from_psi","entropy_update","reservoir_update") and s.stages[-1]==("report",)

def test_declaration_order_invariant():
    f,k=reference_specs(); assert compile_schedule(f,k).fingerprint==compile_schedule(tuple(reversed(f)),tuple(reversed(k))).fingerprint

def test_unknown_field_rejected():
    with pytest.raises(ScheduleError): compile_schedule((FieldSpec("x","d"),),(KernelSpec("k","d",("missing",),("x",)),))

def test_write_conflict_rejected():
    with pytest.raises(ScheduleError): compile_schedule((FieldSpec("x","d"),),(KernelSpec("a","d",(),("x",)),KernelSpec("b","d",(),("x",))))

def test_unlagged_cycle_rejected():
    f=(FieldSpec("a","d"),FieldSpec("b","d"))
    with pytest.raises(ScheduleError): compile_schedule(f,(KernelSpec("ka","d",("b",),("a",)),KernelSpec("kb","d",("a",),("b",))))

def test_lagged_cycle_compiles():
    f=(FieldSpec("a","d"),FieldSpec("b","d")); s=compile_schedule(f,(KernelSpec("ka","d",("b",),("a",),lagged_reads=("b",)),KernelSpec("kb","d",("a",),("b",))))
    assert s.stages==(("ka",),("kb",))

def test_transaction_rolls_back():
    f,k=reference_specs(); s=compile_schedule(f,k); state={"psi":[.8+0j,.4+0j],"density":[0,0],"geometry_source":[0,0],"metric":[0,0],"entropy":0.,"reservoir":0.,"clock":0.,"report":{}}; funcs=reference_functions(); funcs["metric_solve"]=lambda _c:(_ for _ in ()).throw(RuntimeError("forced"))
    with pytest.raises(ExecutionError): execute_generation(s,funcs,state)
    assert state["metric"]==[0,0] and state["report"]=={}

def test_full_study_passes():
    r=run_scheduler_study(); assert r["passed"] and all(r["acceptance"].values())
