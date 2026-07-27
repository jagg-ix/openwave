"""M9.124a: role profile for Page-Wootters, modular, and entropic clocks."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class ClockRole:
    key: str
    display_name: str
    physical_question: str
    carrier: str
    generator: str
    evolution: str
    reversibility: str
    physical_role: str
    formal_sources: tuple[str, ...]
    closed_evidence: tuple[str, ...]
    open_obligations: tuple[str, ...]


CLOCK_ROLES = (
    ClockRole(
        key="page_wootters_relational",
        display_name="Page-Wootters relational clock",
        physical_question="Relative to which subsystem reading is change described?",
        carrier="stationary system-clock history state with Hamiltonian constraint",
        generator="conditional system Hamiltonian; optionally Hamiltonian plus GKSL dissipator",
        evolution="condition the global state on a clock reading and compare conditional system states",
        reversibility="neutral: unitary in the dissipationless limit, dissipative when a GKSL term is supplied",
        physical_role="relational ordering and reference-frame selection",
        formal_sources=(
            "Physlib/QuantumMechanics/RelationalTime/PageWootters.lean",
        ),
        closed_evidence=(
            "Hamiltonian-constraint physical subspace",
            "effective-clock Hamiltonian decomposition",
            "dissipative conditional generator with unitary limit",
            "bipartite system/clock marginals and equal marginal entropy",
        ),
        open_obligations=(
            "derive conditional Schrödinger dynamics from a tensor Hamiltonian constraint and clock-state family",
            "identify and calibrate a physical clock subsystem",
        ),
    ),
    ClockRole(
        key="modular_thermal",
        display_name="Modular / thermal clock",
        physical_question="Which intrinsic reversible flow is selected by the state or thermal reference?",
        carrier="faithful state or Gibbs reference with modular Hamiltonian K = -log rho",
        generator="modular commutator ad_K or unitary U(s) = exp(-i K s)",
        evolution="state-dependent automorphism / isospectral conjugation",
        reversibility="reversible and entropy-preserving",
        physical_role="thermal ordering, equilibrium symmetry, and state-dependent reversible time",
        formal_sources=(
            "Physlib/QuantumMechanics/RelationalTime/EntropicThermalComplementarity.lean",
            "Physlib/QuantumMechanics/Lindblad/ThreeClockReversibilitySpectrum.lean",
        ),
        closed_evidence=(
            "von Neumann entropy invariance under modular unitary conjugation",
            "Hilbert-Schmidt orthogonality to commuting population directions",
            "purely imaginary spectral rate has norm-preserving flow",
        ),
        open_obligations=(
            "identify the modular reference state for a concrete physical system",
            "calibrate modular parameter s against laboratory or proper time",
        ),
    ),
    ClockRole(
        key="entropic_irreversible",
        display_name="Entropic / irreversible clock",
        physical_question="How much irreversible change or approach to equilibrium has accumulated?",
        carrier="open-system trajectory, relative-entropy distance, or positive GKSL jump rate",
        generator="dissipative real spectral part or H_I proportional to sum L_j^dagger L_j",
        evolution="contractive semigroup with nonnegative accumulated dissipation",
        reversibility="irreversible; freezes when the dissipative rate vanishes",
        physical_role="arrow of time, relaxation age, decoherence, and entropy production",
        formal_sources=(
            "Physlib/QuantumMechanics/Lindblad/ThreeClockReversibilitySpectrum.lean",
            "Physlib/QuantumMechanics/RelationalTime/PageWootters.lean",
        ),
        closed_evidence=(
            "negative real spectral rate gives strict contraction",
            "GKSL entropic rate is nonnegative",
            "conditional Page-Wootters dissipation rate is nonnegative and vanishes at jump equilibrium",
        ),
        open_obligations=(
            "prove one universal entropy clock for arbitrary physical processes",
            "calibrate accumulated entropic time against an independent observable",
        ),
    ),
)

PAIRWISE_BRIDGES = {
    "page_wootters__entropic": {
        "status": "formal carrier bridge",
        "content": "A conditioned Page-Wootters system may evolve by a Hamiltonian commutator plus a GKSL dissipator; the jump operators define a nonnegative conditional entropic rate.",
        "boundary": "The tensor-constraint-to-conditioned-GKSL derivation is not completed automatically.",
    },
    "modular__entropic": {
        "status": "static and dynamical complementarity",
        "content": "The modular flow preserves spectrum and entropy, while the entropic direction changes populations and is orthogonal to the modular commutator direction; a static Gibbs bridge relates modular expectation to entropy.",
        "boundary": "Complementarity and a static bridge do not make the two clock parameters identical.",
    },
    "page_wootters__modular": {
        "status": "conditional identification only",
        "content": "A Page-Wootters conditioned system can use the modular Hamiltonian as its generator when the consumer explicitly identifies H_S with K = -log rho.",
        "boundary": "The repository does not derive that identification for every clock state or physical system.",
    },
}


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_three_clock_time_profile() -> dict[str, Any]:
    roles = tuple(asdict(role) for role in CLOCK_ROLES)
    payload = {
        "schema": "openwave.m9.three-clock-time-profile.v1",
        "task": "M9.124a",
        "roles": roles,
        "pairwise_bridges": PAIRWISE_BRIDGES,
        "interpretation": {
            "page_wootters": "relational ordering: change relative to a clock subsystem",
            "modular": "reversible state-dependent thermal/automorphism flow",
            "entropic": "irreversible accumulated relaxation or entropy production",
        },
        "claim_boundary": {
            "three_roles_are_three_identical_parameters": False,
            "pairwise_bridge_is_triple_equivalence": False,
            "formal_clock_carrier_is_physical_calibration": False,
            "page_wootters_conditioning_is_intrinsically_irreversible": False,
        },
    }
    acceptance = {
        "exactly_three_clock_roles_are_profiled": len(roles) == 3,
        "clock_roles_are_distinct": len({role["physical_role"] for role in roles}) == 3,
        "all_roles_have_formal_sources": all(role["formal_sources"] for role in roles),
        "all_three_pairwise_bridges_are_explicit": set(PAIRWISE_BRIDGES) == {
            "page_wootters__entropic",
            "modular__entropic",
            "page_wootters__modular",
        },
        "each_bridge_retains_a_boundary": all(item["boundary"] for item in PAIRWISE_BRIDGES.values()),
        "no_identity_or_calibration_claim_is_promoted": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "three_clock_role_taxonomy_complete": True,
            "pairwise_bridge_ledger_complete": True,
            "single_unified_physical_clock_established": False,
            "external_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
