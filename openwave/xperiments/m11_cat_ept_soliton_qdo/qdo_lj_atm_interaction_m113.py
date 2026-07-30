"""M11.3 QDO-calibrated Lennard-Jones and Axilrod-Teller interactions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import itertools
import json
import math
from typing import Any, Mapping

import numpy as np

MILESTONE = "M11.3"
SCHEMA = "openwave.m11.qdo-lj-atm-interaction.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCE_PATH = (
    "Physlib/QuantumMechanics/ComplexAction/Particles/"
    "LennardJonesAxilrodTeller.lean"
)
FORMAL_SOURCE_SHA = "93f5e1b55d1fbfe44dc5b8106b7331d08bdb5159"
FORMAL_SOURCES = tuple(
    {
        "path": FORMAL_SOURCE_PATH,
        "sha": FORMAL_SOURCE_SHA,
        "theorem": theorem,
    }
    for theorem in (
        "ljPotential_split",
        "lj_tail_dispersion_form",
        "lj_tail_eq_vdw_dispersionEnergy",
        "lj_tail_is_qdo_C6",
        "lattice_couplings_qdo_related",
        "atm_equilateral",
        "atm_linear",
    )
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class QDOLJATMConfig:
    alpha1: float = 1.0
    hbar_omega: float = 1.0
    repulsive_exponent: int = 12
    equilibrium_distance: float = 1.0
    epsilon: float = 0.375
    core_radius: float = 0.08

    def validate(self) -> None:
        if self.alpha1 <= 0 or self.hbar_omega <= 0:
            raise ValueError("positive QDO response parameters are required")
        if self.repulsive_exponent <= 6:
            raise ValueError("repulsive exponent must exceed six")
        if self.equilibrium_distance <= 0 or self.epsilon <= 0:
            raise ValueError("positive LJ parameters are required")
        if self.core_radius < 0:
            raise ValueError("nonnegative core radius required")


def qdo_c6(alpha1: float, hbar_omega: float) -> float:
    return 0.75 * alpha1**2 * hbar_omega


def qdo_c9(alpha1: float, hbar_omega: float) -> float:
    return 3.0 / 16.0 * alpha1**3 * hbar_omega


def lj_c6(epsilon: float, equilibrium_distance: float, exponent: int) -> float:
    return epsilon * exponent * equilibrium_distance**6 / (exponent - 6.0)


def lj_repulsive(epsilon: float, re: float, r: float, n: int, m: int = 6) -> float:
    return epsilon * n * m / (n - m) * (1.0 / n) * (re / r) ** n


def lj_attractive(epsilon: float, re: float, r: float, n: int, m: int = 6) -> float:
    return epsilon * n * m / (n - m) * (1.0 / m) * (re / r) ** m


def lj_potential(epsilon: float, re: float, r: float, n: int, m: int = 6) -> float:
    return lj_repulsive(epsilon, re, r, n, m) - lj_attractive(epsilon, re, r, n, m)


def dispersion_energy(coefficient: float, r: float) -> float:
    return -0.75 * coefficient / r**6


def atm_angular_factor(cosines: tuple[float, float, float]) -> float:
    c1, c2, c3 = cosines
    return 1.0 + 3.0 * c1 * c2 * c3


def atm_energy(
    coupling: float,
    cosines: tuple[float, float, float],
    distances: tuple[float, float, float],
) -> float:
    return coupling * atm_angular_factor(cosines) / np.prod(distances) ** 3


def triangle_cosines(points: np.ndarray) -> tuple[float, float, float]:
    if points.shape != (3, points.shape[1]):
        raise ValueError("three points required")
    cosines: list[float] = []
    for center in range(3):
        left = points[(center + 1) % 3] - points[center]
        right = points[(center + 2) % 3] - points[center]
        cosine = float(np.dot(left, right) / (np.linalg.norm(left) * np.linalg.norm(right)))
        cosines.append(float(np.clip(cosine, -1.0, 1.0)))
    return tuple(cosines)  # type: ignore[return-value]


def trimer_atm_energy(points: np.ndarray, coupling: float) -> float:
    distances = tuple(
        float(np.linalg.norm(points[i] - points[j]))
        for i, j in ((0, 1), (0, 2), (1, 2))
    )
    return atm_energy(coupling, triangle_cosines(points), distances)


def density_smeared_dispersion(
    x: np.ndarray,
    density_a: np.ndarray,
    density_b: np.ndarray,
    separation: float,
    c6: float,
    core_radius: float,
) -> float:
    dx = float(x[1] - x[0])
    shifted = x[:, None] - (x[None, :] + separation)
    kernel = 1.0 / (shifted**2 + core_radius**2) ** 3
    return float(-c6 * np.sum(density_a[:, None] * density_b[None, :] * kernel) * dx**2)


def canonical_payload(config: QDOLJATMConfig | None = None) -> dict[str, Any]:
    cfg = QDOLJATMConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M11",
        "milestone": MILESTONE,
        "configuration": asdict(cfg),
        "study_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "qdo_lj_atm_interaction_m113:run_qdo_lj_atm_study"
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


def run_qdo_lj_atm_study(config: QDOLJATMConfig | None = None) -> dict[str, Any]:
    cfg = QDOLJATMConfig() if config is None else config
    cfg.validate()
    c6_qdo = qdo_c6(cfg.alpha1, cfg.hbar_omega)
    c9_qdo = qdo_c9(cfg.alpha1, cfg.hbar_omega)
    c6_lj = lj_c6(cfg.epsilon, cfg.equilibrium_distance, cfg.repulsive_exponent)
    distances = np.geomspace(1.3, 8.0, 32)
    split_errors = []
    tail_errors = []
    vdw_errors = []
    tails = []
    for r in distances:
        repulsive = lj_repulsive(cfg.epsilon, cfg.equilibrium_distance, float(r), cfg.repulsive_exponent)
        attractive = lj_attractive(cfg.epsilon, cfg.equilibrium_distance, float(r), cfg.repulsive_exponent)
        total = lj_potential(cfg.epsilon, cfg.equilibrium_distance, float(r), cfg.repulsive_exponent)
        split_errors.append(abs(total - (repulsive - attractive)))
        tail = -attractive
        tails.append(abs(tail))
        tail_errors.append(abs(tail + c6_lj / float(r) ** 6))
        vdw_errors.append(abs(tail - dispersion_energy(4.0 / 3.0 * c6_lj, float(r))))
    slope = float(np.polyfit(np.log(distances[-12:]), np.log(np.asarray(tails[-12:])), 1)[0])
    equilateral = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3.0) / 2.0]])
    linear = np.asarray([[-1.0, 0.0], [0.0, 0.0], [1.0, 0.0]])
    permutations = [trimer_atm_energy(equilateral[list(order)], c9_qdo) for order in itertools.permutations(range(3))]
    eq_factor = atm_angular_factor(triangle_cosines(equilateral))
    linear_factor = atm_angular_factor(triangle_cosines(linear))
    scale = 1.7
    atm_scale_ratio = trimer_atm_energy(equilateral * scale, c9_qdo) / trimer_atm_energy(equilateral, c9_qdo)
    diagnostics = {
        "c6_lj": c6_lj,
        "c6_qdo": c6_qdo,
        "c6_match_error": abs(c6_lj - c6_qdo),
        "c9_qdo": c9_qdo,
        "threebody_invariant_error": abs(cfg.alpha1 * c6_qdo - 4.0 * c9_qdo),
        "maximum_split_error": max(split_errors),
        "maximum_tail_error": max(tail_errors),
        "maximum_vdw_error": max(vdw_errors),
        "far_field_log_slope": slope,
        "equilateral_factor": eq_factor,
        "linear_factor": linear_factor,
        "atm_permutation_error": float(max(permutations) - min(permutations)),
        "atm_scaling_error": abs(atm_scale_ratio - scale**-9),
        "well_depth_error": abs(
            lj_potential(cfg.epsilon, cfg.equilibrium_distance, cfg.equilibrium_distance, cfg.repulsive_exponent)
            + cfg.epsilon
        ),
    }
    acceptance = {
        "lj_split_exact": diagnostics["maximum_split_error"] < 5.0e-13,
        "tail_is_minus_c6_over_r6": diagnostics["maximum_tail_error"] < 5.0e-13,
        "tail_equals_vdw_energy": diagnostics["maximum_vdw_error"] < 5.0e-13,
        "lj_c6_is_qdo_c6": diagnostics["c6_match_error"] < 5.0e-13,
        "qdo_two_three_body_invariant": diagnostics["threebody_invariant_error"] < 5.0e-13,
        "tail_slope_is_minus_six": abs(slope + 6.0) < 5.0e-12,
        "atm_equilateral_repulsive": abs(eq_factor - 11.0 / 8.0) < 5.0e-13,
        "atm_linear_attractive": abs(linear_factor + 2.0) < 5.0e-13,
        "atm_permutation_symmetric": diagnostics["atm_permutation_error"] < 5.0e-13,
        "atm_scales_as_r_minus_nine": diagnostics["atm_scaling_error"] < 5.0e-13,
        "well_depth_is_minus_epsilon": diagnostics["well_depth_error"] < 5.0e-13,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M11.3",
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
    }
