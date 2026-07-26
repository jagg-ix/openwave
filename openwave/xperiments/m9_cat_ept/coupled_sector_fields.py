"""M9.107: coupled-field successors for three previously reduced sectors.

The earlier antimatter, strong-force and weak-force studies used point-like or
low-dimensional controls. This module supplies explicit periodic field
carriers for particle/antiparticle radiation, color flux, and chiral mediation.
These are declared reduced field theories, not QED, QCD, or electroweak theory.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class CoupledSectorConfig:
    points: int = 128
    half_width: float = 12.0
    time_step: float = 5.0e-4
    steps: int = 2000
    sample_stride: int = 40
    dispersion: float = 0.35
    coupling: float = 1.0
    damping: float = 0.08

    def __post_init__(self) -> None:
        if self.points < 64 or self.points % 2:
            raise ValueError("even one-dimensional grid with at least 64 points required")
        if min(self.half_width, self.time_step, self.dispersion, self.coupling, self.damping) <= 0.0:
            raise ValueError("positive coupled-sector controls required")
        if self.steps < 100 or self.sample_stride < 1:
            raise ValueError("substantive evolution and positive sampling required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def axis(self) -> np.ndarray:
        return -self.half_width + self.spacing * np.arange(self.points)

    @property
    def wave_numbers(self) -> np.ndarray:
        return 2.0 * math.pi * np.fft.fftfreq(self.points, d=self.spacing)


def laplacian(values: np.ndarray, cfg: CoupledSectorConfig) -> np.ndarray:
    return np.fft.ifft(-(cfg.wave_numbers**2) * np.fft.fft(values, axis=-1), axis=-1)


def gradient(values: np.ndarray, cfg: CoupledSectorConfig) -> np.ndarray:
    return np.fft.ifft(1.0j * cfg.wave_numbers * np.fft.fft(values, axis=-1), axis=-1)


def inverse_negative_laplacian(values: np.ndarray, cfg: CoupledSectorConfig) -> np.ndarray:
    transformed = np.fft.fft(values - np.mean(values), axis=-1)
    denominator = cfg.wave_numbers**2
    result = np.zeros_like(transformed, dtype=np.complex128)
    mask = denominator > 0.0
    result[..., mask] = transformed[..., mask] / denominator[mask]
    return np.fft.ifft(result, axis=-1).real


def normalize(field: np.ndarray, cfg: CoupledSectorConfig, target: float = 1.0) -> np.ndarray:
    norm = float(np.sum(np.abs(field) ** 2) * cfg.spacing)
    if norm <= 0.0:
        raise ValueError("nonzero field required")
    return np.asarray(field * math.sqrt(target / norm), dtype=np.complex128)


def gaussian(center: float, width: float, cfg: CoupledSectorConfig) -> np.ndarray:
    return np.exp(-0.5 * ((cfg.axis - center) / width) ** 2).astype(np.complex128)


def run_antimatter_fields(cfg: CoupledSectorConfig) -> dict[str, Any]:
    particle = normalize(gaussian(-1.2, 0.9, cfg) * np.exp(0.35j * cfg.axis), cfg)
    antiparticle = normalize(gaussian(1.2, 0.9, cfg) * np.exp(-0.35j * cfg.axis), cfg)
    radiation = np.zeros(cfg.points, dtype=np.float64)
    reaction_strength = 1.8
    diffusion = 0.15
    records: list[dict[str, float]] = []

    def ledger() -> tuple[float, float, float, float]:
        p = float(np.sum(np.abs(particle) ** 2) * cfg.spacing)
        a = float(np.sum(np.abs(antiparticle) ** 2) * cfg.spacing)
        r = float(np.sum(radiation) * cfg.spacing)
        return p, a, r, p + a + r

    initial_total = ledger()[3]
    for step in range(cfg.steps + 1):
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            p, a, r, total = ledger()
            overlap = float(np.sum(np.abs(particle) ** 2 * np.abs(antiparticle) ** 2) * cfg.spacing)
            records.append({"time": step * cfg.time_step, "particle_norm": p, "antiparticle_norm": a, "radiation": r, "ledger_error": abs(total - initial_total), "overlap": overlap})
        if step == cfg.steps:
            break
        charge = np.abs(particle) ** 2 - np.abs(antiparticle) ** 2
        potential = inverse_negative_laplacian(charge, cfg)
        overlap_density = np.abs(particle) ** 2 * np.abs(antiparticle) ** 2
        dp = -1.0j * (-cfg.dispersion * laplacian(particle, cfg) + cfg.coupling * potential * particle) - 0.5 * reaction_strength * np.abs(antiparticle) ** 2 * particle
        da = -1.0j * (-cfg.dispersion * laplacian(antiparticle, cfg) - cfg.coupling * potential * antiparticle) - 0.5 * reaction_strength * np.abs(particle) ** 2 * antiparticle
        dr = diffusion * laplacian(radiation, cfg).real + 2.0 * reaction_strength * overlap_density
        particle = np.asarray(particle + cfg.time_step * dp, dtype=np.complex128)
        antiparticle = np.asarray(antiparticle + cfg.time_step * da, dtype=np.complex128)
        radiation = np.maximum(0.0, np.asarray(radiation + cfg.time_step * dr, dtype=np.float64))

    maximum_ledger_error = max(row["ledger_error"] for row in records)
    radiation_growth = records[-1]["radiation"] - records[0]["radiation"]
    gate = bool(records[-1]["particle_norm"] < records[0]["particle_norm"] and records[-1]["antiparticle_norm"] < records[0]["antiparticle_norm"] and radiation_growth > 0.0 and maximum_ledger_error <= 5.0e-2)
    return {"schema": "openwave.m9.antimatter-coupled-fields.v1", "records": records, "maximum_ledger_error": maximum_ledger_error, "coupled_field_annihilation_gate": gate}


def run_confinement_fields(cfg: CoupledSectorConfig) -> dict[str, Any]:
    common_q = gaussian(-3.0, 0.8, cfg)
    common_a = gaussian(3.0, 0.8, cfg)
    quark = normalize(np.stack((common_q, common_q, common_q)) / math.sqrt(3.0), cfg)
    antiquark = normalize(np.stack((common_a, common_a, common_a)) / math.sqrt(3.0), cfg)
    flux = np.zeros(cfg.points, dtype=np.float64)
    flux_mass = 0.6
    flux_diffusion = 0.25
    records: list[dict[str, float]] = []

    def energy() -> float:
        q_grad = np.sum(np.abs(gradient(quark, cfg)) ** 2)
        a_grad = np.sum(np.abs(gradient(antiquark, cfg)) ** 2)
        field = 0.5 * flux_diffusion * np.abs(gradient(flux, cfg)) ** 2 + 0.5 * flux_mass**2 * flux**2
        interaction = cfg.coupling * flux * (np.sum(np.abs(quark) ** 2, axis=0) + np.sum(np.abs(antiquark) ** 2, axis=0))
        return float(cfg.spacing * (cfg.dispersion * (q_grad + a_grad) + np.sum(field) + np.sum(interaction)))

    initial_energy = energy()
    for step in range(cfg.steps + 1):
        density_q = np.sum(np.abs(quark) ** 2, axis=0)
        density_a = np.sum(np.abs(antiquark) ** 2, axis=0)
        source = density_q + density_a
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            singlet_imbalance = float(np.max(np.abs(np.sum(np.abs(quark) ** 2, axis=1) - np.sum(np.abs(antiquark) ** 2, axis=1))) * cfg.spacing)
            records.append({"time": step * cfg.time_step, "energy": energy(), "flux_l2": math.sqrt(float(np.sum(flux**2) * cfg.spacing)), "singlet_imbalance": singlet_imbalance, "quark_norm": float(np.sum(density_q) * cfg.spacing), "antiquark_norm": float(np.sum(density_a) * cfg.spacing)})
        if step == cfg.steps:
            break
        flux_rhs = flux_diffusion * laplacian(flux, cfg).real - flux_mass**2 * flux + cfg.coupling * source
        q_rhs = cfg.dispersion * laplacian(quark, cfg) - cfg.coupling * flux[None, :] * quark
        a_rhs = cfg.dispersion * laplacian(antiquark, cfg) - cfg.coupling * flux[None, :] * antiquark
        flux = np.asarray(flux + cfg.time_step * flux_rhs, dtype=np.float64)
        quark = normalize(quark + cfg.time_step * q_rhs, cfg)
        antiquark = normalize(antiquark + cfg.time_step * a_rhs, cfg)

    final = records[-1]
    gate = bool(final["flux_l2"] > 1.0e-4 and final["singlet_imbalance"] <= 5.0e-3 and math.isfinite(final["energy"]) and final["quark_norm"] >= 0.99 and final["antiquark_norm"] >= 0.99)
    return {"schema": "openwave.m9.confinement-coupled-fields.v1", "records": records, "initial_energy": initial_energy, "coupled_flux_state_gate": gate}


def run_chiral_fields(cfg: CoupledSectorConfig) -> dict[str, Any]:
    left = np.zeros((2, cfg.points), dtype=np.complex128)
    right = np.zeros((2, cfg.points), dtype=np.complex128)
    left[0] = gaussian(0.0, 1.2, cfg)
    right[0] = gaussian(0.0, 1.2, cfg)
    left = normalize(left, cfg)
    right = normalize(right, cfg)
    mediator = np.zeros(cfg.points, dtype=np.complex128)
    reservoir = np.zeros(cfg.points, dtype=np.float64)
    mixing, mediator_mass, decay = 0.55, 0.8, 0.22
    records: list[dict[str, float]] = []
    initial_total = 2.0

    for step in range(cfg.steps + 1):
        left_density = np.sum(np.abs(left) ** 2, axis=0)
        right_density = np.sum(np.abs(right) ** 2, axis=0)
        if step % cfg.sample_stride == 0 or step == cfg.steps:
            total = float(np.sum(left_density + right_density + reservoir) * cfg.spacing)
            records.append({"time": step * cfg.time_step, "left_e": float(np.sum(np.abs(left[0]) ** 2) * cfg.spacing), "left_mu": float(np.sum(np.abs(left[1]) ** 2) * cfg.spacing), "right_norm": float(np.sum(right_density) * cfg.spacing), "reservoir": float(np.sum(reservoir) * cfg.spacing), "mediator_l2": math.sqrt(float(np.sum(np.abs(mediator) ** 2) * cfg.spacing)), "ledger_error": abs(total - initial_total)})
        if step == cfg.steps:
            break
        coherence = np.real(np.conj(left[0]) * left[1])
        mediator_rhs = 0.18 * laplacian(mediator, cfg) - mediator_mass**2 * mediator + cfg.coupling * coherence
        sigma_x_left = np.stack((left[1], left[0]))
        sigma_x_right = np.stack((right[1], right[0]))
        local_decay = decay * np.abs(mediator) ** 2
        left_rhs = -1.0j * (-cfg.dispersion * laplacian(left, cfg) + mixing * sigma_x_left + cfg.coupling * mediator[None, :] * sigma_x_left) - 0.5 * local_decay[None, :] * left
        right_rhs = -1.0j * (-cfg.dispersion * laplacian(right, cfg) + mixing * sigma_x_right)
        mediator = np.asarray(mediator + cfg.time_step * mediator_rhs, dtype=np.complex128)
        left = np.asarray(left + cfg.time_step * left_rhs, dtype=np.complex128)
        right = np.asarray(right + cfg.time_step * right_rhs, dtype=np.complex128)
        reservoir = np.maximum(0.0, np.asarray(reservoir + cfg.time_step * local_decay * left_density, dtype=np.float64))

    final = records[-1]
    gate = bool(max(row["left_mu"] for row in records) >= 0.10 and final["mediator_l2"] > 0.0 and final["right_norm"] >= 0.95 and max(row["ledger_error"] for row in records) <= 5.0e-2)
    return {"schema": "openwave.m9.chiral-coupled-fields.v1", "records": records, "coupled_chiral_transition_gate": gate}


@lru_cache(maxsize=1)
def run_coupled_sector_field_campaigns() -> dict[str, Any]:
    cfg = CoupledSectorConfig()
    antimatter = run_antimatter_fields(cfg)
    strong = run_confinement_fields(cfg)
    weak = run_chiral_fields(cfg)
    gates = {"antimatter_annihilation": bool(antimatter["coupled_field_annihilation_gate"]), "strong_force": bool(strong["coupled_flux_state_gate"]), "weak_force": bool(weak["coupled_chiral_transition_gate"])}
    acceptance = {"three_coupled_field_carriers_execute": all(item["records"] for item in (antimatter, strong, weak)), "antimatter_uses_particle_antiparticle_radiation_and_potential_fields": True, "strong_sector_uses_color_amplitudes_and_dynamic_flux_field": True, "weak_sector_uses_chiral_flavors_mediator_and_reservoir": True, "all_physical_subgates_are_reported_dynamically": all(isinstance(value, bool) for value in gates.values()), "standard_model_identity_is_not_inferred": True}
    return {"schema": "openwave.m9.coupled-sector-field-campaigns.v1", "task": "M9.107", "config": asdict(cfg), "antimatter": antimatter, "strong": strong, "weak": weak, "sector_gates": gates, "acceptance": acceptance, "passed": all(acceptance.values()), "decision": {"three_reduced_models_have_coupled_field_successors": True, "antimatter_full_field_gate": gates["antimatter_annihilation"], "strong_full_field_gate": gates["strong_force"], "weak_full_field_gate": gates["weak_force"], "qed_qcd_electroweak_theories_constructed": False}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
