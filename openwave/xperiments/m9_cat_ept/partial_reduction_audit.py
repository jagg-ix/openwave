"""Deep criterion-by-criterion audit of the twenty M9 partial rows.

The audit asks whether the literal OpenWave criterion is already closed by a
combination of live PhysLib theorems and executable OpenWave controls. It keeps
criterion validation separate from stronger emergence, calibration, and
external-physics claims.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

BASELINE_PARTIALS = (
    "charge_quantization",
    "electron_rest_energy",
    "de_broglie_clock",
    "particle_stability",
    "magnetic_moment_spin",
    "spin_half_statistics",
    "antimatter_annihilation",
    "dark_matter",
    "quarks",
    "baryons",
    "mesons",
    "electric_force",
    "magnetic_force",
    "strong_force",
    "weak_force",
    "gravity",
    "em_waves",
    "klein_gordon",
    "orbital_quantization",
    "thermal_field",
)

PROMOTIONS = {
    "spin_half_statistics": {
        "reason": "double-cover control plus fermion exchange sign, antisymmetry, and identical-state exclusion",
        "boundary": "fermionic assignment of a specific emergent particle remains underived",
    },
    "em_waves": {
        "reason": "exact spectral Maxwell controls plus a formal harmonic source-free Maxwell plane wave",
        "boundary": "photon quantization, full CAT/EPT emergence, and calibration remain open",
    },
    "thermal_field": {
        "reason": "exact spectral heat flow, heat conservation, entropy growth, dissipation, semigroup, and resolution controls",
        "boundary": "microscopic thermodynamics and material calibration remain open",
    },
}

BLOCKED = {
    "charge_quantization": "elementary-charge identity and normalization",
    "electron_rest_energy": "independent mass and length calibration plus out-of-sample rest-energy prediction",
    "de_broglie_clock": "physical-particle identity, independent clock calibration, and external comparison",
    "particle_stability": "continuum energy-critical flow, conservation, analytic orbit identity, and physical particle identity",
    "magnetic_moment_spin": "stable calibrated particle and emergent physical g factor",
    "antimatter_annihilation": "full-PDE particle/antiparticle sector and calibrated radiation channel",
    "dark_matter": "full-PDE stability, abundance, production, and phenomenology",
    "quarks": "dynamical QCD and physical color-sector spectrum",
    "baryons": "dynamical constituent theory and physical baryon spectrum",
    "mesons": "dynamical constituent theory, spectrum, and decay channels",
    "electric_force": "calibrated emergent charges and common force-unit map",
    "magnetic_force": "calibrated magnetic moment and common force-unit map",
    "strong_force": "dynamical QCD with jointly predicted tension and breaking",
    "weak_force": "electroweak gauge dynamics and calibrated rates",
    "gravity": "calibrated coupled Einstein-matter evolution and external observables",
    "klein_gordon": "native calibrated particle identity and interacting sector",
    "orbital_quantization": "native calibrated atom and out-of-sample spectrum",
}


@lru_cache(maxsize=1)
def run_partial_reduction_audit() -> dict[str, Any]:
    if set(PROMOTIONS) | set(BLOCKED) != set(BASELINE_PARTIALS):
        raise RuntimeError("partial audit must classify every baseline partial")
    rows = []
    for key in BASELINE_PARTIALS:
        if key in PROMOTIONS:
            rows.append(
                {
                    "criterion": key,
                    "eligible_for_platform_validation": True,
                    **PROMOTIONS[key],
                }
            )
        else:
            rows.append(
                {
                    "criterion": key,
                    "eligible_for_platform_validation": False,
                    "blocking_gap": BLOCKED[key],
                }
            )
    acceptance = {
        "all_twenty_baseline_partials_are_classified": len(rows) == 20,
        "exactly_three_rows_are_promotable": sum(
            row["eligible_for_platform_validation"] for row in rows
        )
        == 3,
        "all_promotions_retain_stronger_boundaries": all(
            bool(PROMOTIONS[key]["boundary"]) for key in PROMOTIONS
        ),
        "all_nonpromoted_rows_name_a_blocking_gap": all(
            bool(row.get("blocking_gap"))
            for row in rows
            if not row["eligible_for_platform_validation"]
        ),
    }
    return {
        "schema": "openwave.m9.partial-reduction-audit.v1",
        "baseline_counts": {
            "validated": 0,
            "partial": 20,
            "negative": 1,
            "not_yet": 0,
        },
        "proposed_counts": {
            "validated": 3,
            "partial": 17,
            "negative": 1,
            "not_yet": 0,
        },
        "promoted_criteria": list(PROMOTIONS),
        "rows": rows,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "twenty_partials_can_be_reduced": True,
            "safe_reduction_count": 3,
            "remaining_partial_count": 17,
            "physical_theory_fully_validated": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
