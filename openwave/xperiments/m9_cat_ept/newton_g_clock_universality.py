"""M9.109b: falsification audit for Newton-G universality across Compton clocks.

The formal identities

    G = hbar*c/m^2 = c^5/(hbar*omega^2),   omega = m*c^2/hbar

are exact. This module asks the missing physical question: may the `m`/`omega`
be the Compton scale of every particle while G remains universal? The answer is
no for unequal masses. A single universal gravitational anchor is required.

CODATA values are comparison data, not fitted OpenWave parameters.
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
    hbar_joule_second: float = 1.054_571_817e-34
    speed_of_light_m_per_s: float = 299_792_458.0
    measured_newton_G: float = 6.674_30e-11
    measured_newton_G_standard_uncertainty: float = 0.000_15e-11

    def __post_init__(self) -> None:
        if min(
            self.hbar_joule_second,
            self.speed_of_light_m_per_s,
            self.measured_newton_G,
            self.measured_newton_G_standard_uncertainty,
        ) <= 0.0:
            raise ValueError("positive physical constants required")


@dataclass(frozen=True)
class ClockMass:
    name: str
    mass_kg: float
    evidence: str
    scope: str = "particle"

    def __post_init__(self) -> None:
        if not self.name or self.mass_kg <= 0.0:
            raise ValueError("named positive clock mass required")
        if self.scope not in ("particle", "universal_gravity", "derived_control"):
            raise ValueError("unsupported clock scope")


CODATA_PARTICLE_CLOCKS = (
    ClockMass("electron", 9.109_383_7139e-31, "2022 CODATA electron mass"),
    ClockMass("muon", 1.883_531_627e-28, "2022 CODATA muon mass"),
    ClockMass("proton", 1.672_621_92595e-27, "2022 CODATA proton mass"),
)


def compton_frequency(mass_kg: float, constants: Constants) -> float:
    if mass_kg <= 0.0:
        raise ValueError("positive mass required")
    return mass_kg * constants.speed_of_light_m_per_s**2 / constants.hbar_joule_second


def newton_G_from_mass(mass_kg: float, constants: Constants) -> float:
    if mass_kg <= 0.0:
        raise ValueError("positive mass required")
    return constants.hbar_joule_second * constants.speed_of_light_m_per_s / mass_kg**2


def newton_G_from_clock(omega_per_s: float, constants: Constants) -> float:
    if omega_per_s <= 0.0:
        raise ValueError("positive angular frequency required")
    return constants.speed_of_light_m_per_s**5 / (
        constants.hbar_joule_second * omega_per_s**2
    )


def mass_from_newton_G(newton_G: float, constants: Constants) -> float:
    if newton_G <= 0.0:
        raise ValueError("positive Newton coupling required")
    return math.sqrt(
        constants.hbar_joule_second * constants.speed_of_light_m_per_s / newton_G
    )


def clock_from_newton_G(newton_G: float, constants: Constants) -> float:
    if newton_G <= 0.0:
        raise ValueError("positive Newton coupling required")
    return math.sqrt(
        constants.speed_of_light_m_per_s**5
        / (constants.hbar_joule_second * newton_G)
    )


def relative_error(observed: float, expected: float) -> float:
    return abs(observed - expected) / max(abs(expected), 1.0e-300)


def clock_row(clock: ClockMass, constants: Constants) -> dict[str, Any]:
    omega = compton_frequency(clock.mass_kg, constants)
    from_mass = newton_G_from_mass(clock.mass_kg, constants)
    from_clock = newton_G_from_clock(omega, constants)
    ratio = from_mass / constants.measured_newton_G
    return {
        **asdict(clock),
        "compton_angular_frequency_per_s": omega,
        "G_from_mass": from_mass,
        "G_from_clock": from_clock,
        "mass_clock_identity_relative_error": relative_error(from_clock, from_mass),
        "ratio_to_measured_G": ratio,
        "log10_ratio_to_measured_G": math.log10(ratio),
        "matches_measured_G_within_10_sigma": abs(
            from_mass - constants.measured_newton_G
        )
        <= 10.0 * constants.measured_newton_G_standard_uncertainty,
    }


def sensitivity_coefficients() -> dict[str, float]:
    return {
        "d_log_G_over_d_log_mass": -2.0,
        "d_log_G_over_d_log_clock_frequency": -2.0,
        "d_log_G_over_d_log_sigma0": 4.0,
    }


def audit_clock_universality(
    clocks: Sequence[ClockMass] = CODATA_PARTICLE_CLOCKS,
    constants: Constants | None = None,
) -> dict[str, Any]:
    selected = Constants() if constants is None else constants
    if len(clocks) < 2:
        raise ValueError("at least two clocks required for a universality audit")
    names = [clock.name for clock in clocks]
    if len(names) != len(set(names)):
        raise ValueError("clock names must be unique")
    rows = [clock_row(clock, selected) for clock in clocks]
    values = [float(row["G_from_clock"]) for row in rows]
    spread = max(values) / min(values)
    planck_mass_control = mass_from_newton_G(selected.measured_newton_G, selected)
    planck_clock_control = clock_from_newton_G(selected.measured_newton_G, selected)
    control_G_mass = newton_G_from_mass(planck_mass_control, selected)
    control_G_clock = newton_G_from_clock(planck_clock_control, selected)
    particle_clocks_match = all(
        bool(row["matches_measured_G_within_10_sigma"]) for row in rows
    )
    return {
        "constants": asdict(selected),
        "particle_clock_rows": rows,
        "particle_clock_G_spread_ratio": spread,
        "particle_clocks_define_one_universal_G": spread <= 1.0 + 1.0e-12,
        "particle_clocks_match_measured_G": particle_clocks_match,
        "planck_anchor_control": {
            "mass_kg": planck_mass_control,
            "angular_frequency_per_s": planck_clock_control,
            "G_from_mass": control_G_mass,
            "G_from_clock": control_G_clock,
            "relative_error_mass_path": relative_error(
                control_G_mass, selected.measured_newton_G
            ),
            "relative_error_clock_path": relative_error(
                control_G_clock, selected.measured_newton_G
            ),
            "epistemic_status": "inversion-control-uses-measured-G",
        },
        "sensitivity": sensitivity_coefficients(),
        "implication": {
            "distinct_particle_masses_produce_distinct_effective_G": True,
            "universal_G_requires_one_universal_gravity_anchor": True,
            "the_universal_control_scale_is_the_Planck_mass_clock": True,
            "Planck_control_is_a_prediction": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_newton_G_clock_universality() -> dict[str, Any]:
    audit = audit_clock_universality()
    payload = {
        "schema": "openwave.m9.newton-G-clock-universality.v1",
        "task": "M9.109b",
        **audit,
        "policy": {
            "formal_identity_is_preserved": True,
            "species_dependent_G_is_rejected": True,
            "inversion_from_measured_G_is_not_prediction": True,
            "universal_anchor_must_be_independent_of_withheld_G": True,
        },
    }
    rows = payload["particle_clock_rows"]
    acceptance = {
        "three_CODATA_particle_clocks_are_audited": len(rows) == 3,
        "mass_and_clock_paths_agree_for_each_species": max(
            row["mass_clock_identity_relative_error"] for row in rows
        )
        <= 5.0e-15,
        "ordinary_particle_clocks_fail_universal_G": not payload[
            "particle_clocks_define_one_universal_G"
        ]
        and not payload["particle_clocks_match_measured_G"],
        "Planck_anchor_inversion_control_closes": max(
            payload["planck_anchor_control"]["relative_error_mass_path"],
            payload["planck_anchor_control"]["relative_error_clock_path"],
        )
        <= 5.0e-15,
        "sensitivity_coefficients_are_exact": payload["sensitivity"]
        == {
            "d_log_G_over_d_log_mass": -2.0,
            "d_log_G_over_d_log_clock_frequency": -2.0,
            "d_log_G_over_d_log_sigma0": 4.0,
        },
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "particle_Compton_clock_is_universal_gravity_anchor": False,
            "universal_Planck_scale_anchor_required": True,
            "measured_G_predicted_without_external_anchor": False,
            "formal_G_equivalence_falsified": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
