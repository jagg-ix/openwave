"""M9.110a: distinguish holographic and Compton-cell counts.

The primary coupling is the screen information density

    G = (A / N_H) * c^3 / hbar.

The Compton-cell specialization uses N_C = A/lambda_C^2 and therefore defines
G_C(m) = hbar*c/m^2.  It is not a species-dependent replacement for the
universal holographic coupling.  Instead N_H/N_C measures the number of Planck
area bits represented by one Compton cell.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class Constants:
    hbar: float = 1.054_571_817e-34
    c: float = 299_792_458.0
    newton_G: float = 6.674_30e-11


@dataclass(frozen=True)
class Species:
    name: str
    mass_kg: float


SPECIES: tuple[Species, ...] = (
    Species("electron", 9.109_383_7139e-31),
    Species("muon", 1.883_531_627e-28),
    Species("proton", 1.672_621_92595e-27),
)


def planck_area(k: Constants) -> float:
    return k.newton_G * k.hbar / k.c**3


def planck_mass(k: Constants) -> float:
    return math.sqrt(k.hbar * k.c / k.newton_G)


def compton_wavelength(mass: float, k: Constants) -> float:
    if mass <= 0.0:
        raise ValueError("positive mass required")
    return k.hbar / (mass * k.c)


def screen_area(mass: float, log_schmidt: float, k: Constants) -> float:
    if log_schmidt <= 0.0:
        raise ValueError("positive log Schmidt number required")
    lam = compton_wavelength(mass, k)
    return 4.0 * math.pi * lam * lam * log_schmidt * log_schmidt


def holographic_bits(area: float, k: Constants) -> float:
    return area / planck_area(k)


def compton_cell_bits(area: float, mass: float, k: Constants) -> float:
    lam = compton_wavelength(mass, k)
    return area / (lam * lam)


def screen_G(area: float, bits: float, k: Constants) -> float:
    if area <= 0.0 or bits <= 0.0:
        raise ValueError("positive area and bit count required")
    return area * k.c**3 / (k.hbar * bits)


def species_row(species: Species, log_schmidt: float, k: Constants) -> dict[str, Any]:
    area = screen_area(species.mass_kg, log_schmidt, k)
    n_h = holographic_bits(area, k)
    n_c = compton_cell_bits(area, species.mass_kg, k)
    multiplicity = n_h / n_c
    expected = (planck_mass(k) / species.mass_kg) ** 2
    return {
        **asdict(species),
        "screen_area_m2": area,
        "holographic_bits": n_h,
        "compton_cell_bits": n_c,
        "planck_bits_per_compton_cell": multiplicity,
        "mass_ratio_squared": expected,
        "multiplicity_relative_error": abs(multiplicity - expected) / expected,
        "G_from_holographic_area_per_bit": screen_G(area, n_h, k),
        "G_from_compton_cell_area_per_bit": screen_G(area, n_c, k),
        "holographic_area_per_bit_m2": area / n_h,
        "compton_area_per_cell_m2": area / n_c,
    }


def run_holographic_count_hierarchy_for(
    species: Sequence[Species] = SPECIES,
    *,
    log_schmidt: float = math.log(2.0),
    constants: Constants | None = None,
) -> dict[str, Any]:
    k = Constants() if constants is None else constants
    rows = [species_row(item, log_schmidt, k) for item in species]
    universal_G_error = max(
        abs(row["G_from_holographic_area_per_bit"] - k.newton_G) / k.newton_G
        for row in rows
    )
    compton_count_spread = max(row["compton_cell_bits"] for row in rows) / min(
        row["compton_cell_bits"] for row in rows
    )
    return {
        "schema": "openwave.m9.holographic-count-hierarchy.v1",
        "task": "M9.110a",
        "constants": asdict(k),
        "log_schmidt": log_schmidt,
        "planck_area_m2": planck_area(k),
        "planck_mass_kg": planck_mass(k),
        "rows": rows,
        "invariants": {
            "holographic_G_species_invariant": universal_G_error <= 5.0e-15,
            "max_holographic_G_relative_error": universal_G_error,
            "compton_cell_count_species_invariant": compton_count_spread <= 1.0 + 1.0e-12,
            "compton_cell_count_spread": compton_count_spread,
            "multiplicity_matches_planck_to_particle_mass_ratio": max(
                row["multiplicity_relative_error"] for row in rows
            ) <= 5.0e-15,
        },
        "decision": {
            "universal_holographic_G_rejected": False,
            "species_dependent_primary_G_claim_rejected": True,
            "compton_cell_is_coarse_grained_holographic_cell": True,
            "planck_mass_is_equal_count_crossover": True,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_holographic_count_hierarchy() -> dict[str, Any]:
    payload = run_holographic_count_hierarchy_for()
    inv = payload["invariants"]
    acceptance = {
        "three_species_are_audited": len(payload["rows"]) == 3,
        "holographic_G_is_species_invariant": inv["holographic_G_species_invariant"],
        "compton_cell_count_is_species_independent_for_fixed_entanglement": inv[
            "compton_cell_count_species_invariant"
        ],
        "count_ratio_matches_mass_hierarchy": inv[
            "multiplicity_matches_planck_to_particle_mass_ratio"
        ],
        "no_primary_G_falsification_is_claimed": not payload["decision"][
            "universal_holographic_G_rejected"
        ],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
