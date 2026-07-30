"""M11.4 optional SU(3) color coupling for the pointwise soliton carrier.

This layer intentionally reuses the M10 matrix-valued SU(3) link, covariant
Hamiltonian, exact propagator, and gauge-transformation APIs.  The neutral M11
molecular/QDO sector remains available without color.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from openwave.xperiments.m10_cat_ept.color_matter_gauss_m107 import (
    exact_matter_step,
    gauge_transform_matter,
    hamiltonian_action,
    matter_energy,
    matter_norm,
)
from openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106 import (
    deterministic_gauges,
    deterministic_lattice_links,
    gauge_transform_links,
    gauss_residual,
    magnetic_action,
    zero_electric_field,
)

from .pointwise_soliton_carrier_m111 import construct_pointwise_soliton
from .qdo_lj_atm_interaction_m113 import QDOLJATMConfig, run_qdo_lj_atm_study

MILESTONE = "M11.4"
SCHEMA = "openwave.m11.optional-qcd-coupling.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/YangMillsGaugeDynamics.lean",
        "sha": "4fe7ae3471057b5c7b64fc22705d76f854d66766",
        "theorem": "yangMillsEquation_gauge_covariant",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/GellMannStructureConstants.lean",
        "sha": "b721ea5e04a72430a81d84c6a0a6c20b3f9558a0",
        "theorem": "gellMann_structure_constants",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/SuNGaugeSector.lean",
        "sha": "4585ddf9bc44396b5f9dce14321c4d6b2826cb8a",
        "theorem": "su3_adjoint_eq_gluonCount",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/HorizonCell/QCDComplexActionUnification.lean",
        "sha": "c5d7108ec4781eee3068898d0d844b689230a6fa",
        "theorem": "qcd_theta_confinement_factorization",
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class OptionalQCDConfig:
    enabled: bool = True
    lattice_size: int = 2
    link_scale: float = 0.055
    gauge_scale: float = 0.071
    mass: float = 0.9
    hopping: float = 0.08
    timestep: float = 0.035
    inverse_coupling: float = 1.4
    theta: float = 0.23
    beta: float = 0.8

    def validate(self) -> None:
        if self.lattice_size != 2:
            raise ValueError("the M11.4 reference campaign uses a 2x2 lattice")
        if self.link_scale <= 0 or self.gauge_scale <= 0:
            raise ValueError("positive link and gauge scales are required")
        if self.mass <= 0 or self.hopping <= 0 or self.timestep <= 0:
            raise ValueError("positive dynamical parameters are required")


def soliton_color_matter(size: int = 2) -> np.ndarray:
    soliton = construct_pointwise_soliton()
    sample_indices = np.linspace(0, soliton.x.size - 1, size * size, dtype=int)
    scalar = soliton.psi[sample_indices].reshape(size, size)
    matter = np.empty((size, size, 3), dtype=np.complex128)
    for x in range(size):
        for y in range(size):
            color = np.asarray(
                [
                    1.0,
                    (0.63 + 0.05 * x) * np.exp(1.0j * (0.31 * x + 0.17 * y)),
                    (0.41 + 0.04 * y) * np.exp(-1.0j * (0.13 * x + 0.29 * y)),
                ],
                dtype=np.complex128,
            )
            color /= np.linalg.norm(color)
            matter[x, y] = scalar[x, y] * color
    norm = float(np.linalg.norm(matter))
    if norm <= 0.0:
        raise ValueError("nonzero soliton matter field required")
    return np.asarray(matter / norm, dtype=np.complex128)


def _max_link_unitarity_error(links: np.ndarray) -> float:
    identity = np.eye(3)
    return float(
        max(
            np.linalg.norm(links[index].conj().T @ links[index] - identity)
            for index in np.ndindex(links.shape[:3])
        )
    )


def _max_link_determinant_error(links: np.ndarray) -> float:
    return float(
        max(abs(np.linalg.det(links[index]) - 1.0) for index in np.ndindex(links.shape[:3]))
    )


def _qcd_history_weight(cfg: OptionalQCDConfig, magnetic: float, matter_energy_value: float) -> complex:
    if not cfg.enabled:
        return complex(np.exp(-cfg.beta * matter_energy_value))
    return complex(np.exp(1.0j * cfg.theta - cfg.beta * (magnetic + matter_energy_value)))


def canonical_payload(config: OptionalQCDConfig | None = None) -> dict[str, Any]:
    cfg = OptionalQCDConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M11",
        "milestone": MILESTONE,
        "configuration": asdict(cfg),
        "study_api": (
            "openwave.xperiments.m11_cat_ept_soliton_qdo."
            "optional_qcd_coupling_m114:run_optional_qcd_study"
        ),
        "reuses": [
            "openwave.xperiments.m10_cat_ept.periodic_su3_hamiltonian_m106",
            "openwave.xperiments.m10_cat_ept.color_matter_gauss_m107",
        ],
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


def run_optional_qcd_study(config: OptionalQCDConfig | None = None) -> dict[str, Any]:
    cfg = OptionalQCDConfig() if config is None else config
    cfg.validate()
    links = deterministic_lattice_links(cfg.lattice_size, cfg.link_scale)
    gauges = deterministic_gauges(cfg.lattice_size, cfg.gauge_scale)
    matter = soliton_color_matter(cfg.lattice_size)
    transformed_links = gauge_transform_links(links, gauges)
    transformed_matter = gauge_transform_matter(matter, gauges)
    action = hamiltonian_action(links, matter, cfg.mass, cfg.hopping)
    transformed_action = hamiltonian_action(
        transformed_links, transformed_matter, cfg.mass, cfg.hopping
    )
    expected_transformed_action = gauge_transform_matter(action, gauges)
    evolved = exact_matter_step(
        links, matter, cfg.timestep, cfg.mass, cfg.hopping
    )
    evolved_transformed = exact_matter_step(
        transformed_links,
        transformed_matter,
        cfg.timestep,
        cfg.mass,
        cfg.hopping,
    )
    expected_evolved = gauge_transform_matter(evolved, gauges)
    electric = zero_electric_field(cfg.lattice_size)
    magnetic = magnetic_action(links, cfg.inverse_coupling)
    energy = matter_energy(links, matter, cfg.mass, cfg.hopping)
    weight = _qcd_history_weight(cfg, magnetic, energy)
    neutral_cfg = OptionalQCDConfig(**{**asdict(cfg), "enabled": False})
    neutral_weight = _qcd_history_weight(neutral_cfg, magnetic, energy)
    qdo = run_qdo_lj_atm_study(QDOLJATMConfig())
    diagnostics = {
        "matter_norm_error": abs(matter_norm(matter) - 1.0),
        "evolved_norm_error": abs(matter_norm(evolved) - 1.0),
        "gauge_covariance_error": float(np.linalg.norm(transformed_action - expected_transformed_action)),
        "evolution_covariance_error": float(np.linalg.norm(evolved_transformed - expected_evolved)),
        "link_unitarity_error": _max_link_unitarity_error(links),
        "link_determinant_error": _max_link_determinant_error(links),
        "source_free_gauss_residual": gauss_residual(links, electric),
        "magnetic_action": magnetic,
        "matter_energy": energy,
        "qcd_weight_modulus": abs(weight),
        "neutral_weight_phase_error": abs(np.angle(neutral_weight)),
        "colored_weight_phase_error": abs(np.angle(weight) - cfg.theta),
        "qdo_sector_passed": bool(qdo["passed"]),
    }
    acceptance = {
        "normalized_soliton_color_field": diagnostics["matter_norm_error"] < 5.0e-13,
        "exact_propagator_preserves_norm": diagnostics["evolved_norm_error"] < 5.0e-13,
        "hamiltonian_is_gauge_covariant": diagnostics["gauge_covariance_error"] < 5.0e-12,
        "evolution_is_gauge_covariant": diagnostics["evolution_covariance_error"] < 5.0e-12,
        "links_are_unitary": diagnostics["link_unitarity_error"] < 5.0e-12,
        "links_have_unit_determinant": diagnostics["link_determinant_error"] < 5.0e-12,
        "source_free_gauss_closes": diagnostics["source_free_gauss_residual"] < 5.0e-13,
        "neutral_sector_has_no_theta_phase": diagnostics["neutral_weight_phase_error"] < 5.0e-13,
        "colored_sector_carries_theta_phase": diagnostics["colored_weight_phase_error"] < 5.0e-13,
        "qdo_sector_remains_available": diagnostics["qdo_sector_passed"],
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M11.4",
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
    }
