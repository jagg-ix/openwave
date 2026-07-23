import pytest

from openwave.xperiments.m9_cat_ept.experimental_protocol import (
    BinaryContrast,
    ProtocolConfig,
    acquisition_plan,
    contrasts,
    monotonicity_only_audit,
    normal_sample_size,
    preregistration_manifest,
    run_experimental_protocol_study,
)


def test_config_validation() -> None:
    with pytest.raises(ValueError):
        ProtocolConfig(alpha=0.8)
    with pytest.raises(ValueError):
        ProtocolConfig(monte_carlo_trials=100)


def test_contrasts_have_nonzero_effects() -> None:
    assert all(contrast.effect > 0.0 for contrast in contrasts())


def test_binary_contrast_rejects_equal_probabilities() -> None:
    with pytest.raises(ValueError):
        BinaryContrast("bad", 0.5, 0.5, "none")


def test_analytic_sample_sizes_are_finite() -> None:
    config = ProtocolConfig()
    assert all(2 <= normal_sample_size(contrast, config) <= 2048 for contrast in contrasts())


def test_acquisition_plan_meets_power() -> None:
    plan = acquisition_plan(ProtocolConfig())
    assert plan["minimum_empirical_power"] >= 0.88
    assert plan["maximum_recommended_shots_per_arm"] <= 2048


def test_preregistration_has_blinding_and_controls() -> None:
    manifest = preregistration_manifest()
    assert manifest["blinding"]
    assert manifest["randomization"]
    assert len(manifest["controls"]) >= 4
    assert "out-of-family" in manifest["model_selection"]


def test_monotonicity_only_is_rejected() -> None:
    audit = monotonicity_only_audit()
    assert audit["mechanism_identifiable_from_monotonicity_only"] is False
    assert audit["physical_time_identifiable_from_monotonicity_only"] is False


def test_full_protocol_passes_without_physical_promotion() -> None:
    result = run_experimental_protocol_study()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["apparatus_data_available"] is False
    assert result["physical_mechanism_selected"] is None
