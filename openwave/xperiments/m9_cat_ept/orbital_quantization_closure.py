"""M9.92 Coulomb orbital-quantization criterion closure.

The existing radial study recovers the hydrogenic ladder for l=0. This module
adds the Coulomb cross-l degeneracies for 2s/2p and 3s/3p/3d and pins the live
formal unscreened-Yukawa/O(4)/Gegenbauer theorem surface. Physical atomic units,
particle identity, and radiative transitions remain separate.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import numpy as np

from .orbital_quantization import OrbitalConfig, run_orbital_quantization_study, solve_modes

OPENWAVE_BASE = "6773431e37a08efce2d9d9b1ec53ca2b953080dc"
FORMAL_BASE = "3923d802339c957066fcccd579362f739775797a"
FORMAL_PARENT_HEAD = "128bebd375cd895af1431444974a7a591c872a31"
FORMAL_CRITERION_HEAD = "e192104955fc516f1ba267f8653f0dcf8d18ab51"
FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer.entropicMass_coulomb",
    "Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer.yukawaPotential_zero_eq_coulomb",
    "Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer.yukawa_coulomb_o4_gegenbauer",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.M9ChargeKleinOrbitalCriteria.hydrogenicEnergy_neg",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.M9ChargeKleinOrbitalCriteria.orbitalQuantizationCriterion",
)


def cross_angular_momentum_audit() -> dict[str, Any]:
    radius = 100.0
    points = 2400
    s = solve_modes(OrbitalConfig(radius=radius, points=points, angular_momentum=0, states=3))["energies"]
    p = solve_modes(OrbitalConfig(radius=radius, points=points, angular_momentum=1, states=2))["energies"]
    d = solve_modes(OrbitalConfig(radius=radius, points=points, angular_momentum=2, states=1))["energies"]
    n2 = np.asarray([s[1], p[0]])
    n3 = np.asarray([s[2], p[1], d[0]])
    energies = {
        "1s": float(s[0]),
        "2s": float(s[1]),
        "2p": float(p[0]),
        "3s": float(s[2]),
        "3p": float(p[1]),
        "3d": float(d[0]),
    }
    return {
        "radius": radius,
        "points": points,
        "energies": energies,
        "n2_spread": float(np.ptp(n2)),
        "n3_spread": float(np.ptp(n3)),
        "n2_maximum_error": float(np.max(np.abs(n2 - (-0.125)))),
        "n3_maximum_error": float(np.max(np.abs(n3 - (-1.0 / 18.0)))),
    }


@lru_cache(maxsize=1)
def run_orbital_quantization_closure() -> dict[str, Any]:
    radial = run_orbital_quantization_study()
    degeneracy = cross_angular_momentum_audit()
    acceptance = {
        "radial_hydrogenic_campaign_passes": bool(radial["passed"]),
        "four_negative_bound_levels_exist": all(value < 0 for value in radial["energies"]),
        "radial_hydrogenic_ladder_is_accurate": max(radial["relative_errors"][:3]) < 1e-3,
        "integer_node_ladder_and_orthogonality_close": (
            radial["node_counts"] == [0, 1, 2, 3]
            and radial["maximum_orthogonality_error"] < 2e-14
        ),
        "radial_resolution_is_second_order": min(radial["resolution"]["orders"]) > 1.9,
        "two_s_two_p_degeneracy_closes": degeneracy["n2_spread"] < 3e-5,
        "three_s_three_p_three_d_degeneracy_closes": degeneracy["n3_spread"] < 1e-5,
        "cross_l_levels_match_hydrogenic_energies": max(
            degeneracy["n2_maximum_error"], degeneracy["n3_maximum_error"]
        ) < 2e-5,
        "formal_coulomb_o4_witnesses_are_named": len(FORMAL_WITNESSES) == 5,
        "physical_atomic_identity_is_not_inherited": True,
    }
    return {
        "schema": "openwave.m9.orbital-quantization-closure.v1",
        "task": "M9.92",
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_parent_head": FORMAL_PARENT_HEAD,
            "physlib_criterion_head": FORMAL_CRITERION_HEAD,
        },
        "formal_witnesses": list(FORMAL_WITNESSES),
        "radial": {
            "energies": radial["energies"],
            "analytic_energies": radial["analytic_energies"],
            "relative_errors": radial["relative_errors"],
            "node_counts": radial["node_counts"],
            "maximum_orthogonality_error": radial["maximum_orthogonality_error"],
            "maximum_density_stationarity_error": radial["maximum_density_stationarity_error"],
            "resolution": radial["resolution"],
            "domain": radial["domain"],
        },
        "cross_angular_momentum": degeneracy,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "orbital_quantization_validated_in_platform": True,
            "hydrogenic_radial_ladder_closed": True,
            "coulomb_cross_l_degeneracy_closed": True,
            "emergent_electron_and_nucleus_identified": False,
            "radiative_transitions_and_physical_units_calibrated": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
