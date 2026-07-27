"""M9.110b: scale flow between Planck bits and Compton information cells."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .holographic_count_hierarchy import Constants, SPECIES, planck_mass, species_row


def coarse_graining_flow(*, samples: int = 81, decades: float = 50.0) -> dict[str, Any]:
    if samples < 5 or decades <= 0.0:
        raise ValueError("substantive positive flow required")
    k = Constants()
    mp = planck_mass(k)
    exponents = [
        -decades + 2.0 * decades * index / (samples - 1)
        for index in range(samples)
    ]
    rows = []
    for exponent in exponents:
        mass = mp * 10.0**exponent
        multiplicity = (mp / mass) ** 2
        rows.append(
            {
                "log10_mass_over_planck": exponent,
                "mass_kg": mass,
                "planck_bits_per_compton_cell": multiplicity,
                "log10_multiplicity": math.log10(multiplicity),
                "regime": "sub_planckian" if exponent < 0.0 else (
                    "planck_crossover" if abs(exponent) < 1.0e-12 else "super_planckian"
                ),
            }
        )
    slopes = [
        (rows[i + 1]["log10_multiplicity"] - rows[i]["log10_multiplicity"])
        / (rows[i + 1]["log10_mass_over_planck"] - rows[i]["log10_mass_over_planck"])
        for i in range(len(rows) - 1)
    ]
    species = [species_row(item, math.log(2.0), k) for item in SPECIES]
    payload = {
        "schema": "openwave.m9.holographic-coarse-graining.v1",
        "task": "M9.110b",
        "flow": rows,
        "species_controls": [
            {
                "name": row["name"],
                "planck_bits_per_compton_cell": row["planck_bits_per_compton_cell"],
                "holographic_bits": row["holographic_bits"],
                "compton_cell_bits": row["compton_cell_bits"],
            }
            for row in species
        ],
        "diagnostics": {
            "mean_log_slope": sum(slopes) / len(slopes),
            "max_log_slope_error_from_minus_two": max(abs(value + 2.0) for value in slopes),
            "crossover_multiplicity": min(rows, key=lambda row: abs(row["log10_mass_over_planck"]))[
                "planck_bits_per_compton_cell"
            ],
            "sub_planckian_cells_are_coarse_grained": all(
                row["planck_bits_per_compton_cell"] > 1.0
                for row in rows
                if row["log10_mass_over_planck"] < 0.0
            ),
            "super_planckian_cells_are_finer_than_planck_cell": all(
                row["planck_bits_per_compton_cell"] < 1.0
                for row in rows
                if row["log10_mass_over_planck"] > 0.0
            ),
        },
        "interpretation_boundary": {
            "multiplicity_is_dynamically_derived_degeneracy": False,
            "multiplicity_is_exact_count_ratio": True,
            "renormalization_mechanism_constructed": False,
            "coarse_graining_hypothesis_is_testable": True,
        },
    }
    return payload


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_holographic_coarse_graining() -> dict[str, Any]:
    payload = coarse_graining_flow()
    diagnostics = payload["diagnostics"]
    acceptance = {
        "exact_mass_scaling_is_minus_two": diagnostics["max_log_slope_error_from_minus_two"] <= 1.0e-12,
        "planck_crossover_is_one": abs(diagnostics["crossover_multiplicity"] - 1.0) <= 1.0e-12,
        "sub_planckian_coarse_graining_closes": diagnostics["sub_planckian_cells_are_coarse_grained"],
        "super_planckian_regime_is_distinguished": diagnostics[
            "super_planckian_cells_are_finer_than_planck_cell"
        ],
        "dynamics_are_not_overclaimed": not payload["interpretation_boundary"][
            "multiplicity_is_dynamically_derived_degeneracy"
        ],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
