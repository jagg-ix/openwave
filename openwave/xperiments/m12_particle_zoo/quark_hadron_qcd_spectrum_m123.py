"""M12.3 quark, hadron, and one-loop QCD coverage.

Empirical quark and hadron masses are inputs. Executable claims are exact flavor
bookkeeping, SU(3) mass-relation diagnostics, one-loop running, and reuse of the
existing M10 non-Abelian carrier.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .standard_model_zoo_m121 import run_standard_model_zoo_study
from .electroweak_lepton_neutrino_m122 import run_electroweak_lepton_neutrino_study

MILESTONE = "M12.3"
SCHEMA = "openwave.m12.quark-hadron-qcd-spectrum.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {"path": "Physlib/QuantumMechanics/ComplexAction/Particles/HadronFlavorModel.lean", "sha": "dcf30b22a28719ccddff788adcbf3d8f4a970ed9", "theorem": "gmn_strong_baryon"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/Particles/HadronMassSpectrum.lean", "sha": "302e185e6db321d3795561b7bcf372b999120427", "theorem": "gellMannOkubo_octet"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/Particles/HadronMassSpectrum.lean", "sha": "302e185e6db321d3795561b7bcf372b999120427", "theorem": "decuplet_omega_prediction"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/Particles/QuarkMassSpectrumRunning.lean", "sha": "c13f282173ad4587030178727dc93e9e5aafff7d", "theorem": "alphaS_decreases"},
)

@dataclass(frozen=True)
class Quark:
    charge: Fraction
    baryon: Fraction
    i3: Fraction
    flavor: tuple[int, int, int, int]  # S,C,B',T
    mass_mev: float

    @property
    def hypercharge(self) -> Fraction:
        return self.baryon + sum((Fraction(x) for x in self.flavor), Fraction(0))

QUARKS = {
    "u": Quark(Fraction(2,3), Fraction(1,3), Fraction(1,2), (0,0,0,0), 2.16),
    "d": Quark(Fraction(-1,3), Fraction(1,3), Fraction(-1,2), (0,0,0,0), 4.67),
    "s": Quark(Fraction(-1,3), Fraction(1,3), Fraction(0), (-1,0,0,0), 93.4),
    "c": Quark(Fraction(2,3), Fraction(1,3), Fraction(0), (0,1,0,0), 1270.0),
    "b": Quark(Fraction(-1,3), Fraction(1,3), Fraction(0), (0,0,-1,0), 4180.0),
    "t": Quark(Fraction(2,3), Fraction(1,3), Fraction(0), (0,0,0,1), 172690.0),
}

HADRONS = {
    "proton": (("u",1),("u",1),("d",1)),
    "neutron": (("u",1),("d",1),("d",1)),
    "lambda": (("u",1),("d",1),("s",1)),
    "sigma_plus": (("u",1),("u",1),("s",1)),
    "sigma_zero": (("u",1),("d",1),("s",1)),
    "sigma_minus": (("d",1),("d",1),("s",1)),
    "xi_zero": (("u",1),("s",1),("s",1)),
    "xi_minus": (("d",1),("s",1),("s",1)),
    "omega_minus": (("s",1),("s",1),("s",1)),
    "lambda_c_plus": (("u",1),("d",1),("c",1)),
    "pion_plus": (("u",1),("d",-1)),
    "pion_minus": (("d",1),("u",-1)),
    "kaon_plus": (("u",1),("s",-1)),
    "kaon_zero": (("d",1),("s",-1)),
    "d_plus": (("c",1),("d",-1)),
    "jpsi": (("c",1),("c",-1)),
    "upsilon": (("b",1),("b",-1)),
}

HADRON_MASS_MEV = {
    "proton": 938.272, "neutron": 939.565, "lambda": 1115.683,
    "sigma_plus": 1189.37, "sigma_zero": 1192.642, "sigma_minus": 1197.449,
    "xi_zero": 1314.86, "xi_minus": 1321.71, "omega_minus": 1672.45,
    "pion_zero": 134.977, "kaon_plus": 493.677,
}
DECU = {"delta":1232.0, "sigma":1384.57, "xi":1533.4, "omega":1672.45}
ETA_MASS_MEV = 547.862

@dataclass(frozen=True)
class Config:
    alpha_s_reference: float = 0.1181
    reference_scale_gev: float = 91.1876
    active_flavors: int = 5
    scales_gev: tuple[float, ...] = (91.1876, 182.3752, 911.876)

    def validate(self) -> None:
        if self.alpha_s_reference <= 0 or self.reference_scale_gev <= 0:
            raise ValueError("positive QCD inputs required")
        if not 0 <= self.active_flavors <= 16:
            raise ValueError("one-loop asymptotic-freedom range is nf <= 16")
        if not self.scales_gev or min(self.scales_gev) < self.reference_scale_gev:
            raise ValueError("scales must start at or above the reference scale")

def composite_numbers(content):
    charge = baryon = i3 = Fraction(0)
    flavor = [0,0,0,0]
    for name, sign in content:
        q = QUARKS[name]
        charge += sign*q.charge; baryon += sign*q.baryon; i3 += sign*q.i3
        for i, value in enumerate(q.flavor): flavor[i] += sign*value
    hypercharge = baryon + sum((Fraction(x) for x in flavor), Fraction(0))
    return {"charge":charge, "baryon":baryon, "i3":i3, "flavor":tuple(flavor), "hypercharge":hypercharge}

def beta_zero(nf: int) -> float: return 11.0 - 2.0*nf/3.0

def alpha_s_run(alpha0: float, b0: float, mu: float, mu0: float) -> float:
    return alpha0 / (1.0 + b0*alpha0*math.log(mu/mu0)/(2.0*math.pi))

def _m10_registration() -> dict[str, Any]:
    from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
    return run_model_registration_study()

def canonical_payload(config: Config | None = None) -> dict[str, Any]:
    cfg = Config() if config is None else config
    return {"schema":SCHEMA, "model_id":"M12", "milestone":MILESTONE,
            "model":"CAT/EPT executable particle-zoo coverage model", "configuration":asdict(cfg),
            "lineage":["M12.1","M12.2","M12.3"],
            "study_api":"openwave.xperiments.m12_particle_zoo.quark_hadron_qcd_spectrum_m123:run_particle_zoo_model_study",
            "formal_authority":{"repository":"jagg-ix/entropic-physlib-private", "branch":"entropic-physlib-linear-full", "head":FORMAL_HEAD, "sources":list(FORMAL_SOURCES)}}

def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",",":"), default=str).encode()).hexdigest()

def run_particle_zoo_model_study(config: Config | None = None) -> dict[str, Any]:
    cfg = Config() if config is None else config; cfg.validate()
    qmass = [QUARKS[n].mass_mev for n in ("u","d","s","c","b","t")]
    q_gmn = {n:q.charge-(q.i3+q.hypercharge/2) for n,q in QUARKS.items()}
    hnum = {n:composite_numbers(c) for n,c in HADRONS.items()}
    h_gmn = {n:v["charge"]-(v["i3"]+v["hypercharge"]/2) for n,v in hnum.items()}

    n = (HADRON_MASS_MEV["proton"]+HADRON_MASS_MEV["neutron"])/2
    xi = (HADRON_MASS_MEV["xi_zero"]+HADRON_MASS_MEV["xi_minus"])/2
    sigma = (HADRON_MASS_MEV["sigma_plus"]+HADRON_MASS_MEV["sigma_zero"]+HADRON_MASS_MEV["sigma_minus"])/3
    lam = HADRON_MASS_MEV["lambda"]
    oct_rel = abs(2*(n+xi)-(3*lam+sigma))/(3*lam+sigma)
    meson_rel = abs(4*HADRON_MASS_MEV["kaon_plus"]**2-(3*ETA_MASS_MEV**2+HADRON_MASS_MEV["pion_zero"]**2))/(3*ETA_MASS_MEV**2+HADRON_MASS_MEV["pion_zero"]**2)
    spacings = [DECU["sigma"]-DECU["delta"], DECU["xi"]-DECU["sigma"], DECU["omega"]-DECU["xi"]]
    spacing_spread = (max(spacings)-min(spacings))/(sum(spacings)/3)
    omega_pred = 2*DECU["xi"]-DECU["sigma"]
    omega_rel = abs(omega_pred-DECU["omega"])/DECU["omega"]

    b0 = beta_zero(cfg.active_flavors)
    running = [alpha_s_run(cfg.alpha_s_reference,b0,scale,cfg.reference_scale_gev) for scale in cfg.scales_gev]
    prior121 = run_standard_model_zoo_study(); prior122 = run_electroweak_lepton_neutrino_study(); m10 = _m10_registration()
    diagnostics = {
        "quark_mass_hierarchy": all(x<y for x,y in zip(qmass,qmass[1:])),
        "quark_gmn_failures":[n for n,e in q_gmn.items() if e != 0],
        "hadron_gmn_failures":[n for n,e in h_gmn.items() if e != 0],
        "baryon_number_failures":[n for n in HADRONS if (len(HADRONS[n])==3 and hnum[n]["baryon"] != 1)],
        "proton_charge":str(hnum["proton"]["charge"]), "neutron_charge":str(hnum["neutron"]["charge"]),
        "lambda_strangeness":hnum["lambda"]["flavor"][0], "omega_strangeness":hnum["omega_minus"]["flavor"][0],
        "octet_empirical_relative_residual":oct_rel, "meson_empirical_relative_residual":meson_rel,
        "decuplet_spacing_relative_spread":spacing_spread, "omega_prediction_relative_error":omega_rel,
        "beta_zero":b0, "beta_function_negative":(-b0*cfg.alpha_s_reference**2/(2*math.pi))<0,
        "alpha_s_running":running, "m10_qcd_passed":bool(m10["passed"]),
        "m12_1_passed":bool(prior121["passed"]), "m12_2_passed":bool(prior122["passed"]),
    }
    acceptance = {
        "prior_layers_pass": diagnostics["m12_1_passed"] and diagnostics["m12_2_passed"],
        "quark_mass_data_ordered":diagnostics["quark_mass_hierarchy"],
        "strong_gmn_quarks":not diagnostics["quark_gmn_failures"],
        "strong_gmn_hadrons":not diagnostics["hadron_gmn_failures"],
        "named_quantum_numbers":diagnostics["proton_charge"]=="1" and diagnostics["neutron_charge"]=="0" and diagnostics["lambda_strangeness"]==-1 and diagnostics["omega_strangeness"]==-3,
        "pdg_octet_percent_level":oct_rel<0.01, "pdg_meson_order_ten_percent":meson_rel<0.08,
        "pdg_decuplet_approximately_equal":spacing_spread<0.12, "omega_relation_percent_level":omega_rel<0.01,
        "asymptotic_freedom":b0>0 and diagnostics["beta_function_negative"] and all(x>=y for x,y in zip(running,running[1:])),
        "m10_nonabelian_carrier_passes":diagnostics["m10_qcd_passed"],
    }
    payload=canonical_payload(cfg)
    return {**payload, "task":MILESTONE, "diagnostics":diagnostics, "acceptance":acceptance,
            "coverage":{"fundamental_particle_types":17,"gauge_boson_states":12,"quark_flavors":6,"charged_lepton_generations":3,"neutrino_flavors":3,"named_hadrons":len(HADRONS),"reaction_selection_rules":9},
            "fingerprint":fingerprint(payload), "passed":all(acceptance.values()),
            "decision":{"pdg_masses_are_inputs":True,"su3_mass_relations_are_checked":True,"one_loop_qcd_running_is_executable":True,"m10_supplies_finite_nonabelian_dynamics":True,"first_principles_spectrum_is_not_claimed":True}}
