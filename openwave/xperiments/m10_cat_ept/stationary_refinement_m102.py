"""M10.2 stationary descent, refinement, perturbation, and symmetry closure."""
from __future__ import annotations

from dataclasses import asdict
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .dirac_cartan_2i_yukawa_model import (
    BETA,
    DiracCartan2IYukawaConfig,
    DiracCartan2IYukawaState,
    apply_binary_icosahedral,
    binary_icosahedral_quaternions,
    construct_state,
    dirac_charge_current,
    dirac_hamiltonian_action,
    normalize_spinor,
    refresh_state,
)

MILESTONE = "M10.2"
SCHEMA = "openwave.m10.stationary-refinement.v1"


def real_hamiltonian_action(
    spinor: np.ndarray,
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
) -> np.ndarray:
    """Apply the interacting real-energy operator with the imaginary mass removed."""
    result = dirac_hamiltonian_action(spinor, state, cfg)
    beta_spinor = np.einsum("ab,bxyz->axyz", BETA, spinor, optimize=True)
    return np.asarray(
        result - 1.0j * cfg.imaginary_mass * beta_spinor,
        dtype=np.complex128,
    )


def stationary_diagnostics(
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
) -> dict[str, float]:
    geometry = cfg.geometry()
    hamiltonian = real_hamiltonian_action(state.spinor, state, cfg)
    norm = float(np.sum(np.abs(state.spinor) ** 2) * geometry.cell_volume)
    chemical_potential = float(
        np.real(np.vdot(state.spinor, hamiltonian))
        * geometry.cell_volume
        / max(norm, 1.0e-30)
    )
    centered = hamiltonian - chemical_potential * state.spinor
    centered_norm_sq = float(
        np.sum(np.abs(centered) ** 2) * geometry.cell_volume
    )
    operator_norm_sq = float(
        np.sum(np.abs(hamiltonian) ** 2) * geometry.cell_volume
    )

    density = np.asarray(
        np.sum(np.abs(state.spinor) ** 2, axis=0), dtype=np.float64
    )
    axis = (
        np.arange(cfg.points, dtype=np.float64) - cfg.points / 2.0
    ) * cfg.spacing
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    radius_sq = x * x + y * y + z * z
    radius = math.sqrt(
        float(np.sum(radius_sq * density) * geometry.cell_volume)
        / max(norm, 1.0e-30)
    )
    boundary = np.maximum.reduce((np.abs(x), np.abs(y), np.abs(z))) > (
        0.75 * cfg.half_width
    )
    boundary_fraction = float(
        np.sum(density[boundary]) * geometry.cell_volume / max(norm, 1.0e-30)
    )
    return {
        "norm": norm,
        "chemical_potential": chemical_potential,
        "centered_norm_sq": centered_norm_sq,
        "relative_stationary_residual": math.sqrt(
            centered_norm_sq / max(operator_norm_sq, 1.0e-30)
        ),
        "radius": radius,
        "boundary_fraction": boundary_fraction,
        "cartan_contact_energy": float(
            np.sum(state.cartan_contact_density) * geometry.cell_volume
        ),
    }


def _candidate_state(
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
    direction: np.ndarray,
    step: float,
    method: str,
) -> DiracCartan2IYukawaState:
    return refresh_state(
        normalize_spinor(state.spinor - step * direction, cfg),
        cfg,
        time=state.time + step,
        entropic_time=state.entropic_time,
        construction=f"{state.construction}+{method}",
    )


def stationary_step(
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
    base_step: float = 2.0e-4,
) -> tuple[DiracCartan2IYukawaState, dict[str, float | bool | str]]:
    before = stationary_diagnostics(state, cfg)
    hamiltonian = real_hamiltonian_action(state.spinor, state, cfg)
    centered = hamiltonian - before["chemical_potential"] * state.spinor
    squared = (
        real_hamiltonian_action(centered, state, cfg)
        - before["chemical_potential"] * centered
    )

    candidates: list[
        tuple[DiracCartan2IYukawaState, dict[str, float], float, str]
    ] = []
    for factor in (1.0, 0.5, 0.25, 0.125, 0.0625):
        step = base_step * factor
        for direction, method in (
            (squared, "squared-residual-descent"),
            (centered, "normalized-energy-descent"),
        ):
            candidate = _candidate_state(state, cfg, direction, step, method)
            candidates.append(
                (candidate, stationary_diagnostics(candidate, cfg), step, method)
            )

    best_state, best, step, method = min(
        candidates,
        key=lambda item: item[1]["relative_stationary_residual"],
    )
    if (
        best["relative_stationary_residual"]
        >= before["relative_stationary_residual"]
    ):
        return state, {
            "accepted": False,
            "step": 0.0,
            "method": "no-decreasing-candidate",
            "before_residual": before["relative_stationary_residual"],
            "after_residual": before["relative_stationary_residual"],
        }

    entropic_increment = step * before["centered_norm_sq"]
    best_state = refresh_state(
        best_state.spinor,
        cfg,
        time=best_state.time,
        entropic_time=state.entropic_time + entropic_increment,
        construction=best_state.construction,
    )
    return best_state, {
        "accepted": True,
        "step": step,
        "method": method,
        "before_residual": before["relative_stationary_residual"],
        "after_residual": best["relative_stationary_residual"],
        "entropic_increment": entropic_increment,
    }


def run_stationary_descent(
    cfg: DiracCartan2IYukawaConfig = DiracCartan2IYukawaConfig(),
    steps: int = 6,
) -> dict[str, Any]:
    state = construct_state(cfg)
    initial = stationary_diagnostics(state, cfg)
    history = []
    for index in range(steps):
        state, record = stationary_step(state, cfg)
        history.append({"iteration": index + 1, **record})
    return {
        "initial": initial,
        "final": stationary_diagnostics(state, cfg),
        "history": history,
        "accepted_steps": sum(bool(row["accepted"]) for row in history),
        "final_state": state,
    }


def _config_with_points(points: int) -> DiracCartan2IYukawaConfig:
    values = asdict(DiracCartan2IYukawaConfig())
    values["points"] = points
    return DiracCartan2IYukawaConfig(**values)


def refinement_campaign(
    point_counts: tuple[int, ...] = (9, 13, 17),
) -> dict[str, Any]:
    rows = []
    for points in point_counts:
        cfg = _config_with_points(points)
        state = construct_state(cfg)
        diagnostics = stationary_diagnostics(state, cfg)
        charge_density, _ = dirac_charge_current(state.spinor, cfg)
        rows.append(
            {
                "points": points,
                "winding": state.measured_winding,
                "winding_error": state.winding_quantization_error,
                "norm": diagnostics["norm"],
                "charge": float(
                    np.sum(charge_density) * cfg.geometry().cell_volume
                ),
                "radius": diagnostics["radius"],
                "boundary_fraction": diagnostics["boundary_fraction"],
                "stationary_residual": diagnostics[
                    "relative_stationary_residual"
                ],
                "mass_clock_error": abs(
                    cfg.hbar * cfg.compton_frequency
                    - cfg.yukawa_mass * cfg.c * cfg.c
                ),
            }
        )
    radii = [row["radius"] for row in rows]
    return {
        "rows": rows,
        "maximum_radius_spread": max(radii) - min(radii),
        "all_topological_and_charge_invariants_close": all(
            row["winding"] == 3
            and row["winding_error"] <= 2.0e-12
            and abs(row["norm"] - 1.0) <= 2.0e-12
            and abs(row["charge"] - 1.0) <= 2.0e-12
            and row["mass_clock_error"] <= 2.0e-15
            for row in rows
        ),
    }


def perturbation_tube(
    cfg: DiracCartan2IYukawaConfig = DiracCartan2IYukawaConfig(),
) -> dict[str, Any]:
    base = construct_state(cfg)
    axis = (
        np.arange(cfg.points, dtype=np.float64) - cfg.points / 2.0
    ) * cfg.spacing
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    rows = []
    for amplitude in (0.0, 0.01, 0.02, 0.03):
        factor = (
            1.0 + amplitude * np.cos(0.31 * x) * np.cos(0.27 * y)
        ) * np.exp(
            1.0j * amplitude * np.sin(0.23 * x) * np.cos(0.19 * z)
        )
        state = refresh_state(
            normalize_spinor(base.spinor * factor[None, ...], cfg),
            cfg,
            construction=f"smooth-amplitude-phase-perturbation-{amplitude:.3f}",
        )
        diagnostics = stationary_diagnostics(state, cfg)
        rows.append(
            {
                "amplitude": amplitude,
                "winding": state.measured_winding,
                "winding_error": state.winding_quantization_error,
                "norm": diagnostics["norm"],
                "radius": diagnostics["radius"],
                "stationary_residual": diagnostics[
                    "relative_stationary_residual"
                ],
            }
        )
    base_residual = rows[0]["stationary_residual"]
    return {
        "rows": rows,
        "winding_preserved": all(
            row["winding"] == 3 and row["winding_error"] <= 2.0e-12
            for row in rows
        ),
        "normalization_preserved": all(
            abs(row["norm"] - 1.0) <= 2.0e-12 for row in rows
        ),
        "bounded_residual_tube": max(
            row["stationary_residual"] for row in rows
        )
        <= 1.25 * max(base_residual, 1.0e-30),
    }


def central_pair_operator_descent(
    cfg: DiracCartan2IYukawaConfig = DiracCartan2IYukawaConfig(),
) -> dict[str, float]:
    base = construct_state(cfg)
    element = binary_icosahedral_quaternions()[37]
    plus = refresh_state(
        apply_binary_icosahedral(base.spinor, element),
        cfg,
        construction="2I-plus-representative",
    )
    minus = refresh_state(
        apply_binary_icosahedral(
            base.spinor,
            tuple(-value for value in element),  # type: ignore[arg-type]
        ),
        cfg,
        construction="2I-central-partner",
    )
    plus_h = real_hamiltonian_action(plus.spinor, plus, cfg)
    minus_h = real_hamiltonian_action(minus.spinor, minus, cfg)
    return {
        "operator_sign_descent_error": float(
            np.linalg.norm(minus_h + plus_h)
            / max(np.linalg.norm(plus_h), 1.0e-30)
        ),
        "density_descent_error": float(
            np.max(
                np.abs(
                    np.sum(np.abs(minus.spinor) ** 2, axis=0)
                    - np.sum(np.abs(plus.spinor) ** 2, axis=0)
                )
            )
        ),
        "cartan_contact_descent_error": float(
            np.max(
                np.abs(
                    minus.cartan_contact_density - plus.cartan_contact_density
                )
            )
        ),
    }


def global_continuity_residual(
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
) -> dict[str, float]:
    geometry = cfg.geometry()
    psi_dot = -1.0j * real_hamiltonian_action(state.spinor, state, cfg)
    charge_dot = cfg.charge * 2.0 * np.real(
        np.sum(np.conj(state.spinor) * psi_dot, axis=0)
    )
    _, current = dirac_charge_current(state.spinor, cfg)
    divergence = geometry.divergence(current)
    local = charge_dot + divergence
    integrated = float(np.sum(local) * geometry.cell_volume)
    scale = max(
        float(
            np.sum(np.abs(charge_dot) + np.abs(divergence))
            * geometry.cell_volume
        ),
        1.0e-30,
    )
    return {
        "integrated_continuity_residual": abs(integrated),
        "relative_integrated_continuity_residual": abs(integrated) / scale,
        "local_l2_residual": math.sqrt(
            float(np.sum(local * local) * geometry.cell_volume)
        ),
    }


@lru_cache(maxsize=1)
def run_m10_closure_study() -> dict[str, Any]:
    cfg = DiracCartan2IYukawaConfig()
    run = run_stationary_descent(cfg)
    final_state = run["final_state"]
    stationary = {key: value for key, value in run.items() if key != "final_state"}
    refinement = refinement_campaign()
    perturbations = perturbation_tube(cfg)
    central = central_pair_operator_descent(cfg)
    continuity = global_continuity_residual(final_state, cfg)

    acceptance = {
        "stationary_descent_accepts_at_least_one_step": stationary[
            "accepted_steps"
        ]
        >= 1,
        "stationary_residual_strictly_decreases": stationary["final"][
            "relative_stationary_residual"
        ]
        < stationary["initial"]["relative_stationary_residual"],
        "entropic_time_advances": final_state.entropic_time > 0.0,
        "nested_grid_topology_charge_and_clock_close": refinement[
            "all_topological_and_charge_invariants_close"
        ],
        "nested_grid_radius_remains_bounded": refinement[
            "maximum_radius_spread"
        ]
        <= 0.75,
        "smooth_perturbation_tube_preserves_winding": perturbations[
            "winding_preserved"
        ],
        "smooth_perturbation_tube_preserves_normalization": perturbations[
            "normalization_preserved"
        ],
        "smooth_perturbation_residuals_remain_bounded": perturbations[
            "bounded_residual_tube"
        ],
        "central_pair_operator_descends": central[
            "operator_sign_descent_error"
        ]
        <= 2.0e-11,
        "central_pair_density_and_cartan_terms_descend": (
            central["density_descent_error"] <= 2.0e-12
            and central["cartan_contact_descent_error"] <= 2.0e-12
        ),
        "global_dirac_continuity_closes": continuity[
            "relative_integrated_continuity_residual"
        ]
        <= 2.0e-11,
        "final_winding_is_retained": final_state.measured_winding == cfg.winding
        and final_state.winding_quantization_error <= 2.0e-12,
    }
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "task": "M10.2a-e",
        "stationary": stationary,
        "refinement": refinement,
        "perturbations": perturbations,
        "central_pair": central,
        "continuity": continuity,
        "final_state_manifest": final_state.manifest(cfg),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "stationary_residual_descent_established": acceptance[
                "stationary_residual_strictly_decreases"
            ],
            "nested_grid_invariants_established": acceptance[
                "nested_grid_topology_charge_and_clock_close"
            ],
            "perturbation_tube_established": acceptance[
                "smooth_perturbation_tube_preserves_winding"
            ]
            and acceptance["smooth_perturbation_residuals_remain_bounded"],
            "central_pair_operator_descent_established": acceptance[
                "central_pair_operator_descends"
            ],
            "global_continuity_established": acceptance[
                "global_dirac_continuity_closes"
            ],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
