"""Versioned, dimensionless contract for OpenWave theory plugins."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from typing import Any, Literal

Role = Literal["dynamic", "constraint", "auxiliary", "ledger"]
TermKind = Literal["reversible", "irreversible", "constraint", "source"]
LawKind = Literal["invariant", "monotone", "constraint", "balance"]
Direction = Literal["nondecreasing", "nonincreasing", "constant", "zero"]

@dataclass(frozen=True)
class FieldSpec:
    name: str; role: Role; dtype: str = "float64"; shape: tuple[int, ...] = (); description: str = ""
@dataclass(frozen=True)
class ParameterSpec:
    name: str; default: float; bounds: tuple[float, float] | None = None; description: str = ""
@dataclass(frozen=True)
class EvolutionTermSpec:
    name: str; kind: TermKind; reads: tuple[str, ...]; writes: tuple[str, ...]; description: str = ""
@dataclass(frozen=True)
class ObservableSpec:
    name: str; reads: tuple[str, ...]; reduction: str; description: str = ""
@dataclass(frozen=True)
class LawSpec:
    name: str; kind: LawKind; observable: str; tolerance: float; direction: Direction; description: str = ""
@dataclass(frozen=True)
class TheoryManifest:
    name: str
    version: str
    fields: tuple[FieldSpec, ...]
    parameters: tuple[ParameterSpec, ...]
    evolution_terms: tuple[EvolutionTermSpec, ...]
    observables: tuple[ObservableSpec, ...]
    laws: tuple[LawSpec, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    def canonical_dict(self) -> dict[str, Any]: return asdict(self)
    def canonical_json(self) -> str: return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
    def fingerprint(self) -> str: return sha256(self.canonical_json().encode()).hexdigest()

class ContractError(ValueError): pass

def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)): raise ContractError(f"duplicate {label} names")
    if any(not x or x.strip() != x for x in values): raise ContractError(f"invalid {label} name")

def validate_manifest(m: TheoryManifest) -> dict[str, Any]:
    if not m.name or not m.evolution_terms or not m.observables:
        raise ContractError("fields, terms, and observables required")
    groups = {
        "field": [x.name for x in m.fields], "parameter": [x.name for x in m.parameters],
        "term": [x.name for x in m.evolution_terms], "observable": [x.name for x in m.observables],
        "law": [x.name for x in m.laws],
    }
    for label, names in groups.items(): _unique(names, label)
    fields, observables = set(groups["field"]), set(groups["observable"])
    for p in m.parameters:
        if p.bounds is not None:
            lo, hi = p.bounds
            if lo > hi or not lo <= p.default <= hi: raise ContractError(f"parameter {p.name} violates bounds")
    for term in m.evolution_terms:
        missing = (set(term.reads) | set(term.writes)) - fields
        if missing: raise ContractError(f"term {term.name} references unknown fields: {sorted(missing)}")
        if not term.writes: raise ContractError(f"term {term.name} writes nothing")
    for obs in m.observables:
        missing = set(obs.reads) - fields
        if missing: raise ContractError(f"observable {obs.name} references unknown fields: {sorted(missing)}")
    for law in m.laws:
        if law.observable not in observables: raise ContractError(f"law {law.name} references unknown observable")
        if law.tolerance < 0: raise ContractError(f"law {law.name} has negative tolerance")
    kinds = {x.kind for x in m.evolution_terms}
    return {
        "valid": True, "field_count": len(m.fields), "parameter_count": len(m.parameters),
        "term_count": len(m.evolution_terms), "observable_count": len(m.observables),
        "law_count": len(m.laws), "has_reversible_sector": "reversible" in kinds,
        "has_irreversible_sector": "irreversible" in kinds, "has_constraint_sector": "constraint" in kinds,
        "fingerprint": m.fingerprint(),
    }

class TheoryRegistry:
    def __init__(self) -> None: self._items: dict[tuple[str, str], TheoryManifest] = {}
    def register(self, m: TheoryManifest) -> str:
        validate_manifest(m); key = (m.name, m.version)
        if key in self._items: raise ContractError(f"theory {m.name}@{m.version} already registered")
        self._items[key] = m; return m.fingerprint()
    def get(self, name: str, version: str) -> TheoryManifest:
        try: return self._items[(name, version)]
        except KeyError as exc: raise KeyError(f"unknown theory {name}@{version}") from exc
    def list_versions(self) -> tuple[str, ...]: return tuple(f"{n}@{v}" for n, v in sorted(self._items))

def cat_ept_manifest() -> TheoryManifest:
    return TheoryManifest(
        "cat-ept-reference", "1.0",
        (
            FieldSpec("psi", "dynamic", "complex128", (-1,)), FieldSpec("gauge", "dynamic", shape=(-1,)),
            FieldSpec("entropy", "ledger"), FieldSpec("reservoir", "ledger"),
            FieldSpec("constraint", "constraint", shape=(-1,)),
        ),
        (
            ParameterSpec("hbar", 1.0, (1e-12, 1e12)), ParameterSpec("mass", 1.0, (0, 1e12)),
            ParameterSpec("irreversible_rate", 0.0, (0, 1e6)),
            ParameterSpec("backreaction_strength", 0.0, (0, 1e6)),
        ),
        (
            EvolutionTermSpec("hamiltonian_flow", "reversible", ("psi", "gauge"), ("psi",)),
            EvolutionTermSpec("imaginary_action_flow", "irreversible", ("psi", "entropy"), ("psi", "entropy", "reservoir")),
            EvolutionTermSpec("field_backreaction", "source", ("psi", "gauge"), ("gauge",)),
            EvolutionTermSpec("constraint_update", "constraint", ("psi", "gauge"), ("constraint",)),
        ),
        (
            ObservableSpec("matter_norm", ("psi",), "integral_abs2"),
            ObservableSpec("total_balance", ("psi", "reservoir"), "norm_plus_reservoir"),
            ObservableSpec("entropic_clock", ("entropy",), "identity"),
            ObservableSpec("constraint_residual", ("constraint",), "max_abs"),
            ObservableSpec("field_energy", ("gauge",), "quadratic_energy"),
        ),
        (
            LawSpec("extended_balance", "balance", "total_balance", 1e-9, "constant"),
            LawSpec("entropy_arrow", "monotone", "entropic_clock", 1e-12, "nondecreasing"),
            LawSpec("gauss_closure", "constraint", "constraint_residual", 1e-8, "zero"),
        ),
        {"scope": "dimensionless simulation contract", "physical_identity": None, "requires_data_acquisition": False},
    )

def _restore(m: TheoryManifest) -> TheoryManifest:
    d = m.canonical_dict()
    return TheoryManifest(
        d["name"], d["version"], tuple(FieldSpec(**x) for x in d["fields"]),
        tuple(ParameterSpec(**x) for x in d["parameters"]),
        tuple(EvolutionTermSpec(**x) for x in d["evolution_terms"]),
        tuple(ObservableSpec(**x) for x in d["observables"]), tuple(LawSpec(**x) for x in d["laws"]), d["metadata"],
    )

def run_theory_contract_study() -> dict[str, Any]:
    m = cat_ept_manifest(); validation = validate_manifest(m); registry = TheoryRegistry(); fp = registry.register(m)
    acceptance = {
        "manifest_valid": validation["valid"], "reversible_sector_declared": validation["has_reversible_sector"],
        "irreversible_sector_declared": validation["has_irreversible_sector"],
        "constraint_sector_declared": validation["has_constraint_sector"],
        "deterministic_fingerprint": fp == _restore(m).fingerprint(),
        "registry_roundtrip": registry.get(m.name, m.version) == m,
        "simulation_only_scope": m.metadata["requires_data_acquisition"] is False,
    }
    return {"schema": "openwave.m9.theory-contract-result.v1", "task": "M9.19-simcore",
            "manifest": m.canonical_dict(), "validation": validation, "registered": registry.list_versions(),
            "acceptance": acceptance, "passed": all(acceptance.values())}

def result_to_json(result: dict[str, Any]) -> str: return json.dumps(result, indent=2, sort_keys=True) + "\n"
