"""M9.20 noisy open-set discrimination benchmark.

The benchmark asks whether accessible trace, normalized purity, and explicit
reservoir transfer can distinguish the three selected M9 back-reaction
interfaces under controlled synthetic noise. It also exposes two negative
results: trace-only measurements cannot distinguish amplitude loss from a
rescaled reservoir sink, and out-of-family observations must be rejectable.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from typing import Any, Iterable

import numpy as np

MECHANISMS = ("imaginary_action", "lindblad_dephasing", "explicit_reservoir")
OBSERVABLES = ("trace", "purity", "reservoir")


@dataclass(frozen=True)
class BenchmarkConfig:
    rate_min: float = 0.05
    rate_max: float = 0.35
    rate_points: int = 241
    noise_sigma: float = 0.015
    trials_per_mechanism: int = 40
    times: tuple[float, ...] = tuple(np.linspace(0.0, 5.0, 21))

    def __post_init__(self) -> None:
        if not 0.0 < self.rate_min < self.rate_max:
            raise ValueError("invalid rate interval")
        if self.rate_points < 20:
            raise ValueError("rate_points must be at least 20")
        if self.noise_sigma <= 0.0:
            raise ValueError("noise_sigma must be positive")
        if self.trials_per_mechanism < 5:
            raise ValueError("trials_per_mechanism must be at least five")
        if len(self.times) < 8 or self.times[0] != 0.0:
            raise ValueError("times must contain at least eight points starting at zero")


def signature(mechanism: str, times: np.ndarray, rate: float) -> dict[str, np.ndarray]:
    if mechanism not in MECHANISMS:
        raise KeyError(f"unknown mechanism: {mechanism}")
    if rate < 0.0:
        raise ValueError("rate must be nonnegative")
    decay = np.exp(-rate * times)
    if mechanism == "imaginary_action":
        trace = decay**2
        purity = np.ones_like(times)
        reservoir = np.zeros_like(times)
    elif mechanism == "lindblad_dephasing":
        trace = np.ones_like(times)
        purity = 0.5 + 0.5 * decay**4
        reservoir = np.zeros_like(times)
    else:
        trace = decay
        purity = np.ones_like(times)
        reservoir = 1.0 - decay
    return {"trace": trace, "purity": purity, "reservoir": reservoir}


def noisy_observation(
    mechanism: str,
    rate: float,
    config: BenchmarkConfig,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    truth = signature(mechanism, np.asarray(config.times), rate)
    return {
        name: np.clip(values + rng.normal(0.0, config.noise_sigma, values.shape), 0.0, 1.0)
        for name, values in truth.items()
    }


def residual_sum_squares(
    observed: dict[str, np.ndarray],
    predicted: dict[str, np.ndarray],
    observables: Iterable[str],
    indices: np.ndarray,
) -> float:
    return float(
        sum(
            np.sum((observed[name][indices] - predicted[name][indices]) ** 2)
            for name in observables
        )
    )


def fit_candidate(
    mechanism: str,
    observed: dict[str, np.ndarray],
    config: BenchmarkConfig,
    observables: tuple[str, ...],
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
) -> dict[str, float]:
    times = np.asarray(config.times)
    rates = np.linspace(config.rate_min, config.rate_max, config.rate_points)
    train_scores = []
    for rate in rates:
        predicted = signature(mechanism, times, float(rate))
        train_scores.append(
            residual_sum_squares(observed, predicted, observables, train_indices)
        )
    best_index = int(np.argmin(train_scores))
    best_rate = float(rates[best_index])
    predicted = signature(mechanism, times, best_rate)
    validation_rss = residual_sum_squares(
        observed,
        predicted,
        observables,
        validation_indices,
    )
    points = len(validation_indices) * len(observables)
    normalized_validation_rss = validation_rss / points
    return {
        "best_rate": best_rate,
        "train_rss": float(train_scores[best_index]),
        "validation_rss": validation_rss,
        "normalized_validation_rss": normalized_validation_rss,
    }


def classify(
    observed: dict[str, np.ndarray],
    config: BenchmarkConfig,
    observables: tuple[str, ...],
) -> dict[str, Any]:
    indices = np.arange(len(config.times))
    train = indices[::2]
    validation = indices[1::2]
    fits = {
        mechanism: fit_candidate(
            mechanism,
            observed,
            config,
            observables,
            train,
            validation,
        )
        for mechanism in MECHANISMS
    }
    ordered = sorted(
        fits,
        key=lambda name: fits[name]["normalized_validation_rss"],
    )
    best, second = ordered[:2]
    margin = (
        fits[second]["normalized_validation_rss"]
        - fits[best]["normalized_validation_rss"]
    )
    reject_threshold = 16.0 * config.noise_sigma**2
    rejected = fits[best]["normalized_validation_rss"] > reject_threshold
    return {
        "predicted": "out_of_family" if rejected else best,
        "best_in_family": best,
        "runner_up": second,
        "validation_margin": margin,
        "rejected": rejected,
        "fits": fits,
    }


def confusion_benchmark(config: BenchmarkConfig) -> dict[str, Any]:
    rng = np.random.default_rng(20260723)
    rates = {
        "imaginary_action": 0.17,
        "lindblad_dephasing": 0.23,
        "explicit_reservoir": 0.12,
    }
    confusion = {
        truth: {prediction: 0 for prediction in (*MECHANISMS, "out_of_family")}
        for truth in MECHANISMS
    }
    margins: list[float] = []
    correct = 0
    total = 0
    for truth in MECHANISMS:
        for _ in range(config.trials_per_mechanism):
            observed = noisy_observation(truth, rates[truth], config, rng)
            result = classify(observed, config, OBSERVABLES)
            prediction = result["predicted"]
            confusion[truth][prediction] += 1
            margins.append(float(result["validation_margin"]))
            correct += int(prediction == truth)
            total += 1
    return {
        "confusion": confusion,
        "accuracy": correct / total,
        "trials": total,
        "minimum_validation_margin": min(margins),
        "median_validation_margin": float(np.median(margins)),
    }


def trace_only_ambiguity(config: BenchmarkConfig) -> dict[str, Any]:
    times = np.asarray(config.times)
    amplitude_rate = 0.12
    reservoir_rate = 2.0 * amplitude_rate
    amplitude_trace = signature("imaginary_action", times, amplitude_rate)["trace"]
    reservoir_trace = signature("explicit_reservoir", times, reservoir_rate)["trace"]
    return {
        "amplitude_rate": amplitude_rate,
        "equivalent_reservoir_rate": reservoir_rate,
        "maximum_trace_difference": float(np.max(np.abs(amplitude_trace - reservoir_trace))),
        "structurally_identifiable_from_trace_only": False,
    }


def out_of_family_benchmark(config: BenchmarkConfig) -> dict[str, Any]:
    times = np.asarray(config.times)
    observed = {
        "trace": np.clip(0.72 + 0.20 * np.sin(1.7 * times), 0.0, 1.0),
        "purity": np.clip(0.68 + 0.18 * np.cos(1.1 * times), 0.0, 1.0),
        "reservoir": np.clip(0.15 + 0.11 * np.sin(2.3 * times + 0.4), 0.0, 1.0),
    }
    classification = classify(observed, config, OBSERVABLES)
    return {
        "classification": classification,
        "rejected": classification["rejected"],
        "best_normalized_validation_rss": classification["fits"]
        [classification["best_in_family"]]["normalized_validation_rss"],
    }


def noise_sensitivity() -> list[dict[str, float]]:
    results = []
    for noise in (0.005, 0.015, 0.03):
        config = BenchmarkConfig(noise_sigma=noise, trials_per_mechanism=20)
        benchmark = confusion_benchmark(config)
        results.append({"noise_sigma": noise, "accuracy": benchmark["accuracy"]})
    return results


@lru_cache(maxsize=1)
def run_discrimination_benchmark() -> dict[str, Any]:
    config = BenchmarkConfig()
    full = confusion_benchmark(config)
    trace_only = trace_only_ambiguity(config)
    open_set = out_of_family_benchmark(config)
    sensitivity = noise_sensitivity()
    acceptance = {
        "full_panel_accuracy_high": full["accuracy"] >= 0.95,
        "all_full_panel_margins_positive": full["minimum_validation_margin"] > 0.0,
        "trace_only_ambiguity_exposed": (
            trace_only["maximum_trace_difference"] <= 1e-14
            and not trace_only["structurally_identifiable_from_trace_only"]
        ),
        "out_of_family_case_rejected": open_set["rejected"],
        "noise_sensitivity_monotone": all(
            sensitivity[index]["accuracy"] >= sensitivity[index + 1]["accuracy"]
            for index in range(len(sensitivity) - 1)
        ),
        "no_mechanism_selected_from_synthetic_data": True,
    }
    return {
        "schema": "openwave.m9.discrimination-benchmark-result.v1",
        "task": "M9.20",
        "config": {
            "rate_interval": [config.rate_min, config.rate_max],
            "rate_points": config.rate_points,
            "noise_sigma": config.noise_sigma,
            "trials_per_mechanism": config.trials_per_mechanism,
            "time_points": len(config.times),
        },
        "full_panel": full,
        "trace_only": trace_only,
        "open_set": open_set,
        "noise_sensitivity": sensitivity,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "selected_physical_mechanism": None,
        "classification": {
            "establishes": [
                "high synthetic discrimination with trace, purity, and reservoir observables",
                "structural trace-only ambiguity between two rate-rescaled mechanisms",
                "open-set rejection of one out-of-family signature",
                "a deterministic held-out fitting benchmark",
            ],
            "does_not_establish": [
                "performance on experimental apparatus data",
                "correctness of the assumed Gaussian noise model",
                "which mechanism is physically realized",
                "physical calibration or particle identity",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
