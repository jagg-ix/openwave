"""README/MODELS-aligned CAT/EPT conformance profile."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Literal

Status=Literal["validated","partial","negative","not_yet"]

@dataclass(frozen=True)
class Criterion:
    key:str; domain:str; label:str; status:Status; evidence:tuple[str,...]; finding:str

CRITERIA:tuple[Criterion,...]=(
 Criterion("charge_quantization","particles","Charge quantization","partial",("openwave/xperiments/m9_cat_ept/topological_charge.py","openwave/xperiments/m9_cat_ept/research/findings/m9_26_method_note.md"),"Integer winding is field-derived and robust, but the sector is seeded and is not identified with elementary electric charge."),
 Criterion("electron_rest_energy","particles","Electron rest energy (mass)","partial",("openwave/xperiments/m9_cat_ept/scale_selection.py","openwave/xperiments/m9_cat_ept/research/findings/m9_27_method_note.md"),"A selected topological ansatz has an interior dimensionless scale minimum, but no physical mass or full CAT/EPT particle is established."),
 Criterion("de_broglie_clock","particles","de Broglie clock (Zitterbewegung)","partial",("openwave/xperiments/m9_cat_ept/intrinsic_clock_reduction.py","openwave/xperiments/m9_cat_ept/imaginary_action_backreaction.py","openwave/xperiments/m9_cat_ept/entropic_integrator.py"),"Reversible phase, entropic monotone, and geometry clock channels are separated; no Zitterbewegung or physical-time identity is accepted."),
 Criterion("particle_stability","particles","Particle stability (Derrick escape)","negative",("openwave/xperiments/m9_cat_ept/minimizer_3d.py","openwave/xperiments/m9_cat_ept/localized_state_search.py","openwave/xperiments/m9_cat_ept/spatial_3d_localization_decision.py","openwave/xperiments/m9_cat_ept/research/findings/m9_14_method_note.md","openwave/xperiments/m9_cat_ept/research/findings/m9_25_method_note.md","openwave/xperiments/m9_cat_ept/research/findings/m9_37_method_note.md"),"A trapped 3D minimizer and constrained 1D family exist, but the untrapped 3D control is not self-bound and the strongest bounded 3D member fails the frozen long-horizon localization gate."),
 Criterion("magnetic_moment_spin","particles","Magnetic moment and spin J","partial",("openwave/xperiments/m9_cat_ept/spin_magnetic_observables.py","openwave/xperiments/m9_cat_ept/research/findings/m9_29_method_note.md"),"Spin and a Pauli-current magnetic moment are field-integrated controls; no emergent electron g factor or stable particle is established."),
 Criterion("spin_half_statistics","particles","Spin-1/2 statistics (720-degree return)","partial",("openwave/xperiments/m9_cat_ept/spin_magnetic_observables.py","openwave/xperiments/m9_cat_ept/research/findings/m9_29_method_note.md"),"The spinor changes sign after 2pi and returns after 4pi, but exchange statistics are not established."),
 Criterion("antimatter_annihilation","particles","Antimatter and annihilation","partial",("openwave/xperiments/m9_cat_ept/capture_annihilation.py","openwave/xperiments/m9_cat_ept/research/findings/m9_31_method_note.md"),"A reduced opposite-sector model captures, annihilates, and transfers energy into radiation; full-PDE particle annihilation is not established."),
 Criterion("lepton_mass_spectrum","particles","Lepton mass spectrum (mu, tau)","negative",("openwave/xperiments/m9_cat_ept/lepton_hierarchy_audit.py","openwave/xperiments/m9_cat_ept/research/findings/m9_39_method_note.md"),"Current geometric and M9.27 effective-scale candidate laws fail predictive gates; exact three-parameter interpolation has zero residual degrees of freedom. No predictive hierarchy is selected."),
 Criterion("dark_matter","particles","Dark matter candidate","not_yet",(),"No neutral localized CAT/EPT candidate is qualified."),
 Criterion("quarks","particles","Quarks","not_yet",(),"No fractional-charge or color-sector model exists."),
 Criterion("baryons","particles","Baryons (p, n)","partial",("openwave/xperiments/m9_cat_ept/composite_graph.py","openwave/xperiments/m9_cat_ept/research/findings/m9_33_method_note.md"),"A charged-triplet graph binds and preserves ledgers, but no physical baryon or quark dynamics is established."),
 Criterion("mesons","particles","Mesons (pi, K)","partial",("openwave/xperiments/m9_cat_ept/composite_graph.py","openwave/xperiments/m9_cat_ept/research/findings/m9_33_method_note.md"),"A neutral-pair graph binds and preserves ledgers, but no physical meson or decay channel is established."),
 Criterion("electric_force","forces","Electric force (Coulomb 1/r)","partial",("openwave/xperiments/m9_cat_ept/two_body_forces.py","openwave/xperiments/m9_cat_ept/spatial_3d_maxwell_dirac.py","openwave/xperiments/m9_cat_ept/research/findings/m9_30_method_note.md"),"A regularized conservative kernel recovers the Coulomb-force asymptote, but no force between stable emergent charges is established."),
 Criterion("magnetic_force","forces","Magnetic force","partial",("openwave/xperiments/m9_cat_ept/two_body_forces.py","openwave/xperiments/m9_cat_ept/spin_magnetic_observables.py","openwave/xperiments/m9_cat_ept/spatial_3d_maxwell_dirac.py","openwave/xperiments/m9_cat_ept/research/findings/m9_30_method_note.md"),"A regularized dipole kernel recovers the r^-4 force asymptote; a particle-level CAT/EPT interaction is not established."),
 Criterion("strong_force","forces","Strong force / confinement","not_yet",(),"No confinement or string-tension sector exists."),
 Criterion("weak_force","forces","Weak force","not_yet",(),"No chiral transition or decay sector exists."),
 Criterion("gravity","forces","Gravity","partial",("openwave/xperiments/m9_cat_ept/geometry_backreaction.py","openwave/xperiments/m9_cat_ept/research/findings/m9_34_method_note.md"),"A screened weak-field scalar metric responds to matter density and supplies lapse/proper-time probes; Einstein gravity, tensor dynamics, and physical coupling remain open."),
 Criterion("em_waves","waves","EM waves (Maxwell)","partial",("openwave/xperiments/m9_cat_ept/spatial_3d_controls.py","openwave/xperiments/m9_cat_ept/research/data/m9_12_spatial_3d_controls_result.json"),"Vacuum Maxwell propagation is qualified as a control, not derived as an emergent CAT/EPT result."),
 Criterion("klein_gordon","waves","Quantum wave equation (Klein-Gordon)","not_yet",(),"No CAT/EPT reduction to a Klein-Gordon field equation is implemented."),
 Criterion("orbital_quantization","waves","Orbital quantization (atomic structure)","partial",("openwave/xperiments/m9_cat_ept/orbital_quantization.py","openwave/xperiments/m9_cat_ept/research/findings/m9_32_method_note.md"),"A converged Coulomb-like radial standing-wave ladder is resolved; atomic structure from the full CAT/EPT PDE is not established."),
)
EXPECTED_VISIBLE_CRITERIA=20; DOCUMENTED_SUMMARY_TOTAL=21; MISSING_EXPLICIT_CRITERION="heat_or_thermal_sector"

def validate_profile(criteria:tuple[Criterion,...]=CRITERIA)->dict[str,Any]:
    keys=[x.key for x in criteria]; labels=[x.label for x in criteria]
    if len(keys)!=len(set(keys)) or len(labels)!=len(set(labels)): raise ValueError("duplicate criterion")
    if len(criteria)!=EXPECTED_VISIBLE_CRITERIA: raise ValueError("profile must cover 20 explicit rows")
    if any(x.status!="not_yet" and not x.evidence for x in criteria): raise ValueError("non-planned status lacks evidence")
    domains={d:sum(x.domain==d for x in criteria) for d in ("particles","forces","waves")}
    counts={s:sum(x.status==s for x in criteria) for s in ("validated","partial","negative","not_yet")}
    return {"valid":True,"criterion_count":len(criteria),"domain_counts":domains,"status_counts":counts,"documented_summary_total":DOCUMENTED_SUMMARY_TOTAL,"matrix_total_mismatch":DOCUMENTED_SUMMARY_TOTAL-len(criteria),"missing_explicit_criterion":MISSING_EXPLICIT_CRITERION}

def canonical_payload()->dict[str,Any]: return {"schema":"openwave.m9.models-conformance.v1","model":"M9 CAT/EPT","criteria":[asdict(x) for x in CRITERIA],"audit":validate_profile()}
def fingerprint()->str: return sha256(json.dumps(canonical_payload(),sort_keys=True,separators=(",",":")).encode()).hexdigest()
def run_conformance_study()->dict[str,Any]:
    payload=canonical_payload(); acceptance={
      "all_explicit_rows_covered":payload["audit"]["criterion_count"]==20,
      "particle_force_wave_partition_closes":payload["audit"]["domain_counts"]=={"particles":12,"forces":5,"waves":3},
      "nonplanned_cells_have_evidence":all(x["status"]=="not_yet" or bool(x["evidence"]) for x in payload["criteria"]),
      "honest_negative_preserved":any(x["status"]=="negative" for x in payload["criteria"]),
      "summary_mismatch_recorded":payload["audit"]["matrix_total_mismatch"]==1,
      "thermal_gap_named":payload["audit"]["missing_explicit_criterion"]==MISSING_EXPLICIT_CRITERION,
      "deterministic_fingerprint":fingerprint()==fingerprint(),
      "m9_37_39_status_counts":payload["audit"]["status_counts"]=={"validated":0,"partial":13,"negative":2,"not_yet":5},
    }
    return {**payload,"fingerprint":fingerprint(),"acceptance":acceptance,"passed":all(acceptance.values()),"repository_profile":"MODELS_M9.md"}
def result_to_json(result:dict[str,Any])->str: return json.dumps(result,indent=2,sort_keys=True)+"\n"
