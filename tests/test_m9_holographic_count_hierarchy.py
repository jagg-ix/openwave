from openwave.xperiments.m9_cat_ept.holographic_count_hierarchy import run_holographic_count_hierarchy
from openwave.xperiments.m9_cat_ept.holographic_coarse_graining import run_holographic_coarse_graining


def test_holographic_G_is_species_invariant():
    result = run_holographic_count_hierarchy()
    assert result["passed"]
    assert result["invariants"]["holographic_G_species_invariant"]
    assert result["invariants"]["compton_cell_count_species_invariant"]
    assert not result["decision"]["universal_holographic_G_rejected"]


def test_planck_bits_per_compton_cell_match_mass_ratio():
    result = run_holographic_count_hierarchy()
    for row in result["rows"]:
        assert row["multiplicity_relative_error"] <= 5.0e-15
        assert row["planck_bits_per_compton_cell"] > 1.0


def test_coarse_graining_flow_has_planck_crossover():
    result = run_holographic_coarse_graining()
    assert result["passed"]
    assert abs(result["diagnostics"]["mean_log_slope"] + 2.0) <= 1.0e-12
    assert abs(result["diagnostics"]["crossover_multiplicity"] - 1.0) <= 1.0e-12
    assert not result["interpretation_boundary"]["renormalization_mechanism_constructed"]
