"""Composite-state graph and relaxation infrastructure.

Constituents carry dimensionless charge, mass, and spin ledgers. Bond edges use
Morse interactions while all constituent pairs may also carry a regularized
Coulomb control. The templates are graph/integration controls, not identified
with physical mesons or baryons.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any
import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]

@dataclass(frozen=True)
class Constituent:
    name: str
    charge: float
    mass: float
    spin_z: float
    def __post_init__(self) -> None:
        if not self.name or self.mass <= 0.0:
            raise ValueError("named positive-mass constituent required")

@dataclass(frozen=True)
class Bond:
    left: str
    right: str
    depth: float
    width: float
    equilibrium: float
    def __post_init__(self) -> None:
        if self.left == self.right:
            raise ValueError("self-bond rejected")
        if self.depth <= 0.0 or self.width <= 0.0 or self.equilibrium <= 0.0:
            raise ValueError("positive bond parameters required")

@dataclass(frozen=True)
class CompositeSpec:
    name: str
    constituents: tuple[Constituent, ...]
    bonds: tuple[Bond, ...]
    coulomb_strength: float = 0.12
    softening: float = 0.2
    def __post_init__(self) -> None:
        validate_spec(self)
    def canonical_dict(self) -> dict[str, Any]:
        constituents = sorted((asdict(item) for item in self.constituents), key=lambda x: x["name"])
        bonds=[]
        for bond in self.bonds:
            payload=asdict(bond)
            payload["left"],payload["right"]=sorted((payload["left"],payload["right"]))
            bonds.append(payload)
        bonds.sort(key=lambda x:(x["left"],x["right"]))
        return {"name":self.name,"constituents":constituents,"bonds":bonds,
                "coulomb_strength":self.coulomb_strength,"softening":self.softening}
    def fingerprint(self) -> str:
        payload=json.dumps(self.canonical_dict(),sort_keys=True,separators=(",",":"))
        return sha256(payload.encode()).hexdigest()

def validate_spec(spec: CompositeSpec) -> None:
    if not spec.name or not spec.constituents:
        raise ValueError("named nonempty composite required")
    if spec.coulomb_strength < 0.0 or spec.softening <= 0.0:
        raise ValueError("valid interaction controls required")
    names=[item.name for item in spec.constituents]
    if len(names)!=len(set(names)):
        raise ValueError("duplicate constituent names")
    known=set(names); adjacency={name:set() for name in names}; seen=set()
    for bond in spec.bonds:
        if bond.left not in known or bond.right not in known:
            raise ValueError("bond references unknown constituent")
        edge=tuple(sorted((bond.left,bond.right)))
        if edge in seen:
            raise ValueError("duplicate bond")
        seen.add(edge); adjacency[bond.left].add(bond.right); adjacency[bond.right].add(bond.left)
    if len(names)>1:
        visited=set(); stack=[names[0]]
        while stack:
            node=stack.pop()
            if node in visited: continue
            visited.add(node); stack.extend(adjacency[node]-visited)
        if visited!=known:
            raise ValueError("composite graph must be connected")

def total_charge(spec: CompositeSpec) -> float:
    return float(sum(item.charge for item in spec.constituents))

def total_spin(spec: CompositeSpec) -> float:
    return float(sum(item.spin_z for item in spec.constituents))

def rest_energy(spec: CompositeSpec) -> float:
    return float(sum(item.mass for item in spec.constituents))

def _bond_map(spec: CompositeSpec) -> dict[tuple[int,int],Bond]:
    index={item.name:i for i,item in enumerate(spec.constituents)}
    return {tuple(sorted((index[b.left],index[b.right]))):b for b in spec.bonds}

def energy_and_forces(spec: CompositeSpec, positions: RealArray) -> tuple[float,RealArray]:
    positions=np.asarray(positions,dtype=np.float64); count=len(spec.constituents)
    if positions.shape!=(count,2):
        raise ValueError("positions must have shape (constituents,2)")
    energy=rest_energy(spec); forces=np.zeros_like(positions); bond_map=_bond_map(spec)
    for left in range(count):
        for right in range(left+1,count):
            delta=positions[left]-positions[right]; distance=float(np.linalg.norm(delta))
            if distance<=1e-12: raise ValueError("coincident constituents rejected")
            direction=delta/distance; derivative=0.0
            bond=bond_map.get((left,right))
            if bond is not None:
                exponential=math.exp(-bond.width*(distance-bond.equilibrium))
                energy+=bond.depth*((1.0-exponential)**2-1.0)
                derivative+=2.0*bond.depth*bond.width*exponential*(1.0-exponential)
            charge_product=spec.constituents[left].charge*spec.constituents[right].charge
            softened=math.sqrt(distance*distance+spec.softening*spec.softening)
            energy+=spec.coulomb_strength*charge_product/softened
            derivative+=-spec.coulomb_strength*charge_product*distance/(distance*distance+spec.softening*spec.softening)**1.5
            pair_force=-derivative*direction
            forces[left]+=pair_force; forces[right]-=pair_force
    return float(energy),forces

def recenter(positions: RealArray,spec: CompositeSpec)->RealArray:
    masses=np.asarray([item.mass for item in spec.constituents])
    center=np.average(positions,axis=0,weights=masses)
    return positions-center

def relax(spec:CompositeSpec,initial_positions:RealArray,*,steps:int=5000,step_size:float=0.04,tolerance:float=2e-9)->dict[str,Any]:
    positions=recenter(np.asarray(initial_positions,dtype=np.float64).copy(),spec)
    energy,forces=energy_and_forces(spec,positions); energies=[energy]; accepted_steps=0
    for _ in range(steps):
        if float(np.linalg.norm(forces))<=tolerance: break
        trial_step=step_size; accepted=False
        for _attempt in range(24):
            trial=recenter(positions+trial_step*forces,spec)
            trial_energy,trial_forces=energy_and_forces(spec,trial)
            if trial_energy<=energy+1e-14:
                positions,energy,forces=trial,trial_energy,trial_forces
                energies.append(energy); accepted_steps+=1; accepted=True; break
            trial_step*=0.5
        if not accepted: break
    distances=[float(np.linalg.norm(positions[i]-positions[j])) for i in range(len(spec.constituents)) for j in range(i+1,len(spec.constituents))]
    return {"positions":positions,"energy":energy,"energies":np.asarray(energies),
            "force_norm":float(np.linalg.norm(forces)),"accepted_steps":accepted_steps,
            "pair_distances":distances,"binding_energy":energy-rest_energy(spec),
            "dissociation_threshold":rest_energy(spec)-energy}

def neutral_pair_template()->tuple[CompositeSpec,RealArray]:
    spec=CompositeSpec("neutral-pair-control",(
        Constituent("positive",+1.0,1.0,+0.5),Constituent("negative",-1.0,1.0,-0.5)),
        (Bond("positive","negative",0.8,1.5,1.25),))
    return spec,np.asarray([[-1.2,0.2],[1.2,-0.2]],dtype=np.float64)

def triplet_template()->tuple[CompositeSpec,RealArray]:
    spec=CompositeSpec("charged-triplet-control",(
        Constituent("a",+1.0,1.0,+0.5),Constituent("b",+1.0,1.0,+0.5),Constituent("c",-1.0,1.0,-0.5)),(
        Bond("a","b",0.72,1.35,1.35),Bond("a","c",0.72,1.35,1.35),Bond("b","c",0.72,1.35,1.35)))
    return spec,np.asarray([[-1.4,-0.5],[1.3,-0.4],[0.2,1.6]],dtype=np.float64)

def permuted_spec(spec:CompositeSpec)->CompositeSpec:
    return CompositeSpec(spec.name,tuple(reversed(spec.constituents)),tuple(reversed(spec.bonds)),spec.coulomb_strength,spec.softening)

def local_stability_probe(spec:CompositeSpec,relaxed_positions:RealArray,amplitude:float=1e-3)->dict[str,float]:
    base_energy,_=energy_and_forces(spec,relaxed_positions); increases=[]
    for index in range(relaxed_positions.shape[0]):
        for axis in range(2):
            perturbation=np.zeros_like(relaxed_positions); perturbation[index,axis]=amplitude
            shifted=recenter(relaxed_positions+perturbation,spec)
            shifted_energy,_=energy_and_forces(spec,shifted); increases.append(shifted_energy-base_energy)
    return {"minimum_energy_increase":float(min(increases)),"maximum_energy_increase":float(max(increases))}

def run_template(spec:CompositeSpec,positions:RealArray)->dict[str,Any]:
    initial_energy,_=energy_and_forces(spec,positions); relaxed=relax(spec,positions)
    stability=local_stability_probe(spec,relaxed["positions"])
    return {"name":spec.name,"fingerprint":spec.fingerprint(),"constituent_count":len(spec.constituents),
            "bond_count":len(spec.bonds),"total_charge":total_charge(spec),"total_spin_z":total_spin(spec),
            "rest_energy":rest_energy(spec),"initial_energy":initial_energy,"final_energy":relaxed["energy"],
            "binding_energy":relaxed["binding_energy"],"dissociation_threshold":relaxed["dissociation_threshold"],
            "force_norm":relaxed["force_norm"],"pair_distances":relaxed["pair_distances"],
            "energy_monotone":bool(np.all(np.diff(relaxed["energies"])<=2e-13)),
            "local_stability":stability,"relaxed_positions":relaxed["positions"].tolist()}

def run_composite_graph_study()->dict[str,Any]:
    pair_spec,pair_positions=neutral_pair_template(); triplet_spec,triplet_positions=triplet_template()
    pair=run_template(pair_spec,pair_positions); triplet=run_template(triplet_spec,triplet_positions)
    permutation_fingerprints={"pair":pair_spec.fingerprint()==permuted_spec(pair_spec).fingerprint(),
                              "triplet":triplet_spec.fingerprint()==permuted_spec(triplet_spec).fingerprint()}
    acceptance={
        "graphs_are_connected_and_valid":True,
        "canonical_fingerprints_are_permutation_invariant":all(permutation_fingerprints.values()),
        "neutral_pair_charge_closes":abs(pair["total_charge"])<=1e-12,
        "charged_triplet_charge_closes":abs(triplet["total_charge"]-1.0)<=1e-12,
        "both_templates_bind":pair["binding_energy"]<-0.1 and triplet["binding_energy"]<-0.1,
        "relaxation_is_energy_monotone":pair["energy_monotone"] and triplet["energy_monotone"],
        "residual_forces_are_small":pair["force_norm"]<=1e-6 and triplet["force_norm"]<=1e-6,
        "local_minima_are_stable":pair["local_stability"]["minimum_energy_increase"]>=-2e-9 and triplet["local_stability"]["minimum_energy_increase"]>=-2e-9,
    }
    return {"schema":"openwave.m9.composite-graph-result.v1","task":"M9.33",
            "templates":{"neutral_pair":pair,"charged_triplet":triplet},
            "permutation_fingerprints":permutation_fingerprints,"acceptance":acceptance,
            "passed":all(acceptance.values()),"classification":{
                "establishes":["versioned constituent-and-bond graph schema","charge, spin, and rest-energy ledgers","energy-monotone relaxation","binding and dissociation thresholds","neutral-pair and charged-triplet templates"],
                "does_not_establish":["physical mesons or baryons","quark color or fractional-charge dynamics","composites emerging from the full CAT/EPT PDE","physical masses, radii, or decay channels"]}}

def result_to_json(result:dict[str,Any])->str:
    return json.dumps(result,indent=2,sort_keys=True,default=float)+"\n"
