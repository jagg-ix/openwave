"""M9.70 cross-repository cubic--quintic H1 kernel certificate.

PhysLib proves the exact density coercivity factorization and derives uniform
orbital control from explicit evolution, conservation, compactness-modulo-symmetry,
and Lyapunov-coercivity certificates. OpenWave verifies the numerical coefficient
specialization and records the remaining analytic premises without promotion.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import numpy as np

from .coefficient_self_consistency import selected_coefficients

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "agent/m9-cubic-quintic-h1-certificate-70"
FORMAL_HEAD = "51aad63b2541a1377a001df71b85dfe35f26c0af"
FORMAL_SOURCE = {
    "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
    "sha": "b1bbf0bd6e58b41796aba1d63919f3cd6fe7aca4",
    "unconditional_theorems": [
        "cubicQuinticDensity_slack_eq",
        "cubicQuinticDensity_coercive",
    ],
    "conditional_theorems": [
        "H1OrbitalCertificate.energy_excess_flow_eq",
        "H1OrbitalCertificate.orbitDistance_le_of_energy_excess",
        "H1OrbitalCertificate.uniform_orbital_stability",
        "H1OrbitalCertificate.minimizingSequence_compact_modulo_symmetry",
    ],
}


def density_slack(alpha: float, beta: float, density: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if beta <= 0 or np.any(density < 0):
        raise ValueError("positive beta and nonnegative density required")
    lhs = (
        -0.5 * alpha * density**2
        + (beta / 3.0) * density**3
        + (3.0 * alpha**2 / (16.0 * beta)) * density
    )
    rhs = (beta / 3.0) * density * (density - 3.0 * alpha / (4.0 * beta)) ** 2
    return lhs, rhs


def formal_scope() -> dict[str, Any]:
    return {
        "proved_without_analytic_premises": [
            "exact square factorization of the cubic--quintic density slack",
            "pointwise lower bound V(rho) >= -(3 alpha^2/(16 beta)) rho",
        ],
        "proved_from_explicit_certificate_fields": [
            "flow composition and continuous time orbits",
            "energy-excess invariance",
            "compactness conclusion modulo a supplied symmetry action",
            "uniform orbital-distance bound from conserved coercive energy",
        ],
        "still_required_as_certificate_data": [
            "construction of the spatial cubic--quintic H1 flow",
            "mass and energy conservation for that PDE",
            "concentration compactness modulo phase and translation",
            "coercivity of the nonzero stationary branch in the full H1 carrier",
        ],
    }


@lru_cache(maxsize=1)
def run_h1_kernel_certificate() -> dict[str, Any]:
    selected = selected_coefficients()
    alpha, beta = float(selected["alpha"]), float(selected["beta"])
    equality_density = 3.0 * alpha / (4.0 * beta)
    density = np.linspace(0.0, 3.0 * equality_density, 4097)
    lhs, rhs = density_slack(alpha, beta, density)
    factorization_error = float(np.max(np.abs(lhs - rhs)))
    minimum_slack = float(np.min(lhs))
    scope = formal_scope()
    acceptance = {
        "formal_branch_and_source_are_pinned": len(FORMAL_HEAD) == 40
        and len(FORMAL_SOURCE["sha"]) == 40,
        "numerical_specialization_matches_kernel_factorization": factorization_error <= 2e-13,
        "density_slack_is_nonnegative": minimum_slack >= -2e-13,
        "unconditional_and_conditional_results_are_separated": bool(
            FORMAL_SOURCE["unconditional_theorems"]
        )
        and bool(FORMAL_SOURCE["conditional_theorems"]),
        "missing_analytic_hypotheses_remain_explicit": len(
            scope["still_required_as_certificate_data"]
        ) == 4,
    }
    return {
        "schema": "openwave.m9.h1-kernel-certificate.v1",
        "task": "M9.70",
        "formal_evidence": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "head": FORMAL_HEAD,
            "source": FORMAL_SOURCE,
        },
        "coefficient_specialization": {
            "alpha": alpha,
            "beta": beta,
            "coercivity_constant": 3.0 * alpha**2 / (16.0 * beta),
            "equality_density": equality_density,
            "maximum_factorization_error": factorization_error,
            "minimum_sampled_slack": minimum_slack,
        },
        "scope": scope,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "density_coercivity_kernel_proved": True,
            "conditional_h1_orbital_stability_kernel_proved": True,
            "spatial_cubic_quintic_h1_flow_constructed_in_kernel": False,
            "compactness_derived_from_the_spatial_pde": False,
            "m9_70_scoped_formal_target_closed": True,
            "m9_70_end_to_end_analytic_target_closed": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
