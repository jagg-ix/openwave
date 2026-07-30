"""M12.2 electroweak, charged-lepton, and neutrino phenomenology.

The module executes the tree-level formulas and flavor bookkeeping already
formalized in entropic-physlib. Couplings, masses, PMNS angles, and PDG
lifetimes remain explicit inputs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .standard_model_zoo_m121 import (
    AdditiveQuantumNumbers,
    QN,
    antiparticle,
    run_standard_model_zoo_study,
)

MILESTONE = "M12.2"
SCHEMA = "openwave.m12.electroweak-lepton-neutrino.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/ElectroweakGaugeBosonPhenomenology.lean",
        "sha": "da3d6dafa85b1aa9f2bbfc0d2a2b7ccd3f466ab2",
        "theorem": "electroweakGaugeBosonPhenomenology_checked",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/LeptonFlavorNumbers.lean",
        "sha": "000cbb4e074c5a55592ba8fd9da7562a6ac1c1a5",
        "theorem": "sargent_universality_ratio",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/MichelDecayFlavor.lean",
        "sha": "aa0d6a5b05193b4fe108d9c0de462449b67d25c6",
        "theorem": "michel_decay_complete",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/NeutrinoModel.lean",
        "sha": "97cf848ed10ccbc434f89830d765fa9ebe481e11",
        "theorem": "deltaM21Sq_pos_of_normal",
    },
)


@dataclass(frozen=True)
class ElectroweakLeptonNeutrinoConfig:
    g: float = 0.653
    g_prime: float = 0.358
    higgs_vev_gev: float = 246.22
    alpha_em: float = 1.0 / 137.035999084
    fermi_constant_gev2: float = 1.1663787e-5
    center_of_mass_energy_gev: float = 100.0
    neutrino_energy_gev: float = 1.0
    baseline_km: float = 295.0
    m1_ev: float = 0.010
    delta_m21_sq_ev2: float = 7.42e-5
    delta_m31_sq_ev2: float = 2.517e-3
    theta12_deg: float = 33.44
    theta23_deg: float = 49.2
    theta13_deg: float = 8.57
    delta_cp_deg: float = 195.0
    hbar_gev_s: float = 6.582119569e-25

    def validate(self) -> None:
        positive = (
            self.g,
            self.g_prime,
            self.higgs_vev_gev,
            self.alpha_em,
            self.fermi_constant_gev2,
            self.center_of_mass_energy_gev,
            self.neutrino_energy_gev,
            self.m1_ev,
            self.delta_m21_sq_ev2,
            self.delta_m31_sq_ev2,
            self.hbar_gev_s,
        )
        if min(positive) <= 0.0:
            raise ValueError("positive electroweak and neutrino inputs required")
        if self.baseline_km < 0.0:
            raise ValueError("nonnegative baseline required")


def electroweak_mass_data(cfg: ElectroweakLeptonNeutrinoConfig) -> dict[str, Any]:
    norm = math.sqrt(cfg.g**2 + cfg.g_prime**2)
    sin_theta = cfg.g_prime / norm
    cos_theta = cfg.g / norm
    electric_g = cfg.g * sin_theta
    electric_gp = cfg.g_prime * cos_theta
    m_w = cfg.g * cfg.higgs_vev_gev / 2.0
    m_z = norm * cfg.higgs_vev_gev / 2.0
    matrix = cfg.higgs_vev_gev**2 / 4.0 * np.asarray(
        [[cfg.g**2, -cfg.g * cfg.g_prime], [-cfg.g * cfg.g_prime, cfg.g_prime**2]],
        dtype=np.float64,
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "sin_theta": sin_theta,
        "cos_theta": cos_theta,
        "sin_sq_theta": sin_theta**2,
        "electric_g": electric_g,
        "electric_gp": electric_gp,
        "m_w": m_w,
        "m_z": m_z,
        "neutral_mass_matrix": matrix,
        "neutral_mass_eigenvalues": eigenvalues,
        "rho_tree": m_w**2 / (m_z**2 * cos_theta**2),
    }


def ee_to_muon_pair_cross_section(alpha: float, s_gev2: float) -> float:
    return 4.0 * math.pi * alpha**2 / (3.0 * s_gev2)


def four_fermi_neutrino_cross_section(gf: float, energy_gev: float) -> float:
    return gf**2 * energy_gev**2 / math.pi


def w_leptonic_partial_width(g: float, m_w: float) -> float:
    return g**2 * m_w / (48.0 * math.pi)


def z_fermion_partial_width(
    n_color: float, gf: float, m_z: float, g_vector: float, g_axial: float
) -> float:
    return (
        n_color
        * gf
        * m_z**3
        * (g_vector**2 + g_axial**2)
        / (6.0 * math.pi * math.sqrt(2.0))
    )


LEPTON_MASSES_MEV = {
    "electron": 0.51099895,
    "muon": 105.6583755,
    "tau": 1776.86,
}
LEPTON_LIFETIMES_S = {
    "muon": 2.1969811e-6,
    "tau": 2.903e-13,
}
TAU_BRANCHING = {
    "electron": 0.1782,
    "muon": 0.1739,
    "hadron": 0.6479,
}


def sargent_width(gf: float, mass_gev: float) -> float:
    return gf**2 * mass_gev**5 / (192.0 * math.pi**3)


def neutrino_mass_spectrum(cfg: ElectroweakLeptonNeutrinoConfig) -> np.ndarray:
    return np.asarray(
        [
            cfg.m1_ev,
            math.sqrt(cfg.m1_ev**2 + cfg.delta_m21_sq_ev2),
            math.sqrt(cfg.m1_ev**2 + cfg.delta_m31_sq_ev2),
        ],
        dtype=np.float64,
    )


def pmns_matrix(cfg: ElectroweakLeptonNeutrinoConfig) -> np.ndarray:
    t12, t23, t13, delta = map(
        math.radians,
        (cfg.theta12_deg, cfg.theta23_deg, cfg.theta13_deg, cfg.delta_cp_deg),
    )
    c12, s12 = math.cos(t12), math.sin(t12)
    c23, s23 = math.cos(t23), math.sin(t23)
    c13, s13 = math.cos(t13), math.sin(t13)
    phase = np.exp(1.0j * delta)
    phase_conj = np.conj(phase)
    return np.asarray(
        [
            [c12 * c13, s12 * c13, s13 * phase_conj],
            [
                -s12 * c23 - c12 * s23 * s13 * phase,
                c12 * c23 - s12 * s23 * s13 * phase,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * phase,
                -c12 * s23 - s12 * c23 * s13 * phase,
                c23 * c13,
            ],
        ],
        dtype=np.complex128,
    )


def vacuum_oscillation_matrix(
    cfg: ElectroweakLeptonNeutrinoConfig, baseline_km: float | None = None
) -> np.ndarray:
    baseline = cfg.baseline_km if baseline_km is None else baseline_km
    masses = neutrino_mass_spectrum(cfg)
    dm_sq = masses**2 - masses[0] ** 2
    U = pmns_matrix(cfg)
    # A common phase is irrelevant. The conventional 1.267 coefficient gives
    # the pairwise sin^2 phase when amplitudes use twice that phase.
    phases = np.exp(-2.0j * 1.267 * dm_sq * baseline / cfg.neutrino_energy_gev)
    amplitude = U @ np.diag(phases) @ U.conj().T
    return np.asarray(np.abs(amplitude) ** 2, dtype=np.float64)


def _family_balance() -> dict[str, bool]:
    anti_nu_e = antiparticle(QN["nu_e"])
    anti_nu_mu = antiparticle(QN["nu_mu"])
    anti_nu_tau = antiparticle(QN["nu_tau"])
    michel = QN["mu"] == QN["e"] + anti_nu_e + QN["nu_mu"]
    tau_e = QN["tau"] == QN["nu_tau"] + QN["e"] + anti_nu_e
    tau_mu = QN["tau"] == QN["nu_tau"] + QN["mu"] + anti_nu_mu
    # The anti-tau state is used only to verify the conjugate family vector.
    anti_tau_correct = anti_nu_tau.family == (0, 0, -1)
    return {
        "michel": michel,
        "tau_e": tau_e,
        "tau_mu": tau_mu,
        "anti_tau": anti_tau_correct,
    }


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def canonical_payload(
    config: ElectroweakLeptonNeutrinoConfig | None = None,
) -> dict[str, Any]:
    cfg = ElectroweakLeptonNeutrinoConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M12",
        "milestone": MILESTONE,
        "configuration": asdict(cfg),
        "study_api": (
            "openwave.xperiments.m12_particle_zoo."
            "electroweak_lepton_neutrino_m122:run_electroweak_lepton_neutrino_study"
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


def run_electroweak_lepton_neutrino_study(
    config: ElectroweakLeptonNeutrinoConfig | None = None,
) -> dict[str, Any]:
    cfg = ElectroweakLeptonNeutrinoConfig() if config is None else config
    cfg.validate()
    ew = electroweak_mass_data(cfg)
    s = cfg.center_of_mass_energy_gev**2
    qed = ee_to_muon_pair_cross_section(cfg.alpha_em, s)
    nu_cross = four_fermi_neutrino_cross_section(
        cfg.fermi_constant_gev2, cfg.neutrino_energy_gev
    )
    w_width = w_leptonic_partial_width(cfg.g, ew["m_w"])
    electron_gv = -0.5 + 2.0 * ew["sin_sq_theta"]
    electron_ga = -0.5
    z_width_e = z_fermion_partial_width(
        1.0,
        cfg.fermi_constant_gev2,
        ew["m_z"],
        electron_gv,
        electron_ga,
    )
    mu_mass_gev = LEPTON_MASSES_MEV["muon"] / 1000.0
    tau_mass_gev = LEPTON_MASSES_MEV["tau"] / 1000.0
    sargent_ratio = sargent_width(
        cfg.fermi_constant_gev2, tau_mass_gev
    ) / sargent_width(cfg.fermi_constant_gev2, mu_mass_gev)
    expected_ratio = (tau_mass_gev / mu_mass_gev) ** 5
    masses = neutrino_mass_spectrum(cfg)
    dm21 = masses[1] ** 2 - masses[0] ** 2
    dm31 = masses[2] ** 2 - masses[0] ** 2
    U = pmns_matrix(cfg)
    identity = np.eye(3, dtype=np.complex128)
    probability = vacuum_oscillation_matrix(cfg)
    probability_zero = vacuum_oscillation_matrix(cfg, baseline_km=0.0)
    family = _family_balance()
    diagnostics = {
        "w_mass_gev": ew["m_w"],
        "z_mass_gev": ew["m_z"],
        "photon_mass_sq_abs": abs(float(ew["neutral_mass_eigenvalues"][0])),
        "z_mass_sq_error": abs(
            float(ew["neutral_mass_eigenvalues"][1]) - ew["m_z"] ** 2
        ),
        "electric_charge_form_error": abs(ew["electric_g"] - ew["electric_gp"]),
        "custodial_mass_error": abs(ew["m_w"] - ew["m_z"] * ew["cos_theta"]),
        "tree_rho_error": abs(ew["rho_tree"] - 1.0),
        "qed_cross_section": qed,
        "qed_s_scaled_error": abs(qed * s - 4.0 * math.pi * cfg.alpha_em**2 / 3.0),
        "neutrino_cross_section": nu_cross,
        "w_leptonic_width_gev": w_width,
        "z_electron_width_gev": z_width_e,
        "lepton_mass_ordering": (
            LEPTON_MASSES_MEV["electron"]
            < LEPTON_MASSES_MEV["muon"]
            < LEPTON_MASSES_MEV["tau"]
        ),
        "tau_shorter_than_muon": (
            LEPTON_LIFETIMES_S["tau"] < LEPTON_LIFETIMES_S["muon"]
        ),
        "tau_branching_error": abs(sum(TAU_BRANCHING.values()) - 1.0),
        "sargent_ratio_error": abs(sargent_ratio - expected_ratio),
        "delta_m21_sq_error": abs(dm21 - cfg.delta_m21_sq_ev2),
        "delta_m31_sq_error": abs(dm31 - cfg.delta_m31_sq_ev2),
        "pmns_unitarity_error": float(np.linalg.norm(U.conj().T @ U - identity)),
        "oscillation_row_sum_error": float(np.max(np.abs(probabity.sum(axis=1) - 1.0))),
        "oscillation_zero_baseline_error": float(np.linalg.norm(probability_zero - np.eye(3))),
        "oscillation_prob_min": float(probability.min()),
        "oscillation_prob_max": float(probability.max()),
        "family_balance": family,
        "m12_1_passed": bool(run_standard_model_zoo_study()["passed"]),
    }
    acceptance = {
        "m12_1_registry_passes": diagnostics["m12_1_passed"],
        "neutral_mass_matrix_has_massless_photon": diagnostics["photon_mass_sq_abs"] < 1.0e-9,
        "neutral_mass_matrix_has_z_eigenvalue": diagnostics["z_mass_sq_error"] < 1.0e-8,
        "electroweak_charge_forms_match": diagnostics["electric_charge_form_error"] < 1.0e-14,
        "w_z_weinberg_relation_closes": diagnostics["custodial_mass_error"] < 1.0e-12,
        "tree_rho_is_one": diagnostics["tree_rho_error"] < 1.0e-14,
        "qed_and_neutrino_cross_sections_nonnegative": qed >= 0.0 and nu_cross >= 0.0,
        "tree_partial_widths_nonnegative": w_width >= 0.0 and z_width_e >= 0.0,
        "charged_lepton_data_order_correct": (
            diagnostics["lepton_mass_ordering"] and diagnostics["tau_shorter_than_muon"]
        ),
        "tau_branching_normalized": diagnostics["tau_branching_error"] < 1.0e-15,
        "sargent_mass_fifth_ratio_exact": diagnostics["sargent_ratio_error"] < 1.0e-8,
        "neutrino_splittings_reconstructed": (
            diagnostics["delta_m21_sq_error"] < 1.0e-18
            and diagnostics["delta_m31_sq_error"] < 1.0e-17
        ),
        "pmns_is_unitary": diagnostics["pmns_unitarity_error"] < 1.0e-14,
        "oscillation_probabilities_normalize": diagnostics["oscillation_row_sum_error"] < 1.0e-14,
        "zero_baseline_is_identity": diagnostics["oscillation_zero_baseline_error"] < 1.0e-14,
        "oscillation_probabilities_are_bounded": (
            diagnostics["oscillation_prob_min"] >= -1.0e-15
            and diagnostics["oscillation_prob_max"] <= 1.0 + 1.0e-14
        ),
        "michel_and_tau_family_rules_close": all(family.valus()),
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "tree_level_only": True,
            "pdg_masses_lifetimes_are_inputs": True,
            "pmns_angles_and_cp_phase_are_inputs": True,
            "no_loop_or_decay_spectrum_claim": True,
        },
    }
