import numpy as np

from openwave.xperiments.m9_cat_ept.gauge_sector_linear_response import (
    GaugeResponseConfig,
    higgs_radial_tangent_selection,
    run_gauge_sector_linear_response,
    site_scalar_source,
    spectral_response,
)


def test_spectral_response_completeness_sum_rule() -> None:
    operator = np.diag(np.asarray((0.0, 1.0, 2.0, 3.0), dtype=np.complex128))
    state = np.asarray((1.0, 2.0, 0.5, -0.25), dtype=np.complex128)
    observable = site_scalar_source((2, 1), 2, (1.0, 0.35))
    cfg = GaugeResponseConfig(frequency_points=201)

    response = spectral_response(
        operator, state, observable, cfg.broadening, cfg.frequency_points
    )

    assert response["sum_rule_relative_error"] <= 2.0e-14
    assert np.all(response["response"] >= 0.0)


def test_higgs_radial_source_has_no_tangent_strength() -> None:
    selection = higgs_radial_tangent_selection()

    assert selection["radial_strength"] == 1.0
    assert selection["tangent_strength"] == 0.0
    assert selection["completeness_error"] == 0.0


def test_gauge_sector_response_campaign_passes_without_decay_promotion() -> None:
    result = run_gauge_sector_linear_response()

    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["gauge_invariant_transition_response_constructed"]
    assert result["decision"]["spectral_completeness_sum_rules_closed"]
    assert not result["decision"]["intrinsic_decay_channel_constructed"]
    assert not result["decision"]["physical_transition_or_decay_identified"]
    assert not any(result["claim_boundary"].values())
