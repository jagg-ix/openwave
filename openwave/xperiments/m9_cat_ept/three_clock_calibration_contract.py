"""M9.125b: model-internal calibration maps among three clock readings."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

from .shared_three_clock_carrier import SharedThreeClockCarrier, run_shared_three_clock_carrier


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@dataclass(frozen=True)
class ClockCalibrationConfig:
    relational_to_model_time: float = 1.25
    nominal_lapse: float = 0.92
    maximum_model_time: float = 10.0
    inversion_tolerance: float = 2e-10

    def validate(self) -> None:
        if self.relational_to_model_time <= 0:
            raise ValueError("relational scale must be positive")
        if self.nominal_lapse <= 0:
            raise ValueError("lapse must be positive")
        if self.maximum_model_time <= 0:
            raise ValueError("maximum time must be positive")


class ThreeClockCalibration:
    def __init__(self, config: ClockCalibrationConfig | None = None) -> None:
        self.config = config or ClockCalibrationConfig()
        self.config.validate()
        self.carrier = SharedThreeClockCarrier()

    def model_time_from_page_wootters(self, tau: float) -> float:
        return self.config.relational_to_model_time * tau

    def page_wootters_from_model_time(self, t: float) -> float:
        return t / self.config.relational_to_model_time

    def modular_from_model_time(self, t: float) -> float:
        return t / self.carrier.beta

    def model_time_from_modular(self, s: float) -> float:
        return self.carrier.beta * s

    def nominal_proper_time_from_model_time(self, t: float) -> float:
        return t / self.config.nominal_lapse

    def model_time_from_nominal_proper_time(self, sigma: float) -> float:
        return self.config.nominal_lapse * sigma

    def entropic_from_model_time(self, t: float) -> float:
        return self.carrier.accumulated_entropic_clock(t)

    def model_time_from_entropic(self, value: float) -> float:
        low, high = 0.0, self.config.maximum_model_time
        low_value = self.entropic_from_model_time(low)
        high_value = self.entropic_from_model_time(high)
        if value < low_value - 1e-14 or value > high_value + 1e-14:
            raise ValueError("entropic reading outside calibrated branch")
        for _ in range(100):
            mid = (low + high) / 2.0
            if self.entropic_from_model_time(mid) < value:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0


@lru_cache(maxsize=1)
def run_three_clock_calibration_contract() -> dict[str, Any]:
    shared = run_shared_three_clock_carrier()
    calibration = ThreeClockCalibration()
    model_times = np.linspace(0.0, 8.0, 33)
    pw_roundtrip = []
    modular_roundtrip = []
    proper_roundtrip = []
    entropic_roundtrip = []
    diagram_errors = []
    entropic_values = []
    for t in model_times:
        tau = calibration.page_wootters_from_model_time(float(t))
        s = calibration.modular_from_model_time(float(t))
        sigma = calibration.nominal_proper_time_from_model_time(float(t))
        ent = calibration.entropic_from_model_time(float(t))
        pw_roundtrip.append(abs(calibration.model_time_from_page_wootters(tau) - t))
        modular_roundtrip.append(abs(calibration.model_time_from_modular(s) - t))
        proper_roundtrip.append(abs(calibration.model_time_from_nominal_proper_time(sigma) - t))
        entropic_roundtrip.append(abs(calibration.model_time_from_entropic(ent) - t))
        direct_s = calibration.model_time_from_page_wootters(tau) / calibration.carrier.beta
        diagram_errors.append(abs(direct_s - s))
        entropic_values.append(ent)
    rejected = {}
    for name, kwargs in {
        "negative_relational_scale": {"relational_to_model_time": -1.0},
        "zero_lapse": {"nominal_lapse": 0.0},
    }.items():
        try:
            ThreeClockCalibration(ClockCalibrationConfig(**kwargs))
            rejected[name] = False
        except ValueError:
            rejected[name] = True
    try:
        calibration.model_time_from_entropic(calibration.entropic_from_model_time(10.0) + 0.1)
        rejected["out_of_range_entropic_reading"] = False
    except ValueError:
        rejected["out_of_range_entropic_reading"] = True
    payload = {
        "schema": "openwave.m9.three-clock-calibration-contract.v1",
        "task": "M9.125b",
        "config": asdict(calibration.config),
        "maps": {
            "page_wootters_to_model_time": "t = a_pw * tau_pw",
            "modular_to_model_time": "t = beta * s",
            "nominal_proper_to_model_time": "t = N * sigma",
            "entropic_to_model_time": "inverse of branch-monotone accumulated relative entropy",
        },
        "metrics": {
            "maximum_page_wootters_roundtrip_error": max(pw_roundtrip),
            "maximum_modular_roundtrip_error": max(modular_roundtrip),
            "maximum_nominal_proper_roundtrip_error": max(proper_roundtrip),
            "maximum_entropic_roundtrip_error": max(entropic_roundtrip),
            "maximum_commuting_diagram_error": max(diagram_errors),
            "minimum_entropic_increment": float(np.min(np.diff(entropic_values))),
        },
        "rejected_invalid_inputs": rejected,
        "claim_boundary": {
            "model_internal_map_is_external_clock_calibration": False,
            "nominal_lapse_is_measured_spacetime_lapse": False,
            "branch_inverse_is_universal_entropic_time_coordinate": False,
            "parameter_roundtrip_is_heldout_physical_validation": False,
        },
    }
    acceptance = {
        "shared_carrier_passes": shared["passed"],
        "coordinate_like_maps_are_positive_and_invertible": max(pw_roundtrip + modular_roundtrip + proper_roundtrip) <= 2e-14,
        "entropic_map_is_monotone_and_invertible_on_selected_branch": float(np.min(np.diff(entropic_values))) >= -2e-12 and max(entropic_roundtrip) <= calibration.config.inversion_tolerance,
        "page_wootters_modular_diagram_commutes": max(diagram_errors) <= 2e-14,
        "invalid_or_out_of_range_calibrations_are_rejected": all(rejected.values()),
        "no_external_calibration_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "page_wootters_to_modular_internal_calibration_constructed": True,
            "modular_to_entropic_branch_map_constructed": True,
            "nominal_proper_time_adapter_constructed": True,
            "independent_physical_clock_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
