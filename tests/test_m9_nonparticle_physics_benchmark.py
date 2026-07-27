from openwave.xperiments.m9_cat_ept.nonparticle_physics_benchmark import run_entropic_proper_time_control, run_fokker_planck_control, run_irreversible_clock_control, run_kinetic_kolmogorov_control, run_nonparticle_physics_benchmark, run_screen_gravity_control, run_stokes_dissipation_control


def test_irreversible_and_reversible_clock_controls() -> None:
    result = run_irreversible_clock_control()
    assert result["passed"]
    assert result["largest_clock_increment"] <= 0
    assert result["semigroup_error"] < 1e-14
    assert result["unitary_clock_range"] < 1e-13


def test_proper_time_and_fokker_planck_controls() -> None:
    proper, fp = run_entropic_proper_time_control(), run_fokker_planck_control()
    assert proper["passed"] and proper["error"] < 1e-14
    assert fp["passed"] and fp["flux_error"] < 1e-14 and fp["rate_error"] < 1e-14


def test_kinetic_stokes_and_gravity_controls() -> None:
    kinetic, stokes, gravity = run_kinetic_kolmogorov_control(), run_stokes_dissipation_control(), run_screen_gravity_control()
    assert kinetic["passed"] and kinetic["minimum_covariance_eigenvalue"] > 0
    assert stokes["passed"] and stokes["final_energy"] < stokes["initial_energy"]
    assert gravity["passed"] and gravity["coupling_range"] < 1e-15 and gravity["equivalence_error"] < 1e-14


def test_composed_nonparticle_benchmark_passes_without_physical_promotion() -> None:
    result = run_nonparticle_physics_benchmark()
    assert result["passed"] and len(result["results"]) == 6
    assert all(control["passed"] for control in result["results"].values())
    assert not result["decision"]["physical_calibration_complete"]
    assert not result["decision"]["heldout_external_validation_complete"]
