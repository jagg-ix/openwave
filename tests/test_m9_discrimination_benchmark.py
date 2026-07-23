import numpy as np
import pytest

from openwave.xperiments.m9_cat_ept.discrimination_benchmark import (
    BenchmarkConfig,
    OBSERVABLES,
    classify,
    confusion_benchmark,
    noisy_observation,
    out_of_family_benchmark,
    run_discrimination_benchmark,
    signature,
    trace_only_ambiguity,
)


def test_config_validation() -> None:
    with pytest.raises(ValueError):
        BenchmarkConfig(noise_sigma=0.0)
    with pytest.raises(ValueError):
        BenchmarkConfig(rate_points=10)


def test_mechanism_signatures_are_bounded() -> None:
    times = np.linspace(0.0, 5.0, 21)
    for mechanism in (
        "imaginary_action",
        "lindblad_dephasing",
        "explicit_reservoir",
    ):
        values = signature(mechanism, times, 0.2)
        for observable in OBSERVABLES:
            assert np.all(values[observable] >= 0.0)
            assert np.all(values[observable] <= 1.0)


def test_noisy_classification_recovers_each_mechanism() -> None:
    config = BenchmarkConfig(noise_sigma=0.005, trials_per_mechanism=5)
    rng = np.random.default_rng(7)
    rates = {
        "imaginary_action": 0.17,
        "lindblad_dephasing": 0.23,
        "explicit_reservoir": 0.12,
    }
    for mechanism, rate in rates.items():
        observed = noisy_observation(mechanism, rate, config, rng)
        assert classify(observed, config, OBSERVABLES)["predicted"] == mechanism


def test_confusion_benchmark_has_high_accuracy() -> None:
    result = confusion_benchmark(BenchmarkConfig(trials_per_mechanism=10))
    assert result["accuracy"] >= 0.95
    assert result["minimum_validation_margin"] > 0.0


def test_trace_only_ambiguity_is_exact() -> None:
    result = trace_only_ambiguity(BenchmarkConfig())
    assert result["maximum_trace_difference"] <= 1e-14
    assert result["structurally_identifiable_from_trace_only"] is False


def test_out_of_family_signature_is_rejected() -> None:
    result = out_of_family_benchmark(BenchmarkConfig())
    assert result["rejected"]


def test_full_benchmark_does_not_select_physical_mechanism() -> None:
    result = run_discrimination_benchmark()
    assert result["selected_physical_mechanism"] is None
    assert result["classification"]["does_not_establish"]


def test_full_benchmark_passes() -> None:
    result = run_discrimination_benchmark()
    assert result["passed"]
    assert all(result["acceptance"].values())
