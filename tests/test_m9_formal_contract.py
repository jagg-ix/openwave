"""Tests for the M9 CAT/EPT formal-contract transcription."""

from __future__ import annotations

import math

import pytest

from openwave.xperiments.m9_cat_ept.formal_contract import (
    correlation_weight_norm,
    ed_wave_function,
    load_contract,
    run_conformance_suite,
    total_correlation,
)


def test_contract_is_pinned_to_exact_source_commit() -> None:
    contract = load_contract()
    source = contract["formal_source"]
    assert source["branch"] == "entropic-physlib-linear-full"
    assert source["commit"] == "f6e2b37571086e5ef6de40f77439a5eab468f71f"
    assert source["lean_version"] == "4.29.1"


def test_conformance_suite_passes() -> None:
    result = run_conformance_suite()
    assert result["passed"] is True
    assert all(check["passed"] for check in result["checks"])
    assert all(result["properties"].values())


def test_total_correlation_is_zero_for_factorized_distribution() -> None:
    independent = [[0.12, 0.28], [0.18, 0.42]]
    assert total_correlation(independent) == pytest.approx(0.0, abs=1.0e-12)


def test_total_correlation_and_weight_for_correlated_distribution() -> None:
    correlated = [[0.4, 0.1], [0.1, 0.4]]
    correlation = total_correlation(correlated)
    assert correlation > 0.0
    assert correlation_weight_norm(1.0, correlated) == pytest.approx(
        math.exp(-correlation), abs=1.0e-12
    )
    assert correlation_weight_norm(1.0, correlated) < 1.0


def test_wave_function_rejects_negative_density() -> None:
    with pytest.raises(ValueError, match="rho must be nonnegative"):
        ed_wave_function(-1.0, 0.0)


def test_joint_distribution_must_be_normalized() -> None:
    with pytest.raises(ValueError, match="must sum to 1"):
        total_correlation([[0.2, 0.2], [0.2, 0.2]])
