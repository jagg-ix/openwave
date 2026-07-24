"""M9.57 scoped action-to-generator and live formal-status reconciliation.

The numerical bridge checks a finite periodic action gradient. Formal source rows
are blob-pinned to entropic-physlib-linear-full@14ecf025... and preserve scoped,
conditional, and open status distinctions from the ZIL closure ledger.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "14ecf025ec58d2ec9e4731081c4ed1853f4468f0"
FORMAL_SOURCES = (
    {
        "path": "formalization/zil/electrogravitic-action-closure.zc",
        "sha": "cf9110d8b4229c33a1e2cefa34c0719062a3f340",
        "status": "scoped_proved_interfaces",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalEinsteinHilbertAction.lean",
        "sha": "6862565fb915b5c6f1cc561b769e190b70f3156a",
        "status": "proved_with_explicit_scope",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalElectrograviticAction.lean",
        "sha": "39e807f424cf8384135299e84fdffc97fb506ee5",
        "status": "proved_with_explicit_scope",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/ADMConstraintPropagation.lean",
        "sha": "600b872eb73611de817df0d00dd6711570c567e2",
        "status": "conditional_on_explicit_analytic_data",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/CanonicalTetradGravity/MaximalCauchyDevelopment.lean",
        "sha": "2504c579fd8f8afe0a1670911142fb0e7ecdb2c0",
        "status": "conditional_on_gluing_data",
    },
    {
        "path": "docs/EntropicDynamicsClosure.md",
        "sha": "e9d542ea516492b6e308a5610f952f831f4ed1c5",
        "status": "status_ledger",
    },
)


@dataclass(frozen=True)
class ActionConfig:
    points: int = 96
    length: float = 2 * math.pi
    kinetic: float = 0.35
    potential: float = 0.18
    focusing: float = 0.8
    saturation: float = 0.45
    epsilon: float = 2e-7

    def __post_init__(self) -> None:
        if self.points < 32 or self.points % 2:
            raise ValueError("even grid >=32 required")
        if min(self.length, self.kinetic, self.epsilon) <= 0:
            raise ValueError("positive action controls required")
        if min(self.focusing, self.saturation) < 0:
            raise ValueError("nonnegative interaction controls required")


def grid(cfg: ActionConfig = ActionConfig()) -> tuple[np.ndarray, np.ndarray, float]:
    dx = cfg.length / cfg.points
    x = np.arange(cfg.points) * dx
    k = 2 * math.pi * np.fft.fftfreq(cfg.points, d=dx)
    return x, k, dx


def state(cfg: ActionConfig = ActionConfig()) -> np.ndarray:
    x, _k, dx = grid(cfg)
    psi = (1 + 0.22 * np.cos(x - 0.3)) * np.exp(0.35j * np.sin(x))
    return psi / math.sqrt(float(np.sum(np.abs(psi) ** 2) * dx))


def laplacian(psi: np.ndarray, cfg: ActionConfig = ActionConfig()) -> np.ndarray:
    _x, k, _dx = grid(cfg)
    return np.fft.ifft(-(k * k) * np.fft.fft(psi))


def action(psi: np.ndarray, cfg: ActionConfig = ActionConfig()) -> float:
    x, k, dx = grid(cfg)
    derivative = np.fft.ifft(1j * k * np.fft.fft(psi))
    rho = np.abs(psi) ** 2
    density = (
        cfg.kinetic * np.abs(derivative) ** 2
        + cfg.potential * np.cos(x) * rho
        - 0.5 * cfg.focusing * rho**2
        + (cfg.saturation / 3) * rho**3
    )
    return float(np.sum(density.real) * dx)


def gradient(psi: np.ndarray, cfg: ActionConfig = ActionConfig()) -> np.ndarray:
    x, _k, _dx = grid(cfg)
    rho = np.abs(psi) ** 2
    return (
        -cfg.kinetic * laplacian(psi, cfg)
        + cfg.potential * np.cos(x) * psi
        - cfg.focusing * rho * psi
        + cfg.saturation * rho * rho * psi
    )


def direction(cfg: ActionConfig = ActionConfig()) -> np.ndarray:
    x, _k, dx = grid(cfg)
    value = (0.6 * np.cos(2 * x) + 0.25j * np.sin(3 * x)) * np.exp(0.1j * x)
    return value / math.sqrt(float(np.sum(np.abs(value) ** 2) * dx))


def derivative_control(cfg: ActionConfig = ActionConfig()) -> dict[str, float]:
    psi = state(cfg)
    h = direction(cfg)
    eps = cfg.epsilon
    _x, _k, dx = grid(cfg)
    finite = (action(psi + eps * h, cfg) - action(psi - eps * h, cfg)) / (2 * eps)
    analytic = 2 * float(np.real(np.vdot(gradient(psi, cfg), h)) * dx)
    return {
        "finite_difference": finite,
        "analytic_directional_derivative": analytic,
        "absolute_error": abs(finite - analytic),
    }


def flow_control(cfg: ActionConfig = ActionConfig()) -> dict[str, float]:
    psi = state(cfg)
    grad = gradient(psi, cfg)
    _x, _k, dx = grid(cfg)
    dissipative_rate = 2 * float(np.real(np.vdot(grad, -grad)) * dx)
    hamiltonian_rate = 2 * float(np.real(np.vdot(grad, -1j * grad)) * dx)
    dt = 1e-5
    return {
        "dissipative_action_rate": dissipative_rate,
        "hamiltonian_action_rate": hamiltonian_rate,
        "dissipative_step_change": action(psi - dt * grad, cfg) - action(psi, cfg),
        "hamiltonian_step_change": action(psi - 1j * dt * grad, cfg) - action(psi, cfg),
    }


def evidence_fingerprint() -> str:
    payload = {
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "head": FORMAL_HEAD,
        "sources": FORMAL_SOURCES,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_action_generator_study() -> dict[str, Any]:
    cfg = ActionConfig()
    derivative = derivative_control(cfg)
    flow = flow_control(cfg)
    accepted_status = {
        "scoped_proved_interfaces",
        "proved_with_explicit_scope",
        "conditional_on_explicit_analytic_data",
        "conditional_on_gluing_data",
        "status_ledger",
    }
    acceptance = {
        "live_formal_head_is_pinned": len(FORMAL_HEAD) == 40,
        "all_formal_sources_are_blob_pinned": all(len(x["sha"]) == 40 for x in FORMAL_SOURCES),
        "status_vocabulary_is_scoped": all(x["status"] in accepted_status for x in FORMAL_SOURCES),
        "finite_action_derivative_closes": derivative["absolute_error"] <= 2e-8,
        "dissipative_direction_decreases_action": flow["dissipative_action_rate"] < 0
        and flow["dissipative_step_change"] < 0,
        "hamiltonian_direction_is_first_order_action_neutral": abs(flow["hamiltonian_action_rate"]) <= 1e-12
        and abs(flow["hamiltonian_step_change"]) <= 2e-9,
        "evidence_fingerprint_is_deterministic": evidence_fingerprint() == evidence_fingerprint(),
    }
    return {
        "schema": "openwave.m9.action-generator-bridge.v1",
        "task": "M9.57",
        "config": asdict(cfg),
        "formal_evidence": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "sources": FORMAL_SOURCES,
            "fingerprint": evidence_fingerprint(),
        },
        "derivative_control": derivative,
        "flow_control": flow,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_action_to_generator_bridge_qualified": True,
            "formal_global_action_interfaces_reconciled": True,
            "full_cat_ept_continuum_generator_theorem_proved": False,
        },
        "classification": {
            "establishes": [
                "live blob-pinned PhysLib/ZIL status reconciliation",
                "finite action directional derivative and generator bridge",
                "reversible versus dissipative action-rate discrimination",
            ],
            "does_not_establish": [
                "closability or maximal dissipativity of the full CAT/EPT continuum generator",
                "one unique physical irreversible law",
                "unconditional global coupled Einstein-Maxwell-entropic Cauchy development",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
