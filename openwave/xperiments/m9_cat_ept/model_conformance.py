"""README/MODELS-aligned CAT/EPT conformance profile."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Literal

Status = Literal["validated", "partial", "negative", "not_yet"]

@dataclass(frozen=True)
class Criterion:
    key: str
    domain: str
    label: str
    status: Status
    evidence: tuple[str, ...]
    finding: str

CRITERIA: tuple[Criterion, ...] = (
    Criterion("charge_quantization","particles","Charge quantization","not_yet",(),"No emergent topological or dynamical quantization law has been implemented."),
    Criterion("electron_rest_energy","particles","Electron rest energy (mass)","not_yet",(),"Mass remains a model parameter; no localized CAT/EPT rest-energy solution is accepted."),
    Criterion("de_broglie_clock","particles","de Broglie clock (Zitterbewegung)","partial",("openwave/xperiments/m9_cat_ept/imaginary_action_backreaction.py","openwave/xperiments/m9_cat_ept/entropic_integrator.py"),"A monotone entropic clock exists, but it is not identified with Zitterbewegung or physical time."),
    Criterion("particle_stability","particles","Particle stability (Derrick escape)","negative",("openwave/xperiments/m9_cat_ept/spatial_3d_localization_decision.py","openwave/xperiments/m9_cat_ept/research/findings/m9_14_method_note.md"),"The strongest bounded 3D member fails the frozen long-horizon localization gate."),
    Criterion("magnetic_moment_spin","particles","Magnetic moment and spin J","not_yet",(),"Spinor transport and magnetic fields are controls, not an emergent particle moment or spin."),
    Criterion("spin_half_statistics","particles","Spin-1/2 statistics (720-degree return)","not_yet",(),"No field-level double-cover return or exchange-statistics simulation exists."),
    Criterion("antimatter_annihilation","particles","Antimatter and annihilation","not_yet",(),"Opposite charge labels are transported, but annihilation is not modeled."),
    Criterion("lepton_mass_spectrum","particles","Lepton mass spectrum (mu, tau)","not_yet",(),"No parameter-free hierarchy or multiple localized mass eigenstates exist."),
    Criterion("dark_matter","particles","Dark matter candidate","not_yet",(),"No neutral localized CAT/EPT candidate is qualified."),
    Criterion("quarks","particles","Quarks","not_yet",(),"No fractional-charge or color-sector model exists."),
    Criterion("baryons","particles","Baryons (p, n)","not_yet",(),"No three-body composite sector exists."),
    Criterion("mesons","particles","Mesons (pi, K)","not_yet",(),"No bound particle-antiparticle composite sector exists."),
    Criterion("electric_force","forces","Electric force (Coulomb 1/r)","partial",("openwave/xperiments/m9_cat_ept/spatial_3d_maxwell_dirac.py","openwave/xperiments/m9_cat_ept/research/findings/m9_13_method_note.md"),"Gauss and transport ledgers exist, but no force law between stable emergent charges is established."),
    Criterion("magnetic_force","forces","Magnetic force","partial",("openwave/xperiments/m9_cat_ept/spatial_3d_maxwell_dirac.py",),"Magnetic and Poynting fields are simulated; a particle-level magnetic interaction is not."),
    Criterion("strong_force","forces","Strong force / confinement","not_yet",(),"No confinement or string-tension sector exists."),
    Criterion("weak_force","forces","Weak force","not_yet",(),"No chiral transition or decay sector exists."),
    Criterion("gravity","forces","Gravity","not_yet",(),"Geometry appears in the theory manifest, but dynamical metric back-reaction is pending."),
    Criterion("em_waves","waves","EM waves (Maxwell)","partial",("openwave/xperiments/m9_cat_ept/spatial_3d_controls.py","openwave/xperiments/m9_cat_ept/research/data/m9_12_spatial_3d_controls_result.json"),"Vacuum Maxwell propagation is qualified as a control, not derived as an emergent CAT/EPT result."),
    Criterion("klein_gordon","waves","Quantum wave equation (Klein-Gordon)","not_yet",(),"No CAT/EPT reduction to a Klein-Gordon field equation is implemented."),
    Criterion("orbital_quantization","waves","Orbital quantization (atomic structure)","not_yet",(),"No bound-state or standing-wave orbital ladder is implemented."),
)

EXPECTED_VISIBLE_CRITERIA = 20
DOCUMENTED_SUMMARY_TOTAL = 21
MISSING_EXPLICIT_CRITERION = "heat_or_thermal_sector"

def validate_profile(criteria: tuple[Criterion, ...] = CRITERIA) -> dict[str, Any]:
    keys=[x.key for x in criteria]; labels=[x.label for x in criteria]
    if len(keys)!=len(set(keys)) or len(labels)!=len(set(labels)): raise ValueError("duplicate criterion")
    if len(criteria)!=EXPECTED_VISIBLE_CRITERIA: raise ValueError("profile must cover 20 explicit rows")
    if any(x.status!="not_yet" and not x.evidence for x in criteria): raise ValueError("non-planned status lacks evidence")
    domains={d:sum(x.domain==d for x in criteria) for d in ("particles","forces","waves")}
    counts={s:sum(x.status==s for x in criteria) for s in ("validated","partial","negative","not_yet")}
    return {"valid":True,"criterion_count":len(criteria),"domain_counts":domains,"status_counts":counts,
            "documented_summary_total":DOCUMENTED_SUMMARY_TOTAL,"matrix_total_mismatch":DOCUMENTED_SUMMARY_TOTAL-len(criteria),
            "missing_explicit_criterion":MISSING_EXPLICIT_CRITERION}

def canonical_payload() -> dict[str, Any]:
    return {"schema":"openwave.m9.models-conformance.v1","model":"M9 CAT/EPT",
            "criteria":[asdict(x) for x in CRITERIA],"audit":validate_profile()}

def fingerprint() -> str:
    return sha256(json.dumps(canonical_payload(),sort_keys=True,separators=(",",":")).encode()).hexdigest()

def run_conformance_study() -> dict[str, Any]:
    payload=canonical_payload()
    acceptance={
        "all_explicit_rows_covered":payload["audit"]["criterion_count"]==20,
        "particle_force_wave_partition_closes":payload["audit"]["domain_counts"]=={"particles":12,"forces":5,"waves":3},
        "nonplanned_cells_have_evidence":all(x["status"]=="not_yet" or bool(x["evidence"]) for x in payload["criteria"]),
        "honest_negative_preserved":any(x["status"]=="negative" for x in payload["criteria"]),
        "summary_mismatch_recorded":payload["audit"]["matrix_total_mismatch"]==1,
        "thermal_gap_named":payload["audit"]["missing_explicit_criterion"]==MISSING_EXPLICIT_CRITERION,
        "deterministic_fingerprint":fingerprint()==fingerprint(),
    }
    return {**payload,"fingerprint":fingerprint(),"acceptance":acceptance,"passed":all(acceptance.values()),
            "repository_profile":"MODELS_M9.md"}

def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result,indent=2,sort_keys=True)+"\n"
