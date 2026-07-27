from openwave.xperiments.m9_cat_ept.gauge_sector_spectral_refinement import (
    run_gauge_sector_spectral_refinement,
    strictly_decreasing,
)


def test_refinement_errors_and_cluster_changes_decrease() -> None:
    result = run_gauge_sector_spectral_refinement()
    rows = result["rows"]

    assert strictly_decreasing(
        [row["flat_strong_relative_error"] for row in rows]
    )
    assert strictly_decreasing(
        [row["flat_electroweak_relative_error"] for row in rows]
    )
    assert strictly_decreasing(result["strong_cluster_relative_changes"])
    assert strictly_decreasing(result["electroweak_cluster_relative_changes"])


def test_spectral_refinement_campaign_passes_without_continuum_promotion() -> None:
    result = run_gauge_sector_spectral_refinement()
    ledger = result["phenomenology_ledger"]

    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["finite_gauge_spectral_refinement_constructed"]
    assert not result["decision"]["continuum_spectrum_theorem_complete"]
    assert not ledger["physical_unit_calibration_complete"]
    assert not ledger["particle_or_sector_identity_promoted"]
    assert not ledger["out_of_sample_prediction_ready"]
    assert not any(result["claim_boundary"].values())
