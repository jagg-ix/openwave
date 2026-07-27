import math

from openwave.xperiments.m9_cat_ept.newton_g_clock_universality import (
    CODATA_PARTICLE_CLOCKS,
    ClockMass,
    Constants,
    audit_clock_universality,
    compton_frequency,
    newton_G_from_clock,
    newton_G_from_mass,
    run_newton_G_clock_universality,
)


def test_mass_and_clock_forms_are_identical():
    constants = Constants()
    for clock in CODATA_PARTICLE_CLOCKS:
        omega = compton_frequency(clock.mass_kg, constants)
        assert math.isclose(
            newton_G_from_mass(clock.mass_kg, constants),
            newton_G_from_clock(omega, constants),
            rel_tol=5e-15,
        )


def test_particle_compton_clocks_fail_universal_G():
    result = run_newton_G_clock_universality()
    assert result["passed"]
    assert not result["particle_clocks_define_one_universal_G"]
    assert not result["particle_clocks_match_measured_G"]
    assert result["particle_clock_G_spread_ratio"] > 1e6
    assert result["decision"]["universal_Planck_scale_anchor_required"]


def test_equal_masses_are_required_for_equal_clock_G():
    mass = CODATA_PARTICLE_CLOCKS[0].mass_kg
    audit = audit_clock_universality(
        (
            ClockMass("first", mass, "same-mass control"),
            ClockMass("second", mass, "same-mass control"),
        )
    )
    assert audit["particle_clocks_define_one_universal_G"]
