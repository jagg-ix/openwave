from dataclasses import replace

from openwave.xperiments.m9_cat_ept.criterion_maturity import MATURITY_ROWS
from openwave.xperiments.m9_cat_ept.criterion_maturity_current import (
    canonical_payload,
    derive_headline,
    run_criterion_maturity_study,
)


def test_all_21_rows_are_reclassified_without_frozen_partial_bucket():
    result = run_criterion_maturity_study()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["headline_counts"] == {
        "validated_in_scope": 7,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 1,
    }
    assert result["legacy_partial_breakdown"] == {
        "validated_in_scope": 0,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 0,
    }


def test_known_rows_have_precise_headlines():
    rows = {row["key"]: row for row in canonical_payload()["criteria"]}
    assert rows["electron_rest_energy"]["headline"] == "calibration_pending"
    assert rows["de_broglie_clock"]["headline"] == "conditional_validated"
    assert rows["magnetic_moment_spin"]["headline"] == "conditional_validated"
    assert rows["antimatter_annihilation"]["headline"] == "reduced_model_validated"
    assert rows["electric_force"]["headline"] == "conditional_validated"
    assert rows["magnetic_force"]["headline"] == "conditional_validated"
    assert rows["strong_force"]["headline"] == "reduced_model_validated"
    assert rows["weak_force"]["headline"] == "reduced_model_validated"
    assert rows["gravity"]["headline"] == "conditional_validated"


def test_headline_changes_when_evidence_axes_change():
    source = next(row for row in MATURITY_ROWS if row.key == "electric_force")
    assert derive_headline(source) == "conditional_validated"
    stable_and_scoped = replace(
        source,
        state="stable_constructed",
        identity="not_required_for_scope",
        calibration="not_required_for_scope",
        prediction="validated_internal",
    )
    assert derive_headline(stable_and_scoped) == "validated_in_scope"
    failed = replace(source, numerical="negative", prediction="negative_out_of_sample")
    assert derive_headline(failed) == "negative"


def test_policy_does_not_use_promoted_keys_or_7_13_1_gate():
    policy = canonical_payload()["policy"]
    assert not policy["fixed_promoted_key_set_used"]
    assert not policy["fixed_7_13_1_count_used_as_acceptance_gate"]
