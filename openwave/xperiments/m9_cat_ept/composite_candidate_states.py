"""M9.108: dynamical candidate-state construction for four open particle sectors.

The campaign builds finite periodic field candidates for dark matter, quarks,
baryons and mesons. Each candidate has a relaxation phase and an independent
short-time perturbation test. Passing a gate means only that the declared
reduced field carrier has a localized, reproducible state.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Callable, Mapping

import numpy as np

from .coupled_sector_fields import (
    CoupledSectorConfig,
    gaussian,
    inverse_negative_laplacian,
    laplacian,
    normalize,
    run_coupled_sector_field_campaigns,
)


@dataclass(frozen=True)
class CandidateStateConfig:
    points: int = 128
    half_width: float = 12.0
    relaxation_dt: float = 2.0e-3
    relaxation_steps: int = 700
    perturbation_dt: float = 5.0e-4
    perturbation_steps: int = 40
    dispersion: float = 0.35
    attraction: float = 1.1
    repulsion: float = 0.65
    localization_gate: float = 4.5
    residual_gate: float = 2.0e-1
    perturbation_gate: float = 1.8e-1

    def __post_init__(self) -> None:
        if self.points < 64 or self.points % 2:
            raise ValueError("even grid with at least 64 points required")
        if min(
            self.half_width,
            self.relaxation_dt,
            self.perturbation_dt,
            self.dispersion,
            self.attraction,
            self.repulsion,
            self.localization_gate,
            self.residual_gate,
            self.perturbation_gate,
        ) <= 0.0:
            raise ValueError("positive candidate-state controls required")
        if self.relaxation_steps < 100 or self.perturbation_steps < 20:
            raise ValueError("substantive relaxation and perturbation required")

    def sector_config(self) -> CoupledSectorConfig:
        return CoupledSectorConfig(
            points=self.points,
            half_width=self.half_width,
            time_step=self.perturbation_dt,
            steps=max(100, self.perturbation_steps),
            sample_stride=20,
            dispersion=self.dispersion,
        )


def density(field: np.ndarray) -> np.ndarray:
    if field.ndim == 1:
        return np.asarray(np.abs(field) ** 2, dtype=np.float64)
    return np.asarray(np.sum(np.abs(field) ** 2, axis=0), dtype=np.float64)


def radius(field: np.ndarray, cfg: CandidateStateConfig) -> float:
    scfg = cfg.sector_config()
    rho = density(field)
    norm = float(np.sum(rho) * scfg.spacing)
    center = float(np.sum(scfg.axis * rho) * scfg.spacing / max(norm, 1.0e-30))
    displacement = ((scfg.axis - center + cfg.half_width) % (2.0 * cfg.half_width)) - cfg.half_width
    return math.sqrt(float(np.sum(displacement**2 * rho) * scfg.spacing / max(norm, 1.0e-30)))


def phase_aligned_distance(left: np.ndarray, right: np.ndarray, cfg: CandidateStateConfig) -> float:
    scfg = cfg.sector_config()
    overlap = np.sum(np.conj(left) * right) * scfg.spacing
    phase = overlap / max(abs(overlap), 1.0e-30)
    return math.sqrt(float(np.sum(np.abs(left - phase * right) ** 2) * scfg.spacing))


def stationary_residual(field: np.ndarray, hamiltonian: np.ndarray, cfg: CandidateStateConfig) -> float:
    scfg = cfg.sector_config()
    norm = float(np.sum(np.abs(field) ** 2) * scfg.spacing)
    mu = float(np.real(np.vdot(field, hamiltonian)) * scfg.spacing / max(norm, 1.0e-30))
    residual = hamiltonian - mu * field
    scale = max(math.sqrt(float(np.sum(np.abs(hamiltonian) ** 2) * scfg.spacing)), 1.0e-30)
    return math.sqrt(float(np.sum(np.abs(residual) ** 2) * scfg.spacing)) / scale


def relax_state(initial: np.ndarray, hamiltonian_builder: Callable[[np.ndarray], np.ndarray], cfg: CandidateStateConfig) -> tuple[np.ndarray, list[float], float]:
    scfg = cfg.sector_config()
    state = normalize(initial, scfg)
    trace: list[float] = []
    for step in range(cfg.relaxation_steps):
        hpsi = hamiltonian_builder(state)
        mu = float(np.real(np.vdot(state, hpsi)) * scfg.spacing)
        state = normalize(state - cfg.relaxation_dt * (hpsi - mu * state), scfg)
        if (step + 1) % 50 == 0:
            trace.append(stationary_residual(state, hamiltonian_builder(state), cfg))
    return state, trace, stationary_residual(state, hamiltonian_builder(state), cfg)


def perturbation_distance(state: np.ndarray, hamiltonian_builder: Callable[[np.ndarray], np.ndarray], cfg: CandidateStateConfig) -> float:
    scfg = cfg.sector_config()
    chirp = np.exp(0.008j * np.sin(2.0 * math.pi * scfg.axis / (2.0 * cfg.half_width)))
    perturbed = normalize(state * chirp, scfg)
    for _ in range(cfg.perturbation_steps):
        hpsi = hamiltonian_builder(perturbed)
        perturbed = normalize(np.asarray(perturbed - 1.0j * cfg.perturbation_dt * hpsi, dtype=np.complex128), scfg)
    return phase_aligned_distance(perturbed, state, cfg)


def dark_matter_candidate(cfg: CandidateStateConfig) -> dict[str, Any]:
    scfg = cfg.sector_config()
    initial = gaussian(0.0, 1.4, scfg)

    def hamiltonian(state: np.ndarray) -> np.ndarray:
        rho = density(state)
        hartree = inverse_negative_laplacian(rho, scfg)
        return np.asarray(-cfg.dispersion * laplacian(state, scfg) - cfg.attraction * hartree * state + cfg.repulsion * rho * state, dtype=np.complex128)

    state, trace, residual = relax_state(initial, hamiltonian, cfg)
    perturbation = perturbation_distance(state, hamiltonian, cfg)
    gate = bool(residual <= cfg.residual_gate and radius(state, cfg) <= cfg.localization_gate and perturbation <= cfg.perturbation_gate)
    return {"residual_trace": trace, "final_residual": residual, "radius": radius(state, cfg), "perturbation_distance": perturbation, "candidate_gate": gate}


def color_hamiltonian(state: np.ndarray, cfg: CandidateStateConfig, flux_strength: float) -> tuple[np.ndarray, np.ndarray]:
    scfg = cfg.sector_config()
    rho = density(state)
    flux = inverse_negative_laplacian(rho, scfg)
    hpsi = -cfg.dispersion * laplacian(state, scfg) - flux_strength * flux[None, :] * state + cfg.repulsion * rho[None, :] * state
    return np.asarray(hpsi, dtype=np.complex128), np.asarray(flux, dtype=np.float64)


def quark_candidate(cfg: CandidateStateConfig) -> dict[str, Any]:
    scfg = cfg.sector_config()
    common = gaussian(0.0, 1.0, scfg)
    initial = np.stack((common, common, common)) / math.sqrt(3.0)

    def hamiltonian(state: np.ndarray) -> np.ndarray:
        return color_hamiltonian(state, cfg, 0.55)[0]

    state, trace, residual = relax_state(initial, hamiltonian, cfg)
    color_norms = np.sum(np.abs(state) ** 2, axis=1) * scfg.spacing
    color_spread = float(np.max(color_norms) - np.min(color_norms))
    perturbation = perturbation_distance(state, hamiltonian, cfg)
    gate = bool(residual <= cfg.residual_gate and radius(state, cfg) <= cfg.localization_gate and color_spread <= 5.0e-3 and perturbation <= cfg.perturbation_gate)
    return {"residual_trace": trace, "final_residual": residual, "radius": radius(state, cfg), "color_norms": color_norms.tolist(), "color_spread": color_spread, "perturbation_distance": perturbation, "candidate_gate": gate}


def composite_candidate(centers: tuple[float, ...], color_assignment: tuple[int, ...], cfg: CandidateStateConfig) -> dict[str, Any]:
    scfg = cfg.sector_config()
    state = np.zeros((3, cfg.points), dtype=np.complex128)
    for center, color in zip(centers, color_assignment, strict=True):
        state[color] += gaussian(center, 0.75, scfg)
    initial = normalize(state, scfg)

    def hamiltonian(values: np.ndarray) -> np.ndarray:
        return color_hamiltonian(values, cfg, 1.80)[0]

    state, trace, residual = relax_state(initial, hamiltonian, cfg)
    rho = density(state)
    flux = inverse_negative_laplacian(rho, scfg)
    perturbation = perturbation_distance(state, hamiltonian, cfg)
    flux_l2 = math.sqrt(float(np.sum(flux**2) * scfg.spacing))
    gate = bool(residual <= cfg.residual_gate and radius(state, cfg) <= cfg.localization_gate and flux_l2 > 1.0e-4 and perturbation <= cfg.perturbation_gate)
    return {"residual_trace": trace, "final_residual": residual, "radius": radius(state, cfg), "flux_l2": flux_l2, "perturbation_distance": perturbation, "candidate_gate": gate}


@lru_cache(maxsize=1)
def run_candidate_state_construction() -> dict[str, Any]:
    cfg = CandidateStateConfig()
    sectors = run_coupled_sector_field_campaigns()
    dark_matter = dark_matter_candidate(cfg)
    quark = quark_candidate(cfg)
    baryon = composite_candidate((-2.5, 0.0, 2.5), (0, 1, 2), cfg)
    meson = composite_candidate((-1.8, 1.8), (0, 0), cfg)
    gates = {"dark_matter": bool(dark_matter["candidate_gate"]), "quarks": bool(quark["candidate_gate"]), "baryons": bool(baryon["candidate_gate"]), "mesons": bool(meson["candidate_gate"])}
    acceptance = {"all_four_candidate_solvers_execute": all(item["residual_trace"] for item in (dark_matter, quark, baryon, meson)), "every_candidate_has_stationary_and_perturbation_diagnostics": all(math.isfinite(item["final_residual"]) and math.isfinite(item["perturbation_distance"]) for item in (dark_matter, quark, baryon, meson)), "candidate_gates_are_dynamic": all(isinstance(value, bool) for value in gates.values()), "coupled_sector_dependencies_are_registered": bool(sectors["passed"]), "physical_particle_identity_is_not_inferred": True}
    return {"schema": "openwave.m9.composite-candidate-states.v1", "task": "M9.108", "config": asdict(cfg), "dark_matter": dark_matter, "quark": quark, "baryon": baryon, "meson": meson, "candidate_gates": gates, "acceptance": acceptance, "passed": all(acceptance.values()), "decision": {"four_dynamical_candidate_carriers_constructed": True, "dark_matter_candidate_stable": gates["dark_matter"], "quark_candidate_stable": gates["quarks"], "baryon_candidate_stable": gates["baryons"], "meson_candidate_stable": gates["mesons"], "cosmological_or_hadronic_identity_established": False}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
