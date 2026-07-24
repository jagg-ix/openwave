from openwave.xperiments.m9_cat_ept.coefficient_self_consistency import (
    run_coefficient_self_consistency,
    selected_coefficients,
    sensitivity_campaign,
)


def test_selection_equations_close():
    result = selected_coefficients()
    assert result["maximum_equation_residual"] < 2e-13
    assert result["density_matching_error"] < 2e-14


def test_selected_pair_is_near_m9_59():
    result = selected_coefficients()
    assert result["relative_alpha_shift_from_m9_59"] < 0.1
    assert result["relative_beta_shift_from_m9_59"] < 0.1


def test_selection_scales_with_dispersion():
    result = sensitivity_campaign()
    assert result["alpha_scales_linearly"]
    assert result["beta_scales_linearly"]


def test_full_study_passes():
    result = run_coefficient_self_consistency()
    assert result["passed"]
    assert result["finite_grid_confirmation"]["all_grids_retain_localization"]
