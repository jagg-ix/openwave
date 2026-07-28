from openwave.xperiments.m9_cat_ept.planckian_discriminator_m127 import run_planckian_discriminator


def test_discriminator_reports_aggregate_and_mixed_fold_results():
    result = run_planckian_discriminator()
    assert result["passed"]
    assert result["aggregate"]["fixed_mean_absolute_log_error"] < result["aggregate"]["fitted_mean_absolute_log_error"]
    assert result["aggregate"]["fixed_fold_wins"] == 1
    assert not result["decision"]["paper_level_preference_is_consistent"]
    assert not result["decision"]["existing_rounded_dataset_discriminates_entropic_time"]
