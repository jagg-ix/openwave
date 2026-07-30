"""M12.1 executable Standard-Model particle-zoo and selection-rule registry.

The module mirrors the exact finite classifications and additive conservation
laws proved in entropic-physlib. Numerical masses and rates are deliberately
outside this first milestone.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

MILESTONE = "M12.1"
SCHEMA = "openwave.m12.standard-model-zoo.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/StandardModelParticleContent.lean",
        "sha": "1a6164c30723eb78c9bccdaa91ead58fbad7cab9",
        "theorem": "card_SMParticle",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/GaugeBosonZoo.lean",
        "sha": "97a7272bdbc981d52920bb368265ceb335792793",
        "theorem": "gauge_boson_sector",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/ParticleZooCPT.lean",
        "sha": "a26a50038f02ac49ca50b6c5d19ef36e76d611de",
        "theorem": "zoo_cpt_invariance",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/BaryonLeptonNumberConservation.lean",
        "sha": "3c887c6c5f504312bd063d125f5b176ea63a499a",
        "theorem": "beta_decay_conserves",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/ExperimentalParticleReactions.lean",
        "sha": "b57128a851619b9bcbc1c6198e259f5a4a37ba9e",
        "theorem": "observed_reactions_conserve",
    },
)

FamilyVector = tuple[int, int, int]


@dataclass(frozen=True)
class AdditiveQuantumNumbers:
    electric: Fraction
    baryon: Fraction = Fraction(0)
    lepton: Fraction = Fraction(0)
    family: FamilyVector = (0, 0, 0)

    def __add__(self, other: "AdditiveQuantumNumbers") -> "AdditiveQuantumNumbers":
        return AdditiveQuantumNumbers(
            self.electric + other.electric,
            self.baryon + other.baryon,
            self.lepton + other.lepton,
            tuple(a + b for a, b in zip(self.family, other.family)),
        )

    def conjugate(self) -> "AdditiveQuantumNumbers":
        return AdditiveQuantumNumbers(
            -self.electric,
            -self.baryon,
            -self.lepton,
            tuple(-x for x in self.family),
        )

    def is_zero(self) -> bool:
        return self == AdditiveQuantumNumbers(Fraction(0))

    def as_json(self) -> dict[str, Any]:
        return {
            "electric": str(self.electric),
            "baryon": str(self.baryon),
            "lepton": str(self.lepton),
            "family": list(self.family),
        }


@dataclass(frozen=True)
class ParticleType:
    key: str
    name: str
    sector: str
    generation: int | None
    charge: Fraction
    spin: Fraction
    baryon: Fraction
    lepton: Fraction
    family: FamilyVector
    color_multiplicity: int
    self_conjugate: bool

    @property
    def quantum_numbers(self) -> AdditiveQuantumNumbers:
        return AdditiveQuantumNumbers(
            self.charge, self.baryon, self.lepton, self.family
        )


def _fermion(
    key: str,
    name: str,
    sector: str,
    generation: int,
    charge: Fraction,
    baryon: Fraction,
    lepton: Fraction,
    family: FamilyVector,
    color: int,
) -> ParticleType:
    return ParticleType(
        key,
        name,
        sector,
        generation,
        charge,
        Fraction(1, 2),
        baryon,
        lepton,
        family,
        color,
        False,
    )


STANDARD_MODEL_TYPES: tuple[ParticleType, ...] = (
    _fermion("u", "up quark", "quark", 1, Fraction(2, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("d", "down quark", "quark", 1, Fraction(-1, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("c", "charm quark", "quark", 2, Fraction(2, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("s", "strange quark", "quark", 2, Fraction(-1, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("t", "top quark", "quark", 3, Fraction(2, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("b", "bottom quark", "quark", 3, Fraction(-1, 3), Fraction(1, 3), Fraction(0), (0, 0, 0), 3),
    _fermion("e", "electron", "lepton", 1, Fraction(-1), Fraction(0), Fraction(1), (1, 0, 0), 1),
    _fermion("nu_e", "electron neutrino", "lepton", 1, Fraction(0), Fraction(0), Fraction(1), (1, 0, 0), 1),
    _fermion("mu", "muon", "lepton", 2, Fraction(-1), Fraction(0), Fraction(1), (0, 1, 0), 1),
    _fermion("nu_mu", "muon neutrino", "lepton", 2, Fraction(0), Fraction(0), Fraction(1), (0, 1, 0), 1),
    _fermion("tau", "tau", "lepton", 3, Fraction(-1), Fraction(0), Fraction(1), (0, 0, 1), 1),
    _fermion("nu_tau", "tau neutrino", "lepton", 3, Fraction(0), Fraction(0), Fraction(1), (0, 0, 1), 1),
    ParticleType("photon", "photon", "boson", None, Fraction(0), Fraction(1), Fraction(0), Fraction(0), (0, 0, 0), 1, True),
    ParticleType("W", "W boson type", "boson", None, Fraction(0), Fraction(1), Fraction(0), Fraction(0), (0, 0, 0), 2, False),
    ParticleType("Z", "Z boson", "boson", None, Fraction(0), Fraction(1), Fraction(0), Fraction(0), (0, 0, 0), 1, True),
    ParticleType("gluon", "gluon type", "boson", None, Fraction(0), Fraction(1), Fraction(0), Fraction(0), (0, 0, 0), 8, True),
    ParticleType("H", "Higgs boson", "boson", None, Fraction(0), Fraction(0), Fraction(0), Fraction(0), (0, 0, 0), 1, True),
)

GAUGE_STATES: tuple[tuple[str, Fraction], ...] = (
    ("photon", Fraction(0)),
    ("W+", Fraction(1)),
    ("W-", Fraction(-1)),
    ("Z", Fraction(0)),
    *((f"g{index}", Fraction(0)) for index in range(1, 9)),
)

QN: dict[str, AdditiveQuantumNumbers] = {
    p.key: p.quantum_numbers for p in STANDARD_MODEL_TYPES
}
QN.update(
    {
        "proton": AdditiveQuantumNumbers(Fraction(1), Fraction(1), Fraction(0)),
        "neutron": AdditiveQuantumNumbers(Fraction(0), Fraction(1), Fraction(0)),
        "pi+": AdditiveQuantumNumbers(Fraction(1)),
        "pi0": AdditiveQuantumNumbers(Fraction(0)),
        "pi-": AdditiveQuantumNumbers(Fraction(-1)),
        "W+": AdditiveQuantumNumbers(Fraction(1)),
        "W-": AdditiveQuantumNumbers(Fraction(-1)),
    }
)


def antiparticle(qn: AdditiveQuantumNumbers) -> AdditiveQuantumNumbers:
    return qn.conjugate()


def total(items: Iterable[AdditiveQuantumNumbers]) -> AdditiveQuantumNumbers:
    result = AdditiveQuantumNumbers(Fraction(0))
    for item in items:
        result = result + item
    return result


@dataclass(frozen=True)
class Reaction:
    name: str
    incoming: tuple[AdditiveQuantumNumbers, ...]
    outgoing: tuple[AdditiveQuantumNumbers, ...]
    expected_family_conservation: bool = True

    @property
    def incoming_total(self) -> AdditiveQuantumNumbers:
        return total(self.incoming)

    @property
    def outgoing_total(self) -> AdditiveQuantumNumbers:
        return total(self.outgoing)

    @property
    def qbl_conserved(self) -> bool:
        a, b = self.incoming_total, self.outgoing_total
        return (a.electric, a.baryon, a.lepton) == (b.electric, b.baryon, b.lepton)

    @property
    def family_conserved(self) -> bool:
        return self.incoming_total.family == self.outgoing_total.family


def reaction_catalogue() -> tuple[Reaction, ...]:
    anti_nu_e = antiparticle(QN["nu_e"])
    anti_nu_mu = antiparticle(QN["nu_mu"])
    positron = antiparticle(QN["e"])
    anti_muon = antiparticle(QN["mu"])
    return (
        Reaction("beta_decay", (QN["neutron"],), (QN["proton"], QN["e"], anti_nu_e)),
        Reaction("pion_decay", (QN["pi+"],), (anti_muon, QN["nu_mu"])),
        Reaction("michel_decay", (QN["mu"],), (QN["e"], anti_nu_e, QN["nu_mu"])),
        Reaction("inverse_beta_decay", (anti_nu_e, QN["proton"]), (QN["neutron"], positron)),
        Reaction("neutrino_capture", (QN["nu_e"], QN["neutron"]), (QN["proton"], QN["e"])),
        Reaction("w_plus_electron", (QN["W+"],), (positron, QN["nu_e"])),
        Reaction("w_minus_muon", (QN["W-"],), (QN["mu"], anti_nu_mu)),
        Reaction("z_to_e_pair", (QN["Z"],), (QN["e"], positron)),
        Reaction("mu_to_e_gamma", (QN["mu"],), (QN["e"], QN["photon"]), False),
    )


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "model_id": "M12",
        "milestone": MILESTONE,
        "model": "CAT/EPT Standard-Model particle-zoo registry",
        "study_api": (
            "openwave.xperiments.m12_particle_zoo."
            "standard_model_zoo_m121:run_standard_model_zoo_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


def run_standard_model_zoo_study() -> dict[str, Any]:
    quarks = tuple(p for p in STANDARD_MODEL_TYPES if p.sector == "quark")
    leptons = tuple(p for p in STANDARD_MODEL_TYPES if p.sector == "lepton")
    bosons = tuple(p for p in STANDARD_MODEL_TYPES if p.sector == "boson")
    fermions = quarks + leptons
    reactions = reaction_catalogue()
    observed = reactions[:-1]
    forbidden = reactions[-1]
    cpt_errors = {
        p.key: not (p.quantum_numbers + antiparticle(p.quantum_numbers)).is_zero()
        for p in fermions
    }
    diagnostics = {
        "particle_type_count": len(STANDARD_MODEL_TYPES),
        "fermion_type_count": len(fermions),
        "quark_type_count": len(quarks),
        "lepton_type_count": len(leptons),
        "boson_type_count": len(bosons),
        "gauge_state_count": len(GAUGE_STATES),
        "gauge_charge_sum": str(sum((q for _, q in GAUGE_STATES), Fraction(0))),
        "maximum_cpt_pair_error": int(any(cpt_errors.values())),
        "observed_qbl_failures": [r.name for r in observed if not r.qbl_conserved],
        "observed_family_failures": [
            r.name for r in observed if r.expected_family_conservation and not r.family_conserved
        ],
        "mu_to_e_gamma_qbl_conserved": forbidden.qbl_conserved,
        "mu_to_e_gamma_family_conserved": forbidden.family_conserved,
        "quark_charge_set": sorted({str(p.charge) for p in quarks}),
        "all_fermions_spin_half": all(p.spin == Fraction(1, 2) for p in fermions),
                "all_gauge_states_spin_one": all(
            p.spin == Fraction(1) for p in bosons if p.key != "H"
        ),
        "higgs_spin_zero": next(p for p in bosons if p.key == "H").spin == Fraction(0),
    }
    acceptance = {
        "standard_model_has_17_types": diagnostics["particle_type_count"] == 17,
        "fermion_split_is_6_plus_6": (
            diagnostics["fermion_type_count"] == 12
            and diagnostics["quark_type_count"] == 6
            and diagnostics["lepton_type_count"] == 6
        ),
        "boson_type_count_is_five": diagnostics["boson_type_count"] == 5,
        "gauge_state_count_is_twelve": diagnostics["gauge_state_count"] == 12,
        "gauge_charges_balance": diagnostics["gauge_charge_sum"] == "0",
        "quark_charges_are_standard": diagnostics["quark_charge_set"] == ["-1/3", "2/3"],
        "all_fermion_cpt_pairs_annihilate": diagnostics["maximum_cpt_pair_error"] == 0,
        "observed_reactions_conserve_qbl": not diagnostics["observed_qbl_failures"],
        "observed_flavor_rules_close": not diagnostics["observed_family_failures"],
        "mu_to_e_gamma_is_qbl_allowed": diagnostics["mu_to_e_gamma_qbl_conserved"],
        "mu_to_e_gamma_breaks_family_number": not diagnostics["mu_to_e_gamma_family_conserved"],
        "fermion_and_boson_spins_match": (
            diagnostics["all_fermions_spin_half"]
            and diagnostics["all_gauge_states_spin_one"]
            and diagnostics["higgs_spin_zero"]
        ),
    }
    payload = canonical_payload()
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "quantum_numbers_are_empirical_assignments": True,
            "selection_rules_are_exact_bookkeeping": True,
            "rates_and_matrix_elements_are_not_claimed": True,
        },
    }
