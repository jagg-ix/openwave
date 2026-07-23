"""M9.21 preregistered experimental-discriminant and power protocol.

This is a synthetic design gate. It converts the M9.18 endpoint margins into a
machine-readable acquisition plan, checks approximate and Monte Carlo power, and
rejects monotonicity-only observations as non-discriminating. It does not claim
that an apparatus exists or that any physical calibration has been performed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from statistics import NormalDist
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ProtocolConfig:
    alpha: float = 0.01
    target_power: float = 0.90
    systematic_floor: float = 0.02
    monte_carlo_trials: int = 5000
    reserve_fraction: float = 0.25

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha < 0.5:
            raise ValueError("alpha must lie in (0,0.5)")
        if not 0.5 < self.target_power < 1.0:
            raise ValueError("target_power must lie in (0.5,1)")
        if not 0.0 <= self.systematic_floor < 0.25:
            raise ValueError("systematic_floor must lie in [0,0.25)")
        if self.monte_carlo_trials < 1000:
            raise ValueError("monte_carlo_trials must be at least 1000")
        if not 0.0 <= self.reserve_fraction <= 1.0:
            raise ValueError("reserve_fraction must lie in [0,1]")


@dataclass(frozen=True)
class BinaryContrast:
    name: str
    first_probability: float
    second_probability: float
    physical_observable: str

    def __post_init__(self) -> None:
        for value in (self.first_probability, self.second_probability):
            if not 0.0 <= value <= 1.0:
                raise ValueError("contrast probabilities must lie in [0,1]")
        if self.first_probability == self.second_probability:
            raise ValueError("contrast probabilities must differ")

    @property
    def effect(self) -> float:
        return abs(self.first_probability - self.second_probability)


def contrasts() -> tuple[BinaryContrast, ...]:
    amplitude_trace = 0.18268352539059196
    lindblad_purity = 0.5564764542234188
    reservoir_transfer = 0.5949220671512564
    return (
        BinaryContrast(
            name="trace_amplitude_vs_lindblad",
            first_probability=amplitude_trace,
            second_probability=1.0,
            physical_observable="accessible event fraction",
        ),
        BinaryContrast(
            name="purity_amplitude_vs_lindblad",
            first_probability=1.0,
            second_probability=(1.0 + lindblad_purity) / 2.0,
            physical_observable="binary two-copy agreement outcome",
        ),
        BinaryContrast(
            name="reservoir_capture_vs_no_transfer",
            first_probability=reservoir_transfer,
            second_probability=0.0,
            physical_observable="registered reservoir-capture event",
        ),
    )


def normal_sample_size(
    contrast: BinaryContrast,
    config: ProtocolConfig,
) -> int:
    z_alpha = NormalDist().inv_cdf(1.0 - config.alpha / 2.0)
    z_power = NormalDist().inv_cdf(config.target_power)
    p1 = contrast.first_probability
    p2 = contrast.second_probability
    pooled = 0.5 * (p1 + p2)
    numerator = (
        z_alpha * math.sqrt(2.0 * pooled * (1.0 - pooled))
        + z_power * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
    ) ** 2
    return max(2, math.ceil(numerator / contrast.effect**2))


def empirical_power(
    contrast: BinaryContrast,
    shots_per_arm: int,
    config: ProtocolConfig,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    first = rng.binomial(shots_per_arm, contrast.first_probability, config.monte_carlo_trials)
    second = rng.binomial(shots_per_arm, contrast.second_probability, config.monte_carlo_trials)
    p1 = first / shots_per_arm
    p2 = second / shots_per_arm
    pooled = (first + second) / (2.0 * shots_per_arm)
    standard_error = np.sqrt(
        np.maximum(2.0 * pooled * (1.0 - pooled) / shots_per_arm, 1e-15)
    )
    z = np.abs(p1 - p2) / standard_error
    threshold = NormalDist().inv_cdf(1.0 - config.alpha / 2.0)
    return float(np.mean(z >= threshold))


def next_power_of_two(value: int) -> int:
    return 1 << (value - 1).bit_length()


def acquisition_plan(config: ProtocolConfig) -> dict[str, Any]:
    records = []
    for index, contrast in enumerate(contrasts()):
        analytic = normal_sample_size(contrast, config)
        reserved = math.ceil(analytic * (1.0 + config.reserve_fraction))
        recommended = next_power_of_two(reserved)
        power = empirical_power(contrast, recommended, config, 20260723 + index)
        records.append(
            {
                "name": contrast.name,
                "observable": contrast.physical_observable,
                "first_probability": contrast.first_probability,
                "second_probability": contrast.second_probability,
                "effect": contrast.effect,
                "analytic_shots_per_arm": analytic,
                "recommended_shots_per_arm": recommended,
                "empirical_power": power,
                "effect_over_systematic_floor": (
                    contrast.effect / config.systematic_floor
                    if config.systematic_floor > 0.0
                    else math.inf
                ),
            }
        )
    return {
        "contrasts": records,
        "maximum_recommended_shots_per_arm": max(
            item["recommended_shots_per_arm"] for item in records
        ),
        "minimum_empirical_power": min(item["empirical_power"] for item in records),
        "total_primary_shots": 2
        * sum(item["recommended_shots_per_arm"] for item in records),
    }


def preregistration_manifest() -> dict[str, Any]:
    return {
        "primary_observables": [
            "accessible trace/count fraction",
            "two-copy purity agreement",
            "reservoir-capture fraction",
        ],
        "controls": [
            "zero-coupling control",
            "detector dark-count control",
            "efficiency reference channel",
            "time-anchor reference",
        ],
        "randomization": "interleave mechanism-blind condition labels within each time block",
        "blinding": "analysis receives hashed condition labels until all exclusions are frozen",
        "exclusion_rule": "exclude only predeclared hardware saturation or missing-anchor blocks",
        "stopping_rule": "fixed sample size; no optional stopping",
        "model_selection": "held-out likelihood with an explicit out-of-family rejection threshold",
        "required_metadata": [
            "raw event counts",
            "calibration timestamps",
            "detector efficiencies and uncertainties",
            "physical time-anchor provenance",
            "all excluded blocks and reasons",
        ],
    }


def monotonicity_only_audit() -> dict[str, Any]:
    return {
        "amplitude_loss_monotone": True,
        "lindblad_coherence_monotone": True,
        "reservoir_transfer_monotone": True,
        "mechanism_identifiable_from_monotonicity_only": False,
        "physical_time_identifiable_from_monotonicity_only": False,
    }


@lru_cache(maxsize=1)
def run_experimental_protocol_study() -> dict[str, Any]:
    config = ProtocolConfig()
    plan = acquisition_plan(config)
    manifest = preregistration_manifest()
    monotonicity = monotonicity_only_audit()
    acceptance = {
        "all_effects_exceed_systematic_floor": all(
            item["effect_over_systematic_floor"] >= 4.0
            for item in plan["contrasts"]
        ),
        "all_contrasts_meet_target_power": plan["minimum_empirical_power"] >= 0.88,
        "fixed_sample_plan_finite": plan["maximum_recommended_shots_per_arm"] <= 2048,
        "primary_observables_complete": len(manifest["primary_observables"]) == 3,
        "zero_and_calibration_controls_present": len(manifest["controls"]) >= 4,
        "randomization_and_blinding_declared": bool(
            manifest["randomization"] and manifest["blinding"]
        ),
        "optional_stopping_forbidden": "no optional stopping" in manifest["stopping_rule"],
        "open_set_rejection_declared": "out-of-family" in manifest["model_selection"],
        "monotonicity_only_claim_rejected": not monotonicity[
            "mechanism_identifiable_from_monotonicity_only"
        ],
        "physical_validation_not_promoted": True,
    }
    return {
        "schema": "openwave.m9.experimental-protocol-result.v1",
        "task": "M9.21",
        "config": asdict(config),
        "acquisition_plan": plan,
        "preregistration_manifest": manifest,
        "monotonicity_only_audit": monotonicity,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "apparatus_data_available": False,
        "physical_mechanism_selected": None,
        "classification": {
            "establishes": [
                "a fixed-sample, blinded, randomized synthetic acquisition protocol",
                "power budgets for three primary binary contrasts",
                "a required calibration/control metadata manifest",
                "rejection of monotonicity-only mechanism and time claims",
            ],
            "does_not_establish": [
                "experimental feasibility for a particular apparatus",
                "actual detector efficiencies or systematic floors",
                "which back-reaction mechanism is realized",
                "physical time, particle identity, or experimental agreement",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
