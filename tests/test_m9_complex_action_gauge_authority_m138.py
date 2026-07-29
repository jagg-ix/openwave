from __future__ import annotations

import math

import pytest

from openwave.xperiments.m9_cat_ept.complex_action_gauge_authority_m138 import (
    entropic_time_gradient,
    run_m138_complex_action_gauge_authority,
    variational_complex_weight,
)


def test_m138_global_authority_passes_without_physical_promotion() -> None:
    report = run_m138_complex_action_gauge_authority()
    assert report.passed
    assert report.acceptance["physical_promotion_remains_blocked"]
    assert report.physlib["tip"] == "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
    assert len(report.source_records) == 3
    assert len(report.fingerprint()) == 64


def test_variational_weight_modulus_matches_entropic_gradient() -> None:
    hbar = 2.3
    euler_im = 0.71
    weight = variational_complex_weight(-1.2, euler_im, hbar)
    assert abs(weight) == pytest.approx(
        math.exp(-entropic_time_gradient(euler_im, hbar)), rel=1e-13, abs=1e-13
    )


def test_zero_hbar_is_rejected() -> None:
    with pytest.raises(ValueError, match="hbar"):
        entropic_time_gradient(1.0, 0.0)
    with pytest.raises(ValueError, match="hbar"):
        variational_complex_weight(1.0, 1.0, 0.0)
