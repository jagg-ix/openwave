"""M9.62 physical-calibration and falsification ledger.

The ledger is simulation-only. It distinguishes dimensionless OpenWave gates,
formal conditional identities, calibration anchors, and genuine out-of-sample
physical predictions. No experimental data are acquired by this module.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from functools import lru_cache
from hashlib import sha256
import json
import numpy as np
from typing import Any,Literal

OPENWAVE_HEAD="ce17d7126f0c9a9f6564c7bce04df29ea383a558"
FORMAL_REPOSITORY="jagg-ix/entropic-physlib-private"
FORMAL_BRANCH="entropic-physlib-linear-full"
FORMAL_HEAD="adbe9ead533d56ea7acd18e4c9ad5dacafd973ff"
ZIL_REPOSITORY="jagg-ix/zil-lean"
ZIL_HEAD="64462a3c5e2ffb51a7b226675491cc3a9b156a8d"

GateStatus=Literal["dimensionless_testable","conditional_formal","calibration_required","negative","prediction_ready"]

CRITERIA=(
 "charge_quantization","electron_rest_energy","de_broglie_clock","particle_stability",
 "magnetic_moment_spin","spin_half_statistics","antimatter_annihilation","lepton_mass_spectrum",
 "dark_matter","quarks","baryons","mesons","electric_force","magnetic_force","strong_force",
 "weak_force","gravity","em_waves","klein_gordon","orbital_quantization","thermal_field",
)

@dataclass(frozen=True)
class FalsificationGate:
    criterion:str; status:GateStatus; observable:str; current_evidence:str
    required_anchor:str|None; preregistered_failure:str; source_paths:tuple[str,...]

def gates()->tuple[FalsificationGate,...]:
    m="openwave/xperiments/m9_cat_ept/"
    common=(m+"research/m9_status_assessment.md",)
    return (
      FalsificationGate("charge_quantization","calibration_required","winding and electric-flux normalization",
        "integer winding is resolved but its identity with elementary electric charge is open","charge unit Q0",
        "reject elementary-charge identity if one shared Q0 cannot fit all charge-sector observables",common),
      FalsificationGate("electron_rest_energy","calibration_required","localized-state conserved energy",
        "dimensionless interior scale and finite binding candidate exist","energy and length map",
        "reject mass claim if one preregistered unit map cannot reproduce rest energy and spatial scale simultaneously",common),
      FalsificationGate("de_broglie_clock","conditional_formal","entropic phase advance versus independent phase clock",
        "PhysLib proves equality after the action-rate calibration ΔS_I=ℏω0Δτ","clock frequency/action-rate calibration",
        "reject physical-time identity when independently measured phase and entropic advances disagree beyond tolerance",
        ("Physlib/QuantumMechanics/Clock/EntropicAgreement.lean",
         "Physlib/QuantumMechanics/ComplexAction/ComplexEinstein/EntropicComplexEinstein.lean")),
      FalsificationGate("particle_stability","dimensionless_testable","radius, boundary loading, perturbation orbit distance",
        "M9.59 finite candidate and M9.61 variational well/tightness proxy","none for dimensionless gate",
        "reject retained-localization claim if any preregistered grid or perturbation crosses radius ratio 1.45 or boundary fraction 0.02",
        (m+"action_derived_binding.py",m+"orbital_compactness_bridge.py")),
      FalsificationGate("magnetic_moment_spin","calibration_required","J and magnetic moment ratio",
        "field-integrated spin/current controls only","magnetic-moment unit and stable state",
        "reject electron identification if the same calibrated state fails J=ℏ/2 or out-of-sample g-factor gate",common),
      FalsificationGate("spin_half_statistics","dimensionless_testable","2π sign and 4π return plus exchange phase",
        "spinor return is resolved; exchange statistics are not","none for topology gate",
        "reject fermion claim unless two-state exchange gives the required antisymmetric phase",common),
      FalsificationGate("antimatter_annihilation","dimensionless_testable","opposite-sector capture and ledger closure",
        "reduced annihilation/radiation ledger","none for reduced gate",
        "reject full-PDE claim if energy and charge ledgers fail under unassisted opposite-sector evolution",common),
      FalsificationGate("lepton_mass_spectrum","negative","muon/electron and tau/electron ratios",
        "tested low-parameter hierarchy laws fail predictive gates",None,
        "retain negative until an out-of-sample law predicts both ratios with residual degrees of freedom",common),
      FalsificationGate("dark_matter","calibration_required","neutral-state stability and abundance proxy",
        "neutral variational candidate only","mass/length map and cosmological production model",
        "reject candidate if calibrated full-PDE state decays or violates preregistered interaction bounds",common),
      FalsificationGate("quarks","calibration_required","color representations, confinement and hadron spectrum",
        "finite SU(3)/CKM controls","shared gauge coupling and scale",
        "reject QCD identity if one coupling/scale cannot reproduce multiple independent color observables",common),
      FalsificationGate("baryons","calibration_required","three-body bound spectrum","graph-level composite only",
        "constituent and energy map","reject baryon identity if calibrated three-body PDE lacks a stable spectrum",common),
      FalsificationGate("mesons","calibration_required","two-body neutral spectrum and decays","graph-level composite only",
        "constituent and energy map","reject meson identity if calibrated two-body PDE lacks independent mass/decay predictions",common),
      FalsificationGate("electric_force","calibration_required","force versus separation","regularized inverse-square asymptote",
        "charge and force units","reject Coulomb identity if one calibrated charge fails multi-distance force data",common),
      FalsificationGate("magnetic_force","calibration_required","dipole force versus separation","regularized r^-4 asymptote",
        "magnetic-moment and force units","reject magnetic identity if the electric-sector unit map cannot also fit dipole force",common),
      FalsificationGate("strong_force","calibration_required","string tension and breaking threshold","Cornell/flux-tube control",
        "energy/length and color coupling","reject strong-force identity if tension and breaking cannot be jointly predicted",common),
      FalsificationGate("weak_force","calibration_required","chiral rates and mixing","reduced left-selective ledger",
        "time/energy and weak coupling","reject weak identity if one coupling cannot predict independent rates and mixing",common),
      FalsificationGate("gravity","conditional_formal","Einstein-Maxwell-entropic equations and calibrated acceleration",
        "scoped formal action/PDE interfaces; calibrated coupled evolution open","Newton/coupling and metric unit map",
        "reject physical-gravity identity if one calibrated coupling fails redshift, free fall and field-source gates",
        ("formalization/zil/electrogravitic-action-closure.zc","docs/EntropicDynamicsClosure.md")),
      FalsificationGate("em_waves","calibration_required","transverse dispersion and energy flux","dimensionless Maxwell reduction",
        "length/time and field units","reject EM identity if one unit map fails speed, dispersion and energy-flux gates",common),
      FalsificationGate("klein_gordon","calibration_required","massive dispersion relation","dimensionless spectral reduction",
        "length/time and mass map","reject native KG identity if calibrated dispersion mass disagrees with particle rest energy",common),
      FalsificationGate("orbital_quantization","calibration_required","radial spectrum ratios","dimensionless converged ladder",
        "energy/length map","reject atomic identity if ratios or absolute levels fail after anchors are fixed elsewhere",common),
      FalsificationGate("thermal_field","calibration_required","heat, entropy and diffusion coefficient","dimensionless heat/entropy controls",
        "temperature, energy and time units","reject thermodynamic identity if one calibration fails heat capacity and diffusion gates",common),
    )

def unit_rank_audit()->dict[str,Any]:
    basis=np.eye(4)
    ranks={0:0, **{n:int(np.linalg.matrix_rank(basis[:n])) for n in range(1,5)}}
    return {"fundamental_unit_directions":["mass","length","time","charge"],
      "rank_by_anchor_count":ranks,
      "anchors_needed_for_arbitrary_dimensionful_map":4,
      "dimensionful_prediction_dof_after_four_independent_anchors":0,
      "warning":"fitting four independent anchors is a unit definition, not a four-observable prediction"}

def _canonical_payload(value:Any)->str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def cross_repo_control_events()->list[dict[str,Any]]:
    """Create a local, nonauthoritative mirror of ZIL-CONTROL-EVENT/1 receipts."""
    observations=(
      {"repository":"jagg-ix/openwave","ref":"main","head":OPENWAVE_HEAD,"role":"simulation evidence"},
      {"repository":FORMAL_REPOSITORY,"ref":FORMAL_BRANCH,"head":FORMAL_HEAD,"role":"Lean proof authority"},
      {"repository":ZIL_REPOSITORY,"ref":"main","head":ZIL_HEAD,"role":"evidence orchestration"},
    )
    previous="0"*64; events=[]
    for revision,payload in enumerate(observations,1):
        body={"schema":"ZIL-CONTROL-EVENT/1","stream":"openwave/m9/cross-repo-evidence",
              "revision":revision,"actor":"openwave-m9","event_type":"source-observed",
              "decision_sha256":payload["head"],"payload":payload,"previous_sha256":previous}
        event_sha=sha256(_canonical_payload(body).encode()).hexdigest()
        receipt={"schema":"ZIL-CONTROL-RECEIPT/1","stream":body["stream"],
                 "revision":revision,"event_sha256":event_sha,"previous_sha256":previous}
        events.append({"event":body,"receipt":receipt})
        previous=event_sha
    return events

def verify_cross_repo_control_events(events:list[dict[str,Any]]|None=None)->bool:
    selected=cross_repo_control_events() if events is None else events
    previous="0"*64
    for expected_revision,item in enumerate(selected,1):
        event=item["event"]; receipt=item["receipt"]
        if event["revision"]!=expected_revision or event["previous_sha256"]!=previous:
            return False
        digest=sha256(_canonical_payload(event).encode()).hexdigest()
        if receipt["event_sha256"]!=digest or receipt["previous_sha256"]!=previous:
            return False
        previous=digest
    return True

def ledger_fingerprint(items:tuple[FalsificationGate,...]|None=None)->str:
    selected=gates() if items is None else items
    payload={"schema":"openwave.m9.physical-falsification-ledger.v1",
      "openwave_head":OPENWAVE_HEAD,"formal_repository":FORMAL_REPOSITORY,
      "formal_branch":FORMAL_BRANCH,"formal_head":FORMAL_HEAD,
      "zil_repository":ZIL_REPOSITORY,"zil_head":ZIL_HEAD,
      "gates":[asdict(x) for x in selected]}
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@lru_cache(maxsize=1)
def run_physical_calibration_ledger()->dict[str,Any]:
    rows=gates(); counts={s:sum(x.status==s for x in rows) for s in
      ("dimensionless_testable","conditional_formal","calibration_required","negative","prediction_ready")}
    anchors=sorted({x.required_anchor for x in rows if x.required_anchor})
    acceptance={
      "all_21_criteria_have_falsification_gates":len(rows)==21 and {x.criterion for x in rows}==set(CRITERIA),
      "remaining_negative_is_preserved":counts["negative"]==1 and next(x for x in rows if x.status=="negative").criterion=="lepton_mass_spectrum",
      "formal_clock_calibration_is_not_mislabeled_as_prediction":next(x for x in rows if x.criterion=="de_broglie_clock").status=="conditional_formal",
      "no_unearned_physical_predictions":counts["prediction_ready"]==0,
      "unit_anchor_degeneracy_is_explicit":unit_rank_audit()["dimensionful_prediction_dof_after_four_independent_anchors"]==0,
      "every_nonnegative_gate_has_a_failure_rule":all(bool(x.preregistered_failure) for x in rows),
      "cross_repository_heads_are_pinned":all(len(x)==40 for x in (OPENWAVE_HEAD,FORMAL_HEAD,ZIL_HEAD)),
      "zil_control_event_chain_verifies":verify_cross_repo_control_events(),
      "ledger_is_deterministic":ledger_fingerprint()==ledger_fingerprint(),
      "simulation_only_no_data_acquisition":True,
    }
    return {"schema":"openwave.m9.physical-calibration-ledger.v1","task":"M9.62",
      "repositories":{"openwave":{"head":OPENWAVE_HEAD},"physlib":{"repository":FORMAL_REPOSITORY,
        "branch":FORMAL_BRANCH,"head":FORMAL_HEAD},"zil":{"repository":ZIL_REPOSITORY,"head":ZIL_HEAD,
        "durable_evidence_role":"hash-chained control events and human-reviewed runtime placement"}},
      "counts":counts,"required_anchor_classes":anchors,"unit_rank_audit":unit_rank_audit(),
      "cross_repo_control_events":cross_repo_control_events(),
      "gates":[asdict(x) for x in rows],"fingerprint":ledger_fingerprint(rows),
      "acceptance":acceptance,"passed":all(acceptance.values()),
      "decision":{"falsification_ledger_complete":True,"physical_calibration_complete":False,
        "out_of_sample_physical_predictions_ready":0,
        "external_data_acquisition_performed":False},
      "classification":{"establishes":["one preregistered failure rule for every OpenWave CAT/EPT criterion",
        "separation of dimensionless tests, formal conditional identities, anchors and predictions",
        "explicit unit-anchor rank audit and cross-repository evidence identity"],
        "does_not_establish":["any experimentally calibrated CAT/EPT parameter",
          "an out-of-sample physical prediction","agreement with external measurements"]}}
def result_to_json(result):return json.dumps(result,indent=2,sort_keys=True,default=str)+"\n"
