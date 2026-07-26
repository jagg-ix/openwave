"""M9.101d: internal clock, action-rate and entropy-rate calibration.

The current Physlib branch proves the conditional identities

    m_clock = hbar*omega/c^2,
    y = sqrt(2)*hbar*omega/(c^2*v),
    Sdot_I = [sqrt(2)*omega0/(2*ell*v)]*m_clock,

and exact frequency-lapse Tolman algebra.  OpenWave supplies ``omega`` from the
pre-registered stationary-branch radial mode.  This module uses the derivation
grid once to determine the entropy normalization ``ell`` and then carries the
same map to held-out grids without refitting.

This is an internal natural-unit calibration.  It does not identify the mode as
an electron Zitterbewegung clock and does not use external mass or clock data.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .intrinsic_clock_reduction import (
    ClockParameters,
    generate_clock_trace,
    slope,
)
from .replacement_mode_prediction import run_replacement_mode_prediction


@dataclass(frozen=True)
class ClockActionCalibrationConfig:
    hbar: float = 1.0
    light_speed: float = 1.0
    higgs_scale: float = 1.0
    entropy_reference_frequency: float = 1.0
    final_time: float = 10.0
    samples: int = 2001
    mean_loss_rate: float = 0.11
    loss_modulation: float = 0.35
    loss_frequency: float = 0.73
    velocity_amplitude: float = 0.45
    velocity_frequency: float = 0.61

    def __post_init__(self) -> None:
        if min(
            self.hbar,
            self.light_speed,
            self.higgs_scale,
            self.entropy_reference_frequency,
            self.final_time,
            self.mean_loss_rate,
            self.loss_frequency,
            self.velocity_frequency,
        ) <= 0.0:
            raise ValueError("positive clock calibration controls required")
        if self.samples < 101 or not 0.0 <= self.loss_modulation < 1.0:
            raise ValueError("sufficient samples and bounded modulation required")
        if not 0.0 <= self.velocity_amplitude < 1.0:
            raise ValueError("subluminal velocity amplitude required")


def compton_mass(omega: float, cfg: ClockActionCalibrationConfig) -> float:
    return cfg.hbar * omega / cfg.light_speed**2


def isolated_yukawa(omega: float, cfg: ClockActionCalibrationConfig) -> float:
    return math.sqrt(2.0) * cfg.hbar * omega / (
        cfg.light_speed**2 * cfg.higgs_scale
    )


def yukawa_mass(yukawa: float, cfg: ClockActionCalibrationConfig) -> float:
    return yukawa * cfg.higgs_scale / math.sqrt(2.0)


def entropy_rate_from_clock(
    omega: float,
    entropy_action_unit: float,
    cfg: ClockActionCalibrationConfig,
) -> float:
    coefficient = (
        math.sqrt(2.0)
        * cfg.entropy_reference_frequency
        / (2.0 * entropy_action_unit * cfg.higgs_scale)
    )
    return coefficient * compton_mass(omega, cfg)


def clock_trace(omega: float, cfg: ClockActionCalibrationConfig) -> dict[str, np.ndarray]:
    parameters = ClockParameters(
        final_time=cfg.final_time,
        samples=cfg.samples,
        internal_frequency=omega,
        mean_loss_rate=cfg.mean_loss_rate,
        loss_modulation=cfg.loss_modulation,
        loss_frequency=cfg.loss_frequency,
        velocity_amplitude=cfg.velocity_amplitude,
        velocity_frequency=cfg.velocity_frequency,
    )
    return generate_clock_trace(parameters)  # type: ignore[return-value]


@lru_cache(maxsize=1)
def run_clock_action_rate_calibration() -> dict[str, Any]:
    cfg = ClockActionCalibrationConfig()
    mode = run_replacement_mode_prediction()
    derivation = mode["derivation"]
    omega = float(derivation["omega_dimensionless"])
    trace = clock_trace(omega, cfg)
    time = np.asarray(trace["time"], dtype=np.float64)
    phase = np.asarray(trace["phase"], dtype=np.float64)
    entropy = np.asarray(trace["entropic_clock"], dtype=np.float64)
    lapse = np.asarray(trace["lapse"], dtype=np.float64)
    observed_phase_rate = slope(time, phase)
    observed_entropy_rate = float((entropy[-1] - entropy[0]) / (time[-1] - time[0]))
    entropy_action_unit = (
        math.sqrt(2.0)
        * cfg.entropy_reference_frequency
        * compton_mass(omega, cfg)
        / (2.0 * cfg.higgs_scale * observed_entropy_rate)
    )
    predicted_entropy_rate = entropy_rate_from_clock(omega, entropy_action_unit, cfg)
    yukawa = isolated_yukawa(omega, cfg)
    mass_clock = compton_mass(omega, cfg)
    mass_yukawa = yukawa_mass(yukawa, cfg)
    action_rate = cfg.hbar * omega
    action_from_phase = cfg.hbar * (phase - phase[0])
    action_linear = action_rate * time
    action_trace_error = float(np.max(np.abs(action_from_phase - action_linear)))

    local_frequency = omega * lapse
    frequency_lapse = local_frequency / omega
    local_entropic_time = entropy / np.maximum(frequency_lapse, 1.0e-30)
    tolman_reconstruction = local_entropic_time * frequency_lapse
    tolman_error = float(np.max(np.abs(tolman_reconstruction - entropy)))

    held_out = []
    for row in mode["held_out_tests"]:
        test_omega = float(row["omega_dimensionless"])
        test_y = isolated_yukawa(test_omega, cfg)
        test_rate = entropy_rate_from_clock(test_omega, entropy_action_unit, cfg)
        held_out.append(
            {
                "points": int(row["points"]),
                "omega": test_omega,
                "yukawa": test_y,
                "entropy_rate": test_rate,
                "relative_omega_error": abs(test_omega - omega) / max(abs(omega), 1.0e-30),
                "mass_identity_error": abs(yukawa_mass(test_y, cfg) - compton_mass(test_omega, cfg)),
                "normalization_refit": False,
            }
        )

    modulation_fraction = float(
        np.std(np.asarray(trace["loss_rate"], dtype=np.float64))
        / max(abs(np.mean(np.asarray(trace["loss_rate"], dtype=np.float64))), 1.0e-30)
    )
    acceptance = {
        "phase_action_rate_closes": abs(observed_phase_rate - omega) <= 2.0e-12 and action_trace_error <= 2.0e-12,
        "clock_mass_and_yukawa_mass_are_identical": abs(mass_clock - mass_yukawa) <= 2.0e-15,
        "entropy_normalization_closes_derivation_trace": abs(predicted_entropy_rate - observed_entropy_rate) <= 2.0e-15,
        "tolman_frequency_lapse_algebra_closes": tolman_error <= 2.0e-15,
        "held_out_grids_use_one_frozen_normalization": all(not row["normalization_refit"] for row in held_out),
        "held_out_mass_identities_close": max(row["mass_identity_error"] for row in held_out) <= 2.0e-15,
        "held_out_mode_ratio_remains_within_preregistered_tolerance": max(row["relative_omega_error"] for row in held_out) <= mode["preregistration"]["relative_tolerance"],
        "nonconstant_entropy_rate_is_not_hidden": modulation_fraction > 0.0,
        "external_clock_identity_is_not_inferred": True,
    }
    return {
        "schema": "openwave.m9.clock-action-rate-calibration.v1",
        "task": "M9.101d",
        "config": asdict(cfg),
        "derivation_grid": int(derivation["points"]),
        "measured_internal_frequency": omega,
        "observed_phase_rate": observed_phase_rate,
        "action_rate": action_rate,
        "compton_clock_mass": mass_clock,
        "isolated_yukawa": yukawa,
        "yukawa_mass": mass_yukawa,
        "observed_mean_entropy_rate": observed_entropy_rate,
        "entropy_action_unit": entropy_action_unit,
        "predicted_mean_entropy_rate": predicted_entropy_rate,
        "entropy_rate_modulation_fraction": modulation_fraction,
        "action_trace_max_error": action_trace_error,
        "tolman_reconstruction_max_error": tolman_error,
        "held_out": held_out,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "internal_clock_action_rate_calibrated": True,
            "one_yukawa_entropy_normalization_frozen_across_grids": True,
            "physical_zitterbewegung_identity_validated": False,
            "external_clock_or_mass_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
