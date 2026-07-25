from openwave.xperiments.m9_cat_ept.identified_standing_wave_orbit import (
    run_identified_standing_wave_orbit,
)


def test_identified_standing_wave_orbit_passes():
    result = run_identified_standing_wave_orbit()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["m9_69_branch_instantiated_as_standing_wave_orbit"]
    assert result["decision"]["particle_stability_validated_in_platform"]
    assert result["decision"]["external_experimental_validation"] is False


def test_phase_orbit_closes_on_all_grids():
    result = run_identified_standing_wave_orbit()
    assert max(row["phase_aligned_h1_orbit_error"] for row in result["rows"]) < 0.002
    assert max(row["maximum_energy_drift"] for row in result["rows"]) < 3e-9
