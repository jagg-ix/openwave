"""Three-dimensional constrained minimizer and continuation infrastructure.

The reference problem is the normalized Gross--Pitaevskii energy in a harmonic
trap,

    E[psi] = ∫ [1/2 |grad psi|^2 + 1/2 omega^2 r^2 |psi|^2
                + g/2 |psi|^4] d^3x,

with ∫|psi|^2 d^3x = 1.

A projected gradient flow with backtracking minimizes the energy. Continuation
in the nonlinear coupling reuses the previous minimizer. The untrapped control
is included explicitly: without the external trap the normalized state spreads
toward the periodic box scale, so the reference solution is not promoted as a
self-bound CAT/EPT particle.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

ComplexField = NDArray[np.complex128]
RealField = NDArray[np.float64]


@dataclass(frozen=True)
class MinimizerConfig:
    points: int = 24
    half_width: float = 6.0
    trap_frequency: float = 1.0
    coupling: float = 1.0
    max_iterations: int = 1200
    gradient_tolerance: float = 3e-7
    initial_step: float = 0.08
    max_backtracks: int = 18

    def __post_init__(self) -> None:
        if self.points < 12 or self.points % 2:
            raise ValueError("even cubic grid with at least 12 points required")
        if self.half_width <= 0 or self.trap_frequency < 0:
            raise ValueError("valid spatial and trap parameters required")
        if self.coupling < 0 or self.max_iterations < 1:
            raise ValueError("nonnegative coupling and positive iterations required")
        if self.gradient_tolerance <= 0 or self.initial_step <= 0:
            raise ValueError("positive minimization controls required")


def lattice(cfg: MinimizerConfig) -> tuple[RealField, RealField, RealField, float]:
    length = 2.0 * cfg.half_width
    dx = length / cfg.points
    axis = (np.arange(cfg.points, dtype=np.float64) - cfg.points / 2) * dx
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return x, y, z, dx


def k_squared(cfg: MinimizerConfig) -> RealField:
    _x, _y, _z, dx = lattice(cfg)
    wave = 2.0 * math.pi * np.fft.fftfreq(cfg.points, d=dx)
    kx, ky, kz = np.meshgrid(wave, wave, wave, indexing="ij")
    return kx * kx + ky * ky + kz * kz


def normalize(field: ComplexField, dx: float) -> ComplexField:
    norm = math.sqrt(float(np.sum(np.abs(field) ** 2) * dx**3))
    if norm <= 0.0:
        raise ValueError("cannot normalize zero field")
    return field / norm


def gaussian_seed(cfg: MinimizerConfig, width: float = 1.0) -> ComplexField:
    if width <= 0.0:
        raise ValueError("positive seed width required")
    x, y, z, dx = lattice(cfg)
    field = np.exp(-(x * x + y * y + z * z) / (2.0 * width * width))
    return normalize(field.astype(np.complex128), dx)


def laplacian(field: ComplexField, cfg: MinimizerConfig) -> ComplexField:
    return np.fft.ifftn(-k_squared(cfg) * np.fft.fftn(field))


def potential(cfg: MinimizerConfig) -> RealField:
    x, y, z, _dx = lattice(cfg)
    return 0.5 * cfg.trap_frequency**2 * (x * x + y * y + z * z)


def hamiltonian_action(field: ComplexField, cfg: MinimizerConfig) -> ComplexField:
    return (
        -0.5 * laplacian(field, cfg)
        + potential(cfg) * field
        + cfg.coupling * np.abs(field) ** 2 * field
    )


def energy(field: ComplexField, cfg: MinimizerConfig) -> float:
    _x, _y, _z, dx = lattice(cfg)
    lap = laplacian(field, cfg)
    kinetic = -0.5 * np.conjugate(field) * lap
    density = (
        kinetic.real
        + potential(cfg) * np.abs(field) ** 2
        + 0.5 * cfg.coupling * np.abs(field) ** 4
    )
    return float(np.sum(density) * dx**3)


def chemical_potential(field: ComplexField, cfg: MinimizerConfig) -> float:
    _x, _y, _z, dx = lattice(cfg)
    hpsi = hamiltonian_action(field, cfg)
    return float(np.sum(np.conjugate(field) * hpsi).real * dx**3)


def projected_gradient(field: ComplexField, cfg: MinimizerConfig) -> tuple[ComplexField, float]:
    mu = chemical_potential(field, cfg)
    return hamiltonian_action(field, cfg) - mu * field, mu


def observables(field: ComplexField, cfg: MinimizerConfig) -> dict[str, float]:
    x, y, z, dx = lattice(cfg)
    density = np.abs(field) ** 2
    norm = float(np.sum(density) * dx**3)
    r2 = x * x + y * y + z * z
    rms_radius = math.sqrt(float(np.sum(r2 * density) * dx**3 / norm))
    center = cfg.points // 2
    peak = float(np.max(density))
    boundary_mask = (
        (np.abs(x) >= cfg.half_width - 2.0 * dx)
        | (np.abs(y) >= cfg.half_width - 2.0 * dx)
        | (np.abs(z) >= cfg.half_width - 2.0 * dx)
    )
    boundary_fraction = float(np.sum(density[boundary_mask]) * dx**3 / norm)
    com = (
        float(np.sum(x * density) * dx**3 / norm),
        float(np.sum(y * density) * dx**3 / norm),
        float(np.sum(z * density) * dx**3 / norm),
    )
    gradient, mu = projected_gradient(field, cfg)
    residual = math.sqrt(float(np.sum(np.abs(gradient) ** 2) * dx**3))
    return {
        "norm": norm,
        "energy": energy(field, cfg),
        "chemical_potential": mu,
        "projected_residual_l2": residual,
        "rms_radius": rms_radius,
        "peak_density": peak,
        "boundary_fraction": boundary_fraction,
        "center_density": float(density[center, center, center]),
        "center_of_mass_norm": math.sqrt(sum(value * value for value in com)),
    }


def minimize(
    cfg: MinimizerConfig,
    initial: ComplexField | None = None,
) -> dict[str, Any]:
    _x, _y, _z, dx = lattice(cfg)
    field = gaussian_seed(cfg) if initial is None else normalize(initial.copy(), dx)
    current_energy = energy(field, cfg)
    history = [{"iteration": 0, "energy": current_energy, "step": 0.0}]
    step = cfg.initial_step
    accepted = 0

    for iteration in range(1, cfg.max_iterations + 1):
        gradient, _mu = projected_gradient(field, cfg)
        gradient_norm = math.sqrt(float(np.sum(np.abs(gradient) ** 2) * dx**3))
        if gradient_norm <= cfg.gradient_tolerance:
            break

        trial_step = step
        accepted_trial = False
        for _ in range(cfg.max_backtracks):
            trial = normalize(field - trial_step * gradient, dx)
            trial_energy = energy(trial, cfg)
            if trial_energy <= current_energy - 1e-4 * trial_step * gradient_norm**2:
                field = trial
                current_energy = trial_energy
                step = min(1.25 * trial_step, cfg.initial_step)
                accepted_trial = True
                accepted += 1
                break
            trial_step *= 0.5

        if not accepted_trial:
            break

        if iteration <= 8 or iteration % 10 == 0:
            history.append(
                {"iteration": iteration, "energy": current_energy, "step": trial_step}
            )

    final = observables(field, cfg)
    return {
        "field": field,
        "history": history,
        "accepted_steps": accepted,
        "iterations": history[-1]["iteration"],
        "final": final,
        "config": asdict(cfg),
    }


def continuation(
    couplings: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    *,
    points: int = 24,
    half_width: float = 6.0,
) -> dict[str, Any]:
    if not couplings or any(couplings[index + 1] < couplings[index] for index in range(len(couplings) - 1)):
        raise ValueError("nonempty nondecreasing continuation path required")
    field = None
    branches = []
    for coupling in couplings:
        cfg = MinimizerConfig(points=points, half_width=half_width, coupling=coupling)
        run = minimize(cfg, field)
        field = run["field"]
        branches.append(
            {
                "coupling": coupling,
                **run["final"],
                "accepted_steps": run["accepted_steps"],
            }
        )
    return {"couplings": couplings, "branches": branches, "field": field}


def noninteracting_reference() -> dict[str, Any]:
    cfg = MinimizerConfig(coupling=0.0)
    run = minimize(cfg)
    return {
        "energy": run["final"]["energy"],
        "analytic_energy": 1.5,
        "absolute_error": abs(run["final"]["energy"] - 1.5),
        "rms_radius": run["final"]["rms_radius"],
        "analytic_rms_radius": math.sqrt(1.5),
        "rms_error": abs(run["final"]["rms_radius"] - math.sqrt(1.5)),
    }


def resolution_study() -> dict[str, Any]:
    points = (16, 20, 24)
    results = []
    for count in points:
        branch = continuation((0.0, 1.0), points=count)
        results.append(branch["branches"][-1])
    energies = [row["energy"] for row in results]
    radii = [row["rms_radius"] for row in results]
    return {
        "points": points,
        "energy": energies,
        "rms_radius": radii,
        "energy_successive_differences": [
            abs(energies[index] - energies[index + 1]) for index in range(2)
        ],
        "radius_successive_differences": [
            abs(radii[index] - radii[index + 1]) for index in range(2)
        ],
    }


def untrapped_control() -> dict[str, Any]:
    cfg = MinimizerConfig(trap_frequency=0.0, coupling=1.0, max_iterations=800)
    run = minimize(cfg)
    return run["final"]


@lru_cache(maxsize=1)
def run_minimizer_continuation_study() -> dict[str, Any]:
    branch = continuation()
    rows = branch["branches"]
    reference = noninteracting_reference()
    refinement = resolution_study()
    untrapped = untrapped_control()
    trapped = rows[-1]
    energies = [row["energy"] for row in rows]
    radii = [row["rms_radius"] for row in rows]
    residuals = [row["projected_residual_l2"] for row in rows]

    acceptance = {
        "noninteracting_ground_state_recovered": (
            reference["absolute_error"] <= 5e-4 and reference["rms_error"] <= 5e-4
        ),
        "continuation_path_converges": max(residuals) <= 5e-6,
        "normalization_closes": max(abs(row["norm"] - 1.0) for row in rows) <= 2e-12,
        "repulsive_branch_energy_orders": all(
            energies[index + 1] >= energies[index] - 1e-10
            for index in range(len(energies) - 1)
        ),
        "repulsive_branch_expands": all(
            radii[index + 1] >= radii[index] - 1e-8
            for index in range(len(radii) - 1)
        ),
        "trapped_state_is_localized": (
            trapped["boundary_fraction"] <= 1e-7 and trapped["rms_radius"] < 0.4 * 6.0
        ),
        "resolution_stabilizes": (
            refinement["energy_successive_differences"][1]
            < refinement["energy_successive_differences"][0]
            and refinement["radius_successive_differences"][1]
            < refinement["radius_successive_differences"][0]
        ),
        "untrapped_control_is_not_self_bound": (
            untrapped["rms_radius"] > 2.0 * trapped["rms_radius"]
            and untrapped["boundary_fraction"] > 1e-2
        ),
    }
    return {
        "schema": "openwave.m9.minimizer-continuation-result.v1",
        "task": "M9.37",
        "continuation": {"couplings": branch["couplings"], "branches": rows},
        "noninteracting_reference": reference,
        "resolution": refinement,
        "untrapped_control": untrapped,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "three-dimensional normalized variational minimization",
                "stationary projected-Euler-Lagrange residuals",
                "continuation in nonlinear coupling",
                "resolution and boundary diagnostics",
                "explicit untrapped non-self-bound control",
            ],
            "does_not_establish": [
                "a self-bound CAT/EPT particle",
                "full gauge, spinor, entropy, and geometry coupling",
                "topological charge or physical mass",
                "long-horizon real-time stability",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
