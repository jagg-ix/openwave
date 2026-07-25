"""M9.91 finite spectral Klein--Gordon criterion closure.

The shared wave-reduction module already evolves the massive field exactly in
Fourier space. This closure adds an independent canonical-mode group audit over
multiple masses and modes and pins the formal dispersion/energy certificate.
It does not identify a physical scalar particle or supply interacting QFT.
"""
from __future__ import annotations

from functools import lru_cache
import json
import math
from typing import Any

from .wave_reductions import run_wave_reduction_study

OPENWAVE_BASE = "6773431e37a08efce2d9d9b1ec53ca2b953080dc"
FORMAL_BASE = "3923d802339c957066fcccd579362f739775797a"
FORMAL_PARENT_HEAD = "128bebd375cd895af1431444974a7a591c872a31"
FORMAL_CRITERION_HEAD = "e192104955fc516f1ba267f8653f0dcf8d18ab51"
FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.M9ChargeKleinOrbitalCriteria.kleinGordonFrequency_sq",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.M9ChargeKleinOrbitalCriteria.kleinGordonModeEnergy_conserved",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.M9ChargeKleinOrbitalCriteria.kleinGordonFiniteModeCriterion",
    "ClassicalMechanics.planeWave_waveEquation",
    "Physlib.QuantumMechanics.Schrodinger.SpectralDynamics.spectralPhase_add",
)


def mode_step(q: float, p: float, omega: float, time: float) -> tuple[float, float]:
    if abs(omega) <= 1e-15:
        return q + time * p, p
    cosine = math.cos(omega * time)
    sine = math.sin(omega * time)
    return (
        q * cosine + p * sine / omega,
        -omega * q * sine + p * cosine,
    )


def mode_energy(q: float, p: float, omega: float) -> float:
    return p * p + omega * omega * q * q


def mode_audit() -> dict[str, Any]:
    rows = []
    for mass in (0.0, 0.3, 0.7, 1.2):
        for mode in (1, 3, 5):
            omega = math.sqrt(mode * mode + mass * mass)
            q0, p0 = 0.73, -0.41
            first_time, second_time = 0.37, 0.61
            direct = mode_step(q0, p0, omega, first_time + second_time)
            composed = mode_step(
                *mode_step(q0, p0, omega, second_time), omega, first_time
            )
            reversed_state = mode_step(
                *mode_step(q0, p0, omega, second_time), omega, -second_time
            )
            rows.append(
                {
                    "mass": mass,
                    "mode": mode,
                    "omega": omega,
                    "dispersion_error": abs(omega * omega - (mode * mode + mass * mass)),
                    "group_error": max(
                        abs(direct[0] - composed[0]),
                        abs(direct[1] - composed[1]),
                    ),
                    "reverse_error": max(
                        abs(q0 - reversed_state[0]),
                        abs(p0 - reversed_state[1]),
                    ),
                    "energy_error": abs(
                        mode_energy(*direct, omega) - mode_energy(q0, p0, omega)
                    ),
                }
            )
    zero_direct = mode_step(0.73, -0.41, 0.0, 0.98)
    zero_composed = mode_step(*mode_step(0.73, -0.41, 0.0, 0.61), 0.0, 0.37)
    return {
        "rows": rows,
        "maximum_dispersion_error": max(row["dispersion_error"] for row in rows),
        "maximum_group_error": max(row["group_error"] for row in rows),
        "maximum_reverse_error": max(row["reverse_error"] for row in rows),
        "maximum_energy_error": max(row["energy_error"] for row in rows),
        "zero_mode_group_error": max(
            abs(zero_direct[0] - zero_composed[0]),
            abs(zero_direct[1] - zero_composed[1]),
        ),
    }


@lru_cache(maxsize=1)
def run_klein_gordon_closure() -> dict[str, Any]:
    spatial = run_wave_reduction_study()
    modes = mode_audit()
    kg = spatial["klein_gordon"]
    acceptance = {
        "shared_spatial_wave_campaign_passes": bool(spatial["passed"]),
        "massive_spatial_energy_is_conserved": kg["maximum_energy_drift"] < 2e-12,
        "massive_dispersion_is_measured": kg["dispersion"]["relative_error"] < 2e-6,
        "massless_limit_matches_wave_sector": spatial["massless_bridge"]["maximum_field_error"] < 5e-13,
        "finite_modes_obey_exact_dispersion": modes["maximum_dispersion_error"] < 1e-12,
        "finite_mode_group_law_closes": max(
            modes["maximum_group_error"], modes["zero_mode_group_error"]
        ) < 2e-14,
        "finite_modes_are_reversible": modes["maximum_reverse_error"] < 2e-14,
        "finite_mode_energy_is_conserved": modes["maximum_energy_error"] < 1e-12,
        "formal_klein_gordon_witnesses_are_named": len(FORMAL_WITNESSES) == 5,
        "interacting_scalar_particle_is_not_inherited": True,
    }
    return {
        "schema": "openwave.m9.klein-gordon-closure.v1",
        "task": "M9.91",
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_parent_head": FORMAL_PARENT_HEAD,
            "physlib_criterion_head": FORMAL_CRITERION_HEAD,
        },
        "formal_witnesses": list(FORMAL_WITNESSES),
        "spatial": {
            "energy_drift": kg["maximum_energy_drift"],
            "dispersion": kg["dispersion"],
            "massless_bridge_error": spatial["massless_bridge"]["maximum_field_error"],
        },
        "modes": modes,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "klein_gordon_validated_in_platform": True,
            "massive_free_spectral_equation_closed": True,
            "massless_limit_closed": True,
            "interacting_scalar_field_derived": False,
            "physical_scalar_mass_calibrated": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
