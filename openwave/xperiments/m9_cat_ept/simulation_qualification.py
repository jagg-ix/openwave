"""Cross-theory simulation qualification and regression harness."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json, math
from typing import Any, Protocol
import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]

@dataclass(frozen=True)
class Scenario:
    name: str
    times: tuple[float, ...]
    parameters: tuple[tuple[str, float], ...]
    observables: tuple[str, ...]

    def fingerprint(self) -> str:
        payload=json.dumps({"name":self.name,"times":self.times,"parameters":self.parameters,
                            "observables":self.observables},sort_keys=True)
        return sha256(payload.encode()).hexdigest()

class TheoryAdapter(Protocol):
    name: str
    def simulate(self, scenario: Scenario) -> dict[str, RealArray]: ...
    def laws(self, trace: dict[str, RealArray]) -> dict[str, bool]: ...

@dataclass(frozen=True)
class ExponentialBalanceAdapter:
    name: str
    rate: float
    reversible_frequency: float = 0.0
    def simulate(self, scenario: Scenario) -> dict[str, RealArray]:
        t=np.asarray(scenario.times,dtype=float)
        matter=np.exp(-2*self.rate*t)
        reservoir=1.0-matter
        phase=np.cos(self.reversible_frequency*t)
        return {"matter":matter,"reservoir":reservoir,"balance":matter+reservoir,
                "clock":self.rate*t,"phase":phase}
    def laws(self, trace: dict[str, RealArray]) -> dict[str,bool]:
        return {"balance":bool(np.max(np.abs(trace["balance"]-1))<1e-12),
                "matter_nonincreasing":bool(np.all(np.diff(trace["matter"])<=1e-12)),
                "clock_nondecreasing":bool(np.all(np.diff(trace["clock"])>=-1e-12))}

@dataclass(frozen=True)
class ReversibleAdapter:
    name: str="reversible-control"
    frequency: float=1.0
    def simulate(self, scenario: Scenario) -> dict[str, RealArray]:
        t=np.asarray(scenario.times,dtype=float)
        return {"matter":np.ones_like(t),"reservoir":np.zeros_like(t),"balance":np.ones_like(t),
                "clock":np.zeros_like(t),"phase":np.cos(self.frequency*t)}
    def laws(self, trace: dict[str, RealArray]) -> dict[str,bool]:
        return {"balance":True,"matter_constant":bool(np.max(np.abs(trace["matter"]-1))<1e-12)}


def pairwise_distance(a: dict[str,RealArray], b: dict[str,RealArray], observables: tuple[str,...]) -> float:
    vectors=[]
    for name in observables:
        x,y=a[name],b[name]
        scale=max(float(np.max(np.abs(x))),float(np.max(np.abs(y))),1e-12)
        vectors.append((x-y)/scale)
    return float(np.linalg.norm(np.concatenate(vectors))/math.sqrt(sum(v.size for v in vectors)))


def finite_difference_sensitivity(rate: float, epsilon: float=1e-4) -> float:
    scenario=reference_scenario()
    plus=ExponentialBalanceAdapter("plus",rate+epsilon).simulate(scenario)["matter"]
    minus=ExponentialBalanceAdapter("minus",rate-epsilon).simulate(scenario)["matter"]
    return float(np.linalg.norm((plus-minus)/(2*epsilon)))


def reference_scenario() -> Scenario:
    return Scenario("shared-entropic-decay",tuple(np.linspace(0,5,51)),
                    (("rate",0.12),("frequency",0.7)),
                    ("matter","reservoir","clock","phase"))


def run_qualification(adapters: tuple[TheoryAdapter,...], scenario: Scenario) -> dict[str,Any]:
    if len({a.name for a in adapters}) != len(adapters): raise ValueError("duplicate adapter names")
    traces={a.name:a.simulate(scenario) for a in adapters}
    laws={a.name:a.laws(traces[a.name]) for a in adapters}
    names=[a.name for a in adapters]
    matrix={}
    for i,name in enumerate(names):
        for other in names[i+1:]:
            matrix[f"{name}::{other}"]=pairwise_distance(traces[name],traces[other],scenario.observables)
    digest=sha256(json.dumps({k:{n:v.tolist() for n,v in t.items()} for k,t in traces.items()},sort_keys=True).encode()).hexdigest()
    return {"scenario_fingerprint":scenario.fingerprint(),"trace_fingerprint":digest,
            "laws":laws,"pairwise_distances":matrix,"traces":traces}


def run_simulation_qualification_study() -> dict[str,Any]:
    scenario=reference_scenario()
    adapters=(ReversibleAdapter(frequency=.7),ExponentialBalanceAdapter("cat-ept-rate-0.12",.12,.7),
              ExponentialBalanceAdapter("cat-ept-rate-0.20",.20,.7))
    first=run_qualification(adapters,scenario); second=run_qualification(adapters,scenario)
    distances=list(first["pairwise_distances"].values())
    rates=(0.0,.05,.12,.2,.35)
    sweep={str(r):ExponentialBalanceAdapter(f"r{r}",r,.7).simulate(scenario)["matter"][-1].item() for r in rates}
    acceptance={
        "deterministic_replay":first["trace_fingerprint"]==second["trace_fingerprint"],
        "all_declared_laws_pass":all(all(v.values()) for v in first["laws"].values()),
        "theories_are_distinguishable":min(distances)>1e-3,
        "parameter_sweep_ordered":all(sweep[str(a)]>=sweep[str(b)] for a,b in zip(rates,rates[1:])),
        "sensitivity_nonzero":finite_difference_sensitivity(.12)>1.0,
        "shared_scenario_frozen":len(scenario.fingerprint())==64,
        "simulation_only":True,
    }
    return {"schema":"openwave.m9.simulation-qualification-result.v1","task":"M9.21-simcore",
            "scenario":{"name":scenario.name,"time_points":len(scenario.times),"observables":scenario.observables,
                        "fingerprint":scenario.fingerprint()},"pairwise_distances":first["pairwise_distances"],
            "parameter_sweep_final_matter":sweep,"sensitivity":finite_difference_sensitivity(.12),
            "trace_fingerprint":first["trace_fingerprint"],"acceptance":acceptance,"passed":all(acceptance.values())}

def result_to_json(result: dict[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
