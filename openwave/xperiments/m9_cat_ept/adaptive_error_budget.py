"""Adaptive refinement and propagated numerical error budgets."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json,math
from typing import Any,Callable

@dataclass(frozen=True)
class BudgetConfig:
    total_tolerance:float=1e-5; temporal_fraction:float=.25; spatial_fraction:float=.25; domain_fraction:float=.25; coupling_fraction:float=.25; safety_factor:float=1.25; max_refinements:int=16
    def __post_init__(self)->None:
        fractions=(self.temporal_fraction,self.spatial_fraction,self.domain_fraction,self.coupling_fraction)
        if self.total_tolerance<=0 or self.safety_factor<1: raise ValueError("invalid tolerance")
        if any(x<=0 for x in fractions) or abs(sum(fractions)-1)>1e-12: raise ValueError("allocation fractions must be positive and sum to one")
        if self.max_refinements<1: raise ValueError("positive refinement limit required")
    def allocations(self):
        return {"temporal":self.total_tolerance*self.temporal_fraction,"spatial":self.total_tolerance*self.spatial_fraction,"domain":self.total_tolerance*self.domain_fraction,"coupling":self.total_tolerance*self.coupling_fraction}

def heun_decay(steps:int)->float:
    if steps<1: raise ValueError("positive step count required")
    dt=1/steps; value=1.
    for _ in range(steps):
        predictor=value-dt*value; value+=.5*dt*(-value-predictor)
    return value

def trapezoid_sine(intervals:int)->float:
    if intervals<2: raise ValueError("at least two intervals required")
    dx=math.pi/intervals; values=[math.sin(i*dx) for i in range(intervals+1)]
    return dx*(.5*values[0]+sum(values[1:-1])+.5*values[-1])

def gaussian_mass(half_width:float)->float:
    if half_width<=0: raise ValueError("positive half-width required")
    return math.erf(half_width)

def coupling_map(value:float)->float:return .2+.5*math.cos(value)
def coupling_iterate(iterations:int,initial:float=0.)->float:
    if iterations<1: raise ValueError("positive iteration count required")
    value=initial
    for _ in range(iterations): value=coupling_map(value)
    return value

def coupling_reference()->float:
    value=.6
    for _ in range(30): value-=(value-coupling_map(value))/(1+.5*math.sin(value))
    return value

def richardson_estimate(coarse:float,fine:float,order:float,safety:float)->float:
    return safety*abs(fine-coarse)/(2**order-1)

def refine_power(name:str,evaluator:Callable[[int],float],initial:int,order:float,tolerance:float,cfg:BudgetConfig):
    level=initial; coarse=evaluator(level); history=[]
    for refinement in range(cfg.max_refinements):
        fine_level=2*level; fine=evaluator(fine_level); estimate=richardson_estimate(coarse,fine,order,cfg.safety_factor); history.append({"level":fine_level,"value":fine,"estimated_error":estimate})
        if estimate<=tolerance: return {"name":name,"method":"richardson","level":fine_level,"value":fine,"estimated_error":estimate,"allocated_tolerance":tolerance,"history":history,"refinements":refinement+1}
        level,coarse=fine_level,fine
    raise RuntimeError(f"{name} failed to meet error budget")

def refine_domain(tolerance:float,cfg:BudgetConfig):
    width=2.; history=[]
    for refinement in range(cfg.max_refinements):
        value=gaussian_mass(width); estimate=math.erfc(width); history.append({"level":width,"value":value,"estimated_error":estimate})
        if estimate<=tolerance:return {"name":"domain","method":"analytic-tail-bound","level":width,"value":value,"estimated_error":estimate,"allocated_tolerance":tolerance,"history":history,"refinements":refinement+1}
        width+=.5
    raise RuntimeError("domain failed to meet error budget")

def refine_coupling(tolerance:float,cfg:BudgetConfig):
    iterations=4; history=[]
    for refinement in range(cfg.max_refinements):
        value=coupling_iterate(iterations); estimate=abs(value-coupling_map(value))/(1-.5); history.append({"level":iterations,"value":value,"estimated_error":estimate})
        if estimate<=tolerance:return {"name":"coupling","method":"contraction-residual-bound","level":iterations,"value":value,"estimated_error":estimate,"allocated_tolerance":tolerance,"history":history,"refinements":refinement+1}
        iterations+=2
    raise RuntimeError("coupling failed to meet error budget")

def adaptive_plan(cfg:BudgetConfig=BudgetConfig())->dict[str,Any]:
    a=cfg.allocations(); components={"temporal":refine_power("temporal",heun_decay,8,2,a["temporal"],cfg),"spatial":refine_power("spatial",trapezoid_sine,16,2,a["spatial"],cfg),"domain":refine_domain(a["domain"],cfg),"coupling":refine_coupling(a["coupling"],cfg)}
    approximate=sum(x["value"] for x in components.values()); exact=math.exp(-1)+2+1+coupling_reference(); bound=sum(x["estimated_error"] for x in components.values())
    canonical={"config":asdict(cfg),"components":{name:{k:value for k,value in item.items() if k in {"method","level","value","estimated_error","allocated_tolerance"}} for name,item in sorted(components.items())},"approximate_observable":approximate,"propagated_bound":bound}
    fingerprint=sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {**canonical,"exact_benchmark_observable":exact,"actual_benchmark_error":abs(approximate-exact),"fingerprint":fingerprint,"components_full":components}

def _monotone(component):
    e=[x["estimated_error"] for x in component["history"]]; return all(e[i+1]<=e[i]+1e-18 for i in range(len(e)-1))

@lru_cache(maxsize=1)
def run_adaptive_error_budget_study()->dict[str,Any]:
    cfg=BudgetConfig(); first=adaptive_plan(cfg); second=adaptive_plan(cfg); components=first["components_full"]; rejected=False
    try: adaptive_plan(BudgetConfig(max_refinements=1))
    except RuntimeError: rejected=True
    acceptance={"every_component_meets_allocation":all(x["estimated_error"]<=x["allocated_tolerance"] for x in components.values()),"propagated_bound_meets_total_budget":first["propagated_bound"]<=cfg.total_tolerance,"actual_benchmark_error_is_bounded":first["actual_benchmark_error"]<=first["propagated_bound"],"component_estimates_are_monotone":all(_monotone(x) for x in components.values()),"deterministic_plan":first["fingerprint"]==second["fingerprint"],"insufficient_refinement_is_rejected":rejected,"all_error_channels_are_present":set(components)=={"temporal","spatial","domain","coupling"},"allocations_close":abs(sum(cfg.allocations().values())-cfg.total_tolerance)<=1e-18}
    return {"schema":"openwave.m9.adaptive-error-budget-result.v1","task":"M9.36","config":asdict(cfg),"components":first["components"],"approximate_observable":first["approximate_observable"],"exact_benchmark_observable":first["exact_benchmark_observable"],"actual_benchmark_error":first["actual_benchmark_error"],"propagated_bound":first["propagated_bound"],"fingerprint":first["fingerprint"],"acceptance":acceptance,"passed":all(acceptance.values()),"classification":{"establishes":["component-wise temporal, spatial, domain, and coupling budgets","adaptive refinement to allocated tolerances","propagated total observable error bound","deterministic refinement fingerprints","explicit failure when refinement limits are insufficient"],"does_not_establish":["rigorous error bounds for every OpenWave solver","automatic model-specific stability proofs","GPU or distributed adaptive meshes","physical uncertainty or experimental error"]}}

def result_to_json(result:dict[str,Any])->str:return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
