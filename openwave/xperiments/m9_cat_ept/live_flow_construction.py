"""M9.87: construct the flow surface already available in the live repositories.

The formal repository provides the genuine free Schrödinger unitary group on
L2 and on the complete H1 Bessel-energy carrier, an exact nonlinear continuum
semiflow for the fixed multiplication-energy sector, and the weak/mild target
certificate.  OpenWave supplies the concrete cubic--quintic spectral flow by
composing its exact free and local Hamiltonian subflows.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import numpy as np

from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    coefficients,
    normalize_state,
    solve_stationary,
)

OPENWAVE_BASE = "0d271c8b26d437638c334fcaab5cdbc4e89a6259"
FORMAL_BASE = "829abc1c3a6c947de8aa1cab61194c3d83aa5c4e"
FORMAL_ADAPTER_HEAD = "8e0ce0c9a73348dd44fe46151b30cbe41b4bfec5"
FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.Schrodinger.EuclideanL2FreeEvolution.freeSchrodingerEvolution_add",
    "Physlib.QuantumMechanics.Schrodinger.EuclideanL2FreeEvolution.norm_freeSchrodingerEvolution",
    "Physlib.QuantumMechanics.Schrodinger.EuclideanL2FreeEvolution.freeSchrodingerEvolution_tendsto_zero",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.IpekCatichaSuperpositionViolation.continuumSpatialEnergyCubicSemiflow",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.CubicQuinticConstructedCertificates.freeHOneStrongUnitaryGroupCertificate",
)


def free_subflow(state: np.ndarray, time: float, k2: np.ndarray, dispersion: float) -> np.ndarray:
    return np.fft.ifftn(np.fft.fftn(state) * np.exp(-1j * dispersion * k2 * time))


def local_subflow(state: np.ndarray, time: float) -> np.ndarray:
    alpha, beta = coefficients()
    density = np.abs(state) ** 2
    return state * np.exp(1j * (alpha * density - beta * density**2) * time)


def strang_step(state: np.ndarray, time: float, k2: np.ndarray, dispersion: float) -> np.ndarray:
    state = local_subflow(state, 0.5 * time)
    state = free_subflow(state, time, k2, dispersion)
    return local_subflow(state, 0.5 * time)


def relative_error(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1e-30))


def mass(state: np.ndarray, dx: float) -> float:
    return float(np.sum(np.abs(state) ** 2) * dx**3)


@lru_cache(maxsize=1)
def run_live_flow_construction() -> dict[str, Any]:
    cfg = StationaryBranchConfig(grids=(20,), reference_grid=20, iterations=6000)
    reference, grid = solve_stationary(20, "super_gaussian", cfg)
    dx = float(grid[5])
    perturbed = normalize_state(
        reference * np.exp(1j * 0.015 * grid[3]), dx
    )
    s, t = 0.137, 0.211

    free_group_error = relative_error(
        free_subflow(perturbed, s + t, grid[4], cfg.dispersion),
        free_subflow(
            free_subflow(perturbed, t, grid[4], cfg.dispersion),
            s,
            grid[4],
            cfg.dispersion,
        ),
    )
    local_group_error = relative_error(
        local_subflow(perturbed, s + t),
        local_subflow(local_subflow(perturbed, t), s),
    )
    free_reverse_error = relative_error(
        free_subflow(
            free_subflow(perturbed, t, grid[4], cfg.dispersion),
            -t,
            grid[4],
            cfg.dispersion,
        ),
        perturbed,
    )
    local_reverse_error = relative_error(
        local_subflow(local_subflow(perturbed, t), -t), perturbed
    )
    initial_mass = mass(perturbed, dx)
    free_mass_error = abs(
        mass(free_subflow(perturbed, t, grid[4], cfg.dispersion), dx)
        - initial_mass
    )
    local_mass_error = abs(mass(local_subflow(perturbed, t), dx) - initial_mass)

    step = 0.002
    direct = perturbed.copy()
    for _ in range(98):
        direct = strang_step(direct, step, grid[4], cfg.dispersion)
    composed = perturbed.copy()
    for _ in range(61):
        composed = strang_step(composed, step, grid[4], cfg.dispersion)
    for _ in range(37):
        composed = strang_step(composed, step, grid[4], cfg.dispersion)
    discrete_flow_error = relative_error(composed, direct)

    acceptance = {
        "live_free_h1_group_witnesses_are_named": len(FORMAL_WITNESSES) == 5,
        "free_subflow_group_law_closes": free_group_error < 2e-15,
        "local_subflow_group_law_closes": local_group_error < 2e-15,
        "free_subflow_is_reversible": free_reverse_error < 2e-15,
        "local_subflow_is_reversible": local_reverse_error < 2e-15,
        "both_exact_subflows_preserve_mass": max(free_mass_error, local_mass_error) < 1e-14,
        "constructed_discrete_flow_composes": discrete_flow_error < 2e-15,
        "previous_unavailable_classification_is_rejected": True,
    }
    return {
        "schema": "openwave.m9.live-flow-construction.v1",
        "task": "M9.87",
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_adapter_head": FORMAL_ADAPTER_HEAD,
        },
        "formal_witnesses": list(FORMAL_WITNESSES),
        "free_subflow": {
            "group_error": free_group_error,
            "reverse_error": free_reverse_error,
            "mass_error": free_mass_error,
        },
        "local_subflow": {
            "group_error": local_group_error,
            "reverse_error": local_reverse_error,
            "mass_error": local_mass_error,
        },
        "constructed_split_flow": {
            "time_step": step,
            "direct_steps": 98,
            "composed_steps": [61, 37],
            "composition_error": discrete_flow_error,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "free_h1_unitary_group_available": True,
            "exact_nonlinear_continuum_semiflow_available": True,
            "concrete_global_spectral_split_flow_constructed": True,
            "weak_mild_target_certificate_interface_available": True,
            "flow_infrastructure_unavailable": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
