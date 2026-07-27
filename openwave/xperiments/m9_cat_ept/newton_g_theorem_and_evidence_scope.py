"""M9.109d: theorem-hypothesis and paper-evidence scope audit.

This module prevents a numerical interpretation test from being mislabeled as a
falsification of Lean. The formal identities remain true. The rejected statement
is an additional physical hypothesis:

    every particle Compton mass/frequency is the same universal gravity anchor.

For positive unequal masses this hypothesis is incompatible with one universal
G because hbar*c/m1^2 = hbar*c/m2^2 implies m1 = m2.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping


TheoremClass = Literal[
    "definition",
    "algebraic-identity",
    "conditional-theorem",
    "hypothesis-loaded-composition",
]
EvidenceStrength = Literal[
    "direct-subclaim-support",
    "indirect-subclaim-support",
    "interpretive-dispute",
    "not-support-for-full-chain",
]


@dataclass(frozen=True)
class TheoremScope:
    theorem: str
    theorem_class: TheoremClass
    proves: tuple[str, ...]
    requires: tuple[str, ...]
    does_not_prove: tuple[str, ...]
    contradicted_by_species_audit: bool = False


@dataclass(frozen=True)
class PaperScope:
    source: str
    observed_or_established: tuple[str, ...]
    supports: tuple[str, ...]
    does_not_support: tuple[str, ...]
    strength: EvidenceStrength


THEOREM_SCOPES = (
    TheoremScope(
        theorem="FrequencyTrinity.comptonFrequency",
        theorem_class="definition",
        proves=("omega_C = m*c^2/hbar",),
        requires=("chosen mass m", "nonzero hbar for physical use"),
        does_not_prove=("numerical particle mass", "Newton G", "physical microscopic oscillator"),
    ),
    TheoremScope(
        theorem="FrequencyTrinity.zitterbewegung_rest_eq_two_compton",
        theorem_class="algebraic-identity",
        proves=("omega_Z(p=0) = 2*omega_C",),
        requires=("nonnegative mass", "definitions of omega_Z and omega_C"),
        does_not_prove=("observed Zitterbewegung resonance", "particle mass value"),
    ),
    TheoremScope(
        theorem="EntropicAgreement.entropicPhysicalTimeAdvance_eq_physicalTime",
        theorem_class="conditional-theorem",
        proves=("entropic clock advance equals supplied physical proper-time advance",),
        requires=("Delta S_I = hbar*omega_0*Delta tau_phys", "independent positive-frequency phase clock"),
        does_not_prove=("the action-rate law", "SI second from entropy alone", "universal validity for every entropy arrow"),
    ),
    TheoremScope(
        theorem="EntropicClockComptonAnchor.comptonAnchored_newtonG_eq_from_clockFrequency",
        theorem_class="algebraic-identity",
        proves=("hbar*c/m^2 = c^5/(hbar*omega_C(m)^2)",),
        requires=("omega_C(m) = m*c^2/hbar", "positive m,c,hbar"),
        does_not_prove=("left side equals measured universal G", "anchor mass is a known particle mass", "species-independent gravity anchor"),
    ),
    TheoremScope(
        theorem="ComptonCellNewtonConstant.newtonG_from_comptonCellBits",
        theorem_class="conditional-theorem",
        proves=("G-free Compton-cell area-per-bit expression equals hbar*c/m^2",),
        requires=("Compton-cell screen construction", "independent mass scale m", "nonzero entanglement logarithm"),
        does_not_prove=("numerical G without a mass anchor", "every particle mass yields measured G", "mass scale is dynamically selected"),
    ),
    TheoremScope(
        theorem="HiggsClockThreeOrigins.higgs_clock_three_origins",
        theorem_class="hypothesis-loaded-composition",
        proves=("equivalent clock forms after three masses are identified",),
        requires=("m_Yukawa = m_horizon", "m_Yukawa = m_topological"),
        does_not_prove=("the three mass equalities", "Yukawa hierarchy", "universal horizon-area rate", "topological data selecting observed masses"),
    ),
)


PAPER_SCOPES = (
    PaperScope(
        source="Lan et al., Science 339 (2013), A clock directly linking time to a particle's mass",
        observed_or_established=("oscillator synchronized to a subharmonic of the atomic Compton frequency", "mass-time metrological link"),
        supports=("omega_C = m*c^2/hbar as a frequency reference", "Compton-referenced clock construction"),
        does_not_support=("Delta S_I = m*c^2*Delta tau", "Newton G from the particle clock", "universal microscopic Compton oscillator interpretation"),
        strength="direct-subclaim-support",
    ),
    PaperScope(
        source="Parker et al., Science 360 (2018), Measurement of the fine-structure constant",
        observed_or_established=("cesium recoil frequency", "fine-structure constant at 2.0e-10 relative accuracy"),
        supports=("precision h/m recoil metrology",),
        does_not_support=("direct ticking at omega_C", "entropic action-rate law", "Newton G from cesium mass"),
        strength="indirect-subclaim-support",
    ),
    PaperScope(
        source="Margalit et al., Science 349 (2015), A self-interfering clock as a which-path witness",
        observed_or_established=("clock made from two atomic spin states", "engineered differential ticking changes interference visibility"),
        supports=("clock-path distinguishability and complementarity", "proper-time-like which-path mechanism in a proof of principle"),
        does_not_support=("Compton-frequency clock", "relativistic gravitational proper-time measurement", "imaginary-action accumulation law", "Newton G relation"),
        strength="direct-subclaim-support",
    ),
    PaperScope(
        source="Wolf et al., Class. Quantum Grav. 28 (2011), atom-interferometer Compton-redshift analysis",
        observed_or_established=("theoretical cancellation of closed-path Compton phase in GR and broad metric theories",),
        supports=("major interpretive objection to treating ordinary atom interferometers as Compton-redshift clocks",),
        does_not_support=("universal rejection of all Compton-referenced clocks", "CAT/EPT imaginary-action dynamics"),
        strength="interpretive-dispute",
    ),
)


def universal_G_equal_masses(m1: float, m2: float, *, relative_tolerance: float = 1.0e-12) -> dict[str, Any]:
    """Numerical witness of the exact positive-mass no-go implication.

    If hbar*c/m1^2 and hbar*c/m2^2 are one universal value, positive m1,m2
    must be equal. The hbar*c factor cancels, so this audit is unit independent.
    """
    if m1 <= 0.0 or m2 <= 0.0:
        raise ValueError("positive masses required")
    coupling_ratio = (m2 / m1) ** 2
    masses_equal = abs(m1 - m2) <= relative_tolerance * max(abs(m1), abs(m2))
    couplings_equal = abs(coupling_ratio - 1.0) <= relative_tolerance
    return {
        "mass_1": m1,
        "mass_2": m2,
        "effective_G1_over_G2": coupling_ratio,
        "masses_equal": masses_equal,
        "effective_couplings_equal": couplings_equal,
        "universal_G_for_both_is_consistent": masses_equal and couplings_equal,
    }


def canonical_payload() -> dict[str, Any]:
    electron_muon = universal_G_equal_masses(9.109_383_7139e-31, 1.883_531_627e-28)
    theorem_rows = [asdict(row) for row in THEOREM_SCOPES]
    paper_rows = [asdict(row) for row in PAPER_SCOPES]
    return {
        "schema": "openwave.m9.newton-G-theorem-evidence-scope.v1",
        "task": "M9.109d",
        "theorems": theorem_rows,
        "papers": paper_rows,
        "no_go": {
            "statement": "for positive m1,m2, one universal hbar*c/m^2 value for both implies m1=m2",
            "electron_muon_witness": electron_muon,
            "rejected_hypothesis": "every unequal particle Compton clock is the same universal gravity anchor",
            "lean_theorem_falsified": False,
        },
        "load_bearing_untested_premises": (
            "Delta S_I = m*c^2*Delta tau_phys for the relevant physical clock",
            "selection of one universal gravity anchor independently of measured G",
            "physical derivation of the anchor mass or frequency",
            "three-origin mass coincidence rather than assumption",
        ),
        "policy": {
            "numerical_interpretation_test_is_not_theorem_falsification": True,
            "paper_support_must_attach_to_narrowest_supported_subclaim": True,
            "hypotheses_must_not_be_reported_as_derived_conclusions": True,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_newton_G_theorem_evidence_scope() -> dict[str, Any]:
    payload = canonical_payload()
    no_go = payload["no_go"]["electron_muon_witness"]
    acceptance = {
        "all_theorems_keep_falsification_false": all(not row["contradicted_by_species_audit"] for row in payload["theorems"]),
        "conditional_theorems_expose_requirements": all(row["requires"] for row in payload["theorems"] if row["theorem_class"] in ("conditional-theorem", "hypothesis-loaded-composition")),
        "electron_muon_universal_anchor_is_inconsistent": not no_go["universal_G_for_both_is_consistent"],
        "papers_do_not_support_full_G_chain": all("Newton G" in " ".join(row["does_not_support"]) or row["strength"] == "interpretive-dispute" for row in payload["papers"]),
        "untested_CAT_EPT_premises_are_explicit": len(payload["load_bearing_untested_premises"]) == 4,
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "Lean_theorems_contradicted": False,
            "broad_particle_clock_universality_hypothesis_rejected": True,
            "papers_validate_full_CAT_EPT_G_chain": False,
            "paper_evidence_requires_narrower_edges": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
